<template>
  <div class="options-container">
    <!-- Background subtle ambient glow -->
    <div class="ambient-glow"></div>

    <div class="options-shell">
      <!-- Top Navigation & Global Controls -->
      <header class="options-header">
        <div class="brand-group">
          <img src="/icon/32.png" alt="NexusAI" class="brand-logo" />
          <div class="brand-text">
            <div class="title-row">
              <h1 class="brand-title">{{ m('userscriptsManagerTitle') || 'Userscripts Manager' }}</h1>
              <span class="brand-badge">NexusAI Engine</span>
            </div>
            <p class="brand-subtitle">Configure autonomous script injection, frame targets, and execution worlds</p>
          </div>
        </div>

        <div class="emergency-wrapper">
          <div :class="['emergency-pill', emergencyDisabled ? 'emergency-active' : 'emergency-idle']">
            <span class="emergency-indicator"></span>
            <span class="emergency-text">{{ emergencyDisabled ? 'Emergency Halt Active' : 'Runtime Normal' }}</span>
          </div>
          <label class="nexus-switch" :title="m('emergencySwitchLabel') || 'Emergency script killswitch'">
            <input type="checkbox" v-model="emergencyDisabled" @change="saveEmergency" />
            <span class="nexus-slider"></span>
          </label>
        </div>
      </header>

      <!-- Main Content Grid -->
      <main class="options-main">
        <!-- Section 1: Create / Deploy Script -->
        <section class="cyber-card">
          <div class="card-header">
            <div class="card-title-group">
              <span class="card-icon">⚡</span>
              <h2 class="card-title">{{ m('createRunSectionTitle') || 'Deploy New Script' }}</h2>
            </div>
            <span class="card-hint">Supports Isolated and Main DOM worlds</span>
          </div>

          <div class="form-grid">
            <div class="field-col">
              <label class="field-label">{{ m('nameLabel') || 'Script Identifier' }}</label>
              <input
                v-model="form.name"
                class="cyber-input"
                :placeholder="m('placeholderOptional') || 'e.g. Dark Mode Injector'"
              />
            </div>

            <div class="field-col">
              <label class="field-label">{{ m('runAtLabel') || 'Injection Stage' }}</label>
              <div class="select-wrapper">
                <select v-model="form.runAt" class="cyber-select">
                  <option value="auto">{{ m('runAtAuto') || 'Auto (Default)' }}</option>
                  <option value="document_start">{{ m('runAtDocumentStart') || 'Document Start' }}</option>
                  <option value="document_end">{{ m('runAtDocumentEnd') || 'Document End' }}</option>
                  <option value="document_idle">{{ m('runAtDocumentIdle') || 'Document Idle' }}</option>
                </select>
                <span class="select-chevron">▾</span>
              </div>
            </div>

            <div class="field-col">
              <label class="field-label">{{ m('worldLabel') || 'Execution World' }}</label>
              <div class="select-wrapper">
                <select v-model="form.world" class="cyber-select">
                  <option value="auto">{{ m('worldAuto') || 'Auto' }}</option>
                  <option value="ISOLATED">{{ m('worldIsolated') || 'Isolated (Secure)' }}</option>
                  <option value="MAIN">{{ m('worldMain') || 'Main (Page Context)' }}</option>
                </select>
                <span class="select-chevron">▾</span>
              </div>
            </div>

            <div class="field-col">
              <label class="field-label">{{ m('modeLabel') || 'Execution Mode' }}</label>
              <div class="select-wrapper">
                <select v-model="form.mode" class="cyber-select">
                  <option value="auto">{{ m('modeAuto') || 'Auto' }}</option>
                  <option value="persistent">{{ m('modePersistent') || 'Persistent' }}</option>
                  <option value="css">{{ m('modeCss') || 'CSS Injection' }}</option>
                  <option value="once">{{ m('modeOnce') || 'Run Once' }}</option>
                </select>
                <span class="select-chevron">▾</span>
              </div>
            </div>
          </div>

          <!-- Feature Flags -->
          <div class="toggles-row">
            <label class="checkbox-badge">
              <input type="checkbox" v-model="form.allFrames" class="checkbox-input" />
              <span class="checkbox-custom"></span>
              <span class="checkbox-label">{{ m('allFramesLabel') || 'All Sub-frames' }}</span>
            </label>

            <label class="checkbox-badge">
              <input type="checkbox" v-model="form.persist" class="checkbox-input" />
              <span class="checkbox-custom"></span>
              <span class="checkbox-label">{{ m('persistLabel') || 'Persist State' }}</span>
            </label>

            <label class="checkbox-badge">
              <input type="checkbox" v-model="form.dnrFallback" class="checkbox-input" />
              <span class="checkbox-custom"></span>
              <span class="checkbox-label">{{ m('dnrFallbackLabel') || 'DNR Fallback' }}</span>
            </label>
          </div>

          <!-- Matching Patterns -->
          <div class="patterns-grid">
            <div class="field-col">
              <label class="field-label">{{ m('matchesInputLabel') || 'URL Match Patterns (comma separated)' }}</label>
              <input
                v-model="form.matches"
                class="cyber-input font-mono text-xs"
                :placeholder="m('placeholderMatchesExample') || '*://*.example.com/*, https://github.com/*'"
              />
            </div>
            <div class="field-col">
              <label class="field-label">{{ m('excludesInputLabel') || 'Exclude Patterns' }}</label>
              <input
                v-model="form.excludes"
                class="cyber-input font-mono text-xs"
                :placeholder="m('placeholderOptional') || 'https://example.com/login*'"
              />
            </div>
            <div class="field-col">
              <label class="field-label">{{ m('tagsInputLabel') || 'Categorization Tags' }}</label>
              <input
                v-model="form.tags"
                class="cyber-input"
                :placeholder="m('placeholderOptional') || 'automation, scraper, dom'"
              />
            </div>
          </div>

          <!-- Script Source Code -->
          <div class="field-col script-container">
            <div class="script-header">
              <label class="field-label">{{ m('scriptLabel') || 'JavaScript / CSS Payload' }}</label>
              <span class="script-meta font-mono">ES2022 / Vanilla JS</span>
            </div>
            <textarea
              v-model="form.script"
              class="cyber-textarea font-mono"
              :placeholder="m('placeholderScriptHint') || '// Write your automation logic here\nconsole.log(\'NexusAI Userscript active on\', location.href);'"
              rows="7"
            ></textarea>
          </div>

          <!-- Actions & Feedback -->
          <div class="actions-bar">
            <div class="btn-group">
              <button
                class="cyber-btn cyber-btn-primary"
                :disabled="submitting"
                @click="apply('auto')"
              >
                <span class="btn-glow"></span>
                <span>{{ submitting ? 'Deploying...' : (m('applyButton') || 'Deploy Script') }}</span>
              </button>

              <button
                class="cyber-btn cyber-btn-secondary"
                :disabled="submitting"
                @click="apply('once')"
              >
                <span>{{ m('runOnceButton') || 'Execute Once' }}</span>
              </button>
            </div>

            <div v-if="lastResult" class="result-badge">
              <span class="result-dot"></span>
              <span class="result-text">{{ lastResult }}</span>
            </div>
          </div>
        </section>

        <!-- Section 2: Active Registry & Controls -->
        <section class="cyber-card">
          <div class="card-header">
            <div class="card-title-group">
              <span class="card-icon">📋</span>
              <h2 class="card-title">{{ m('listSectionTitle') || 'Registered Userscripts' }}</h2>
              <span class="count-pill">{{ items.length }}</span>
            </div>

            <button class="cyber-btn-subtle" @click="exportAll" title="Export rules as JSON">
              <svg class="w-3.5 h-3.5 mr-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" />
              </svg>
              <span>{{ m('exportAllButton') || 'Export JSON' }}</span>
            </button>
          </div>

          <!-- Search & Filters -->
          <div class="filter-bar">
            <div class="search-box">
              <span class="search-icon">🔍</span>
              <input
                v-model="filters.query"
                @input="reload()"
                class="cyber-input search-input"
                :placeholder="m('queryLabel') || 'Search scripts by name or ID...'"
              />
            </div>

            <div class="select-wrapper filter-select">
              <select v-model="filters.status" @change="reload()" class="cyber-select">
                <option value="">{{ m('statusAll') || 'All Statuses' }}</option>
                <option value="enabled">{{ m('statusEnabled') || 'Enabled Only' }}</option>
                <option value="disabled">{{ m('statusDisabled') || 'Disabled Only' }}</option>
              </select>
              <span class="select-chevron">▾</span>
            </div>

            <input
              v-model="filters.domain"
              @input="reload()"
              class="cyber-input filter-domain"
              :placeholder="m('placeholderDomainHint') || 'Filter by domain...'"
            />
          </div>

          <!-- Data Table -->
          <div class="table-wrap">
            <table class="cyber-table" v-if="items.length > 0">
              <thead>
                <tr>
                  <th>{{ m('tableHeaderName') || 'Script Name' }}</th>
                  <th>{{ m('statusLabel') || 'Status' }}</th>
                  <th>{{ m('tableHeaderWorld') || 'World' }}</th>
                  <th>{{ m('tableHeaderRunAt') || 'Run At' }}</th>
                  <th>{{ m('tableHeaderUpdated') || 'Last Modified' }}</th>
                  <th class="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="it in items" :key="it.id" class="table-row">
                  <td class="cell-name">
                    <div class="script-title-group">
                      <span class="script-icon">📜</span>
                      <span class="script-name-text">{{ it.name || it.id }}</span>
                    </div>
                  </td>
                  <td class="cell-status">
                    <label class="status-toggle" :title="it.status === 'enabled' ? 'Click to disable' : 'Click to enable'">
                      <input
                        type="checkbox"
                        :checked="it.status === 'enabled'"
                        @change="toggle(it)"
                        class="status-checkbox"
                      />
                      <span :class="['status-chip', it.status === 'enabled' ? 'chip-enabled' : 'chip-disabled']">
                        {{ it.status }}
                      </span>
                    </label>
                  </td>
                  <td>
                    <span :class="['world-chip', it.world === 'MAIN' ? 'world-main' : 'world-isolated']">
                      {{ it.world }}
                    </span>
                  </td>
                  <td>
                    <span class="stage-tag font-mono">{{ it.runAt }}</span>
                  </td>
                  <td class="cell-time">
                    {{ formatTime(it.updatedAt) }}
                  </td>
                  <td class="cell-actions">
                    <button class="delete-btn" @click="remove(it)" title="Remove script">
                      <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>

            <div v-else class="empty-state">
              <div class="empty-icon">📂</div>
              <p class="empty-text">No active userscripts match the current filters.</p>
              <p class="empty-sub">Deploy a script above to inject custom logic into web pages.</p>
            </div>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { TOOL_NAMES } from '@nexusai/shared';
import { STORAGE_KEYS } from '@/common/constants';

type ListItem = {
  id: string;
  name?: string;
  status: 'enabled' | 'disabled';
  world: 'ISOLATED' | 'MAIN';
  runAt: 'document_start' | 'document_end' | 'document_idle';
  updatedAt: number;
};

const emergencyDisabled = ref(false);
const items = ref<ListItem[]>([]);
const filters = ref({ query: '', status: '', domain: '' });

const form = ref({
  name: '',
  runAt: 'auto',
  world: 'auto',
  mode: 'auto',
  allFrames: true,
  persist: true,
  dnrFallback: true,
  script: '',
  matches: '',
  excludes: '',
  tags: '',
});

const submitting = ref(false);
const lastResult = ref('');

function formatTime(ts?: number) {
  if (!ts) return '—';
  try {
    return new Date(ts).toLocaleString();
  } catch {
    return String(ts);
  }
}

async function saveEmergency() {
  await globalThis.chrome?.storage?.local.set({
    [STORAGE_KEYS.USERSCRIPTS_DISABLED]: emergencyDisabled.value,
  });
}

async function loadEmergency() {
  const v = await globalThis.chrome?.storage?.local.get([STORAGE_KEYS.USERSCRIPTS_DISABLED] as any);
  emergencyDisabled.value = !!v[STORAGE_KEYS.USERSCRIPTS_DISABLED];
}

async function callTool(name: string, args: any) {
  const res = await globalThis.chrome?.runtime?.sendMessage({
    type: 'call_tool',
    name,
    args,
  } as any);
  if (!res || !res.success) throw new Error(res?.error || 'call failed');
  return res.result;
}

async function reload() {
  try {
    const result = await callTool(TOOL_NAMES.BROWSER.USERSCRIPT, {
      action: 'list',
      args: { ...filters.value },
    });
    const txt = (result?.content?.[0]?.text as string) || '{}';
    const data = JSON.parse(txt);
    items.value = data.items || [];
  } catch (e) {
    console.warn('parse list failed', e);
  }
}

async function apply(mode: 'auto' | 'once') {
  if (!form.value.script.trim()) return;
  submitting.value = true;
  lastResult.value = '';
  try {
    const args: any = {
      script: form.value.script,
      name: form.value.name || undefined,
      runAt: form.value.runAt as any,
      world: form.value.world as any,
      allFrames: !!form.value.allFrames,
      persist: !!form.value.persist,
      dnrFallback: !!form.value.dnrFallback,
      mode,
    };
    if (form.value.matches.trim())
      args.matches = form.value.matches.split(',').map((s) => s.trim());
    if (form.value.excludes.trim())
      args.excludes = form.value.excludes.split(',').map((s) => s.trim());
    if (form.value.tags.trim()) args.tags = form.value.tags.split(',').map((s) => s.trim());

    const result = await callTool(TOOL_NAMES.BROWSER.USERSCRIPT, { action: 'create', args });
    lastResult.value = (result?.content?.[0]?.text as string) || 'Script successfully deployed';
    await reload();
  } catch (e: any) {
    lastResult.value = 'Error: ' + (e?.message || String(e));
  } finally {
    submitting.value = false;
  }
}

async function toggle(it: ListItem) {
  try {
    await callTool(TOOL_NAMES.BROWSER.USERSCRIPT, {
      action: it.status === 'enabled' ? 'disable' : 'enable',
      args: { id: it.id },
    });
    await reload();
  } catch (e) {
    console.warn('toggle failed', e);
  }
}

async function remove(it: ListItem) {
  try {
    const ok = confirm(`Permanently remove userscript "${it.name || it.id}"?`);
    if (!ok) return;
    await callTool(TOOL_NAMES.BROWSER.USERSCRIPT, { action: 'remove', args: { id: it.id } });
    await reload();
  } catch (e) {
    console.warn('remove failed', e);
  }
}

async function exportAll() {
  try {
    const res = await callTool(TOOL_NAMES.BROWSER.USERSCRIPT, { action: 'export', args: {} });
    const txt = (res?.content?.[0]?.text as string) || '{}';
    const blob = new Blob([txt], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    await globalThis.chrome?.downloads?.download({
      url,
      filename: 'nexusai-userscripts.json',
      saveAs: true,
    } as any);
    URL.revokeObjectURL(url);
  } catch (e) {
    console.warn('export failed', e);
  }
}

onMounted(async () => {
  await loadEmergency();
  await reload();
});

function m(key: string, substitutions?: string | string[]) {
  const msg = (globalThis.chrome?.i18n?.getMessage(key, substitutions as any) || '').trim();
  return msg || key;
}
</script>

<style scoped>
.options-container {
  min-height: 100vh;
  background-color: #07090e;
  background-image: 
    radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.08) 0px, transparent 50%),
    radial-gradient(at 100% 0%, rgba(99, 102, 241, 0.08) 0px, transparent 50%),
    radial-gradient(at 50% 100%, rgba(15, 23, 42, 0.9) 0px, transparent 100%);
  color: #f1f5f9;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  padding: 32px 24px;
  position: relative;
  box-sizing: border-box;
}

.ambient-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 240px;
  background: radial-gradient(circle at 50% -20%, rgba(56, 189, 248, 0.15), transparent 70%);
  pointer-events: none;
}

.options-shell {
  max-width: 1120px;
  margin: 0 auto;
  position: relative;
  z-index: 10;
}

/* Header */
.options-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 24px;
  margin-bottom: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.brand-group {
  display: flex;
  align-items: center;
  gap: 16px;
}

.brand-logo {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  box-shadow: 0 0 20px rgba(56, 189, 248, 0.35);
}

.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-title {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0;
  background: linear-gradient(to right, #ffffff, #94a3b8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-badge {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 3px 8px;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: 9999px;
  color: #38bdf8;
}

.brand-subtitle {
  font-size: 13px;
  color: #64748b;
  margin: 4px 0 0 0;
}

.emergency-wrapper {
  display: flex;
  align-items: center;
  gap: 14px;
  background: rgba(15, 23, 42, 0.6);
  padding: 8px 14px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.emergency-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
}

.emergency-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.emergency-idle .emergency-indicator {
  background: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}

.emergency-idle .emergency-text {
  color: #94a3b8;
}

.emergency-active .emergency-indicator {
  background: #ef4444;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.7);
}

.emergency-active .emergency-text {
  color: #f87171;
}

/* Switch */
.nexus-switch {
  position: relative;
  display: inline-block;
  width: 36px;
  height: 20px;
  cursor: pointer;
}

.nexus-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.nexus-slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background-color: #334155;
  transition: 0.2s;
  border-radius: 20px;
}

.nexus-slider:before {
  position: absolute;
  content: "";
  height: 14px;
  width: 14px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.2s;
  border-radius: 50%;
}

input:checked + .nexus-slider {
  background-color: #ef4444;
}

input:checked + .nexus-slider:before {
  transform: translateX(16px);
}

/* Cyber Card */
.cyber-card {
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 8px 32px -4px rgba(0, 0, 0, 0.3);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.card-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-icon {
  font-size: 18px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #f8fafc;
  margin: 0;
}

.count-pill {
  font-size: 11px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.1);
  color: #94a3b8;
  padding: 2px 8px;
  border-radius: 9999px;
}

.card-hint {
  font-size: 12px;
  color: #64748b;
}

/* Forms */
.form-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.field-col {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 12px;
  font-weight: 500;
  color: #94a3b8;
}

.cyber-input {
  background: #090d16;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 8px 12px;
  color: #e2e8f0;
  font-size: 13px;
  outline: none;
  transition: all 0.2s;
  width: 100%;
  box-sizing: border-box;
}

.cyber-input:focus {
  border-color: #38bdf8;
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
}

.select-wrapper {
  position: relative;
  width: 100%;
}

.cyber-select {
  appearance: none;
  background: #090d16;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 8px 28px 8px 12px;
  color: #e2e8f0;
  font-size: 13px;
  width: 100%;
  outline: none;
  cursor: pointer;
  transition: all 0.2s;
  box-sizing: border-box;
}

.cyber-select:focus {
  border-color: #38bdf8;
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
}

.select-chevron {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  pointer-events: none;
  font-size: 10px;
}

/* Toggles Row */
.toggles-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.checkbox-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  background: rgba(15, 23, 42, 0.4);
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: 0.2s;
  user-select: none;
}

.checkbox-badge:hover {
  background: rgba(15, 23, 42, 0.8);
  border-color: rgba(255, 255, 255, 0.12);
}

.checkbox-input {
  display: none;
}

.checkbox-custom {
  width: 14px;
  height: 14px;
  border-radius: 4px;
  border: 1px solid #475569;
  background: #0f172a;
  display: inline-block;
  position: relative;
  transition: 0.2s;
}

.checkbox-input:checked + .checkbox-custom {
  background: #38bdf8;
  border-color: #38bdf8;
}

.checkbox-input:checked + .checkbox-custom:after {
  content: "";
  position: absolute;
  left: 4px;
  top: 1px;
  width: 4px;
  height: 8px;
  border: solid #090d16;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.checkbox-label {
  font-size: 12px;
  color: #cbd5e1;
}

/* Patterns */
.patterns-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

/* Script payload */
.script-container {
  margin-bottom: 18px;
}

.script-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.script-meta {
  font-size: 11px;
  color: #475569;
}

.cyber-textarea {
  background: #06080e;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 12px;
  color: #38bdf8;
  font-size: 12.5px;
  line-height: 1.5;
  width: 100%;
  box-sizing: border-box;
  outline: none;
  resize: vertical;
  transition: all 0.2s;
}

.cyber-textarea:focus {
  border-color: #38bdf8;
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
}

/* Buttons */
.actions-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.btn-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cyber-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 9px 18px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
}

.cyber-btn-primary {
  background: linear-gradient(135deg, #0284c7, #2563eb);
  color: white;
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35);
}

.cyber-btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #0ea5e9, #3b82f6);
  box-shadow: 0 6px 18px rgba(2, 132, 199, 0.5);
  transform: translateY(-1px);
}

.cyber-btn-secondary {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
}

.cyber-btn-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.cyber-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.cyber-btn-subtle {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  color: #94a3b8;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: 0.2s;
}

.cyber-btn-subtle:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #f8fafc;
}

.result-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.1);
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid rgba(56, 189, 248, 0.2);
}

.result-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #38bdf8;
}

/* Filter bar */
.filter-bar {
  display: grid;
  grid-template-columns: 2fr 1fr 1.5fr;
  gap: 12px;
  margin-bottom: 20px;
}

.search-box {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  pointer-events: none;
}

.search-input {
  padding-left: 32px;
}

/* Table */
.table-wrap {
  overflow-x: auto;
}

.cyber-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.cyber-table th {
  padding: 10px 14px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.cyber-table td {
  padding: 12px 14px;
  font-size: 13px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  vertical-align: middle;
}

.table-row:hover td {
  background: rgba(255, 255, 255, 0.02);
}

.script-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.script-icon {
  font-size: 14px;
}

.script-name-text {
  font-weight: 500;
  color: #f1f5f9;
}

.status-toggle {
  cursor: pointer;
  display: inline-flex;
}

.status-checkbox {
  display: none;
}

.status-chip {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 2px 8px;
  border-radius: 9999px;
  transition: 0.2s;
}

.chip-enabled {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.chip-disabled {
  background: rgba(148, 163, 184, 0.1);
  color: #94a3b8;
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.world-chip {
  font-size: 11px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  padding: 2px 6px;
  border-radius: 4px;
}

.world-isolated {
  background: rgba(99, 102, 241, 0.15);
  color: #a5b4fc;
  border: 1px solid rgba(99, 102, 241, 0.25);
}

.world-main {
  background: rgba(245, 158, 11, 0.15);
  color: #fcd34d;
  border: 1px solid rgba(245, 158, 11, 0.25);
}

.stage-tag {
  font-size: 12px;
  color: #94a3b8;
}

.cell-time {
  font-size: 12px;
  color: #64748b;
}

.cell-actions {
  text-align: right;
}

.delete-btn {
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: 0.2s;
}

.delete-btn:hover {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 48px 24px;
}

.empty-icon {
  font-size: 32px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.empty-text {
  font-size: 14px;
  font-weight: 500;
  color: #cbd5e1;
  margin: 0 0 4px 0;
}

.empty-sub {
  font-size: 12px;
  color: #64748b;
  margin: 0;
}

@media (max-width: 960px) {
  .form-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .patterns-grid {
    grid-template-columns: 1fr;
  }
  .filter-bar {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  .options-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style>
