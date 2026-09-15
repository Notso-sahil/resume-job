/**
 * @fileoverview RunQueue 
 * @description  Run 
 */

import type { JsonObject, UnixMillis } from '../../domain/json';
import type { FlowId, NodeId, RunId } from '../../domain/ids';
import type { TriggerFireContext } from '../../domain/triggers';

/**
 * RunQueue 
 */
export interface RunQueueConfig {
  /** item Run item */
  maxParallelRuns: number;
  /** item TTL（item） */
  leaseTtlMs: number;
  /** item（item） */
  heartbeatIntervalMs: number;
}

/**
 * 
 */
export const DEFAULT_QUEUE_CONFIG: RunQueueConfig = {
  maxParallelRuns: 3,
  leaseTtlMs: 15_000,
  heartbeatIntervalMs: 5_000,
};

/**
 * 
 */
export type QueueItemStatus = 'queued' | 'running' | 'paused';

/**
 * 
 */
export interface Lease {
  /** item ID */
  ownerId: string;
  /** item */
  expiresAt: UnixMillis;
}

/**
 * RunQueue 
 */
export interface RunQueueItem {
  /** Run ID */
  id: RunId;
  /** Flow ID */
  flowId: FlowId;
  /** item */
  status: QueueItemStatus;
  /** item */
  createdAt: UnixMillis;
  /** item */
  updatedAt: UnixMillis;
  /** item（item） */
  priority: number;
  /** item */
  attempt: number;
  /** item */
  maxAttempts: number;
  /** Tab ID */
  tabId?: number;
  /** item */
  args?: JsonObject;
  /** item */
  trigger?: TriggerFireContext;
  /** item */
  lease?: Lease;
  /** item */
  debug?: { breakpoints?: NodeId[]; pauseOnStart?: boolean };
}

/**
 * （）
 * - priority  0
 * - maxAttempts  1
 */
export type EnqueueInput = Omit<
  RunQueueItem,
  'status' | 'createdAt' | 'updatedAt' | 'attempt' | 'lease' | 'priority' | 'maxAttempts'
> & {
  id: RunId;
  /** item（item，item 0） */
  priority?: number;
  /** item（item 1） */
  maxAttempts?: number;
};

/**
 * RunQueue 
 * @description  Run 
 */
export interface RunQueue {
  /**
   * 
   * @param input 
   * @returns 
   */
  enqueue(input: EnqueueInput): Promise<RunQueueItem>;

  /**
   *  Run
   * @param ownerId  ID
   * @param now 
   * @returns  null
   */
  claimNext(ownerId: string, now: UnixMillis): Promise<RunQueueItem | null>;

  /**
   * 
   * @param ownerId  ID
   * @param now 
   */
  heartbeat(ownerId: string, now: UnixMillis): Promise<void>;

  /**
   * 
   * @description  lease.expiresAt < now  running/paused  queued
   * @param now 
   * @returns  Run ID 
   */
  reclaimExpiredLeases(now: UnixMillis): Promise<RunId[]>;

  /**
   * （SW ）
   * @description
   * -  running  queued（status -> queued，）
   * -  paused （ status=paused， ownerId  ownerId）
   * @param ownerId  ownerId（ Service Worker ）
   * @param now 
   * @returns  runId （ ownerId ）
   */
  recoverOrphanLeases(
    ownerId: string,
    now: UnixMillis,
  ): Promise<{
    requeuedRunning: Array<{ runId: RunId; prevOwnerId?: string }>;
    adoptedPaused: Array<{ runId: RunId; prevOwnerId?: string }>;
  }>;

  /**
   *  running
   */
  markRunning(runId: RunId, ownerId: string, now: UnixMillis): Promise<void>;

  /**
   *  paused
   */
  markPaused(runId: RunId, ownerId: string, now: UnixMillis): Promise<void>;

  /**
   * （）
   */
  markDone(runId: RunId, now: UnixMillis): Promise<void>;

  /**
   *  Run
   */
  cancel(runId: RunId, now: UnixMillis, reason?: string): Promise<void>;

  /**
   * 
   */
  get(runId: RunId): Promise<RunQueueItem | null>;

  /**
   * 
   */
  list(status?: QueueItemStatus): Promise<RunQueueItem[]>;
}

/**
 *  NotImplemented  RunQueue
 * @description Phase 0 
 */
export function createNotImplementedQueue(): RunQueue {
  const notImplemented = () => {
    throw new Error('RunQueue not implemented');
  };

  return {
    enqueue: async () => notImplemented(),
    claimNext: async () => notImplemented(),
    heartbeat: async () => notImplemented(),
    reclaimExpiredLeases: async () => notImplemented(),
    recoverOrphanLeases: async () => notImplemented(),
    markRunning: async () => notImplemented(),
    markPaused: async () => notImplemented(),
    markDone: async () => notImplemented(),
    cancel: async () => notImplemented(),
    get: async () => notImplemented(),
    list: async () => notImplemented(),
  };
}
