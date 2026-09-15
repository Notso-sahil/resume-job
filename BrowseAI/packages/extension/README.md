# NexusAI Browser Agent — Chrome Extension

Autonomous AI browser automation and interaction agent for Antigravity, built with WXT and Vue 3 (Manifest V3).

## Features
- **MCP Protocol Integration**: Connects seamlessly to the local Fastify MCP server (`nexus-bridge`) on port `12307`.
- **Autonomous Tool Matrix**: Comprehensive suite of DOM manipulation, navigation, form intelligence, visual capture, and quiz evaluation tools.
- **English-First Runtime**: Modern, bespoke UI designed for AI-driven pair programming and web automation.

## Development
```bash
pnpm dev
```

## Production Build
```bash
pnpm build
```
Output is generated in `.output/chrome-mv3/`. Load this directory as an unpacked extension in `chrome://extensions/`.
