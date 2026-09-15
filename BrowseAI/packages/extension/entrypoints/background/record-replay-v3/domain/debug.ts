/**
 * @fileoverview 
 * @description  Record-Replay V3 
 */

import type { JsonValue } from './json';
import type { NodeId, RunId } from './ids';
import type { PauseReason } from './events';

/**
 * 
 */
export interface Breakpoint {
  /** item ID */
  nodeId: NodeId;
  /** item */
  enabled: boolean;
}

/**
 * 
 * @description 
 */
export interface DebuggerState {
  /** item Run ID */
  runId: RunId;
  /** item */
  status: 'attached' | 'detached';
  /** item */
  execution: 'running' | 'paused';
  /** item（item execution='paused' item） */
  pauseReason?: PauseReason;
  /** item ID */
  currentNodeId?: NodeId;
  /** item */
  breakpoints: Breakpoint[];
  /** item */
  stepMode?: 'none' | 'stepOver';
}

/**
 * 
 * @description 
 */
export type DebuggerCommand =
  // =====  =====
  | { type: 'debug.attach'; runId: RunId }
  | { type: 'debug.detach'; runId: RunId }

  // =====  =====
  | { type: 'debug.pause'; runId: RunId }
  | { type: 'debug.resume'; runId: RunId }
  | { type: 'debug.stepOver'; runId: RunId }

  // =====  =====
  | { type: 'debug.setBreakpoints'; runId: RunId; nodeIds: NodeId[] }
  | { type: 'debug.addBreakpoint'; runId: RunId; nodeId: NodeId }
  | { type: 'debug.removeBreakpoint'; runId: RunId; nodeId: NodeId }

  // =====  =====
  | { type: 'debug.getState'; runId: RunId }

  // =====  =====
  | { type: 'debug.getVar'; runId: RunId; name: string }
  | { type: 'debug.setVar'; runId: RunId; name: string; value: JsonValue };

/** item（item） */
export type DebuggerCommandType = DebuggerCommand['type'];

/**
 * 
 */
export type DebuggerResponse =
  | { ok: true; state?: DebuggerState; value?: JsonValue }
  | { ok: false; error: string };

/**
 * 
 */
export function createInitialDebuggerState(runId: RunId): DebuggerState {
  return {
    runId,
    status: 'detached',
    execution: 'running',
    breakpoints: [],
    stepMode: 'none',
  };
}
