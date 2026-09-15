<template>
  <div class="resume-hub-page">
    <!-- Header -->
    <div class="page-header">
      <button class="back-button" @click="$emit('back')" title="Back to Main View">
        <svg
          viewBox="0 0 24 24"
          width="20"
          height="20"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        <span>Back</span>
      </button>
      <div class="header-title-container">
        <h2 class="page-title">Resume Vault</h2>
        <span class="vault-badge">🔒 On-Device Private</span>
      </div>
    </div>

    <div class="page-content">
      <!-- Quick Autofill Trigger on Active Tab -->
      <div class="section action-card-section">
        <div class="autofill-banner">
          <div class="banner-text">
            <h3 class="banner-title">Autonomous Job Applier</h3>
            <p class="banner-subtitle">
              Scan active job posting, extract company context, and auto-fill form inputs.
            </p>
            <div class="humanizer-toggle-row">
              <div class="humanizer-toggle-info">
                <span class="humanizer-toggle-title">✍️ Human-Generated Voice</span>
                <span class="humanizer-toggle-hint">
                  Natural tone, concrete facts, zero AI clichés
                </span>
              </div>
              <label class="nexus-switch-modern" title="Toggle Human-Generated Voice mode">
                <input
                  type="checkbox"
                  v-model="isHumanTextEnabled"
                  @change="saveHumanTextPreference"
                />
                <span class="nexus-slider-round"></span>
              </label>
            </div>
          </div>
          <button
            class="autofill-trigger-btn"
            :disabled="isRunningApplier"
            @click="triggerJobAutofill"
          >
            <span v-if="isRunningApplier" class="spinner-small"></span>
            <svg
              v-else
              viewBox="0 0 24 24"
              width="18"
              height="18"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <span>{{ isRunningApplier ? 'Filling Application...' : 'Fill Active Job Page' }}</span>
          </button>
        </div>

        <!-- Applier Result Banner -->
        <div v-if="applierResult" class="applier-result-box" :class="{ error: !applierResult.success }">
          <div class="result-header">
            <span class="result-icon">{{ applierResult.success ? '✅' : '⚠️' }}</span>
            <span class="result-title">{{ applierResult.message }}</span>
          </div>
          <div v-if="applierResult.details" class="result-stats">
            <div v-if="applierResult.details.companyName" class="stat-tag">
              🏢 <strong>{{ applierResult.details.companyName }}</strong>
            </div>
            <div v-if="applierResult.details.jobTitle" class="stat-tag">
              💼 <strong>{{ applierResult.details.jobTitle }}</strong>
            </div>
            <div v-if="applierResult.details.filledFieldsCount !== undefined" class="stat-tag">
              📝 <strong>{{ applierResult.details.filledFieldsCount }}</strong> fields populated
            </div>
          </div>
          <div v-if="applierResult.details && applierResult.details.tailoredQuestions && applierResult.details.tailoredQuestions.length > 0" class="tailored-preview">
            <p class="preview-title">Synthesized Company Answers:</p>
            <div v-for="(q, idx) in applierResult.details.tailoredQuestions" :key="idx" class="tailored-item">
              <span class="q-label">Q: {{ q.question }}</span>
              <p class="a-text">{{ q.answer }}</p>
            </div>
          </div>
          <div v-if="applierResult.details && applierResult.details.reviewNeeded && applierResult.details.reviewNeeded.length > 0" class="review-items">
            <p class="review-title">Items for Manual Review:</p>
            <ul>
              <li v-for="(item, idx) in applierResult.details.reviewNeeded" :key="idx">{{ item }}</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Upload / Import Options -->
      <div class="section">
        <div class="section-header-row">
          <h3 class="section-title">Import & Sync Resume</h3>
          <button class="text-action-btn" @click="loadSampleProfile">Load Demo Profile</button>
        </div>

        <div
          class="drop-zone"
          :class="{ dragging: isDragging }"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleFileDrop"
          @click="triggerFileInput"
        >
          <input
            type="file"
            ref="fileInputRef"
            class="hidden-file-input"
            accept=".json,.txt,.doc,.docx,.pdf"
            @change="handleFileInputChange"
          />
          <svg
            class="upload-icon"
            viewBox="0 0 24 24"
            width="32"
            height="32"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p class="drop-text">Click or drop resume file (JSON, TXT, DOCX, PDF)</p>
          <span class="drop-hint">Data is parsed directly inside your browser and stored in encrypted extension storage</span>
        </div>
      </div>

      <!-- Profile Form Fields -->
      <div class="section">
        <h3 class="section-title">Candidate Profile Vault</h3>

        <div class="form-card">
          <!-- Personal Info -->
          <div class="form-group-title">Personal Information</div>
          <div class="form-grid">
            <div class="form-field">
              <label>Full Name</label>
              <input v-model="profile.fullName" type="text" placeholder="e.g. Alex Morgan" />
            </div>
            <div class="form-field">
              <label>Email Address</label>
              <input v-model="profile.email" type="email" placeholder="e.g. alex.morgan@example.com" />
            </div>
            <div class="form-field">
              <label>Phone Number</label>
              <input v-model="profile.phone" type="tel" placeholder="e.g. +1 (555) 234-5678" />
            </div>
            <div class="form-field">
              <label>Location / City</label>
              <input v-model="profile.location" type="text" placeholder="e.g. San Francisco, CA" />
            </div>
          </div>

          <!-- Links -->
          <div class="form-group-title">Web & Portfolios</div>
          <div class="form-grid">
            <div class="form-field">
              <label>LinkedIn URL</label>
              <input v-model="profile.linkedIn" type="url" placeholder="https://linkedin.com/in/alexmorgan" />
            </div>
            <div class="form-field">
              <label>GitHub URL</label>
              <input v-model="profile.github" type="url" placeholder="https://github.com/alexmorgan" />
            </div>
            <div class="form-field full-width">
              <label>Portfolio / Personal Website</label>
              <input v-model="profile.portfolio" type="url" placeholder="https://alexmorgan.dev" />
            </div>
          </div>

          <!-- Professional History -->
          <div class="form-group-title">Professional Experience</div>
          <div class="form-grid">
            <div class="form-field">
              <label>Current / Most Recent Role</label>
              <input v-model="profile.currentRole" type="text" placeholder="e.g. Senior Full-Stack Engineer" />
            </div>
            <div class="form-field">
              <label>Current Company</label>
              <input v-model="profile.currentCompany" type="text" placeholder="e.g. CloudScale Systems" />
            </div>
            <div class="form-field">
              <label>Years of Experience</label>
              <input v-model="profile.yearsOfExperience" type="text" placeholder="e.g. 6" />
            </div>
            <div class="form-field">
              <label>Notice Period / Availability</label>
              <input v-model="profile.noticePeriod" type="text" placeholder="e.g. 2 weeks" />
            </div>
          </div>

          <!-- Skills & Summary -->
          <div class="form-group-title">Skills & Highlights</div>
          <div class="form-field full-width">
            <label>Core Technical Skills (comma separated)</label>
            <input
              v-model="skillsInput"
              type="text"
              placeholder="e.g. TypeScript, Vue.js, Node.js, Python, PostgreSQL, AWS, Docker"
              @blur="updateSkillsArray"
            />
          </div>

          <div class="form-field full-width">
            <label>Professional Summary & Elevator Pitch</label>
            <textarea
              v-model="profile.summary"
              rows="3"
              placeholder="Highlight your key accomplishments, architectural expertise, and engineering focus..."
            ></textarea>
          </div>

          <!-- Action Buttons -->
          <div class="form-actions">
            <button class="save-vault-btn" @click="saveProfile">
              <svg
                viewBox="0 0 24 24"
                width="16"
                height="16"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
              </svg>
              <span>{{ saveButtonText }}</span>
            </button>
            <button class="clear-btn" @click="clearProfile">Clear Vault</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { STORAGE_KEYS } from '@/common/constants';
import type { ResumeProfile } from '@nexusai/shared';

defineEmits(['back']);

const fileInputRef = ref<HTMLInputElement | null>(null);
const isDragging = ref(false);
const isRunningApplier = ref(false);
const saveButtonText = ref('Save to Vault');
const applierResult = ref<{
  success: boolean;
  message: string;
  details?: any;
} | null>(null);

const defaultProfile: ResumeProfile = {
  fullName: '',
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  location: '',
  linkedIn: '',
  github: '',
  portfolio: '',
  currentRole: '',
  currentCompany: '',
  yearsOfExperience: '',
  noticePeriod: '',
  summary: '',
  skills: [],
  workHistory: [],
  education: [],
  customFields: {},
};

const profile = ref<ResumeProfile>({ ...defaultProfile });
const skillsInput = ref('');

const isHumanTextEnabled = ref(true);

onMounted(async () => {
  await loadStoredProfile();
  await loadHumanTextPreference();
});

async function loadHumanTextPreference() {
  try {
    const res = await chrome.storage.local.get([STORAGE_KEYS.HUMAN_TEXT_ENABLED]);
    if (res[STORAGE_KEYS.HUMAN_TEXT_ENABLED] !== undefined) {
      isHumanTextEnabled.value = res[STORAGE_KEYS.HUMAN_TEXT_ENABLED] !== false;
    } else {
      isHumanTextEnabled.value = true;
    }
  } catch (e) {
    console.error('Failed to load human text preference:', e);
  }
}

async function saveHumanTextPreference() {
  try {
    await chrome.storage.local.set({
      [STORAGE_KEYS.HUMAN_TEXT_ENABLED]: isHumanTextEnabled.value,
    });
  } catch (e) {
    console.error('Failed to persist human text preference:', e);
  }
}

async function loadStoredProfile() {
  try {
    const data = await chrome.storage.local.get([STORAGE_KEYS.RESUME_PROFILE]);
    if (data[STORAGE_KEYS.RESUME_PROFILE]) {
      profile.value = { ...defaultProfile, ...data[STORAGE_KEYS.RESUME_PROFILE] };
      skillsInput.value = Array.isArray(profile.value.skills) ? profile.value.skills.join(', ') : '';
    }
  } catch (error) {
    console.error('Failed to load profile from storage:', error);
  }
}

function updateSkillsArray() {
  if (!skillsInput.value) {
    profile.value.skills = [];
    return;
  }
  profile.value.skills = skillsInput.value
    .split(',')
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
}

async function saveProfile() {
  updateSkillsArray();
  try {
    await chrome.storage.local.set({
      [STORAGE_KEYS.RESUME_PROFILE]: JSON.parse(JSON.stringify(profile.value)),
    });
    saveButtonText.value = 'Saved!';
    setTimeout(() => {
      saveButtonText.value = 'Save to Vault';
    }, 2000);
  } catch (error) {
    console.error('Failed to save resume profile:', error);
    saveButtonText.value = 'Save Failed';
  }
}

async function clearProfile() {
  if (confirm('Are you sure you want to clear your stored resume profile?')) {
    profile.value = { ...defaultProfile };
    skillsInput.value = '';
    await chrome.storage.local.remove([STORAGE_KEYS.RESUME_PROFILE]);
  }
}

function loadSampleProfile() {
  profile.value = {
    fullName: 'Jordan Vance',
    firstName: 'Jordan',
    lastName: 'Vance',
    email: 'jordan.vance@example.com',
    phone: '+1 (415) 890-1234',
    location: 'San Francisco, CA',
    linkedIn: 'https://linkedin.com/in/jordanvance',
    github: 'https://github.com/jordanvance',
    portfolio: 'https://jordanvance.dev',
    currentRole: 'Senior Staff Software Engineer',
    currentCompany: 'Nexus Technologies',
    yearsOfExperience: '7',
    noticePeriod: '2 weeks',
    summary:
      'Full-stack systems engineer passionate about browser automation, AI tool orchestration, and resilient cloud architecture. Proven track record leading high-throughput distributed systems.',
    skills: ['TypeScript', 'Vue.js', 'Node.js', 'Python', 'Docker', 'GraphQL', 'PostgreSQL'],
    workHistory: [
      {
        title: 'Senior Staff Software Engineer',
        company: 'Nexus Technologies',
        startDate: '2021',
        description: 'Led architecture of high-speed browser automation pipeline handling 10M+ daily operations.',
      },
    ],
    education: [
      {
        degree: 'B.S. in Computer Science',
        institution: 'University of California, Berkeley',
        year: '2019',
      },
    ],
  };
  skillsInput.value = profile.value.skills.join(', ');
  saveProfile();
}

function triggerFileInput() {
  if (fileInputRef.value) {
    fileInputRef.value.click();
  }
}

function handleFileInputChange(e: Event) {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    parseResumeFile(target.files[0]);
  }
}

function handleFileDrop(e: DragEvent) {
  isDragging.value = false;
  if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
    parseResumeFile(e.dataTransfer.files[0]);
  }
}

async function parseResumeFile(file: File) {
  try {
    const text = await file.text();

    // Check if JSON format
    if (file.name.endsWith('.json')) {
      try {
        const parsed = JSON.parse(text);
        profile.value = { ...defaultProfile, ...parsed };
        skillsInput.value = Array.isArray(profile.value.skills) ? profile.value.skills.join(', ') : '';
        await saveProfile();
        return;
      } catch {
        // Fall through to text heuristic parsing
      }
    }

    // Heuristic text parsing
    const lines = text.split('\n').map((l) => l.trim()).filter((l) => l.length > 0);
    if (lines.length > 0 && !profile.value.fullName) {
      profile.value.fullName = lines[0];
    }

    const emailMatch = text.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/);
    if (emailMatch) profile.value.email = emailMatch[0];

    const phoneMatch = text.match(/(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/);
    if (phoneMatch) profile.value.phone = phoneMatch[0];

    const linkedInMatch = text.match(/https?:\/\/(www\.)?linkedin\.com\/in\/[a-zA-Z0-9_-]+/);
    if (linkedInMatch) profile.value.linkedIn = linkedInMatch[0];

    const githubMatch = text.match(/https?:\/\/(www\.)?github\.com\/[a-zA-Z0-9_-]+/);
    if (githubMatch) profile.value.github = githubMatch[0];

    await saveProfile();
  } catch (error) {
    console.error('File parsing error:', error);
  }
}

async function triggerJobAutofill() {
  isRunningApplier.value = true;
  applierResult.value = null;

  try {
    // 1. Ensure profile is saved
    updateSkillsArray();
    await saveProfile();

    // 2. Query active tab
    const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!activeTab || !activeTab.id) {
      throw new Error('No active browser tab detected');
    }

    // 3. Delegate to background worker tool executor via runtime message or direct tool invocation
    const response = await chrome.runtime.sendMessage({
      action: 'CALL_TOOL',
      name: 'nexus_job_applier',
      args: {
        tabId: activeTab.id,
        mode: 'full',
        resumeProfile: JSON.parse(JSON.stringify(profile.value)),
        tailorAnswers: true,
        humanizeText: isHumanTextEnabled.value,
      },
    });

    if (response && response.error) {
      throw new Error(response.error);
    }

    let parsedResult: any = response;
    if (response && response.content && response.content[0] && response.content[0].text) {
      try {
        parsedResult = JSON.parse(response.content[0].text);
      } catch {
        parsedResult = response.content[0].text;
      }
    }

    applierResult.value = {
      success: true,
      message: `Successfully populated job application at ${parsedResult.companyName || 'active site'}!`,
      details: parsedResult,
    };
  } catch (error) {
    console.error('Job autofill execution error:', error);
    applierResult.value = {
      success: false,
      message: error instanceof Error ? error.message : 'Job autofill failed',
    };
  } finally {
    isRunningApplier.value = false;
  }
}
</script>

<style scoped>
.resume-hub-page {
  display: flex;
  flex-direction: column;
  min-height: 100%;
  background: var(--bg-primary, #0f172a);
  color: var(--text-primary, #f8fafc);
  font-family: inherit;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(8px);
  position: sticky;
  top: 0;
  z-index: 10;
}

.back-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #94a3b8;
  padding: 6px 10px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
}

.header-title-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #f1f5f9;
}

.vault-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 12px;
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.3);
  font-weight: 500;
}

.page-content {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.section-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #94a3b8;
}

.text-action-btn {
  background: none;
  border: none;
  color: #38bdf8;
  font-size: 12px;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
}

.text-action-btn:hover {
  color: #7dd3fc;
}

/* Autofill Banner */
.autofill-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.95));
  border: 1px solid rgba(56, 189, 248, 0.3);
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.banner-title {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: #38bdf8;
}

.banner-subtitle {
  margin: 0;
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.4;
}

.humanizer-toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 10px;
  padding: 6px 10px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(56, 189, 248, 0.2);
  border-radius: 8px;
}

.humanizer-toggle-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.humanizer-toggle-title {
  font-size: 12px;
  font-weight: 600;
  color: #38bdf8;
}

.humanizer-toggle-hint {
  font-size: 11px;
  color: #94a3b8;
}

/* Modern Switch */
.nexus-switch-modern {
  position: relative;
  display: inline-block;
  width: 34px;
  height: 18px;
  flex-shrink: 0;
  cursor: pointer;
}

.nexus-switch-modern input {
  opacity: 0;
  width: 0;
  height: 0;
}

.nexus-slider-round {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #334155;
  transition: 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 34px;
}

.nexus-slider-round:before {
  position: absolute;
  content: "";
  height: 14px;
  width: 14px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  transition: 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.nexus-switch-modern input:checked + .nexus-slider-round {
  background-color: #0284c7;
}

.nexus-switch-modern input:checked + .nexus-slider-round:before {
  transform: translateX(16px);
}

.autofill-trigger-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #0284c7, #2563eb);
  color: white;
  border: none;
  border-radius: 10px;
  padding: 10px 16px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.autofill-trigger-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
}

.autofill-trigger-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Result Box */
.applier-result-box {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(16, 185, 129, 0.4);
  border-radius: 10px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.applier-result-box.error {
  border-color: rgba(239, 68, 68, 0.4);
}

.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #f1f5f9;
}

.result-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.stat-tag {
  font-size: 12px;
  background: rgba(255, 255, 255, 0.06);
  padding: 3px 8px;
  border-radius: 6px;
  color: #cbd5e1;
}

.tailored-preview {
  margin-top: 6px;
  background: rgba(0, 0, 0, 0.25);
  padding: 8px 10px;
  border-radius: 8px;
}

.preview-title, .review-title {
  margin: 0 0 4px 0;
  font-size: 12px;
  font-weight: 600;
  color: #38bdf8;
}

.tailored-item {
  margin-bottom: 6px;
}

.q-label {
  font-size: 11px;
  color: #94a3b8;
  font-weight: 600;
}

.a-text {
  margin: 2px 0 0 0;
  font-size: 12px;
  color: #e2e8f0;
  line-height: 1.4;
}

.review-items ul {
  margin: 0;
  padding-left: 18px;
  font-size: 12px;
  color: #fcd34d;
}

/* Drop Zone */
.drop-zone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2px dashed rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 18px 14px;
  cursor: pointer;
  background: rgba(30, 41, 59, 0.4);
  transition: all 0.2s ease;
  text-align: center;
}

.drop-zone:hover, .drop-zone.dragging {
  border-color: #38bdf8;
  background: rgba(56, 189, 248, 0.08);
}

.hidden-file-input {
  display: none;
}

.upload-icon {
  color: #38bdf8;
  margin-bottom: 6px;
}

.drop-text {
  margin: 0 0 4px 0;
  font-size: 13px;
  font-weight: 500;
  color: #e2e8f0;
}

.drop-hint {
  font-size: 11px;
  color: #64748b;
  max-width: 320px;
}

/* Form Card */
.form-card {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-group-title {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #38bdf8;
  margin-top: 4px;
  padding-bottom: 4px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-field.full-width {
  grid-column: 1 / -1;
}

.form-field label {
  font-size: 11px;
  font-weight: 500;
  color: #94a3b8;
}

.form-field input, .form-field textarea {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  padding: 8px 10px;
  color: #f8fafc;
  font-size: 12px;
  font-family: inherit;
  transition: border-color 0.2s ease;
}

.form-field input:focus, .form-field textarea:focus {
  outline: none;
  border-color: #38bdf8;
  background: rgba(15, 23, 42, 0.95);
}

.form-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 8px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.save-vault-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.save-vault-btn:hover {
  background: #059669;
}

.clear-btn {
  background: transparent;
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-btn:hover {
  background: rgba(239, 68, 68, 0.1);
}
</style>
