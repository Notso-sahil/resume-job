#!/usr/bin/env bash
set -e

# NexusAI One-Click Build & Host Registration for Unix/macOS
echo -e "\033[36m=====================================================\033[0m"
echo -e "\033[1;36m     NexusAI One-Click Build & Registration         \033[0m"
echo -e "\033[36m=====================================================\033[0m"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Build all packages
echo -e "\n\033[33m[Step 1/2] Building all NexusAI packages...\033[0m"
node scripts/build-all.mjs

# 2. Register Native Messaging host
echo -e "\n\033[33m[Step 2/2] Registering Native Messaging Host...\033[0m"
node scripts/install-host.mjs

echo -e "\n\033[32m=====================================================\033[0m"
echo -e "\033[1;32m   NexusAI is ready to run on Unix/macOS!           \033[0m"
echo -e "\033[32m=====================================================\033[0m"
echo -e "\n\033[36mTo load the extension:\033[0m"
echo "1. Open Google Chrome and go to chrome://extensions"
echo "2. Enable 'Developer mode' in top-right"
echo "3. Click 'Load unpacked' and select:"
echo -e "   \033[33m$SCRIPT_DIR/packages/extension/.output/chrome-mv3\033[0m"
echo "4. Open the popup to test connection."
