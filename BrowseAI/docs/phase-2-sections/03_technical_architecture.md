# Technical Architecture: Manifest V3, Build Engine, and Lifecycle

## Chrome Manifest V3 Specifications

The NexusAI extension targets Google Chrome Manifest V3 (MV3). MV3 replaces persistent background pages with ephemeral service workers and enforces a declarative security model.

### Key Manifest Configuration
The extension manifest configuration in `packages/extension/wxt.config.ts` defines the following core attributes:
- **Default Locale**: Configured to `en`. All UI messages are sourced exclusively from `_locales/en/messages.json`.
- **Identity & Keys**: The `key` attribute is deliberately omitted, enabling Chrome to assign a fresh, distinct extension ID upon installation without colliding with previous installations.
- **Permissions**:
  - `activeTab`, `tabs`: Tab querying, creation, and state observation.
  - `debugger`: Direct attachment via Chrome DevTools Protocol (CDP) for low-level DOM inspection, event synthesis, and performance tracing.
  - `offscreen`: Creation of background DOM contexts for long-running processes and audio/image encoding.
  - `storage`: High-speed local persistence using Chrome's built-in IndexedDB and local storage APIs.
  - `nativeMessaging`: Local inter-process communication (IPC) with the NexusAI native host application.

```typescript
// packages/extension/wxt.config.ts (Extract)
export default defineConfig({
  srcDir: '.',
  modules: ['@wxt-dev/module-vue'],
  manifest: {
    name: 'NexusAI Browser Agent',
    description: 'Autonomous browser automation runtime for Antigravity',
    default_locale: 'en',
    action: {
      default_title: 'NexusAI Browser Agent',
    },
    permissions: [
      'activeTab',
      'tabs',
      'debugger',
      'storage',
      'offscreen',
      'nativeMessaging',
    ],
  },
  vite: () => ({
    build: {
      target: 'es2022',
    },
  }),
});
```

## The WXT and Vite 5 Build Engine Patch

During the initial build phase, running `wxt build` triggered catastrophic build failures during Rollup module resolution. Modules threw unexpected errors:
```
[vite:resolve-virtual] throwOutdatedRequest
[vite:download] fetchCached failed for virtual module
```

### Root Cause Analysis
WXT version 0.20.27 was designed with anticipation of Rolldown (the Rust-based Rollup successor). As part of this design, several internal WXT plugins (including `download.mjs`, `wxtPluginLoader.mjs`, `resolveVirtualModules.mjs`, `noopBackground.mjs`, and `extensionApiMock.mjs`) authored their plugin hooks using the experimental object format:
```javascript
// Rolldown hook format in WXT
resolveId: {
  filter: { id: /^virtual:wxt-/ },
  handler(id) { /* module resolution */ }
}
```

Under Vite 5.4.21 and standard Rollup 4, Rollup expects hook functions directly (`resolveId(id)`). When passed an object, Rollup checks if the object itself is callable or treats the object as a plugin hook without evaluating `filter`. Consequently, the inner `handler` was invoked on every single file across `node_modules` regardless of whether the module matched the virtual prefix. This caused non-virtual imports to be hijacked and corrupted.

### Engineering Resolution: Hook Interceptor Wrapper
To solve this issue without degrading build performance, we implemented an in-flight wrapper function, `wrapPluginForVite`, within WXT's Vite builder subsystem (`wxt/dist/core/builders/vite/index.mjs`).

The wrapper inspects each plugin registered in Vite's plugin pipeline. For any hook defined as `{ filter, handler }`, it wraps the hook in a standard function that strictly evaluates the regular expression filter before invoking the underlying handler:

```javascript
function wrapPluginForVite(plugin) {
  if (!plugin || typeof plugin !== 'object') return plugin;
  const wrapped = { ...plugin };
  const hooks = ['resolveId', 'load', 'transform'];
  for (const hook of hooks) {
    const original = wrapped[hook];
    if (original && typeof original === 'object' && typeof original.handler === 'function') {
      const { filter, handler } = original;
      wrapped[hook] = function (id, ...args) {
        if (filter?.id instanceof RegExp && !filter.id.test(id)) {
          return null; // Skip execution if ID does not match filter
        }
        return handler.call(this, id, ...args);
      };
    }
  }
  return wrapped;
}
```
Applying this fix resolved the virtual resolution failure immediately, reducing build times from an error state to a clean 28.9-second production compile.

## JavaScript Target Migration: ES2015 to ES2022

The legacy configuration used `es2015` as its build target. When bundling `@nexusai/extension`, the embedded ONNX WebAssembly SIMD runtime (`onnxruntime-web`) generated esbuild transform errors due to native BigInt numeric literals (`1n`, `0n`).

Chromium Manifest V3 extensions run inside modern Chromium environments (versions 120+) that natively support ES2022 features including:
- Top-level `await`
- Class fields and private identifiers
- Native BigInt math operations
- Regular expression indices (`/d` flag)

We updated the Vite build target in `wxt.config.ts` to `es2022`. This eliminated the transpilation bottleneck, enabled clean compilation of all machine learning vector calculation routines, and avoided unnecessary polyfill overhead in the final bundle.

## Background Service Worker Keepalive Architecture

Chrome Manifest V3 terminates background service workers after approximately 30 seconds of idle time. In an autonomous agent workflow, an AI assistant may spend 45 to 90 seconds planning complex tool chains or evaluating web page content before issuing its next browser command. If the service worker terminates during this window, active debugger sessions detach and in-memory execution contexts are lost.

### Offscreen Document Keepalive Protocol
To guarantee runtime resilience, NexusAI implements a dual-layer keepalive protocol coordinating between the Background Service Worker and a dedicated Offscreen Document:

1. **Protocol Constants (`packages/extension/common/rr-v3-keepalive-protocol.ts`)**:
   - `RR_V3_KEEPALIVE_PORT_NAME`: `'rr_v3_keepalive'`
   - `DEFAULT_KEEPALIVE_PING_INTERVAL_MS`: `20_000` (20 seconds)
   - `MAX_KEEPALIVE_PING_INTERVAL_MS`: `25_000` (25 seconds)

2. **Handshake Lifecycle**:
   - When the extension initializes, the service worker checks `chrome.offscreen.hasDocument()`. If absent, it creates `offscreen.html` with the `BLOBS` and `LOCAL_STORAGE` reasons.
   - The offscreen document establishes a persistent connection port (`chrome.runtime.connect`) with name `'rr_v3_keepalive'`.
   - Every 20 seconds, the offscreen document transmits a `keepalive.ping` message with the current timestamp.
   - The service worker responds with `keepalive.pong`. This active message transit resets Chrome's internal 30-second idle timer, maintaining continuous operational readiness without unbounded memory leakage.
