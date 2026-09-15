#!/usr/bin/env node

/**
 * NexusAI Unified Cross-Platform Build Pipeline
 * Builds all monorepo packages in topological dependency order:
 * 1. @nexusai/shared
 * 2. @nexusai/bridge
 * 3. @nexusai/extension
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

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

function printHeader() {
  log('=====================================================', colors.cyan);
  log('       NexusAI Autonomous Browser Runtime Build      ', colors.bright + colors.cyan);
  log('=====================================================', colors.cyan);
  log(`Root directory: ${rootDir}`);
  log(`Node runtime:   ${process.execPath} (${process.version})`);
  log(`Platform:       ${process.platform} (${process.arch})\n`);
}

function runStep(name, cmd, cwd) {
  log(`▶ [${name}] Running: ${cmd} (in ${path.relative(rootDir, cwd) || '.'})`, colors.blue);
  const startTime = Date.now();
  try {
    execSync(cmd, { cwd, stdio: 'inherit' });
    const duration = ((Date.now() - startTime) / 1000).toFixed(2);
    log(`✓ [${name}] Completed in ${duration}s\n`, colors.green);
    return true;
  } catch (err) {
    log(`✗ [${name}] Failed with error: ${err.message}\n`, colors.red);
    process.exit(1);
  }
}

async function main() {
  printHeader();

  const sharedDir = path.join(rootDir, 'packages', 'shared');
  const bridgeDir = path.join(rootDir, 'packages', 'bridge');
  const extensionDir = path.join(rootDir, 'packages', 'extension');

  // Verify directory existence
  if (!fs.existsSync(sharedDir) || !fs.existsSync(bridgeDir) || !fs.existsSync(extensionDir)) {
    log('Error: One or more package directories do not exist.', colors.red);
    process.exit(1);
  }

  // 1. Build @nexusai/shared
  runStep('1/3 @nexusai/shared', 'pnpm --filter @nexusai/shared build', rootDir);

  // Verify shared artifacts
  const sharedDist = path.join(sharedDir, 'dist', 'index.js');
  if (!fs.existsSync(sharedDist)) {
    log(`Error: Expected shared artifact missing: ${sharedDist}`, colors.red);
    process.exit(1);
  }

  // 2. Build @nexusai/bridge
  runStep('2/3 @nexusai/bridge', 'pnpm --filter @nexusai/bridge build', rootDir);

  // Ensure node_path.txt is written inside bridge/dist
  const bridgeDist = path.join(bridgeDir, 'dist');
  const nodePathFile = path.join(bridgeDist, 'node_path.txt');
  fs.writeFileSync(nodePathFile, process.execPath, 'utf8');
  log(`✓ Saved execution node path to: ${nodePathFile}`, colors.green);

  // 3. Build @nexusai/extension
  runStep('3/3 @nexusai/extension', 'pnpm --filter @nexusai/extension build', rootDir);

  // Verification of build outputs
  log('=====================================================', colors.cyan);
  log('             Build Verification Summary              ', colors.bright + colors.cyan);
  log('=====================================================', colors.cyan);

  const outputs = [
    { name: '@nexusai/shared CJS bundle', path: path.join(sharedDir, 'dist', 'index.js') },
    { name: '@nexusai/shared ESM bundle', path: path.join(sharedDir, 'dist', 'index.mjs') },
    { name: '@nexusai/shared Types (.d.ts)', path: path.join(sharedDir, 'dist', 'index.d.ts') },
    { name: '@nexusai/bridge Host entry', path: path.join(bridgeDist, 'index.js') },
    { name: '@nexusai/bridge CLI entry', path: path.join(bridgeDist, 'cli.js') },
    { name: '@nexusai/bridge launcher (bat)', path: path.join(bridgeDist, 'run_host.bat') },
    { name: '@nexusai/bridge launcher (sh)', path: path.join(bridgeDist, 'run_host.sh') },
    { name: '@nexusai/extension Chrome MV3', path: path.join(extensionDir, '.output', 'chrome-mv3', 'manifest.json') },
  ];

  let allValid = true;
  for (const item of outputs) {
    if (fs.existsSync(item.path)) {
      const stats = fs.statSync(item.path);
      log(`✓ ${item.name.padEnd(32)} [${(stats.size / 1024).toFixed(1)} KB]`, colors.green);
    } else {
      log(`✗ MISSING: ${item.name} (${item.path})`, colors.red);
      allValid = false;
    }
  }

  if (allValid) {
    log('\n🎉 All NexusAI packages built successfully!', colors.bright + colors.green);
    log('To register the native messaging host, run: node scripts/install-host.mjs\n', colors.yellow);
  } else {
    log('\n⚠️ Build completed with missing verification artifacts.', colors.yellow);
    process.exit(1);
  }
}

main();
