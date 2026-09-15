import { createErrorResponse, ToolResult } from '@/common/tool-handler';
import { BaseBrowserToolExecutor } from '../base-browser';
import { TOOL_NAMES, ResumeProfile, NexusJobApplierParams } from '@nexusai/shared';
import { STORAGE_KEYS } from '@/common/constants';

/**
 * Autonomous Job Application Form Filling Tool
 * Extracts company/job context from active tab, maps candidate resume profile to form inputs,
 * synthesizes contextual tailored responses for open-ended application questions,
 * and dispatches native reactive DOM events.
 */
class JobApplierTool extends BaseBrowserToolExecutor {
  name = TOOL_NAMES.BROWSER.JOB_APPLIER;

  async execute(args: NexusJobApplierParams): Promise<ToolResult> {
    try {
      const {
        tabId: explicitTabId,
        mode = 'full',
        resumeProfile: argProfile,
        tailorAnswers = true,
        customAnswers = {},
        submitAfter = false,
        humanizeText: argHumanize,
      } = args || {};

      let humanizeText = argHumanize;
      if (humanizeText === undefined) {
        const storedSetting = await chrome.storage.local.get([STORAGE_KEYS.HUMAN_TEXT_ENABLED]);
        humanizeText = storedSetting[STORAGE_KEYS.HUMAN_TEXT_ENABLED] !== false; // Default to true
      }

      // 1. Resolve Target Tab
      let tab: chrome.tabs.Tab;
      if (typeof explicitTabId === 'number') {
        const foundTab = await this.tryGetTab(explicitTabId);
        if (!foundTab || !foundTab.id) {
          return createErrorResponse(`Tab with ID ${explicitTabId} not found`);
        }
        tab = foundTab;
      } else {
        tab = await this.getActiveTabOrThrow();
      }

      const tabId = tab.id!;

      // 2. Resolve Applicant Profile (from arguments or local vault storage)
      let profile: ResumeProfile = argProfile || {};
      if (!argProfile || Object.keys(argProfile).length === 0) {
        const storageData = await chrome.storage.local.get([STORAGE_KEYS.RESUME_PROFILE]);
        if (storageData[STORAGE_KEYS.RESUME_PROFILE]) {
          profile = storageData[STORAGE_KEYS.RESUME_PROFILE] as ResumeProfile;
        }
      }

      // Ensure profile has at least minimal structure
      profile = {
        fullName: profile.fullName || '',
        firstName: profile.firstName || (profile.fullName ? profile.fullName.split(' ')[0] : ''),
        lastName:
          profile.lastName ||
          (profile.fullName ? profile.fullName.split(' ').slice(1).join(' ') : ''),
        email: profile.email || '',
        phone: profile.phone || '',
        location: profile.location || profile.city || '',
        linkedIn: profile.linkedIn || '',
        github: profile.github || '',
        portfolio: profile.portfolio || '',
        currentRole: profile.currentRole || '',
        currentCompany: profile.currentCompany || '',
        yearsOfExperience: profile.yearsOfExperience || '',
        noticePeriod: profile.noticePeriod || '',
        summary: profile.summary || '',
        skills: profile.skills || [],
        workHistory: profile.workHistory || [],
        education: profile.education || [],
        customFields: profile.customFields || {},
      };

      // 3. Execute in-page autonomous job applier script
      const injectionResults = await chrome.scripting.executeScript({
        target: { tabId },
        func: inPageJobApplierScript,
        args: [
          {
            mode,
            profile,
            tailorAnswers,
            customAnswers,
            submitAfter,
            humanizeText,
          },
        ],
      });

      if (!injectionResults || !injectionResults[0] || !injectionResults[0].result) {
        return createErrorResponse('Failed to execute job applier in page context');
      }

      const executionData = injectionResults[0].result;

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(
              {
                success: true,
                tabId,
                pageUrl: tab.url,
                ...executionData,
              },
              null,
              2,
            ),
          },
        ],
      };
    } catch (error) {
      console.error('[JobApplierTool] Execution error:', error);
      return createErrorResponse(
        `Job application filling failed: ${error instanceof Error ? error.message : String(error)}`,
      );
    }
  }
}

/**
 * Self-contained in-page script executed within the job application page
 */
function inPageJobApplierScript(config: {
  mode: 'inspect' | 'fill' | 'full';
  profile: any;
  tailorAnswers: boolean;
  customAnswers: Record<string, string>;
  submitAfter: boolean;
  humanizeText?: boolean;
}) {
  const { mode, profile, tailorAnswers, customAnswers, submitAfter, humanizeText = true } = config;

  // ==========================================
  // 1. Detect Company & Job Context
  // ==========================================
  function detectPageContext() {
    let companyName = '';
    let jobTitle = '';
    let jobDescription = '';

    // A. Greenhouse
    const ghCompany = document.querySelector('#header .company-name, [data-qa="company-name"]');
    if (ghCompany && ghCompany.textContent) {
      companyName = ghCompany.textContent.trim();
    }
    const ghTitle = document.querySelector('#header .app-title, .job-title');
    if (ghTitle && ghTitle.textContent) {
      jobTitle = ghTitle.textContent.trim();
    }

    // B. Lever
    const leverHeader = document.querySelector('.posting-headline h2');
    if (leverHeader && leverHeader.textContent) {
      jobTitle = leverHeader.textContent.trim();
    }
    const leverCompany = document.querySelector('.main-header-logo img, .posting-header-logo img');
    if (leverCompany && (leverCompany as HTMLImageElement).alt) {
      companyName = (leverCompany as HTMLImageElement).alt.replace(/logo/i, '').trim();
    }

    // C. Meta Tags Fallback
    if (!companyName) {
      const ogSiteName = document.querySelector('meta[property="og:site_name"]');
      if (ogSiteName && ogSiteName.getAttribute('content')) {
        companyName = ogSiteName.getAttribute('content')!.trim();
      }
    }

    // D. Document Title Parsing
    if (!companyName || !jobTitle) {
      const docTitle = document.title || '';
      // Pattern: "Senior Engineer at Acme Corp" or "Acme Corp - Senior Engineer"
      if (docTitle.includes(' at ')) {
        const parts = docTitle.split(' at ');
        if (!jobTitle) jobTitle = parts[0].trim();
        if (!companyName) companyName = parts[1].split(/[-–|]/)[0].trim();
      } else if (docTitle.includes(' - ')) {
        const parts = docTitle.split(' - ');
        if (!companyName) companyName = parts[0].trim();
        if (!jobTitle) jobTitle = parts[1].split(/[-–|]/)[0].trim();
      } else if (docTitle.includes(' | ')) {
        const parts = docTitle.split(' | ');
        if (!jobTitle) jobTitle = parts[0].trim();
        if (!companyName) companyName = parts[1].trim();
      }
    }

    // E. Fallback Domain Name
    if (!companyName) {
      const host = window.location.hostname.replace(/^www\./, '');
      const parts = host.split('.');
      if (parts.length >= 2) {
        companyName = parts[0].charAt(0).toUpperCase() + parts[0].slice(1);
      }
    }

    // F. Job Title Fallback
    if (!jobTitle) {
      const h1 = document.querySelector('h1');
      if (h1 && h1.textContent && h1.textContent.length < 100) {
        jobTitle = h1.textContent.trim();
      }
    }

    // G. Job Description Content
    const descEl = document.querySelector(
      '#content, .job-description, .posting-page, [data-automation-id="jobPostingDescription"], main, article',
    );
    if (descEl && descEl.textContent) {
      jobDescription = descEl.textContent.trim().slice(0, 3000);
    }

    return {
      companyName: companyName || 'the company',
      jobTitle: jobTitle || 'this position',
      jobDescription,
    };
  }

  const context = detectPageContext();

  // ==========================================
  // 2. Synthesize Tailored Answer Helper
  // ==========================================
  function sanitizeHumanOutput(text: string): string {
    let clean = text;
    // Strip em dashes (—) and en dashes with spaces
    clean = clean.replace(/\s*—\s*/g, ', ').replace(/\s*–\s*/g, ', ');
    // Remove conversational throat-clearing
    clean = clean.replace(/^(Certainly!?|Sure!?|Here is [^:]+:|As an AI[^,]*,\s*)/i, '').trim();
    // Replace banned AI buzzwords with natural human words
    const replacements: Record<string, string> = {
      'delve into': 'look into',
      'delve': 'explore',
      'spearheaded': 'led',
      'spearhead': 'lead',
      'robust': 'reliable',
      'pivotal': 'important',
      'transformative': 'major',
      'cutting-edge': 'modern',
      'showcasing': 'demonstrating',
      'underscoring': 'highlighting',
      'streamline': 'simplify',
      'streamlined': 'simplified',
      'foster': 'build',
      'fostered': 'built',
      'beacon': 'model',
      'testament': 'proof',
      'tapestry': 'variety',
      'game-changer': 'breakthrough',
      'multifaceted': 'diverse',
      'harness': 'use',
      'harnessed': 'used',
      'seamless': 'smooth',
      'seamlessly': 'smoothly',
      'passionate about': 'focused on',
      'excited about the opportunity to': 'keen to',
      'in today\'s fast-paced world': 'today',
      'not only': 'both',
    };
    for (const [bad, good] of Object.entries(replacements)) {
      const regex = new RegExp(`\\b${bad}\\b`, 'gi');
      clean = clean.replace(regex, good);
    }
    // Remove generic conclusions
    clean = clean.replace(/\s*(In conclusion|To summarize|All in all)[^.]*\.?$/i, '').trim();
    return clean;
  }

  function generateTailoredAnswer(promptText: string): string {
    const p = promptText.toLowerCase();

    // Check manual override
    for (const [key, val] of Object.entries(customAnswers)) {
      if (p.includes(key.toLowerCase())) {
        return humanizeText ? sanitizeHumanOutput(val) : val;
      }
    }

    const skillsList = Array.isArray(profile.skills) ? profile.skills.join(', ') : 'software engineering';
    const primarySkill = Array.isArray(profile.skills) && profile.skills.length > 0 ? profile.skills[0] : 'software development';
    const currentRole = profile.currentRole || 'Software Engineer';
    const currentComp = profile.currentCompany ? ` at ${profile.currentCompany}` : '';
    const summaryText = profile.summary || '';

    let output = '';

    if (humanizeText) {
      // Question: Why do you want to work here / Why company?
      if (p.includes('why do you want') || p.includes('why us') || p.includes(`why ${context.companyName.toLowerCase()}`) || p.includes('what interests you')) {
        output = `I've worked as a ${currentRole}${currentComp} building systems with ${skillsList}. What stands out to me about ${context.companyName} is your practical focus on ${primarySkill} and the direction you're taking with this product. I want to bring my day-to-day experience shipping clean code and solving technical bottlenecks directly to the ${context.jobTitle} team.`;
      }
      // Question: Tell me about yourself / Background
      else if (p.includes('tell us about yourself') || p.includes('about you') || p.includes('summary') || p.includes('cover letter')) {
        if (summaryText) {
          output = `I'm a ${currentRole}${currentComp}. ${summaryText.replace(/I am/g, "I'm")} I'm looking forward to applying what I've learned to the ${context.jobTitle} position at ${context.companyName}.`;
        } else {
          output = `I'm a ${currentRole}${currentComp} working primarily with ${skillsList}. Most of my recent work involves designing straightforward architectures, fixing performance issues, and shipping reliable code that teams can easily maintain.`;
        }
      }
      // Question: Challenging project / Accomplishment
      else if (p.includes('project') || p.includes('challenge') || p.includes('proud') || p.includes('accomplishment')) {
        if (profile.workHistory && profile.workHistory.length > 0 && profile.workHistory[0].description) {
          output = `At ${profile.workHistory[0].company}, our team delivered ${profile.workHistory[0].description}. I helped sort through the technical bottlenecks, cleaned up the core flow using ${primarySkill}, and got the release out on schedule without breaking production.`;
        } else {
          output = `In my recent work, our team addressed major service bottlenecks. I restructured our core data queries using ${primarySkill}, which cut response times by over 35% and stabilized deployment cycles under heavy traffic.`;
        }
      }
      // Question: Salary expectations
      else if (p.includes('salary') || p.includes('compensation') || p.includes('rate')) {
        output = 'Competitive market rate, open to discussion based on the total package.';
      }
      // Question: Availability / Notice period
      else if (p.includes('notice') || p.includes('available') || p.includes('start date')) {
        output = profile.noticePeriod || 'Available within 2-4 weeks or immediately upon offer finalization.';
      }
      // Default open-ended response
      else {
        output = `I'm a ${currentRole} with hands-on experience in ${skillsList}. I focus on writing clean, tested code and collaborating directly with product teams to get high-priority features into production for ${context.companyName}.`;
      }

      return sanitizeHumanOutput(output);
    }

    // Standard mode fallback
    if (p.includes('why do you want') || p.includes('why us') || p.includes(`why ${context.companyName.toLowerCase()}`) || p.includes('what interests you')) {
      return `I am excited about the opportunity to contribute to ${context.companyName} as a ${context.jobTitle}. With my background in ${skillsList}, I have built resilient systems and solved complex domain problems.`;
    }
    if (p.includes('tell us about yourself') || p.includes('about you') || p.includes('summary') || p.includes('cover letter')) {
      if (summaryText) {
        return `${summaryText} I look forward to bringing these skills to ${context.companyName}.`;
      }
      return `I am an experienced ${currentRole}${currentComp} specializing in ${skillsList}. Throughout my career, I have driven projects with a focus on reliability, clean architecture, and performance.`;
    }
    if (p.includes('project') || p.includes('challenge') || p.includes('proud') || p.includes('accomplishment')) {
      if (profile.workHistory && profile.workHistory.length > 0 && profile.workHistory[0].description) {
        return `At ${profile.workHistory[0].company}, I led the implementation of ${profile.workHistory[0].description}.`;
      }
      return `In my recent work, I improved system latency and uptime using ${skillsList}.`;
    }
    if (p.includes('salary') || p.includes('compensation') || p.includes('rate')) {
      return 'Competitive market rate / Open to negotiation based on the complete compensation package.';
    }
    if (p.includes('notice') || p.includes('available') || p.includes('start date')) {
      return profile.noticePeriod || 'Available within 2-4 weeks or immediately upon offer finalization.';
    }
    return `As a ${currentRole}, I specialize in ${skillsList}. I look forward to contributing to ${context.companyName}.`;
  }

  // ==========================================
  // 3. Discover Form Fields
  // ==========================================
  interface DiscoveredField {
    element: HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement;
    label: string;
    fieldType: string; // 'first_name' | 'last_name' | 'full_name' | 'email' | 'phone' | etc.
    inputType: string;
  }

  function getFieldLabel(el: HTMLElement): string {
    // 1. Associated label via for attribute
    if (el.id) {
      const lbl = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
      if (lbl && lbl.textContent) return lbl.textContent.trim();
    }
    // 2. Parent label element
    const parentLabel = el.closest('label');
    if (parentLabel && parentLabel.textContent) {
      return parentLabel.textContent.trim();
    }
    // 3. ARIA attributes
    const ariaLabel = el.getAttribute('aria-label');
    if (ariaLabel) return ariaLabel.trim();
    const ariaLabelledBy = el.getAttribute('aria-labelledby');
    if (ariaLabelledBy) {
      const ref = document.getElementById(ariaLabelledBy);
      if (ref && ref.textContent) return ref.textContent.trim();
    }
    // 4. Placeholder
    const placeholder = el.getAttribute('placeholder');
    if (placeholder) return placeholder.trim();
    // 5. Name or ID attribute
    const name = el.getAttribute('name');
    if (name) return name.trim();
    return el.id || '';
  }

  function classifyField(el: HTMLElement, labelText: string): string {
    const txt = `${labelText} ${(el.getAttribute('name') || '')} ${(el.getAttribute('autocomplete') || '')} ${el.id || ''}`.toLowerCase();

    if (txt.includes('first name') || txt.includes('firstname') || txt.includes('given-name') || txt.includes('fname')) {
      return 'first_name';
    }
    if (txt.includes('last name') || txt.includes('lastname') || txt.includes('family-name') || txt.includes('lname') || txt.includes('surname')) {
      return 'last_name';
    }
    if (txt.includes('full name') || txt.includes('fullname') || (txt.includes('name') && !txt.includes('company') && !txt.includes('file') && !txt.includes('user'))) {
      return 'full_name';
    }
    if (txt.includes('email') || txt.includes('e-mail')) {
      return 'email';
    }
    if (txt.includes('phone') || txt.includes('mobile') || txt.includes('tel') || txt.includes('cell')) {
      return 'phone';
    }
    if (txt.includes('linkedin') || txt.includes('linked-in')) {
      return 'linkedin';
    }
    if (txt.includes('github') || txt.includes('git')) {
      return 'github';
    }
    if (txt.includes('portfolio') || txt.includes('website') || txt.includes('personal url') || txt.includes('site')) {
      return 'portfolio';
    }
    if (txt.includes('city') || txt.includes('location') || txt.includes('address')) {
      return 'location';
    }
    if (txt.includes('current company') || txt.includes('employer') || txt.includes('organization')) {
      return 'current_company';
    }
    if (txt.includes('current title') || txt.includes('headline') || txt.includes('current role')) {
      return 'current_role';
    }
    if (txt.includes('experience') || txt.includes('years of')) {
      return 'years_of_experience';
    }
    if (txt.includes('notice period') || txt.includes('availability') || txt.includes('start date')) {
      return 'notice_period';
    }
    if (txt.includes('authorized') || txt.includes('sponsorship') || txt.includes('visa')) {
      return 'authorization';
    }
    if (el.tagName.toLowerCase() === 'textarea' || (el as HTMLInputElement).type === 'textarea') {
      return 'custom_question';
    }
    return 'generic';
  }

  // Find all form controls
  const inputs = Array.from(
    document.querySelectorAll<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>(
      'input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="reset"]), textarea, select',
    ),
  );

  const discoveredFields: DiscoveredField[] = [];
  const fileUploadElements: string[] = [];

  for (const el of inputs) {
    if (el instanceof HTMLInputElement && el.type === 'file') {
      fileUploadElements.push(getFieldLabel(el) || 'Resume / CV File Input');
      continue;
    }

    // Ignore invisible / disabled elements
    if (el.offsetParent === null && el.offsetWidth === 0 && el.offsetHeight === 0) {
      continue;
    }
    if (el.disabled || el.readOnly) {
      continue;
    }

    const label = getFieldLabel(el);
    const fieldType = classifyField(el, label);
    discoveredFields.push({
      element: el,
      label,
      fieldType,
      inputType: el.tagName.toLowerCase() === 'input' ? (el as HTMLInputElement).type : el.tagName.toLowerCase(),
    });
  }

  // If inspect mode only, return scan findings
  if (mode === 'inspect') {
    return {
      companyName: context.companyName,
      jobTitle: context.jobTitle,
      totalDiscoveredFields: discoveredFields.length,
      fileUploadFields: fileUploadElements,
      fields: discoveredFields.map((f) => ({
        label: f.label,
        type: f.fieldType,
        inputType: f.inputType,
      })),
      reviewNeeded: fileUploadElements.length > 0 ? ['Resume file attachment required'] : [],
    };
  }

  // ==========================================
  // 4. Fill Fields and Dispatch Synthetic Events
  // ==========================================
  const filledFields: Array<{ label: string; fieldType: string; value: string }> = [];
  const tailoredQuestions: Array<{ question: string; answer: string }> = [];
  const reviewNeeded: string[] = [];

  function setNativeValue(element: HTMLInputElement | HTMLTextAreaElement, value: string) {
    const prototype = Object.getPrototypeOf(element);
    const prototypeValueSetter = Object.getOwnPropertyDescriptor(prototype, 'value')?.set;
    if (prototypeValueSetter) {
      prototypeValueSetter.call(element, value);
    } else {
      element.value = value;
    }
    element.dispatchEvent(new Event('focus', { bubbles: true, composed: true }));
    element.dispatchEvent(new Event('input', { bubbles: true, composed: true }));
    element.dispatchEvent(new Event('change', { bubbles: true, composed: true }));
    element.dispatchEvent(new Event('blur', { bubbles: true, composed: true }));
  }

  for (const item of discoveredFields) {
    const el = item.element;
    let valToSet: string | null = null;

    switch (item.fieldType) {
      case 'first_name':
        valToSet = profile.firstName || (profile.fullName ? profile.fullName.split(' ')[0] : '');
        break;
      case 'last_name':
        valToSet = profile.lastName || (profile.fullName ? profile.fullName.split(' ').slice(1).join(' ') : '');
        break;
      case 'full_name':
        valToSet = profile.fullName || (profile.firstName ? `${profile.firstName} ${profile.lastName}`.trim() : '');
        break;
      case 'email':
        valToSet = profile.email || '';
        break;
      case 'phone':
        valToSet = profile.phone || '';
        break;
      case 'location':
        valToSet = profile.location || '';
        break;
      case 'linkedin':
        valToSet = profile.linkedIn || '';
        break;
      case 'github':
        valToSet = profile.github || '';
        break;
      case 'portfolio':
        valToSet = profile.portfolio || '';
        break;
      case 'current_company':
        valToSet = profile.currentCompany || '';
        break;
      case 'current_role':
        valToSet = profile.currentRole || '';
        break;
      case 'years_of_experience':
        valToSet = profile.yearsOfExperience ? String(profile.yearsOfExperience) : '';
        break;
      case 'notice_period':
        valToSet = profile.noticePeriod || '';
        break;
      case 'authorization':
        // Common work authorization selects / radios
        if (el instanceof HTMLSelectElement) {
          for (const opt of Array.from(el.options)) {
            if (opt.text.toLowerCase().includes('yes') || opt.value.toLowerCase().includes('yes')) {
              el.value = opt.value;
              el.dispatchEvent(new Event('change', { bubbles: true }));
              valToSet = opt.text;
              break;
            }
          }
        }
        break;
      case 'custom_question':
        if (tailorAnswers) {
          valToSet = generateTailoredAnswer(item.label);
          tailoredQuestions.push({
            question: item.label,
            answer: valToSet,
          });
        }
        break;
      default:
        // Check if label matches any customField
        if (profile.customFields && profile.customFields[item.label]) {
          valToSet = profile.customFields[item.label];
        } else if (item.inputType === 'textarea' && tailorAnswers) {
          valToSet = generateTailoredAnswer(item.label);
          tailoredQuestions.push({
            question: item.label,
            answer: valToSet,
          });
        }
        break;
    }

    if (valToSet !== null && valToSet !== undefined && valToSet.trim() !== '') {
      if (el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement) {
        if (el.type === 'checkbox' || el.type === 'radio') {
          el.checked = true;
          el.dispatchEvent(new Event('click', { bubbles: true }));
          el.dispatchEvent(new Event('change', { bubbles: true }));
        } else {
          setNativeValue(el, valToSet);
        }
        filledFields.push({ label: item.label, fieldType: item.fieldType, value: valToSet });
      } else if (el instanceof HTMLSelectElement) {
        // Find best matching option
        let matched = false;
        for (const opt of Array.from(el.options)) {
          if (
            opt.text.toLowerCase().includes(valToSet.toLowerCase()) ||
            opt.value.toLowerCase().includes(valToSet.toLowerCase())
          ) {
            el.value = opt.value;
            el.dispatchEvent(new Event('change', { bubbles: true }));
            filledFields.push({ label: item.label, fieldType: item.fieldType, value: opt.text });
            matched = true;
            break;
          }
        }
        if (!matched && el.options.length > 1) {
          reviewNeeded.push(`Select dropdown "${item.label}" needs manual option choice`);
        }
      }
    }
  }

  // File upload alerts
  if (fileUploadElements.length > 0) {
    reviewNeeded.push(
      `File attachment field detected (${fileUploadElements.join(', ')}). Please verify or attach your resume file.`,
    );
  }

  // ==========================================
  // 5. Submit Form if requested
  // ==========================================
  let submitted = false;
  if (submitAfter) {
    const submitBtn = document.querySelector<HTMLButtonElement | HTMLInputElement>(
      'button[type="submit"], input[type="submit"], button#submit_app, [data-qa="btn-submit"]',
    );
    if (submitBtn) {
      submitBtn.click();
      submitted = true;
    } else {
      reviewNeeded.push('Submit button could not be automatically located');
    }
  }

  return {
    companyName: context.companyName,
    jobTitle: context.jobTitle,
    totalDiscoveredFields: discoveredFields.length,
    filledFieldsCount: filledFields.length,
    filledFields,
    tailoredQuestions,
    fileUploadFields: fileUploadElements,
    reviewNeeded,
    submitted,
  };
}

export const jobApplierTool = new JobApplierTool();
