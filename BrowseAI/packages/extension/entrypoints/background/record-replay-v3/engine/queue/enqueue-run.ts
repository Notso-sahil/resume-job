/**
 * @fileoverview 
 * @description
 *  Run ， RPC Server  TriggerManager 。
 *
 * ：
 * -  RpcServer 
 * -  RPC  TriggerManager 
 * - 、Run 、、
 */

import type { JsonObject, UnixMillis } from '../../domain/json';
import type { FlowId, NodeId, RunId } from '../../domain/ids';
import type { TriggerFireContext } from '../../domain/triggers';
import { RUN_SCHEMA_VERSION, type RunRecordV3 } from '../../domain/events';
import type { StoragePort } from '../storage/storage-port';
import type { EventsBus } from '../transport/events-bus';
import type { RunScheduler } from './scheduler';

// ==================== Types ====================

/**
 * 
 */
export interface EnqueueRunDeps {
  /** item (item flows/runs/queue) */
  storage: Pick<StoragePort, 'flows' | 'runs' | 'queue'>;
  /** item */
  events: Pick<EventsBus, 'append'>;
  /** item (item) */
  scheduler?: Pick<RunScheduler, 'kick'>;
  /** RunId item (item) */
  generateRunId?: () => RunId;
  /** item (item) */
  now?: () => UnixMillis;
}

/**
 * 
 */
export interface EnqueueRunInput {
  /** Flow ID (item) */
  flowId: FlowId;
  /** item ID (item，item Flow item entryNodeId) */
  startNodeId?: NodeId;
  /** item (item 0) */
  priority?: number;
  /** item (item 1) */
  maxAttempts?: number;
  /** item Flow item */
  args?: JsonObject;
  /** item (item TriggerManager item) */
  trigger?: TriggerFireContext;
  /** item */
  debug?: {
    breakpoints?: NodeId[];
    pauseOnStart?: boolean;
  };
}

/**
 * 
 */
export interface EnqueueRunResult {
  /** item Run ID */
  runId: RunId;
  /** item (1-based) */
  position: number;
}

// ==================== Utilities ====================

/**
 *  RunId 
 */
function defaultGenerateRunId(): RunId {
  return `run_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

/**
 * 
 */
function validateInt(
  value: unknown,
  defaultValue: number,
  fieldName: string,
  opts?: { min?: number; max?: number },
): number {
  if (value === undefined || value === null) {
    return defaultValue;
  }
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new Error(`${fieldName} must be a finite number`);
  }
  const intValue = Math.floor(value);
  if (opts?.min !== undefined && intValue < opts.min) {
    throw new Error(`${fieldName} must be >= ${opts.min}`);
  }
  if (opts?.max !== undefined && intValue > opts.max) {
    throw new Error(`${fieldName} must be <= ${opts.max}`);
  }
  return intValue;
}

/**
 *  Run 
 * @description : priority DESC + createdAt ASC
 * @returns 1-based position, or -1 if run not found in queued items
 *
 * Note: Due to race conditions (scheduler may claim the run before this is called),
 * position may be -1. Callers should handle this gracefully.
 */
async function computeQueuePosition(
  storage: Pick<StoragePort, 'queue'>,
  runId: RunId,
): Promise<number> {
  const queueItems = await storage.queue.list('queued');
  queueItems.sort((a, b) => {
    if (a.priority !== b.priority) return b.priority - a.priority;
    return a.createdAt - b.createdAt;
  });
  const index = queueItems.findIndex((item) => item.id === runId);
  // Return -1 if not found (run may have been claimed already)
  return index === -1 ? -1 : index + 1;
}

// ==================== Main Function ====================

/**
 *  Run
 * @description
 * ：
 * 1. 
 * 2.  Flow 
 * 3.  RunRecordV3 (status=queued)
 * 4.  RunQueue
 * 5.  run.queued 
 * 6.  (best-effort)
 * 7. 
 */
export async function enqueueRun(
  deps: EnqueueRunDeps,
  input: EnqueueRunInput,
): Promise<EnqueueRunResult> {
  const { flowId } = input;
  if (!flowId) {
    throw new Error('flowId is required');
  }

  const now = deps.now ?? (() => Date.now());
  const generateRunId = deps.generateRunId ?? defaultGenerateRunId;

  // Note
  const priority = validateInt(input.priority, 0, 'priority');
  const maxAttempts = validateInt(input.maxAttempts, 1, 'maxAttempts', { min: 1 });

  //  Flow 
  const flow = await deps.storage.flows.get(flowId);
  if (!flow) {
    throw new Error(`Flow "${flowId}" not found`);
  }

  //  startNodeId  Flow 
  if (input.startNodeId) {
    const nodeExists = flow.nodes.some((n) => n.id === input.startNodeId);
    if (!nodeExists) {
      throw new Error(`startNodeId "${input.startNodeId}" not found in flow "${flowId}"`);
    }
  }

  const ts = now();
  const runId = generateRunId();

  // 1.  RunRecordV3
  const runRecord: RunRecordV3 = {
    schemaVersion: RUN_SCHEMA_VERSION,
    id: runId,
    flowId,
    status: 'queued',
    createdAt: ts,
    updatedAt: ts,
    attempt: 0,
    maxAttempts,
    args: input.args,
    trigger: input.trigger,
    debug: input.debug,
    startNodeId: input.startNodeId,
    nextSeq: 0,
  };
  await deps.storage.runs.save(runRecord);

  // 2. 
  await deps.storage.queue.enqueue({
    id: runId,
    flowId,
    priority,
    maxAttempts,
    args: input.args,
    trigger: input.trigger,
    debug: input.debug,
  });

  // 3.  run.queued 
  await deps.events.append({
    runId,
    type: 'run.queued',
    flowId,
  });

  // 4.  ( kick ， position=-1 )
  const position = await computeQueuePosition(deps.storage, runId);

  // 5.  (best-effort, returns)
  if (deps.scheduler) {
    void deps.scheduler.kick();
  }

  return { runId, position };
}
