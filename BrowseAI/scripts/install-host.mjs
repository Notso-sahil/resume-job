#!/usr/bin/env node

/**
 * NexusAI Native Messaging Host Installer
 * Registers com.nexusai.browserhost with Chrome and Chromium.
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import os from 'os';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

const HOST_NAME = 'com.nexusai.browserhost';
const EXTENSION_ID = 'ijmgdinpcbmgfmefblpgbcoacnbkiokj';
const ALLOWED_EXTENSION_IDS = [
  'ijmgdinpcbmgfmefblpgbcoacnbkiokj',
  'hbdgbgagpkpjffpklnamcljpakneikee',
];
const DESCRIPTION = 'NexusAI Native Messaging Host for Autonomous Browser Agent';

const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  red: '\x1b[31m',
};

function log(msg, color = colors.reset) {
  console.log(`${color}${msg}${colors.reset}`);
}

async function main() {
  log('=====================================================', colors.cyan);
  log('     NexusAI Native Messaging Host Registration      ', colors.bright + colors.cyan);
  log('=====================================================', colors.cyan);

  const bridgeDist = path.join(rootDir, 'packages', 'bridge', 'dist');
  const wrapperScriptName = process.platform === 'win32' ? 'run_host.bat' : 'run_host.sh';
  const launcherPath = path.resolve(bridgeDist, wrapperScriptName);

  if (!fs.existsSync(launcherPath)) {
    log(`Error: Launcher script not found at ${launcherPath}`, colors.red);
    log('Please build the bridge package first: node scripts/build-all.mjs', colors.yellow);
    process.exit(1);
  }

  // Ensure execution permissions on Unix
  if (process.platform !== 'win32') {
    try {
      fs.chmodSync(launcherPath, '755');
      const indexPath = path.join(bridgeDist, 'index.js');
      if (fs.existsSync(indexPath)) fs.chmodSync(indexPath, '755');
      log(`✓ Set execution permissions (755) on ${launcherPath}`, colors.green);
    } catch (e) {
      log(`Warning: Failed to set permissions: ${e.message}`, colors.yellow);
    }
  }

  // Ensure node_path.txt is updated
  const nodePathFile = path.join(bridgeDist, 'node_path.txt');
  fs.writeFileSync(nodePathFile, process.execPath, 'utf8');
  log(`✓ Saved current Node.js binary path: ${process.execPath}`, colors.green);

  // Manifest payload
  const manifest = {
    name: HOST_NAME,
    description: DESCRIPTION,
    path: launcherPath,
    type: 'stdio',
    allowed_origins: ALLOWED_EXTENSION_IDS.map((id) => `chrome-extension://${id}/`),
  };

  const manifestJson = JSON.stringify(manifest, null, 2);
  const home = os.homedir();
  const targets = [];

  if (process.platform === 'win32') {
    const appData = process.env.APPDATA || path.join(home, 'AppData', 'Roaming');
    targets.push({
      browser: 'Google Chrome',
      manifestPath: path.join(appData, 'Google', 'Chrome', 'NativeMessagingHosts', `${HOST_NAME}.json`),
      registryKey: `HKCU\\Software\\Google\\Chrome\\NativeMessagingHosts\\${HOST_NAME}`,
    });
    targets.push({
      browser: 'Chromium',
      manifestPath: path.join(appData, 'Chromium', 'NativeMessagingHosts', `${HOST_NAME}.json`),
      registryKey: `HKCU\\Software\\Chromium\\NativeMessagingHosts\\${HOST_NAME}`,
    });
  } else if (process.platform === 'darwin') {
    targets.push({
      browser: 'Google Chrome',
      manifestPath: path.join(home, 'Library', 'Application Support', 'Google', 'Chrome', 'NativeMessagingHosts', `${HOST_NAME}.json`),
    });
    targets.push({
      browser: 'Chromium',
      manifestPath: path.join(home, 'Library', 'Application Support', 'Chromium', 'NativeMessagingHosts', `${HOST_NAME}.json`),
    });
  } else {
    // Linux
    targets.push({
      browser: 'Google Chrome',
      manifestPath: path.join(home, '.config', 'google-chrome', 'NativeMessagingHosts', `${HOST_NAME}.json`),
    });
    targets.push({
      browser: 'Chromium',
      manifestPath: path.join(home, '.config', 'chromium', 'NativeMessagingHosts', `${HOST_NAME}.json`),
    });
  }

  let successCount = 0;

  for (const target of targets) {
    try {
      // Create parent directory
      fs.mkdirSync(path.dirname(target.manifestPath), { recursive: true });

      // Write manifest
      fs.writeFileSync(target.manifestPath, manifestJson, 'utf8');
      log(`✓ Wrote manifest for ${target.browser}: ${target.manifestPath}`, colors.green);

      // On Windows, configure registry entry
      if (process.platform === 'win32' && target.registryKey) {
        const regCmd = `reg add "${target.registryKey}" /ve /t REG_SZ /d "${target.manifestPath}" /f`;
        execSync(regCmd, { stdio: 'pipe' });
        log(`✓ Created registry entry: ${target.registryKey}`, colors.green);
      }

      successCount++;
    } catch (err) {
      log(`✗ Failed for ${target.browser}: ${err.message}`, colors.yellow);
    }
  }

  log('\n=====================================================', colors.cyan);
  if (successCount > 0) {
    log('🎉 Host registration completed successfully!', colors.bright + colors.green);
    log(`Host Name:       ${HOST_NAME}`);
    log(`Extension ID:    ${EXTENSION_ID}`);
    log(`Binary Launcher: ${launcherPath}\n`);
    log('Next steps:');
    log('1. Open Chrome and navigate to chrome://extensions');
    log('2. Enable "Developer mode" (top right toggle)');
    log('3. Click "Load unpacked" and select:');
    log(`   ${path.join(rootDir, 'packages', 'extension', '.output', 'chrome-mv3')}`);
    log('4. Click the NexusAI extension icon in Chrome toolbar to connect!\n');
  } else {
    log('❌ Host registration encountered errors. Please check permissions.', colors.red);
    process.exit(1);
  }
}

main();
