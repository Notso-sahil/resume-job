# Deep Tech Subsystems: Semantic Intelligence, Marker Engine, and CDP Bridge

## Semantic Similarity Engine

Autonomous agents often need to locate interactive elements based on semantic intent rather than brittle CSS paths or volatile DOM attributes. For example, finding a button that says "Register for Free" when the user requested to "Create Account".

NexusAI includes an in-browser Semantic Similarity Engine (`packages/extension/utils/semantic-similarity-engine.ts`) operating entirely on the local client:

### 1. Architecture and Execution Context
- **Web Worker Offloading (`packages/extension/workers/similarity.worker.js`)**: To prevent vector computations from blocking the UI thread or tab rendering, all vector embedding generations execute inside a background worker.
- **ONNX Runtime Web Integration**: The engine utilizes `ort-web` with WebAssembly SIMD execution providers. It loads a compact sentence-transformer embedding model directly into client memory.
- **Cosine Distance Computation**: The engine normalizes vectors and computes pairwise cosine similarity between the natural language directive and candidate DOM element metadata (text content, placeholder, ARIA label, and tooltip).

```typescript
// packages/extension/utils/semantic-similarity-engine.ts (Extract)
export function cosineSimilarity(vecA: Float32Array, vecB: Float32Array): number {
  let dotProduct = 0.0;
  let normA = 0.0;
  let normB = 0.0;
  for (let i = 0; i < vecA.length; i++) {
    dotProduct += vecA[i] * vecB[i];
    normA += vecA[i] * vecA[i];
    normB += vecB[i] * vecB[i];
  }
  if (normA === 0 || normB === 0) return 0.0;
  return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}
```

### 2. Algorithmic Fallback Matrix
When running in restricted environments (such as headless Chromium without WebGL or WebAssembly hardware acceleration), the engine automatically degrades to a multi-signal lexical matcher combining:
- Normalized Levenshtein edit distance
- Token-level Jaccard set intersection
- Prefix and substring containment scoring

This dual-tier approach guarantees that element discovery remains functional regardless of the underlying machine capabilities.

## The Element Marker Engine

To allow the AI agent to "see" the interactive surface of a page without processing multi-megabyte image payloads for every action, NexusAI utilizes a deterministic Element Marker system (`packages/extension/inject-scripts/element-marker.js`):

1. **DOM Tree Traversal**: The marker traverses the active document, identifying interactive elements (buttons, links, inputs, selects, textareas, and elements with `role="button"` or click handlers).
2. **Deterministic Numbering & Overlays**: Each discovered element is assigned an index badge displayed as a discrete visual overlay on the page.
3. **Selector Fingerprinting**: For each marked element, the engine generates multiple resilient selector strategies:
   - Unique CSS selector path
   - ARIA label and role combination
   - Text content and parent container relationship
   - DOM tree coordinate index
4. **Agent Consumption**: The complete marked tree is serialized into a lightweight structured JSON payload sent to the AI agent, allowing the model to specify actions using simple, unambiguous targets (e.g. `click_element(marker_id: 14)`).

## Chrome DevTools Protocol (CDP) Bridge

Standard browser extension content script APIs cannot reliably simulate user interactions on complex enterprise web applications (e.g. canvas elements, closed Shadow DOMs, or applications with strict `isTrusted` event validation).

NexusAI leverages direct Chrome DevTools Protocol attachment via the `chrome.debugger` API:

| CDP Domain | Purpose within NexusAI |
| :--- | :--- |
| **`Page`** | Page navigation, screenshot capture (viewport and full page), and layout lifecycle event monitoring. |
| **`DOM`** | Deep document querying, bounding box retrieval, and node inspection across iframe boundaries. |
| **`Input`** | Low-level dispatch of mouse events (`mousePressed`, `mouseReleased`, `mouseMoved`) and keyboard strokes with synthetic touch and scroll coordinates. |
| **`Runtime`** | Execution of sandboxed JavaScript expressions and asynchronous evaluation within isolated execution contexts. |
| **`Network`** | Request interception, header analysis, cookie management, and status code verification. |
| **`Log` / `Console`**| Persistent capture of console warnings, exceptions, and stdout streams via `ConsoleBuffer`. |

## Native Messaging and Port 12307 Relay

The extension interacts with the local operating system through a two-step communication pipeline:
1. **Chrome Native Messaging Host (`com.nexusai.browserhost`)**: An approved native manifest registers the local bridge process with Chrome, establishing high-throughput standard I/O byte streams.
2. **Fastify MCP Server (Port 12307)**: The bridge process runs a local Fastify HTTP/JSON-RPC server listening on `127.0.0.1:12307`. External tools (including Antigravity and CLI utilities) communicate with this server using the standard Model Context Protocol (MCP). The bridge translates MCP tool calls directly into Native Messaging messages routed into the extension background service worker.
