/**
 * @fileoverview 
 * @description  Record-Replay V3 
 */

import { z } from 'zod';

import type { JsonObject, JsonValue } from '../../domain/json';
import type { FlowId, NodeId, RunId, TriggerId } from '../../domain/ids';
import type { NodeKind } from '../../domain/flow';
import type { RRError } from '../../domain/errors';
import type { NodePolicy } from '../../domain/policy';
import type { FlowV3, NodeV3 } from '../../domain/flow';
import type { TriggerKind } from '../../domain/triggers';

/**
 * Schema 
 * @description  Zod 
 */
export type Schema<T> = z.ZodType<T, z.ZodTypeDef, unknown>;

/**
 * 
 * @description 
 */
export interface NodeExecutionContext {
  /** Run ID */
  runId: RunId;
  /** Flow item（item） */
  flow: FlowV3;
  /** item ID */
  nodeId: NodeId;

  /** item Tab ID（item Run item） */
  tabId: number;
  /** Frame ID（item 0 item） */
  frameId?: number;

  /** item */
  vars: Record<string, JsonValue>;

  /**
   * 
   */
  log: (level: 'debug' | 'info' | 'warn' | 'error', message: string, data?: JsonValue) => void;

  /**
   * 
   * @description 
   */
  chooseNext: (label: string) => { kind: 'edgeLabel'; label: string };

  /**
   * 
   */
  artifacts: {
    /** item */
    screenshot: () => Promise<{ ok: true; base64: string } | { ok: false; error: RRError }>;
  };

  /**
   * 
   */
  persistent: {
    /** item */
    get: (name: `$${string}`) => Promise<JsonValue | undefined>;
    /** item */
    set: (name: `$${string}`, value: JsonValue) => Promise<void>;
    /** item */
    delete: (name: `$${string}`) => Promise<void>;
  };
}

/**
 * 
 */
export interface VarsPatchOp {
  op: 'set' | 'delete';
  name: string;
  value?: JsonValue;
}

/**
 * 
 */
export type NodeExecutionResult =
  | {
      status: 'succeeded';
      /** item */
      next?: { kind: 'edgeLabel'; label: string } | { kind: 'end' };
      /** item */
      outputs?: JsonObject;
      /** item */
      varsPatch?: VarsPatchOp[];
    }
  | { status: 'failed'; error: RRError };

/**
 * 
 * @description 
 */
export interface NodeDefinition<
  TKind extends NodeKind = NodeKind,
  TConfig extends JsonObject = JsonObject,
> {
  /** item */
  kind: TKind;
  /** item Schema */
  schema: Schema<TConfig>;
  /** item */
  defaultPolicy?: NodePolicy;
  /**
   * 
   * @param ctx 
   * @param node （）
   */
  execute(
    ctx: NodeExecutionContext,
    node: NodeV3 & { kind: TKind; config: TConfig },
  ): Promise<NodeExecutionResult>;
}

/**
 * 
 */
export interface TriggerInstallContext<
  TKind extends TriggerKind = TriggerKind,
  TConfig extends JsonObject = JsonObject,
> {
  /** item ID */
  triggerId: TriggerId;
  /** item */
  kind: TKind;
  /** item */
  enabled: boolean;
  /** item Flow ID */
  flowId: FlowId;
  /** item */
  config: TConfig;
  /** item Flow item */
  args?: JsonObject;
}

/**
 * 
 * @description 
 */
export interface TriggerDefinition<
  TKind extends TriggerKind = TriggerKind,
  TConfig extends JsonObject = JsonObject,
> {
  /** item */
  kind: TKind;
  /** item Schema */
  schema: Schema<TConfig>;
  /** item */
  install(ctx: TriggerInstallContext<TKind, TConfig>): Promise<void> | void;
  /** item */
  uninstall(ctx: TriggerInstallContext<TKind, TConfig>): Promise<void> | void;
}

/**
 * 
 */
export interface PluginRegistrationContext {
  /** item */
  registerNode(def: NodeDefinition): void;
  /** item */
  registerTrigger(def: TriggerDefinition): void;
}

/**
 * 
 * @description Record-Replay 
 */
export interface RRPlugin {
  /** item */
  name: string;
  /** item */
  register(ctx: PluginRegistrationContext): void;
}
