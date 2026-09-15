# Project Context & Identity

## What This Project Is

**NexusAI Browser Agent** is an original Chrome browser automation platform that enables AI agents (specifically Antigravity) to see, read, and interact with any web page in real-time.

It consists of three components:
1. **Chrome Extension** (`packages/extension`) — A Manifest V3 Chrome extension that provides browser access APIs.
2. **Node.js Bridge** (`packages/bridge`) — A local MCP server that exposes browser tools to AI clients over HTTP.
3. **Shared Package** (`packages/shared`) — TypeScript types and tool schema definitions shared between extension and bridge.

---

## What This Project Is NOT

- It is NOT the `hangwin/mcp-chrome` project.
- It does NOT depend on `mcp-chrome-bridge` or `chrome-mcp-shared` npm packages.
- It does NOT use the Chrome Web Store — the extension is always loaded unpacked.

---

## Branding Identity

| Property | Value |
|:---|:---|
| Product name | NexusAI Browser Agent |
| Bridge CLI command | `nexus-bridge` |
| Native host name | `com.nexusai.browserhost` |
| MCP server key (in config) | `nexus-browser` |
| Bridge port | `12307` |
| Package namespace | `@nexusai/*` |

---

## Repository Layout

```
NexusAI/
├── .agents/
│   ├── mcp_config.json          ← MCP connection config (port 12307)
│   └── rules/
│       ├── browser-agent.md     ← How to use browser tools as an agent
│       ├── dev-workflow.md      ← Development process rules
│       ├── fork-policy.md       ← What can/cannot be copied from source
│       ├── project-context.md   ← This file — project identity & layout
│       └── tool-reference.md    ← All 28 tools with descriptions
├── docs/                        ← Auto-generated Word documents (one per phase)
├── packages/
│   ├── extension/               ← Chrome MV3 Extension (Vue 3, WXT)
│   ├── bridge/                  ← Node.js MCP server (Fastify)
│   └── shared/                  ← Shared TypeScript types
├── scripts/
│   ├── verify-bridge.ps1        ← Test bridge connectivity
│   ├── build-and-install.ps1    ← One-command setup
│   └── generate-docs.js         ← Generate Word documents
├── source-repo/                 ← READ-ONLY: original hangwin/mcp-chrome clone
├── plan.md                      ← Original project roadmap (legacy)
├── SETUP.md                     ← User-facing setup guide
├── pnpm-workspace.yaml
└── tsconfig.base.json
```

---

## Current Status

Phases completed:
- [x] Phase 1: Monorepo scaffold (pnpm workspace, tsconfig)
- [x] Phase 3: Bridge package (Fastify, MCP SDK, CLI)
- [x] Phase 4: Shared package (tool schemas, message types) — built successfully
- [ ] Phase 2: Chrome Extension (WXT, popup UI, tool implementations)
- [ ] Phase 5: New tools (`nexus_quiz_solver`, `nexus_form_autofill`)
- [ ] Phase 6: Build pipeline (`build-and-install.ps1`)
- [ ] Phase 7: Config final update
- [ ] Phase 8: End-to-end testing
- [ ] Phase 9: Word document regeneration

---

## Source Reference

The original MIT-licensed project used as reference:
- GitHub: `https://github.com/hangwin/mcp-chrome`
- Cloned locally at: `source-repo/` (read-only, never commit changes here)
- License: MIT — attribution required in our `README.md` and `LICENSE`
