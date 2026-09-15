<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NATIVE_HOST } from '@/common/constants';

const bridgeUrl = `http://127.0.0.1:${NATIVE_HOST.DEFAULT_PORT}/mcp`;

const COMMANDS = {
  startBridge: 'nexus-bridge start',
  startNode: 'node packages/bridge/dist/cli.js start',
  registerHost: 'node scripts/install-host.mjs',
  buildAll: 'npm run setup',
  mcpUrl: bridgeUrl,
} as const;

type CommandKey = keyof typeof COMMANDS;

const copiedKey = ref<CommandKey | string | null>(null);
const pingStatus = ref<'checking' | 'online' | 'offline'>('checking');
const pingLatency = ref<number | null>(null);
const activeConfigTab = ref<'antigravity' | 'claude'>('antigravity');

const antigravityConfig = JSON.stringify(
  {
    mcpServers: {
      'nexus-browser': {
        url: bridgeUrl,
        type: 'http',
      },
    },
  },
  null,
  2
);

const claudeConfig = JSON.stringify(
  {
    mcpServers: {
      'nexus-browser': {
        command: 'nexus-bridge',
        args: ['start'],
      },
    },
  },
  null,
  2
);

async function copyText(text: string, key: CommandKey | string): Promise<void> {
  try {
    await navigator.clipboard.writeText(text);
    copiedKey.value = key;
    window.setTimeout(() => {
      if (copiedKey.value === key) copiedKey.value = null;
    }, 2000);
  } catch (err) {
    console.error('Failed to copy text:', err);
    copiedKey.value = null;
  }
}

async function checkBridgeHealth(): Promise<void> {
  pingStatus.value = 'checking';
  const start = performance.now();
  try {
    // Attempt fetch to Fastify MCP endpoint
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);
    const res = await fetch(bridgeUrl, {
      method: 'GET',
      signal: controller.signal,
      headers: { Accept: 'application/json, text/plain' },
    });
    clearTimeout(timeoutId);
    pingLatency.value = Math.round(performance.now() - start);
    pingStatus.value = res.ok || res.status === 404 || res.status === 405 ? 'online' : 'offline';
  } catch {
    pingLatency.value = null;
    pingStatus.value = 'offline';
  }
}


onMounted(() => {
  checkBridgeHealth();
});
</script>

<template>
  <div class="welcome-container">
    <!-- Ambient Background Glows -->
    <div class="ambient-glow glow-cyan"></div>
    <div class="ambient-glow glow-purple"></div>

    <div class="content-wrapper">
      <!-- Top Brand Header -->
      <header class="hero-header">
        <div class="brand-badge">
          <img src="/icon/logo.png" alt="NexusAI Logo" class="brand-logo-img" />
          <div class="status-pill" :class="pingStatus">
            <span class="status-dot"></span>
            <span v-if="pingStatus === 'online'">Bridge Online ({{ pingLatency }}ms)</span>
            <span v-else-if="pingStatus === 'checking'">Checking Bridge...</span>
            <span v-else>Bridge Offline</span>
          </div>
        </div>

        <h1 class="hero-title">
          Nexus<span class="gradient-text">AI</span> Browser Agent
        </h1>
        <p class="hero-subtitle">
          Autonomous Browser Intelligence, Model Context Protocol (MCP) Bridge & On-Device Automation
        </p>

        <div class="header-actions">
          <button class="action-btn secondary-btn" @click="checkBridgeHealth">
            <svg class="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Test Bridge Ping
          </button>
        </div>
      </header>

      <!-- Main Setup Grid -->
      <main class="main-grid">
        <!-- Step 1 & 2 Card: Quick Start -->
        <section class="glass-card main-setup-card">
          <div class="card-header">
            <div class="step-badge">1</div>
            <div>
              <h2 class="card-title">Start the Native MCP Bridge</h2>
              <p class="card-desc">The local bridge exposes 30 browser automation tools via Fastify on port {{ NATIVE_HOST.DEFAULT_PORT }}.</p>
            </div>
          </div>

          <div class="commands-group">
            <div class="command-box">
              <div class="command-label">Recommended CLI Launch:</div>
              <div class="command-row">
                <code>{{ COMMANDS.startBridge }}</code>
                <button
                  class="copy-btn"
                  :class="{ copied: copiedKey === 'startBridge' }"
                  @click="copyText(COMMANDS.startBridge, 'startBridge')"
                >
                  {{ copiedKey === 'startBridge' ? '✓ Copied' : 'Copy' }}
                </button>
              </div>
            </div>

            <div class="command-box">
              <div class="command-label">Direct Node.js Entry:</div>
              <div class="command-row">
                <code>{{ COMMANDS.startNode }}</code>
                <button
                  class="copy-btn"
                  :class="{ copied: copiedKey === 'startNode' }"
                  @click="copyText(COMMANDS.startNode, 'startNode')"
                >
                  {{ copiedKey === 'startNode' ? '✓ Copied' : 'Copy' }}
                </button>
              </div>
            </div>

            <div class="divider"></div>

            <div class="card-header pt-2">
              <div class="step-badge">2</div>
              <div>
                <h2 class="card-title">Register Native Host (One-Time Setup)</h2>
                <p class="card-desc">Registers <code>com.nexusai.browserhost</code> manifest for Google Chrome & Chromium.</p>
              </div>
            </div>

            <div class="command-box">
              <div class="command-row">
                <code>{{ COMMANDS.registerHost }}</code>
                <button
                  class="copy-btn"
                  :class="{ copied: copiedKey === 'registerHost' }"
                  @click="copyText(COMMANDS.registerHost, 'registerHost')"
                >
                  {{ copiedKey === 'registerHost' ? '✓ Copied' : 'Copy' }}
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- Step 3 Card: MCP Client Connection Config -->
        <section class="glass-card client-config-card">
          <div class="card-header">
            <div class="step-badge">3</div>
            <div>
              <h2 class="card-title">Connect MCP Client</h2>
              <p class="card-desc">Streamable HTTP endpoint: <code>{{ COMMANDS.mcpUrl }}</code></p>
            </div>
          </div>

          <!-- Tab Bar -->
          <div class="tab-bar">
            <button
              class="tab-btn"
              :class="{ active: activeConfigTab === 'antigravity' }"
              @click="activeConfigTab = 'antigravity'"
            >
              Antigravity IDE
            </button>
            <button
              class="tab-btn"
              :class="{ active: activeConfigTab === 'claude' }"
              @click="activeConfigTab = 'claude'"
            >
              Claude Desktop
            </button>
          </div>

          <div class="code-preview-container">
            <pre class="code-block"><code>{{ activeConfigTab === 'antigravity' ? antigravityConfig : claudeConfig }}</code></pre>
            <button
              class="copy-floating-btn"
              :class="{ copied: copiedKey === activeConfigTab }"
              @click="copyText(activeConfigTab === 'antigravity' ? antigravityConfig : claudeConfig, activeConfigTab)"
            >
              {{ copiedKey === activeConfigTab ? '✓ Copied Config' : 'Copy Config' }}
            </button>
          </div>

          <div class="endpoint-quickcopy">
            <span class="text-xs text-slate-400 font-mono">Streamable HTTP URL:</span>
            <div class="command-row mt-1">
              <code class="text-cyan-400">{{ COMMANDS.mcpUrl }}</code>
              <button
                class="copy-btn"
                :class="{ copied: copiedKey === 'mcpUrl' }"
                @click="copyText(COMMANDS.mcpUrl, 'mcpUrl')"
              >
                {{ copiedKey === 'mcpUrl' ? '✓ Copied' : 'Copy' }}
              </button>
            </div>
          </div>
        </section>
      </main>

      <!-- Key Capabilities Grid -->
      <section class="features-section">
        <h2 class="features-heading">Engine Capabilities & Autonomous Features</h2>

        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon-wrapper cyan-glow">
              <svg class="w-6 h-6 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 class="feature-title">Autonomous Job Applier</h3>
            <p class="feature-desc">
              Detects applications on Greenhouse, Lever, LinkedIn, and Ashby. Autofills candidate fields and synthesizes authentic answers.
            </p>
            <span class="feature-tag">nexus_job_applier</span>
          </div>

          <div class="feature-card">
            <div class="feature-icon-wrapper purple-glow">
              <svg class="w-6 h-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 class="feature-title">On-Device Resume Vault</h3>
            <p class="feature-desc">
              Secure client-side candidate profiles stored encrypted in local browser storage. Zero personal data touches external clouds.
            </p>
            <span class="feature-tag">ResumeHub.vue</span>
          </div>

          <div class="feature-card">
            <div class="feature-icon-wrapper emerald-glow">
              <svg class="w-6 h-6 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </div>
            <h3 class="feature-title">Human-Generated Text</h3>
            <p class="feature-desc">
              Deterministic sanitization engine enforcing direct, authentic writing: 0 em dashes, 0 AI buzzwords, and natural contractions.
            </p>
            <span class="feature-tag">Active Humanizer</span>
          </div>

          <div class="feature-card">
            <div class="feature-icon-wrapper blue-glow">
              <svg class="w-6 h-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 class="feature-title">Quiz Solver & Form Fill</h3>
            <p class="feature-desc">
              Autonomous DOM structure recognition, radio and checkbox evaluation, select dropdown handling, and synthetic event dispatching.
            </p>
            <span class="feature-tag">nexus_quiz_solver</span>
          </div>
        </div>
      </section>

      <!-- Footer -->
      <footer class="welcome-footer">
        <div class="footer-info">
          <p>NexusAI Browser Agent · Version 1.0.0 · Dual Protocol (MCP + Native Messaging)</p>
          <p class="footer-subtext">Storage isolated to <code>~/.nexusai-agent</code> · 30 Registered Tools · 100% English Verified</p>
        </div>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.welcome-container {
  min-height: 100vh;
  background-color: #07090e;
  background-image:
    radial-gradient(at 15% 15%, rgba(6, 182, 212, 0.08) 0px, transparent 50%),
    radial-gradient(at 85% 85%, rgba(139, 92, 246, 0.08) 0px, transparent 50%),
    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 100% 100%, 100% 100%, 36px 36px, 36px 36px;
  color: #f1f5f9;
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  position: relative;
  overflow-x: hidden;
  padding-bottom: 3rem;
}

.ambient-glow {
  position: fixed;
  border-radius: 50%;
  filter: blur(120px);
  pointer-events: none;
  z-index: 0;
}

.glow-cyan {
  width: 450px;
  height: 450px;
  top: -100px;
  left: -50px;
  background: radial-gradient(circle, rgba(6, 182, 212, 0.15), transparent 70%);
}

.glow-purple {
  width: 500px;
  height: 500px;
  bottom: -150px;
  right: -50px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.12), transparent 70%);
}

.content-wrapper {
  position: relative;
  z-index: 1;
  max-width: 1100px;
  margin: 0 auto;
  padding: 3rem 1.5rem;
}

/* Header */
.hero-header {
  text-align: center;
  margin-bottom: 3rem;
}

.brand-badge {
  display: inline-flex;
  align-items: center;
  gap: 1rem;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 0.5rem 1rem 0.5rem 0.6rem;
  border-radius: 9999px;
  margin-bottom: 1.5rem;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 24px -6px rgba(0, 0, 0, 0.5);
}

.brand-logo-img {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  box-shadow: 0 0 16px rgba(6, 182, 212, 0.5);
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  padding: 0.25rem 0.6rem;
  border-radius: 9999px;
}

.status-pill.online {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-pill.online .status-dot {
  background: #10b981;
  box-shadow: 0 0 8px #10b981;
}

.status-pill.checking {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.status-pill.checking .status-dot {
  background: #f59e0b;
}

.status-pill.offline {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.status-pill.offline .status-dot {
  background: #ef4444;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.hero-title {
  font-size: 2.75rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  margin-bottom: 0.75rem;
  line-height: 1.15;
}

.gradient-text {
  background: linear-gradient(135deg, #22d3ee 0%, #a855f7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 1.1rem;
  color: #94a3b8;
  max-width: 680px;
  margin: 0 auto 1.75rem;
  line-height: 1.6;
}

.header-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  font-size: 0.85rem;
  font-weight: 600;
  padding: 0.6rem 1.15rem;
  border-radius: 0.6rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.primary-btn {
  background: linear-gradient(135deg, #06b6d4, #8b5cf6);
  color: #ffffff;
  border: none;
  box-shadow: 0 4px 14px rgba(6, 182, 212, 0.35);
}

.primary-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(6, 182, 212, 0.45);
}

.secondary-btn {
  background: rgba(15, 23, 42, 0.8);
  color: #cbd5e1;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(8px);
}

.secondary-btn:hover {
  background: rgba(30, 41, 59, 0.8);
  border-color: rgba(6, 182, 212, 0.4);
  color: #ffffff;
}

/* Glass Cards */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 3.5rem;
}

.glass-card {
  background: rgba(15, 23, 42, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 1rem;
  padding: 1.75rem;
  backdrop-filter: blur(16px);
  box-shadow: 0 16px 36px -8px rgba(0, 0, 0, 0.4);
  transition: border-color 0.2s ease;
}

.glass-card:hover {
  border-color: rgba(6, 182, 212, 0.25);
}

.card-header {
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
  margin-bottom: 1.25rem;
}

.step-badge {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #06b6d4, #3b82f6);
  color: #ffffff;
  font-size: 0.85rem;
  font-weight: 700;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 10px rgba(6, 182, 212, 0.4);
}

.card-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 0.25rem;
}

.card-desc {
  font-size: 0.85rem;
  color: #94a3b8;
  margin: 0;
  line-height: 1.45;
}

.card-desc code {
  color: #22d3ee;
  background: rgba(6, 182, 212, 0.1);
  padding: 0.15rem 0.35rem;
  border-radius: 0.3rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
}

/* Commands Group */
.commands-group {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.command-box {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.command-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #64748b;
}

.command-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  background: rgba(2, 6, 23, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 0.6rem 0.85rem;
  border-radius: 0.5rem;
}

.command-row code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.82rem;
  color: #38bdf8;
  overflow-x: auto;
  white-space: nowrap;
}

.copy-btn {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #cbd5e1;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.25rem 0.55rem;
  border-radius: 0.35rem;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.copy-btn:hover {
  background: rgba(6, 182, 212, 0.15);
  border-color: rgba(6, 182, 212, 0.3);
  color: #ffffff;
}

.copy-btn.copied {
  background: rgba(16, 185, 129, 0.2);
  border-color: rgba(16, 185, 129, 0.4);
  color: #34d399;
}

.divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.06);
  margin: 0.5rem 0;
}

/* Tabs & Config Code Preview */
.tab-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  background: rgba(2, 6, 23, 0.5);
  padding: 0.25rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.tab-btn {
  flex: 1;
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.45rem;
  border-radius: 0.35rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn.active {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.code-preview-container {
  position: relative;
  margin-bottom: 1rem;
}

.code-block {
  background: #020617;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 0.5rem;
  padding: 1rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
  line-height: 1.45;
  color: #e2e8f0;
  overflow-x: auto;
  max-height: 170px;
}

.copy-floating-btn {
  position: absolute;
  top: 0.6rem;
  right: 0.6rem;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #cbd5e1;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  font-weight: 500;
  padding: 0.25rem 0.55rem;
  border-radius: 0.35rem;
  cursor: pointer;
  backdrop-filter: blur(4px);
  transition: all 0.2s ease;
}

.copy-floating-btn:hover {
  background: rgba(6, 182, 212, 0.2);
  color: #ffffff;
}

.copy-floating-btn.copied {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
}

.endpoint-quickcopy {
  margin-top: 0.75rem;
}

/* Features Grid */
.features-section {
  margin-top: 2rem;
}

.features-heading {
  font-size: 1.35rem;
  font-weight: 700;
  color: #f8fafc;
  margin-bottom: 1.5rem;
  text-align: center;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
}

.feature-card {
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 0.85rem;
  padding: 1.4rem;
  display: flex;
  flex-direction: column;
  transition: all 0.2s ease;
}

.feature-card:hover {
  transform: translateY(-2px);
  background: rgba(15, 23, 42, 0.75);
  border-color: rgba(255, 255, 255, 0.12);
}

.feature-icon-wrapper {
  width: 42px;
  height: 42px;
  border-radius: 0.6rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.cyan-glow {
  background: rgba(6, 182, 212, 0.12);
  box-shadow: 0 0 16px rgba(6, 182, 212, 0.2);
}

.purple-glow {
  background: rgba(168, 85, 247, 0.12);
  box-shadow: 0 0 16px rgba(168, 85, 247, 0.2);
}

.emerald-glow {
  background: rgba(16, 185, 129, 0.12);
  box-shadow: 0 0 16px rgba(16, 185, 129, 0.2);
}

.blue-glow {
  background: rgba(59, 130, 246, 0.12);
  box-shadow: 0 0 16px rgba(59, 130, 246, 0.2);
}

.feature-title {
  font-size: 0.98rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 0.5rem;
}

.feature-desc {
  font-size: 0.82rem;
  color: #94a3b8;
  line-height: 1.45;
  margin: 0 0 1rem;
  flex: 1;
}

.feature-tag {
  align-self: flex-start;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  font-weight: 600;
  color: #94a3b8;
  background: rgba(255, 255, 255, 0.05);
  padding: 0.2rem 0.45rem;
  border-radius: 0.3rem;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

/* Footer */
.welcome-footer {
  margin-top: 4rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  text-align: center;
}

.footer-info {
  font-size: 0.82rem;
  color: #64748b;
  line-height: 1.6;
}

.footer-subtext code {
  color: #38bdf8;
  background: rgba(6, 182, 212, 0.08);
  padding: 0.1rem 0.3rem;
  border-radius: 0.25rem;
}

@media (max-width: 960px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .features-grid {
    grid-template-columns: 1fr;
  }
  .hero-title {
    font-size: 2rem;
  }
}
</style>
