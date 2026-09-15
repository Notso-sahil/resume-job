import { createErrorResponse, ToolResult } from '@/common/tool-handler';
import { BaseBrowserToolExecutor } from '../base-browser';
import { TOOL_NAMES, NexusQuizSolverParams } from '@nexusai/shared';

/**
 * Autonomous Quiz Solver Tool
 * Automatically detects quiz question blocks, evaluates choices, matches answers,
 * and selects or fills answers with synthetic event bubbling.
 */
class QuizSolverTool extends BaseBrowserToolExecutor {
  name = TOOL_NAMES.BROWSER.QUIZ_SOLVER;

  async execute(args: NexusQuizSolverParams): Promise<ToolResult> {
    const {
      tabId: explicitTabId,
      answers = {},
      autoSolve = true,
      submitAfter = false,
    } = args || {};

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
        func: inPageQuizSolverScript,
        args: [
          {
            answers,
            autoSolve,
            submitAfter,
          },
        ],
      });

      if (!injectionResults || !injectionResults[0] || !injectionResults[0].result) {
        return createErrorResponse('Failed to execute quiz solver in tab');
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
      console.error('[QuizSolverTool] Execution error:', error);
      return createErrorResponse(
        `Quiz solver failed: ${error instanceof Error ? error.message : String(error)}`,
      );
    }
  }
}

/**
 * In-page script executed to detect and solve quiz questions
 */
function inPageQuizSolverScript(config: {
  answers: Record<string, string> | Array<{ question: string; answer: string }>;
  autoSolve: boolean;
  submitAfter: boolean;
}) {
  const { answers, autoSolve, submitAfter } = config;

  // Convert answers array or object into a lookup list
  const answerEntries: Array<{ question: string; answer: string }> = [];
  if (Array.isArray(answers)) {
    for (const a of answers) {
      if (a && a.question && a.answer) {
        answerEntries.push({ question: a.question.toLowerCase(), answer: String(a.answer).toLowerCase() });
      }
    }
  } else if (answers && typeof answers === 'object') {
    for (const [q, a] of Object.entries(answers)) {
      answerEntries.push({ question: q.toLowerCase(), answer: String(a).toLowerCase() });
    }
  }

  // Question container selectors
  const questionContainerSelectors = [
    'fieldset',
    '[role="radiogroup"]',
    '.quiz-question',
    '.question-card',
    '.question',
    '.form-group',
    '[data-question]',
  ];

  let containers: HTMLElement[] = [];
  for (const sel of questionContainerSelectors) {
    const found = Array.from(document.querySelectorAll<HTMLElement>(sel));
    if (found.length > 0) {
      containers = found;
      break;
    }
  }

  // Fallback: group radio buttons by their name attribute
  if (containers.length === 0) {
    const radios = Array.from(document.querySelectorAll<HTMLInputElement>('input[type="radio"]'));
    const nameGroups = new Map<string, HTMLElement[]>();
    for (const r of radios) {
      const name = r.name || 'unnamed';
      if (!nameGroups.has(name)) nameGroups.set(name, []);
      nameGroups.get(name)!.push(r);
    }

    containers = Array.from(nameGroups.values()).map((radioList) => {
      // Find common ancestor
      let parent: HTMLElement | null = radioList[0].parentElement;
      while (parent && !radioList.every((r) => parent!.contains(r))) {
        parent = parent.parentElement;
      }
      return parent || radioList[0].parentElement || radioList[0];
    });
  }

  const results: Array<{
    questionText: string;
    optionsFound: string[];
    selectedAnswer: string;
    status: string;
  }> = [];

  for (let i = 0; i < containers.length; i++) {
    const container = containers[i];
    // Find question title/prompt inside container
    const promptEl = container.querySelector(
      'legend, .question-title, .question-text, h2, h3, h4, [data-prompt], label:first-child',
    );
    const questionText = (promptEl ? promptEl.textContent : container.innerText.split('\n')[0])?.trim() || `Question ${i + 1}`;

    // Find options inside this container
    const radios = Array.from(container.querySelectorAll<HTMLInputElement>('input[type="radio"]'));
    const checkboxes = Array.from(container.querySelectorAll<HTMLInputElement>('input[type="checkbox"]'));
    const select = container.querySelector<HTMLSelectElement>('select');
    const textInput = container.querySelector<HTMLInputElement>('input[type="text"]');

    const optionsList: string[] = [];

    // Find target answer from lookup if available
    let targetAnswer: string | null = null;
    for (const entry of answerEntries) {
      if (questionText.toLowerCase().includes(entry.question) || entry.question.includes(questionText.toLowerCase())) {
        targetAnswer = entry.answer;
        break;
      }
    }

    if (radios.length > 0) {
      let selectedText = '';
      for (const r of radios) {
        const optLabel =
          (r.id ? document.querySelector(`label[for="${CSS.escape(r.id)}"]`)?.textContent : '') ||
          r.closest('label')?.textContent ||
          r.value ||
          '';
        optionsList.push(optLabel.trim());
      }

      let selectedRadio: HTMLInputElement | null = null;
      if (targetAnswer) {
        for (let j = 0; j < radios.length; j++) {
          if (optionsList[j].toLowerCase().includes(targetAnswer) || radios[j].value.toLowerCase().includes(targetAnswer)) {
            selectedRadio = radios[j];
            selectedText = optionsList[j];
            break;
          }
        }
      }

      // If no answer matched and autoSolve is enabled, pick the first option if nothing is checked
      if (!selectedRadio && autoSolve && radios.length > 0) {
        const alreadyChecked = radios.find((r) => r.checked);
        if (!alreadyChecked) {
          selectedRadio = radios[0];
          selectedText = optionsList[0];
        } else {
          selectedRadio = alreadyChecked;
          selectedText = optionsList[radios.indexOf(alreadyChecked)];
        }
      }

      if (selectedRadio) {
        selectedRadio.checked = true;
        selectedRadio.dispatchEvent(new Event('click', { bubbles: true }));
        selectedRadio.dispatchEvent(new Event('change', { bubbles: true }));
        results.push({
          questionText,
          optionsFound: optionsList,
          selectedAnswer: selectedText,
          status: 'solved',
        });
      }
    } else if (checkboxes.length > 0) {
      for (const cb of checkboxes) {
        const optLabel =
          (cb.id ? document.querySelector(`label[for="${CSS.escape(cb.id)}"]`)?.textContent : '') ||
          cb.closest('label')?.textContent ||
          cb.value ||
          '';
        optionsList.push(optLabel.trim());
      }

      let chosenText = '';
      for (let j = 0; j < checkboxes.length; j++) {
        if (targetAnswer && (optionsList[j].toLowerCase().includes(targetAnswer) || checkboxes[j].value.toLowerCase().includes(targetAnswer))) {
          checkboxes[j].checked = true;
          checkboxes[j].dispatchEvent(new Event('click', { bubbles: true }));
          checkboxes[j].dispatchEvent(new Event('change', { bubbles: true }));
          chosenText = optionsList[j];
          break;
        }
      }

      results.push({
        questionText,
        optionsFound: optionsList,
        selectedAnswer: chosenText || '(none matched)',
        status: chosenText ? 'solved' : 'review_needed',
      });
    } else if (select) {
      const opts = Array.from(select.options);
      optionsList.push(...opts.map((o) => o.text));
      let selectedVal = '';
      if (targetAnswer) {
        for (const o of opts) {
          if (o.text.toLowerCase().includes(targetAnswer) || o.value.toLowerCase().includes(targetAnswer)) {
            select.value = o.value;
            select.dispatchEvent(new Event('change', { bubbles: true }));
            selectedVal = o.text;
            break;
          }
        }
      }
      results.push({
        questionText,
        optionsFound: optionsList,
        selectedAnswer: selectedVal || '(none matched)',
        status: selectedVal ? 'solved' : 'review_needed',
      });
    } else if (textInput && targetAnswer) {
      textInput.value = targetAnswer;
      textInput.dispatchEvent(new Event('input', { bubbles: true }));
      textInput.dispatchEvent(new Event('change', { bubbles: true }));
      results.push({
        questionText,
        optionsFound: ['[Text Input Blank]'],
        selectedAnswer: targetAnswer,
        status: 'solved',
      });
    }
  }

  // Auto-submit if enabled
  let submitted = false;
  if (submitAfter) {
    const submitBtn = document.querySelector<HTMLButtonElement | HTMLInputElement>(
      'button[type="submit"], input[type="submit"], button.submit, button.finish-quiz',
    );
    if (submitBtn) {
      submitBtn.click();
      submitted = true;
    }
  }

  return {
    totalQuestionsDetected: containers.length,
    solvedQuestionsCount: results.filter((r) => r.status === 'solved').length,
    questions: results,
    submitted,
  };
}

export const quizSolverTool = new QuizSolverTool();
