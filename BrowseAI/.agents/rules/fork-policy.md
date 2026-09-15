# Fork Policy Rules

## Rule 1: Always Generate an Implementation Plan First

Before writing any code, making any structural changes, or executing any phase of this project, you MUST:

1. Create or update `implementation_plan.md` in the artifacts directory with a detailed plan.
2. Present the plan to the user and request explicit approval.
3. Only begin execution after the user has approved the plan.

**No exceptions.** Even for "small" changes — if they affect files in `packages/`, the bridge, or the extension, a plan must be written first.

---

## Rule 2: Smart Copying Policy

This project is a fork of open-source code from `hangwin/mcp-chrome`. We are building a clean, independent product called **NexusAI Browser Agent**. The following rules govern what can and cannot be copied:

### ✅ What You CAN Copy or Derive From

These are permissible because they are open-source (MIT licensed) and contain no proprietary backend:
- Extension source code (TypeScript/Vue components from `app/chrome-extension/`)
- Native server source (TypeScript from `app/native-server/`)
- Shared package source (from `packages/shared/`)
- Chrome Extension API usage patterns
- MCP protocol message format and type definitions
- Build configuration (WXT, tsup, pnpm workspace setup)
- Inject scripts (`inject-scripts/*.js`) — DOM manipulation helpers

### ❌ What You CANNOT Copy or Must Rebuild

These items depend on hangwin's private infrastructure, proprietary accounts, or backend services that we do NOT have access to:
- **npm registry packages**: `chrome-mcp-shared`, `mcp-chrome-bridge` — we must replace these with our own `@nexusai/shared` and `@nexusai/bridge` packages.
- **The published Chrome Web Store extension** — we load unpacked; we do not publish under their ID.
- **Their extension ID** — we never hardcode `hbdgbgagpkpjffpklnamcljpakneikee` or any of their IDs into our code.
- **Their `key` field in manifest.json** — the manifest key is what locks an extension to a specific ID. We omit it entirely so Chrome generates a fresh ID.
- **Their native messaging host name** `com.chromemcp.nativehost` — we use `com.nexusai.browserhost`.
- **Their database schemas or stored data** — if any feature relies on a backend API or cloud service they own, we do NOT attempt to replicate or call it. We build a local-only alternative.
- **Their registry keys** — we write only to `HKCU\...\com.nexusai.browserhost`.
- **Their release CDN / GitHub releases** — we never fetch their pre-built binaries; we build from source.

### 🔄 What You Must Rebuild From Scratch

If a feature cannot be cleanly copied due to proprietary dependencies:
- Rebuild it from the Chrome Extension API specification and MCP specification directly.
- Document the new implementation in the appropriate phase Word document.
- Note in a code comment: `// NexusAI implementation — rebuilt from spec, not copied.`

---

## Rule 3: No Proprietary Identifiers in Code

**Search and replace all occurrences of the following before any file is committed:**

| Find | Replace With |
|:---|:---|
| `hangwin` | (remove entirely) |
| `hangye` | (remove entirely) |
| `chrome-mcp-server` | `nexus-browser` |
| `mcp-chrome-bridge` | `nexus-bridge` |
| `chrome-mcp-shared` | `@nexusai/shared` |
| `com.chromemcp.nativehost` | `com.nexusai.browserhost` |
| `Chrome MCP` (UI text) | `NexusAI Browser Agent` |
| `12306` (port) | `12307` |
| Chinese text (any) | English equivalent |

---

## Rule 4: 100% Original UI Text & Placeholders (No Copying or Direct Translation)

- Every comment, log message, UI string, variable name, and documentation in this project MUST be in English.
- No Chinese characters anywhere in the source tree.
- **Do NOT copy or directly translate UI strings, placeholders, or tool descriptions from the original project.**
- Write **completely new, original, and modern English copy**, placeholders, labels, and status messages designed specifically for NexusAI Browser Agent.

---

## Rule 5: Source Attribution

In `LICENSE` and `README.md`, acknowledge the original MIT-licensed project:

```
This project is based on concepts from hangwin/mcp-chrome (MIT License).
The NexusAI Browser Agent is an independent reimplementation with additional
features, full English localization, and a different architecture.
```

This satisfies the MIT license attribution requirement while making clear that NexusAI Browser Agent is an independent product.
