# NexusAI Browser Agent — Setup & Testing Guide

## Architecture Overview

```
Google Antigravity (IDE / Agent)
       │
       ▼  MCP Streamable HTTP / SSE (JSON-RPC)
  http://127.0.0.1:12307/mcp
       │
NexusAI Bridge (`nexus-bridge` / Fastify)
       │
       ▼  Chrome Native Messaging (`com.nexusai.browserhost`)
NexusAI Chrome Extension (MV3 Service Worker)
       │
       ▼  DOM / CDP / Tabs API
Active Browser Tabs & Web Pages
```

---

## Prerequisites

| Requirement | Version | Verification Command |
|:---|:---|:---|
| Node.js | >= 20.x | `node -v` |
| npm / pnpm | Latest | `npm -v` |
| Google Chrome | Stable / Dev | — |

---

## Step 1: Build & Link the Monorepo

If not already built, run:

```powershell
node scripts/build-all.mjs
```

This compiles:
- `@nexusai/shared`
- `@nexusai/bridge`
- `@nexusai/extension` (output folder: `packages/extension/.output/chrome-mv3`)

Make the CLI accessible globally by linking the bridge package:

```powershell
pnpm link:bridge
```

---

## Step 2: Register Native Messaging Host

Register `com.nexusai.browserhost` into your Windows Registry:

```powershell
node scripts/install-host.mjs
```

This registers:
- **Host Name**: `com.nexusai.browserhost`
- **Registry Key**: `HKCU\Software\Google\Chrome\NativeMessagingHosts\com.nexusai.browserhost`
- **Allowed Extension ID**: `ijmgdinpcbmgfmefblpgbcoacnbkiokj`
- **Native Launcher**: `packages/bridge/dist/run_host.bat`

---

## Step 3: Load the Extension in Google Chrome

1. Open Google Chrome and navigate to `chrome://extensions/`
2. Turn **ON** the **Developer mode** toggle in the top-right corner.
3. If previously installed, click the **Reload (🔄)** button on the **NexusAI Browser Agent** card, or click **Load unpacked** and select:
   `c:\Users\elite\Desktop\Browser-interaction\packages\extension\.output\chrome-mv3`
4. Confirm the extension ID is `ijmgdinpcbmgfmefblpgbcoacnbkiokj`.

---

## Step 4: Connect the Extension to the Runtime

1. Click the **NexusAI** extension icon in your Chrome toolbar.
2. In the popup window, verify the port is set to `12307`.
3. Click **Connect Runtime**.
4. The status badge will change to **Connected (Listening on 127.0.0.1:12307)**.
5. You can also click **Welcome Hub** in the header to view the full onboarding dashboard.

---

## Step 5: Verify the Bridge Connection

Run the automated verification script:

```powershell
.\scripts\verify-bridge.ps1
```

Expected output:
```text
[OK] Port 12307 is listening
[OK] MCP endpoint reachable at http://127.0.0.1:12307/mcp
```

---

## Step 6: Antigravity MCP Configuration

Antigravity automatically detects workspace MCP servers from `.agents/mcp_config.json`:

```json
{
  "mcpServers": {
    "nexus-browser": {
      "type": "streamableHttp",
      "url": "http://127.0.0.1:12307/mcp"
    }
  }
}
```

To make NexusAI available across **all projects globally**, add this to `C:\Users\elite\.gemini\config\mcp_config.json`:

```json
{
  "mcpServers": {
    "nexus-browser": {
      "serverUrl": "http://127.0.0.1:12307/mcp"
    }
  }
}
```

---

## Testing Prompts in Antigravity

Once connected, ask Antigravity:

> *"List my currently open Chrome tabs and summarize what's on the active tab."*

> *"Open a new tab to https://news.ycombinator.com, read the top 3 headlines, and take a screenshot."*
