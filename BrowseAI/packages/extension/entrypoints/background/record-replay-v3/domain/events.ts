/**
 * @fileoverview 
 * @description  Record-Replay V3 
 */

import type { JsonObject, JsonValue, UnixMillis } from './json';
import type { EdgeLabel, FlowId, NodeId, RunId } from './ids';
import type { RRError } from './errors';
import type { TriggerFireContext } from './triggers';

/** item */
export type Unsubscribe = () => void;

/** Run item */
export type RunStatus = 'queued' | 'running' | 'paused' | 'succeeded' | 'failed' | 'canceled';

/**
 * 
 * @description 
 */
export interface EventBase {
  /** item Run ID */
  runId: RunId;
  /** item */
  ts: UnixMillis;
  /** item */
  seq: number;
}

/**
 * 
 * @description  Run 
 */
export type PauseReason =
  | { kind: 'breakpoint'; nodeId: NodeId }
  | { kind: 'step'; nodeId: NodeId }
  | { kind: 'command' }
  | { kind: 'policy'; nodeId: NodeId; reason: string };

/** item */
export type RecoveryReason = 'sw_restart' | 'lease_expired';

/**
 * Run 
 * @description 
 */
export type RunEvent =
  // ===== Run  =====
  | (EventBase & { type: 'run.queued'; flowId: FlowId })
  | (EventBase & { type: 'run.started'; flowId: FlowId; tabId: number })
  | (EventBase & { type: 'run.paused'; reason: PauseReason; nodeId?: NodeId })
  | (EventBase & { type: 'run.resumed' })
  | (EventBase & {
      type: 'run.recovered';
      /** item */
      reason: RecoveryReason;
      /** item */
      fromStatus: 'running' | 'paused';
      /** item */
      toStatus: 'queued';
      /** item ownerId（item） */
      prevOwnerId?: string;
    })
  | (EventBase & { type: 'run.canceled'; reason?: string })
  | (EventBase & { type: 'run.succeeded'; tookMs: number; outputs?: JsonObject })
  | (EventBase & { type: 'run.failed'; error: RRError; nodeId?: NodeId })

  // ===== Node  =====
  | (EventBase & { type: 'node.queued'; nodeId: NodeId })
  | (EventBase & { type: 'node.started'; nodeId: NodeId; attempt: number })
  | (EventBase & {
      type: 'node.succeeded';
      nodeId: NodeId;
      tookMs: number;
      next?: { kind: 'edgeLabel'; label: EdgeLabel } | { kind: 'end' };
    })
  | (EventBase & {
      type: 'node.failed';
      nodeId: NodeId;
      attempt: number;
      error: RRError;
      decision: 'retry' | 'continue' | 'stop' | 'goto';
    })
  | (EventBase & { type: 'node.skipped'; nodeId: NodeId; reason: 'disabled' | 'unreachable' })

  // =====  =====
  | (EventBase & {
      type: 'vars.patch';
      patch: Array<{ op: 'set' | 'delete'; name: string; value?: JsonValue }>;
    })
  | (EventBase & { type: 'artifact.screenshot'; nodeId: NodeId; data: string; savedAs?: string })
  | (EventBase & {
      type: 'log';
      level: 'debug' | 'info' | 'warn' | 'error';
      message: string;
      data?: JsonValue;
    });

/** Run item（item） */
export type RunEventType = RunEvent['type'];

/**
 *  Omit（）
 */
type DistributiveOmit<T, K extends keyof T> = T extends unknown ? Omit<T, K> : never;

/**
 * Run 
 * @description seq required storage （ RunRecordV3.nextSeq）
 * ts ， Date.now()
 */
export type RunEventInput = DistributiveOmit<RunEvent, 'seq' | 'ts'> & {
  ts?: UnixMillis;
};

/** Run Schema item */
export const RUN_SCHEMA_VERSION = 3 as const;

/**
 * Run  V3
 * @description  IndexedDB  Run 
 */
export interface RunRecordV3 {
  /** Schema item */
  schemaVersion: typeof RUN_SCHEMA_VERSION;
  /** Run item */
  id: RunId;
  /** item Flow ID */
  flowId: FlowId;

  /** item */
  status: RunStatus;
  /** item */
  createdAt: UnixMillis;
  /** item */
  updatedAt: UnixMillis;

  /** item */
  startedAt?: UnixMillis;
  /** item */
  finishedAt?: UnixMillis;
  /** item（item） */
  tookMs?: number;

  /** item Tab ID（item Run item） */
  tabId?: number;
  /** item ID（item） */
  startNodeId?: NodeId;
  /** item ID */
  currentNodeId?: NodeId;

  /** item */
  attempt: number;
  /** item */
  maxAttempts: number;

  /** item */
  args?: JsonObject;
  /** item */
  trigger?: TriggerFireContext;
  /** item */
  debug?: { breakpoints?: NodeId[]; pauseOnStart?: boolean };

  /** item（item） */
  error?: RRError;
  /** item */
  outputs?: JsonObject;

  /** item（item） */
  nextSeq: number;
}

/**
 *  Run 
 */
export function isTerminalStatus(status: RunStatus): boolean {
  return status === 'succeeded' || status === 'failed' || status === 'canceled';
}

/**
 *  Run 
 */
export function isActiveStatus(status: RunStatus): boolean {
  return status === 'running' || status === 'paused';
}
