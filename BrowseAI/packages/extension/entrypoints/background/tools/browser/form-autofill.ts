import { createErrorResponse, ToolResult } from '@/common/tool-handler';
import { BaseBrowserToolExecutor } from '../base-browser';
import { TOOL_NAMES, NexusFormAutofillParams } from '@nexusai/shared';

/**
 * Intelligent Form Autofill Tool
 * Matches page form fields against a dictionary of field keys and values using
 * heuristic label, name, ID, placeholder, and ARIA scoring.
 */
class FormAutofillTool extends BaseBrowserToolExecutor {
  name = TOOL_NAMES.BROWSER.FORM_AUTOFILL;

  async execute(args: NexusFormAutofillParams): Promise<ToolResult> {
    const { tabId: explicitTabId, fields = {}, clearBefore = true, submit = false } = args || {};

    if (!fields || Object.keys(fields).length === 0) {
      return createErrorResponse('No fields provided for autofill');
    }

    try {
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

      const injectionResults = await chrome.scripting.executeScript({
        target: { tabId },
        func: inPageFormAutofillScript,
        args: [
          {
            fields,
            clearBefore,
            submit,
          },
        ],
      });

      if (!injectionResults || !injectionResults[0] || !injectionResults[0].result) {
        return createErrorResponse('Failed to execute form autofill in tab');
      }

      const result = injectionResults[0].result;

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(
              {
                success: true,
                tabId,
                pageUrl: tab.url,
                ...result,
              },
              null,
              2,
            ),
          },
        ],
      };
    } catch (error) {
      console.error('[FormAutofillTool] Execution error:', error);
      return createErrorResponse(
        `Form autofill failed: ${error instanceof Error ? error.message : String(error)}`,
      );
    }
  }
}

/**
 * In-page script executed to match and fill form controls
 */
function inPageFormAutofillScript(config: {
  fields: Record<string, any>;
  clearBefore: boolean;
  submit: boolean;
}) {
  const { fields, clearBefore, submit } = config;

  function getFieldMetadata(el: HTMLElement) {
    let label = '';
    if (el.id) {
      const lbl = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
      if (lbl && lbl.textContent) label = lbl.textContent.trim();
    }
    if (!label) {
      const parentLabel = el.closest('label');
      if (parentLabel && parentLabel.textContent) label = parentLabel.textContent.trim();
    }
    if (!label) {
      label = el.getAttribute('aria-label') || '';
    }
    if (!label) {
      label = el.getAttribute('placeholder') || '';
    }
    const name = el.getAttribute('name') || '';
    const id = el.id || '';
    const autocomplete = el.getAttribute('autocomplete') || '';

    return {
      label,
      name,
      id,
      autocomplete,
      searchable: `${label} ${name} ${id} ${autocomplete}`.toLowerCase(),
    };
  }

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

  const controls = Array.from(
    document.querySelectorAll<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>(
      'input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="reset"]):not([type="file"]), textarea, select',
    ),
  );

  const matchedFields: Array<{
    key: string;
    label: string;
    value: string;
    controlType: string;
  }> = [];

  const fieldEntries = Object.entries(fields);
  const usedKeys = new Set<string>();

  for (const control of controls) {
    // Skip disabled or invisible elements
    if (control.disabled || control.readOnly) continue;
    if (control.offsetParent === null && control.offsetWidth === 0 && control.offsetHeight === 0) continue;

    const meta = getFieldMetadata(control);

    // Score against each field entry
    let bestKey: string | null = null;
    let bestValue: any = null;
    let highestScore = 0;

    for (const [key, val] of fieldEntries) {
      const lowerKey = key.toLowerCase();
      let score = 0;

      // Exact matches
      if (meta.name.toLowerCase() === lowerKey || meta.id.toLowerCase() === lowerKey) {
        score = 100;
      } else if (meta.label.toLowerCase() === lowerKey) {
        score = 90;
      } else if (meta.autocomplete.toLowerCase() === lowerKey) {
        score = 80;
      } else if (meta.searchable.includes(lowerKey)) {
        score = 60;
      } else if (lowerKey.includes(meta.name.toLowerCase()) && meta.name.length > 2) {
        score = 50;
      }

      if (score > highestScore) {
        highestScore = score;
        bestKey = key;
        bestValue = val;
      }
    }

    // Threshold for matching
    if (highestScore >= 50 && bestKey && bestValue !== null && bestValue !== undefined) {
      usedKeys.add(bestKey);
      const strVal = String(bestValue);

      if (control instanceof HTMLInputElement || control instanceof HTMLTextAreaElement) {
        if (control.type === 'checkbox' || control.type === 'radio') {
          const shouldCheck =
            bestValue === true ||
            strVal.toLowerCase() === 'true' ||
            strVal.toLowerCase() === 'yes' ||
            strVal.toLowerCase() === control.value.toLowerCase();
          control.checked = shouldCheck;
          control.dispatchEvent(new Event('click', { bubbles: true }));
          control.dispatchEvent(new Event('change', { bubbles: true }));
        } else {
          if (clearBefore) {
            control.value = '';
          }
          setNativeValue(control, strVal);
        }
        matchedFields.push({
          key: bestKey,
          label: meta.label || meta.name || meta.id,
          value: strVal,
          controlType: control.tagName.toLowerCase(),
        });
      } else if (control instanceof HTMLSelectElement) {
        for (const opt of Array.from(control.options)) {
          if (
            opt.text.toLowerCase().includes(strVal.toLowerCase()) ||
            opt.value.toLowerCase() === strVal.toLowerCase()
          ) {
            control.value = opt.value;
            control.dispatchEvent(new Event('change', { bubbles: true }));
            matchedFields.push({
              key: bestKey,
              label: meta.label || meta.name || meta.id,
              value: opt.text,
              controlType: 'select',
            });
            break;
          }
        }
      }
    }
  }

  // Find unmapped keys
  const unmappedKeys = Object.keys(fields).filter((k) => !usedKeys.has(k));

  let submitted = false;
  if (submit) {
    const submitBtn = document.querySelector<HTMLButtonElement | HTMLInputElement>(
      'button[type="submit"], input[type="submit"], button.btn-submit',
    );
    if (submitBtn) {
      submitBtn.click();
      submitted = true;
    }
  }

  return {
    totalFormControls: controls.length,
    filledCount: matchedFields.length,
    matchedFields,
    unmappedKeys,
    submitted,
  };
}

export const formAutofillTool = new FormAutofillTool();
