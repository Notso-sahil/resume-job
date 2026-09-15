# NexusAI Bridge

Fastify-based Model Context Protocol (MCP) server and Native Messaging relay for **NexusAI Browser Agent**.

## Overview

`@nexusai/bridge` functions as the bidirectional translation layer connecting MCP clients (such as Google Antigravity, Claude Desktop, or custom agent engines) with the NexusAI Chrome Extension.

- **MCP Transport**: Exposes a streamable HTTP JSON-RPC endpoint at `http://127.0.0.1:12307/mcp`.
- **Native Messaging Relay**: Communicates with Google Chrome via standard input/output (`stdio`) streams under the native host identifier `com.nexusai.browserhost`.
- **Local Storage Isolation**: Retains session history, workflows, and database records strictly inside `~/.nexusai-agent/agent.db`.

---

## Installation & Setup

Build and register the bridge using the root setup scripts:

```powershell
# Windows
.\build-and-install.ps1

# macOS / Linux
./build-and-install.sh
```

Or execute package commands:

```bash
pnpm install
pnpm --filter @nexusai/bridge build
node scripts/install-host.mjs
```

---

## CLI Usage

Run the `nexus-bridge` CLI directly:

```bash
# Start the MCP server on default port 12307
nexus-bridge start

# Specify a custom port
nexus-bridge start --port 12308

# Register Chrome Native Messaging Host manifests
nexus-bridge register

# Inspect current configuration
nexus-bridge info
```

---

## Architecture

```
Antigravity (MCP Client)
         │  HTTP / JSON-RPC
         ▼
NexusAI Bridge (:12307)
         │  Native Messaging (stdio)
         ▼
Google Chrome Background Worker
         │  Chrome Scripting / CDP
         ▼
Target Web Pages & Active Tabs
```

---

## License

MIT
