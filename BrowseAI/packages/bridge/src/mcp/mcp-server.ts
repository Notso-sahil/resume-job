import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { setupTools } from './register-tools';

export const createMcpServer = (): Server => {
  const server = new Server(
    {
      name: 'NexusAI-Browser-MCP',
      version: '1.0.0',
    },
    {
      capabilities: {
        tools: {},
        resources: {},
        prompts: {},
      },
    },
  );

  setupTools(server);
  return server;
};

// Backwards compatibility
export const getMcpServer = createMcpServer;
export let mcpServer: Server | null = null;
