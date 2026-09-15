/**
 * Storage path helpers for agent-related state.
 *
 * Provides unified path resolution for:
 * - SQLite database file
 * - Data directory
 * - Default workspace directory
 *
 * All paths can be overridden via environment variables.
 */
import os from 'node:os';
import path from 'node:path';

const DEFAULT_DATA_DIR = path.join(os.homedir(), '.nexusai-agent');

/**
 * Resolve base data directory for agent state.
 *
 * Environment:
 * - NEXUSAI_AGENT_DATA_DIR / CHROME_MCP_AGENT_DATA_DIR: overrides the default base directory.
 */
export function getAgentDataDir(): string {
  const raw = process.env.NEXUSAI_AGENT_DATA_DIR || process.env.CHROME_MCP_AGENT_DATA_DIR;
  if (raw && raw.trim()) {
    return path.resolve(raw.trim());
  }
  return DEFAULT_DATA_DIR;
}

/**
 * Resolve database file path.
 *
 * Environment:
 * - NEXUSAI_AGENT_DB_FILE / CHROME_MCP_AGENT_DB_FILE: overrides the default database path.
 */
export function getDatabasePath(): string {
  const raw = process.env.NEXUSAI_AGENT_DB_FILE || process.env.CHROME_MCP_AGENT_DB_FILE;
  if (raw && raw.trim()) {
    return path.resolve(raw.trim());
  }
  return path.join(getAgentDataDir(), 'agent.db');
}

/**
 * Get the default workspace directory for agent projects.
 * This is a subdirectory under the agent data directory.
 *
 * Cross-platform compatible:
 * - Mac/Linux: ~/.nexusai-agent/workspaces
 * - Windows: %USERPROFILE%\.nexusai-agent\workspaces
 */
export function getDefaultWorkspaceDir(): string {
  return path.join(getAgentDataDir(), 'workspaces');
}

/**
 * Generate a default project root path for a given project name.
 */
export function getDefaultProjectRoot(projectName: string): string {
  // Sanitize project name for use as directory name
  const safeName = projectName
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9_-]/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
  return path.join(getDefaultWorkspaceDir(), safeName || 'default-project');
}
