# NexusAI Browser Agent — Project Plan

## Executive Summary

NexusAI Browser Agent is an original Chrome browser automation platform that gives AI agents (Antigravity and any MCP client) real-time eyes and hands in the browser. The agent can:

- Read live DOM elements and page structure from any tab
- Capture viewport screenshots
- **Fill forms, input fields, and answer quizzes directly in the browser**
- Click buttons and submit forms
- Capture network traffic and console output
- Record browser activity as GIF

The primary goal is eliminating the slow manual round-trip of copy-paste from browser → agent → browser, making Antigravity a true browser co-pilot.

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Google Chrome                        │
│   ┌──────────────┐         ┌────────────────────────────┐   │
│   │ Active Tabs  │ ◄─────► │ NexusAI Browser Agent      │   │
│   │ (DOM/Inputs) │         │ Chrome Extension (MV3)     │   │
│   └──────────────┘         └─────────────┬──────────────┘   │
└──────────────────────────────────────────┼──────────────────┘
                                           │ Native Messaging (stdin/stdout)
┌──────────────────────────────────────────▼──────────────────┐
│                    NexusAI Bridge                            │
│   com.nexusai.browserhost                                    │
│   Node.js / Fastify — http://127.0.0.1:12307/mcp            │
└──────────────────────────────────────────▲──────────────────┘
                                           │ Streamable HTTP / MCP
┌──────────────────────────────────────────▼──────────────────┐
│                    Antigravity Agent Engine                  │
│   .agents/mcp_config.json → nexus-browser → :12307          │
│   .agents/rules/*.md → 5 rule files                         │
│   28 tools available                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Project File Structure

```
NexusAI/
├── plan.md                          ← This document
├── SETUP.md                         ← User setup guide
├── pnpm-workspace.yaml              ← pnpm monorepo config
├── tsconfig.base.json               ← Base TypeScript config
├── .gitignore
├── .agents/
│   ├── mcp_config.json              ← nexus-browser on :12307
│   └── rules/
│       ├── browser-agent.md         ← How the agent uses browser tools
│       ├── dev-workflow.md          ← Development process rules
│       ├── fork-policy.md           ← Copy policy & proprietary ID rules
│       ├── project-context.md       ← Project identity & layout
│       └── tool-reference.md        ← All 28 tools reference
├── packages/
│   ├── extension/                   ← Chrome MV3 Extension (Vue 3, WXT)
│   ├── bridge/                      ← Node.js MCP server (@nexusai/bridge)
│   └── shared/                      ← Shared types (@nexusai/shared)
├── docs/                            ← Auto-generated Word documents
├── source-repo/                     ← READ-ONLY reference clone
└── scripts/
    ├── verify-bridge.ps1
    ├── build-and-install.ps1
    └── generate-docs.js
```

---

## 3. Identity & Branding

| Property | Value |
|:---|:---|
| Product name | NexusAI Browser Agent |
| Bridge CLI | `nexus-bridge` |
| Native host | `com.nexusai.browserhost` |
| MCP server key | `nexus-browser` |
| Bridge port | `12307` |
| Package namespace | `@nexusai/*` |

---

## 4. Phase Roadmap

> **Rule:** Always generate and approve an implementation plan before starting any phase.

### Phase 1 — Monorepo Scaffold ✅
- pnpm workspace with 3 packages
- tsconfig.base.json, .gitignore, root package.json

### Phase 2 — Chrome Extension (In Progress)
- WXT build setup
- Manifest V3 with English locale
- Full popup UI (4 sections)
- All 28 tools implemented in TypeScript
- No Chinese text anywhere

### Phase 3 — Bridge Rewrite ✅
- Fastify HTTP MCP server on :12307
- Native messaging relay
- CLI: `nexus-bridge start` / `register`
- New identity (no hangwin references)

### Phase 4 — Shared Package ✅
- `@nexusai/shared` built (CJS + ESM)
- 28 tool schemas (English)
- NexusMessageType enum

### Phase 5 — New Features
- `nexus_quiz_solver`: extracts quiz structure from any tab
- `nexus_form_autofill`: semantic label-matching form fill

### Phase 6 — Build Pipeline
- `build-and-install.ps1`: one-command setup

### Phase 7 — Configuration
- Final `mcp_config.json` (already updated)
- Final rules files (already updated)

### Phase 8 — Testing
- Connection test
- Form fill test (httpbin.org)
- Quiz test (Google Form)
- English localization test (no Chinese)

### Phase 9 — Documentation
- Regenerate all 9 Word documents

---

## 5. Tool Capabilities

| Tool | Category | Purpose |
|:---|:---|:---|
| `get_windows_and_tabs` | Tab | List all windows/tabs |
| `chrome_navigate` | Tab | Navigate URL / history |
| `chrome_switch_tab` | Tab | Switch active tab |
| `chrome_close_tabs` | Tab | Close tabs by ID |
| `chrome_history` | Tab | Search browser history |
| `chrome_bookmark_search` | Tab | Search bookmarks |
| `chrome_bookmark_add` | Tab | Add bookmark |
| `chrome_bookmark_delete` | Tab | Delete bookmark |
| `chrome_read_page` | DOM | Accessibility tree (viewport) |
| `chrome_get_web_content` | DOM | Extract page text |
| `chrome_javascript` | DOM | Execute JS in tab |
| `chrome_console` | DOM | Capture console output |
| `chrome_handle_dialog` | DOM | Handle JS alert/confirm/prompt |
| `chrome_click_element` | DOM | Click by selector/ref/coords |
| `chrome_keyboard` | DOM | Keyboard simulation |
| `chrome_request_element_selection` | DOM | Human element picker fallback |
| `chrome_computer` | DOM | Mouse+keyboard full control |
| `chrome_fill_or_select` | Form | Fill input/select/checkbox |
| `chrome_upload_file` | Form | Upload file to input |
| `nexus_form_autofill` | Form | ⭐ Semantic multi-field fill |
| `chrome_screenshot` | Visual | Capture viewport/element |
| `chrome_gif_recorder` | Visual | Record tab as GIF |
| `performance_start_trace` | Perf | Start DevTools trace |
| `performance_stop_trace` | Perf | Stop trace |
| `performance_analyze_insight` | Perf | Summarize trace |
| `chrome_network_request` | Network | Send request with browser cookies |
| `chrome_network_capture` | Network | Capture network traffic |
| `chrome_handle_download` | Network | Wait for download |
| `nexus_quiz_solver` | Quiz | ⭐ Extract quiz Q&A structure |

---

## 6. Security Rules

| Issue | Cause | Solution |
|:---|:---|:---|
| Port 12307 collision | Another process bound | `netstat -ano \| findstr 12307` |
| React/Vue input not firing | Virtual DOM event system | Use `nexus_form_autofill` (native setter) |
| Agent targets sensitive fields | No isolation | `fork-policy.md` and `browser-agent.md` block these |
| Extension not connecting | Manifest not registered | `nexus-bridge register`, restart Chrome |
| Chinese text found | Original source not cleaned | Search-replace per `fork-policy.md` table |

---

## 7. Setup Status Checklist

- [x] Node.js >= 18 installed (v22.18.0)
- [x] pnpm installed globally
- [x] `@nexusai/shared` built (`packages/shared/dist/`)
- [x] `@nexusai/bridge` built (`packages/bridge/dist/`)
- [x] 5 rules files in `.agents/rules/`
- [x] `mcp_config.json` → `nexus-browser` on port `12307`
- [x] Source reference cloned (`source-repo/`)
- [ ] Extension built (`packages/extension/.output/`)
- [ ] Extension loaded unpacked in Chrome
- [ ] New Extension ID recorded
- [ ] `nexus-bridge register` run with new Extension ID
- [ ] Chrome restarted — NexusAI popup shows **Connected**
- [ ] Antigravity tool inventory shows 28 tools from `nexus-browser`
- [ ] Scenario A (form fill) verified
- [ ] Scenario B (quiz) verified
