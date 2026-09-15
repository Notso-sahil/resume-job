#!/usr/bin/env bash
# Verify NexusAI Bridge connectivity (Unix/macOS/Linux)

set -e

echo -e "\033[36mChecking NexusAI Bridge status...\033[0m"

# Check if port 12307 is listening
if lsof -i :12307 | grep -q LISTEN; then
    echo -e "\033[32m[OK] Port 12307 is listening\033[0m"
else
    echo -e "\033[31m[FAIL] Port 12307 is NOT listening. Make sure:\033[0m"
    echo -e "\033[33m  1. Chrome is open\033[0m"
    echo -e "\033[33m  2. The NexusAI Browser Agent extension is loaded and Connected\033[0m"
    echo -e "\033[33m  3. Run: nexus-bridge register (or node scripts/install-host.mjs)\033[0m"
    exit 1
fi

# Check MCP endpoint
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://127.0.0.1:12307/mcp || echo "000")
if [ "$HTTP_STATUS" != "000" ]; then
    echo -e "\033[32m[OK] MCP endpoint reachable at http://127.0.0.1:12307/mcp (HTTP $HTTP_STATUS)\033[0m"
else
    echo -e "\033[33m[WARN] Could not reach MCP endpoint — bridge may still be running (requires SSE/POST)\033[0m"
fi

# Check bridge installed
if command -v nexus-bridge &> /dev/null; then
    BRIDGE_VER=$(nexus-bridge --version 2>&1 || echo "unknown")
    echo -e "\033[32m[OK] nexus-bridge installed: $BRIDGE_VER\033[0m"
else
    if [ -f "$(dirname "$0")/../packages/bridge/dist/cli.js" ]; then
        LOCAL_VER=$(node "$(dirname "$0")/../packages/bridge/dist/cli.js" --version 2>&1 || echo "unknown")
        echo -e "\033[32m[OK] Local nexus-bridge ready: $LOCAL_VER\033[0m"
        echo -e "\033[90m[TIP] To make nexus-bridge accessible globally, run: pnpm link:bridge\033[0m"
    else
        echo -e "\033[31m[ERROR] nexus-bridge CLI is not found in PATH and local build is missing.\033[0m"
        echo -e "\033[31m        Run 'pnpm --filter @nexusai/bridge build' then 'pnpm link:bridge'\033[0m"
        exit 1
    fi
fi

echo ""
echo -e "\033[36mNexusAI Browser Agent looks ready! Open Antigravity and try:\033[0m"
echo '  "Look at my active Chrome tab and tell me what you see."'
