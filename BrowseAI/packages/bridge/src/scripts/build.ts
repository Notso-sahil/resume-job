import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

const distDir = path.join(__dirname, '..', '..', 'dist');

// Clean previous build artifacts
console.log('Cleaning previous build artifacts...');
try {
  fs.rmSync(distDir, { recursive: true, force: true });
} catch (err) {
  // Ignore errors if directory does not exist
  console.log(err);
}

// Create dist directory
fs.mkdirSync(distDir, { recursive: true });
fs.mkdirSync(path.join(distDir, 'logs'), { recursive: true });
console.log('Created dist and dist/logs directories');

// Compile TypeScript
console.log('Compiling TypeScript sources...');
execSync('tsc', { stdio: 'inherit' });

// Copy configuration files
console.log('Copying configuration files...');
const configSourcePath = path.join(__dirname, '..', 'mcp', 'stdio-config.json');
const configDestPath = path.join(distDir, 'mcp', 'stdio-config.json');

try {
  fs.mkdirSync(path.dirname(configDestPath), { recursive: true });

  if (fs.existsSync(configSourcePath)) {
    fs.copyFileSync(configSourcePath, configDestPath);
    console.log(`Copied stdio-config.json to ${configDestPath}`);
  } else {
    console.error(`Error: Configuration file not found: ${configSourcePath}`);
  }
} catch (error) {
  console.error('Error copying configuration file:', error);
}

// Prepare package.json and README
console.log('Preparing package distribution metadata...');
const packageJson = require('../../package.json');

const readmeContent = `# ${packageJson.name}

NexusAI Native Messaging Host & MCP Bridge for Autonomous Browser Control.

## Installation & Registration

1. Ensure Node.js (v20+) is installed.
2. Build and register the native host:
   \`\`\`bash
   # User-level installation (recommended)
   node dist/scripts/register.js

   # Or via global CLI
   nexus-bridge register
   \`\`\`

## Operation

This application is spawned automatically by the NexusAI Chrome Extension via Native Messaging. Manual execution is only required for diagnostics:
\`\`\`bash
nexus-bridge doctor
\`\`\`
`;

fs.writeFileSync(path.join(distDir, 'README.md'), readmeContent);

console.log('Copying host launcher wrapper scripts...');
const scriptsSourceDir = path.join(__dirname, '.');
const macOsWrapperSourcePath = path.join(scriptsSourceDir, 'run_host.sh');
const windowsWrapperSourcePath = path.join(scriptsSourceDir, 'run_host.bat');

const macOsWrapperDestPath = path.join(distDir, 'run_host.sh');
const windowsWrapperDestPath = path.join(distDir, 'run_host.bat');

try {
  if (fs.existsSync(macOsWrapperSourcePath)) {
    fs.copyFileSync(macOsWrapperSourcePath, macOsWrapperDestPath);
    console.log(`Copied ${macOsWrapperSourcePath} to ${macOsWrapperDestPath}`);
  } else {
    console.error(`Error: macOS wrapper script not found: ${macOsWrapperSourcePath}`);
  }

  if (fs.existsSync(windowsWrapperSourcePath)) {
    fs.copyFileSync(windowsWrapperSourcePath, windowsWrapperDestPath);
    console.log(`Copied ${windowsWrapperSourcePath} to ${windowsWrapperDestPath}`);
  } else {
    console.error(`Error: Windows wrapper script not found: ${windowsWrapperSourcePath}`);
  }
} catch (error) {
  console.error('Error copying launcher wrapper scripts:', error);
}

// Add execution permissions for critical scripts and binaries
console.log('Setting execution permissions...');
const filesToMakeExecutable = ['index.js', 'cli.js', 'run_host.sh'];

filesToMakeExecutable.forEach((file) => {
  const filePath = path.join(distDir, file);
  try {
    if (fs.existsSync(filePath)) {
      fs.chmodSync(filePath, '755');
      console.log(`Set execution permissions (755) for ${file}`);
    } else {
      console.warn(`Warning: ${filePath} does not exist, cannot set permissions`);
    }
  } catch (error) {
    console.error(`Error setting execution permissions for ${file}:`, error);
  }
});

// Write node_path.txt immediately after build to ensure Chrome uses the correct Node.js runtime.
console.log('Writing node_path.txt...');
const nodePathFile = path.join(distDir, 'node_path.txt');
fs.writeFileSync(nodePathFile, process.execPath, 'utf8');
console.log(`Saved Node.js path: ${process.execPath}`);

console.log('Build completed successfully.');
