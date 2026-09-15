/**
 * @fileoverview 
 * @description  Record-Replay V3 
 */

import type { JsonObject, UnixMillis } from './json';
import type { FlowId, TriggerId } from './ids';

/** item */
export type TriggerKind =
  | 'manual'
  | 'url'
  | 'cron'
  | 'interval'
  | 'once'
  | 'command'
  | 'contextMenu'
  | 'dom';

/**
 * 
 */
export interface TriggerSpecBase {
  /** item ID */
  id: TriggerId;
  /** item */
  kind: TriggerKind;
  /** item */
  enabled: boolean;
  /** item Flow ID */
  flowId: FlowId;
  /** item Flow item */
  args?: JsonObject;
}

/**
 * URL 
 */
export interface UrlMatchRule {
  kind: 'url' | 'domain' | 'path';
  value: string;
}

/**
 * 
 */
export type TriggerSpec =
  // Note
  | (TriggerSpecBase & { kind: 'manual' })

  // URL 
  | (TriggerSpecBase & {
      kind: 'url';
      match: UrlMatchRule[];
    })

  // Cron 
  | (TriggerSpecBase & {
      kind: 'cron';
      cron: string;
      timezone?: string;
    })

  // Interval （）
  | (TriggerSpecBase & {
      kind: 'interval';
      /** item，item 1 */
      periodMinutes: number;
    })

  // Once （）
  | (TriggerSpecBase & {
      kind: 'once';
      /** item (Unix milliseconds) */
      whenMs: UnixMillis;
    })

  // Note
  | (TriggerSpecBase & {
      kind: 'command';
      commandKey: string;
    })

  // Note
  | (TriggerSpecBase & {
      kind: 'contextMenu';
      title: string;
      contexts?: ReadonlyArray<string>;
    })

  // DOM 
  | (TriggerSpecBase & {
      kind: 'dom';
      selector: string;
      appear?: boolean;
      once?: boolean;
      debounceMs?: UnixMillis;
    });

/**
 * 
 * @description 
 */
export interface TriggerFireContext {
  /** item ID */
  triggerId: TriggerId;
  /** item */
  kind: TriggerKind;
  /** item */
  firedAt: UnixMillis;
  /** item Tab ID */
  sourceTabId?: number;
  /** item URL */
  sourceUrl?: string;
}

/**
 * 
 */
export type TriggerSpecByKind<K extends TriggerKind> = Extract<TriggerSpec, { kind: K }>;

/**
 * 
 */
export function isTriggerEnabled(trigger: TriggerSpec): boolean {
  return trigger.enabled;
}

/**
 * 
 */
export function createTriggerFireContext(
  trigger: TriggerSpec,
  options?: { sourceTabId?: number; sourceUrl?: string },
): TriggerFireContext {
  return {
    triggerId: trigger.id,
    kind: trigger.kind,
    firedAt: Date.now(),
    sourceTabId: options?.sourceTabId,
    sourceUrl: options?.sourceUrl,
  };
}
