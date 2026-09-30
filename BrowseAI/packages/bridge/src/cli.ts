#!/usr/bin/env node

import { program } from 'commander';
import * as fs from 'fs';
import * as path from 'path';
import {
  tryRegisterUserLevelHost,
  colorText,
  registerWithElevatedPermissions,
  ensureExecutionPermissions,
  writeNodePathFile,
  setExtensionId,
  isValidExtensionId,
  getBridgeConfigPath,
  patchMcpConfig,
} from './scripts/utils';
import { BrowserType, parseBrowserType, detectInstalledBrowsers } from './scripts/browser-config';
import { runDoctor } from './scripts/doctor';
import { runReport } from './scripts/report';

program
  .version(require('../package.json').version)
  .description('Mcp Chrome Bridge - Local service for communicating with Chrome extension');

/** Printed after any successful `register` run — the #1 setup failure point otherwise. */
function printSetIdNextSteps(): void {
  console.log('');
  console.log(colorText('✓ Native host registered.', 'green'));
  console.log('');
  console.log(colorText('NEXT STEP — Tell the bridge your Extension ID:', 'blue'));
  console.log('  1. Open Chrome → Extensions (chrome://extensions) → Enable Developer Mode');
  console.log('  2. Load unpacked from: BrowseAI/packages/extension/.output/chrome-mv3');
  console.log('  3. Copy the Extension ID shown under the extension name');
  console.log(colorText('  4. Run:  nexus-bridge set-id <PASTE_ID_HERE>', 'cyan'));
}

// Register Native Messaging host
program
  .command('register')
  .description('Register Native Messaging host')
  .option('-f, --force', 'Force re-registration')
  .option('-s, --system', 'Use system-level installation (requires administrator/sudo privileges)')
  .option('-b, --browser <browser>', 'Register for specific browser (chrome, chromium, or all)')
  .option('-d, --detect', 'Auto-detect installed browsers')
  .action(async (options) => {
    try {
      // Write Node.js path for run_host scripts
      writeNodePathFile(__dirname);

      // Determine which browsers to register
      let targetBrowsers: BrowserType[] | undefined;

      if (options.browser) {
        if (options.browser.toLowerCase() === 'all') {
          targetBrowsers = [BrowserType.CHROME, BrowserType.CHROMIUM];
          console.log(colorText('Registering for all supported browsers...', 'blue'));
        } else {
          const browserType = parseBrowserType(options.browser);
          if (!browserType) {
            console.error(
              colorText(
                `Invalid browser: ${options.browser}. Use 'chrome', 'chromium', or 'all'`,
                'red',
              ),
            );
            process.exit(1);
          }
          targetBrowsers = [browserType];
        }
      } else if (options.detect) {
        targetBrowsers = detectInstalledBrowsers();
        if (targetBrowsers.length === 0) {
          console.log(
            colorText(
              'No supported browsers detected, will register for Chrome and Chromium',
              'yellow',
            ),
          );
          targetBrowsers = undefined; // Will use default behavior
        }
      }
      // If neither option specified, tryRegisterUserLevelHost will detect browsers

      // Detect if running with root/administrator privileges
      const isRoot = process.getuid && process.getuid() === 0; // Unix/Linux/Mac

      let isAdmin = false;
      if (process.platform === 'win32') {
        try {
          isAdmin = require('is-admin')(); // Windows requires additional package
        } catch (error) {
          console.warn(
            colorText('Warning: Unable to detect administrator privileges on Windows', 'yellow'),
          );
          isAdmin = false;
        }
      }

      const hasElevatedPermissions = isRoot || isAdmin;

      // If --system option is specified or running with root/administrator privileges
      if (options.system || hasElevatedPermissions) {
        // TODO: Update registerWithElevatedPermissions to support multiple browsers
        await registerWithElevatedPermissions();
        console.log(
          colorText('System-level Native Messaging host registered successfully!', 'green'),
        );
        console.log(
          colorText(
            'You can now use connectNative in Chrome extension to connect to this service.',
            'blue',
          ),
        );
        printSetIdNextSteps();
      } else {
        // Regular user-level installation
        console.log(colorText('Registering user-level Native Messaging host...', 'blue'));
        const success = await tryRegisterUserLevelHost(targetBrowsers);

        if (success) {
          console.log(colorText('Native Messaging host registered successfully!', 'green'));
          console.log(
            colorText(
              'You can now use connectNative in Chrome extension to connect to this service.',
              'blue',
            ),
          );
          printSetIdNextSteps();
        } else {
          console.log(
            colorText(
              'User-level registration failed, please try the following methods:',
              'yellow',
            ),
          );
          console.log(colorText('  1. sudo nexus-bridge register', 'yellow'));
          console.log(colorText('  2. nexus-bridge register --system', 'yellow'));
          process.exit(1);
        }
      }
    } catch (error: any) {
      console.error(colorText(`Registration failed: ${error.message}`, 'red'));
      process.exit(1);
    }
  });

// Tell the bridge the extension's actual (randomly-assigned) ID
program
  .command('set-id <extensionId>')
  .description(
    'Set the Chrome extension ID (from chrome://extensions after loading unpacked) that the ' +
      'native host will accept connections from',
  )
  .action(async (extensionId: string) => {
    try {
      const normalizedId = extensionId.trim().toLowerCase();

      if (!isValidExtensionId(normalizedId)) {
        console.error(
          colorText(
            `Error: "${extensionId}" doesn't look like a Chrome extension ID. ` +
              'Expected 32 lowercase letters (a-p), e.g. abcdefghijklmnopabcdefghijklmnop.',
            'red',
          ),
        );
        console.error(
          colorText(
            'Copy the ID from chrome://extensions, shown under the NexusAI extension name.',
            'yellow',
          ),
        );
        process.exit(1);
      }

      const { updatedManifestPaths } = await setExtensionId(normalizedId);

      console.log(colorText(`✓ Extension ID saved to ${getBridgeConfigPath()}`, 'green'));

      if (updatedManifestPaths.length > 0) {
        console.log(colorText('✓ Updated existing native host manifest(s):', 'green'));
        for (const manifestPath of updatedManifestPaths) {
          console.log(colorText(`   ${manifestPath}`, 'cyan'));
        }
      } else {
        console.log(
          colorText(
            'No existing native host manifest found yet — run "nexus-bridge register" to create one ' +
              '(it will automatically use this extension ID).',
            'yellow',
          ),
        );
      }

      console.log(colorText('\nReload the extension in chrome://extensions to pick this up.', 'blue'));
    } catch (error: any) {
      console.error(colorText(`Failed to set extension ID: ${error.message}`, 'red'));
      process.exit(1);
    }
  });

// Patch known MCP client configs to point at this bridge's stdio server
program
  .command('patch-mcp')
  .description(
    'Point known MCP client configs (Antigravity/Gemini CLI, Claude Desktop, Cursor) at this ' +
      "bridge's stdio server, so you don't have to hand-edit them",
  )
  .action(async () => {
    try {
      const { patchedPaths } = await patchMcpConfig();
      if (patchedPaths.length === 0) {
        console.log(colorText('No MCP client configs were patched.', 'yellow'));
      } else {
        console.log(colorText(`\n✓ Patched ${patchedPaths.length} MCP client config(s).`, 'green'));
      }
    } catch (error: any) {
      console.error(colorText(`Failed to patch MCP configs: ${error.message}`, 'red'));
      process.exit(1);
    }
  });

// Fix execution permissions
program
  .command('fix-permissions')
  .description('Fix execution permissions for native host files')
  .action(async () => {
    try {
      console.log(colorText('Fixing execution permissions...', 'blue'));
      await ensureExecutionPermissions();
      console.log(colorText('✓ Execution permissions fixed successfully!', 'green'));
    } catch (error: any) {
      console.error(colorText(`Failed to fix permissions: ${error.message}`, 'red'));
      process.exit(1);
    }
  });

// Update port in stdio-config.json
program
  .command('update-port <port>')
  .description('Update the port number in stdio-config.json')
  .action(async (port: string) => {
    try {
      const portNumber = parseInt(port, 10);
      if (isNaN(portNumber) || portNumber < 1 || portNumber > 65535) {
        console.error(colorText('Error: Port must be a valid number between 1 and 65535', 'red'));
        process.exit(1);
      }

      const configPath = path.join(__dirname, 'mcp', 'stdio-config.json');

      if (!fs.existsSync(configPath)) {
        console.error(colorText(`Error: Configuration file not found at ${configPath}`, 'red'));
        process.exit(1);
      }

      const configData = fs.readFileSync(configPath, 'utf8');
      const config = JSON.parse(configData);

      const currentUrl = new URL(config.url);
      currentUrl.port = portNumber.toString();
      config.url = currentUrl.toString();

      fs.writeFileSync(configPath, JSON.stringify(config, null, 4));

      console.log(colorText(`✓ Port updated successfully to ${portNumber}`, 'green'));
      console.log(colorText(`Updated URL: ${config.url}`, 'blue'));
    } catch (error: any) {
      console.error(colorText(`Failed to update port: ${error.message}`, 'red'));
      process.exit(1);
    }
  });

// Diagnose installation and environment issues
program
  .command('doctor')
  .description('Diagnose installation and environment issues')
  .option('--json', 'Output diagnostics as JSON')
  .option('--fix', 'Attempt to fix common issues automatically')
  .option('-b, --browser <browser>', 'Target browser (chrome, chromium, or all)')
  .action(async (options) => {
    try {
      const exitCode = await runDoctor({
        json: Boolean(options.json),
        fix: Boolean(options.fix),
        browser: options.browser,
      });
      process.exit(exitCode);
    } catch (error: any) {
      console.error(colorText(`Doctor failed: ${error.message}`, 'red'));
      process.exit(1);
    }
  });

// Export diagnostic report for GitHub Issues
program
  .command('report')
  .description('Export a diagnostic report for GitHub Issues')
  .option('--json', 'Output report as JSON (default: Markdown)')
  .option('--output <file>', 'Write report to file instead of stdout')
  .option('--copy', 'Copy report to clipboard')
  .option('--no-redact', 'Disable redaction of usernames/paths/tokens')
  .option('--include-logs <mode>', 'Include wrapper logs: none | tail | full', 'tail')
  .option('--log-lines <n>', 'Lines to include when --include-logs=tail', '200')
  .option('-b, --browser <browser>', 'Target browser (chrome, chromium, or all)')
  .action(async (options) => {
    try {
      const exitCode = await runReport({
        json: Boolean(options.json),
        output: options.output,
        copy: Boolean(options.copy),
        redact: options.redact,
        includeLogs: options.includeLogs,
        logLines: options.logLines ? parseInt(options.logLines, 10) : undefined,
        browser: options.browser,
      });
      process.exit(exitCode);
    } catch (error: any) {
      console.error(colorText(`Report failed: ${error.message}`, 'red'));
      process.exit(1);
    }
  });

program.parse(process.argv);

// If no command provided, show help
if (!process.argv.slice(2).length) {
  program.outputHelp();
}
