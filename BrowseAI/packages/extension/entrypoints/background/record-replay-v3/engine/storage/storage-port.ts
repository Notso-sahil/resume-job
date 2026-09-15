/**
 * @fileoverview StoragePort 
 * @description  Storage ，
 */

import type { FlowId, RunId, TriggerId } from '../../domain/ids';
import type { FlowV3 } from '../../domain/flow';
import type { RunEvent, RunEventInput, RunRecordV3 } from '../../domain/events';
import type { PersistentVarRecord, PersistentVariableName } from '../../domain/variables';
import type { TriggerSpec } from '../../domain/triggers';
import type { RunQueue } from '../queue/queue';

/**
 * FlowsStore 
 */
export interface FlowsStore {
  /** item Flow */
  list(): Promise<FlowV3[]>;
  /** item Flow */
  get(id: FlowId): Promise<FlowV3 | null>;
  /** item Flow */
  save(flow: FlowV3): Promise<void>;
  /** item Flow */
  delete(id: FlowId): Promise<void>;
}

/**
 * RunsStore 
 */
export interface RunsStore {
  /** item Run item */
  list(): Promise<RunRecordV3[]>;
  /** item Run item */
  get(id: RunId): Promise<RunRecordV3 | null>;
  /** item Run item */
  save(record: RunRecordV3): Promise<void>;
  /** item Run item */
  patch(id: RunId, patch: Partial<RunRecordV3>): Promise<void>;
}

/**
 * EventsStore 
 * @description seq required append() 
 */
export interface EventsStore {
  /**
   *  seq
   * @description ： RunRecordV3.nextSeq ->  ->  nextSeq
   * @param event （ seq）
   * @returns （ seq  ts）
   */
  append(event: RunEventInput): Promise<RunEvent>;

  /**
   * 
   * @param runId Run ID
   * @param opts 
   */
  list(runId: RunId, opts?: { fromSeq?: number; limit?: number }): Promise<RunEvent[]>;
}

/**
 * PersistentVarsStore 
 */
export interface PersistentVarsStore {
  /** item */
  get(key: PersistentVariableName): Promise<PersistentVarRecord | undefined>;
  /** item */
  set(
    key: PersistentVariableName,
    value: PersistentVarRecord['value'],
  ): Promise<PersistentVarRecord>;
  /** item */
  delete(key: PersistentVariableName): Promise<void>;
  /** item */
  list(prefix?: PersistentVariableName): Promise<PersistentVarRecord[]>;
}

/**
 * TriggersStore 
 */
export interface TriggersStore {
  /** item */
  list(): Promise<TriggerSpec[]>;
  /** item */
  get(id: TriggerId): Promise<TriggerSpec | null>;
  /** item */
  save(spec: TriggerSpec): Promise<void>;
  /** item */
  delete(id: TriggerId): Promise<void>;
}

/**
 * StoragePort 
 * @description ，
 */
export interface StoragePort {
  /** Flows item */
  flows: FlowsStore;
  /** Runs item */
  runs: RunsStore;
  /** Events item */
  events: EventsStore;
  /** Queue item */
  queue: RunQueue;
  /** item */
  persistentVars: PersistentVarsStore;
  /** item */
  triggers: TriggersStore;
}

/**
 *  NotImplemented  Store
 * @description  Proxy  'then'  thenable 
 */
function createNotImplementedStore<T extends object>(name: string): T {
  const target = {} as T;
  return new Proxy(target, {
    get(_, prop) {
      // Avoid thenable behavior by returning undefined for 'then'
      if (prop === 'then') {
        return undefined;
      }
      return async () => {
        throw new Error(`${name}.${String(prop)} not implemented`);
      };
    },
  });
}

/**
 *  NotImplemented  StoragePort
 * @description Phase 0 
 */
export function createNotImplementedStoragePort(): StoragePort {
  return {
    flows: createNotImplementedStore<FlowsStore>('FlowsStore'),
    runs: createNotImplementedStore<RunsStore>('RunsStore'),
    events: createNotImplementedStore<EventsStore>('EventsStore'),
    queue: createNotImplementedStore<RunQueue>('RunQueue'),
    persistentVars: createNotImplementedStore<PersistentVarsStore>('PersistentVarsStore'),
    triggers: createNotImplementedStore<TriggersStore>('TriggersStore'),
  };
}
