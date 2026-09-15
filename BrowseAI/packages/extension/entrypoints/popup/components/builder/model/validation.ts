import type { NodeBase } from '@/entrypoints/background/record-replay/types';
import { STEP_TYPES } from '@nexusai/shared';

export function validateNode(n: NodeBase): string[] {
  const errs: string[] = [];
  const c: any = n.config || {};

  switch (n.type) {
    case STEP_TYPES.CLICK:
    case STEP_TYPES.DBLCLICK:
    case 'fill': {
      const hasCandidate = !!c?.target?.candidates?.length;
      if (!hasCandidate) errs.push('Target selector candidate is missing');
      if (n.type === 'fill' && (!('value' in c) || c.value === undefined)) errs.push('Input value is missing');
      break;
    }
    case STEP_TYPES.WAIT: {
      if (!c?.condition) errs.push('Wait condition expression is missing');
      break;
    }
    case STEP_TYPES.ASSERT: {
      if (!c?.assert) errs.push('Assertion condition predicate is missing');
      break;
    }
    case STEP_TYPES.NAVIGATE: {
      if (!c?.url) errs.push('Target URL is missing');
      break;
    }
    case STEP_TYPES.HTTP: {
      if (!c?.url) errs.push('HTTP request requires a valid URL');
      if (c?.assign && typeof c.assign === 'object') {
        const pathRe = /^[A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+|\[\d+\])*$/;
        for (const v of Object.values(c.assign)) {
          const s = String(v);
          if (!pathRe.test(s)) errs.push(`Assign: Invalid destination path ${s}`);
        }
      }
      break;
    }
    case STEP_TYPES.HANDLE_DOWNLOAD: {

      break;
    }
    case STEP_TYPES.EXTRACT: {
      if (!c?.saveAs) errs.push('Extract: Target variable name is required');
      if (!c?.selector && !c?.js) errs.push('Extract: Requires either a CSS selector or JavaScript expression');
      break;
    }
    case STEP_TYPES.SWITCH_TAB: {
      if (!c?.tabId && !c?.urlContains && !c?.titleContains)
        errs.push('SwitchTab: Must specify tab ID, URL pattern, or title match');
      break;
    }
    case STEP_TYPES.SCREENSHOT: {

      break;
    }
    case STEP_TYPES.TRIGGER_EVENT: {
      const hasCandidate = !!c?.target?.candidates?.length;
      if (!hasCandidate) errs.push('Target selector candidate is missing');
      if (!String(c?.event || '').trim()) errs.push('Event type must be specified');
      break;
    }
    case STEP_TYPES.IF: {
      const arr = Array.isArray(c?.branches) ? c.branches : [];
      if (arr.length === 0) errs.push('At least one conditional branch must be added');
      for (let i = 0; i < arr.length; i++) {
        if (!String(arr[i]?.expr || '').trim()) errs.push(`Branch ${i + 1}: Conditional expression is required`);
      }
      break;
    }
    case STEP_TYPES.SET_ATTRIBUTE: {
      const hasCandidate = !!c?.target?.candidates?.length;
      if (!hasCandidate) errs.push('Target selector candidate is missing');
      if (!String(c?.name || '').trim()) errs.push('DOM attribute name is required');
      break;
    }
    case STEP_TYPES.LOOP_ELEMENTS: {
      if (!String(c?.selector || '').trim()) errs.push('Element selector must be provided');
      if (!String(c?.subflowId || '').trim()) errs.push('Subflow ID is required');
      break;
    }
    case STEP_TYPES.SWITCH_FRAME: {
      // Both index/urlContains optional; empty means switch back to top frame
      break;
    }
    case STEP_TYPES.EXECUTE_FLOW: {
      if (!String(c?.flowId || '').trim()) errs.push('Target workflow must be selected');
      break;
    }
    case STEP_TYPES.CLOSE_TAB: {

      break;
    }
    case STEP_TYPES.SCRIPT: {

      const hasAssign = c?.assign && Object.keys(c.assign).length > 0;
      if ((c?.saveAs || hasAssign) && !String(c?.code || '').trim())
        errs.push('Script: Variable mapping configured without script body');
      if (hasAssign) {
        const pathRe = /^[A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+|\[\d+\])*$/;
        for (const v of Object.values(c.assign || {})) {
          const s = String(v);
          if (!pathRe.test(s)) errs.push(`Assign: Invalid destination path ${s}`);
        }
      }
      break;
    }
  }
  return errs;
}

export function validateFlow(nodes: NodeBase[]): {
  totalErrors: number;
  nodeErrors: Record<string, string[]>;
} {
  const nodeErrors: Record<string, string[]> = {};
  let totalErrors = 0;
  for (const n of nodes) {
    const e = validateNode(n);
    if (e.length) {
      nodeErrors[n.id] = e;
      totalErrors += e.length;
    }
  }
  return { totalErrors, nodeErrors };
}
