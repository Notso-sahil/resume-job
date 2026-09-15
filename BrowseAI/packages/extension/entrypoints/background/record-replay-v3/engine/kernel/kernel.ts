/**
 * @fileoverview ExecutionKernel 
 * @description  Record-Replay V3 
 */

import type { JsonObject } from '../../domain/json';
import type { FlowId, NodeId, RunId } from '../../domain/ids';
import type { RRError } from '../../domain/errors';
import type { FlowV3 } from '../../domain/flow';
import type { DebuggerCommand, DebuggerState } from '../../domain/debug';
import type { RunEvent, RunStatus, Unsubscribe } from '../../domain/events';

/**
 * Run 
 */
export interface RunStartRequest {
  /** Run ID（item） */
  runId: RunId;
  /** Flow ID */
  flowId: FlowId;
  /** Flow item（item Flow item） */
  flowSnapshot: FlowV3;
  /** item */
  args?: JsonObject;
  /** item ID（item Flow item entryNodeId） */
  startNodeId?: NodeId;
  /** Tab ID（requireditem，item Run item） */
  tabId: number;
  /** item */
  debug?: { breakpoints?: NodeId[]; pauseOnStart?: boolean };
}

/**
 * Run 
 */
export interface RunResult {
  /** Run ID */
  runId: RunId;
  /** item */
  status: Extract<RunStatus, 'succeeded' | 'failed' | 'canceled'>;
  /** item（item） */
  tookMs: number;
  /** item（item） */
  error?: RRError;
  /** item */
  outputs?: JsonObject;
}

/**
 * Run 
 */
export interface RunStatusInfo {
  /** item */
  status: RunStatus;
  /** item ID */
  currentNodeId?: NodeId;
  /** item */
  startedAt?: number;
  /** item */
  updatedAt: number;
  /** Tab ID */
  tabId?: number;
}

/**
 * ExecutionKernel 
 * @description Record-Replay V3 
 */
export interface ExecutionKernel {
  /**
   * 
   * @param listener 
   * @returns 
   */
  onEvent(listener: (event: RunEvent) => void): Unsubscribe;

  /**
   *  Run
   * @description  Run 
   */
  startRun(req: RunStartRequest): Promise<void>;

  /**
   *  Run
   * @param runId Run ID
   * @param reason 
   */
  pauseRun(runId: RunId, reason?: { kind: 'command' }): Promise<void>;

  /**
   *  Run
   * @param runId Run ID
   */
  resumeRun(runId: RunId): Promise<void>;

  /**
   *  Run
   * @param runId Run ID
   * @param reason 
   */
  cancelRun(runId: RunId, reason?: string): Promise<void>;

  /**
   * 
   * @param runId Run ID
   * @param cmd 
   */
  debug(
    runId: RunId,
    cmd: DebuggerCommand,
  ): Promise<{ ok: true; state?: DebuggerState } | { ok: false; error: string }>;

  /**
   *  Run 
   * @param runId Run ID
   * @returns Run  null（）
   */
  getRunStatus(runId: RunId): Promise<RunStatusInfo | null>;

  /**
   * 
   * @description  Service Worker ， Run
   */
  recover(): Promise<void>;
}

/**
 *  NotImplemented  ExecutionKernel
 * @description Phase 0 
 */
export function createNotImplementedKernel(): ExecutionKernel {
  const notImplemented = () => {
    throw new Error('ExecutionKernel not implemented');
  };

  return {
    onEvent: () => {
      notImplemented();
      return () => {};
    },
    startRun: async () => notImplemented(),
    pauseRun: async () => notImplemented(),
    resumeRun: async () => notImplemented(),
    cancelRun: async () => notImplemented(),
    debug: async () => notImplemented(),
    getRunStatus: async () => notImplemented(),
    recover: async () => notImplemented(),
  };
}
