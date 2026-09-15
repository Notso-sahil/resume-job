/**
 * @fileoverview Flow 
 * @description  Record-Replay V3  Flow IR（）
 */

import type { ISODateTimeString, JsonObject } from './json';
import type { EdgeId, EdgeLabel, FlowId, NodeId } from './ids';
import type { FlowPolicy, NodePolicy } from './policy';
import type { VariableDefinition } from './variables';

/** Flow Schema item */
export const FLOW_SCHEMA_VERSION = 3 as const;

/**
 * Edge V3
 * @description DAG ，
 */
export interface EdgeV3 {
  /** Edge item */
  id: EdgeId;
  /** item ID */
  from: NodeId;
  /** item ID */
  to: NodeId;
  /** item（item） */
  label?: EdgeLabel;
}

/** item（item） */
export type NodeKind = string;

/**
 * Node V3
 * @description DAG ，
 */
export interface NodeV3 {
  /** Node item */
  id: NodeId;
  /** item */
  kind: NodeKind;
  /** item（item） */
  name?: string;
  /** item */
  disabled?: boolean;
  /** item */
  policy?: NodePolicy;
  /** item（item kind item） */
  config: JsonObject;
  /** UI item */
  ui?: { x: number; y: number };
}

/**
 * Flow 
 * @description  Flow //URL 
 */
export interface FlowBinding {
  kind: 'domain' | 'path' | 'url';
  value: string;
}

/**
 * Flow V3
 * @description  Flow ，、
 */
export interface FlowV3 {
  /** Schema item */
  schemaVersion: typeof FLOW_SCHEMA_VERSION;
  /** Flow item */
  id: FlowId;
  /** Flow item */
  name: string;
  /** Flow item */
  description?: string;
  /** item */
  createdAt: ISODateTimeString;
  /** item */
  updatedAt: ISODateTimeString;

  /** item ID（item，item） */
  entryNodeId: NodeId;
  /** item */
  nodes: NodeV3[];
  /** item */
  edges: EdgeV3[];

  /** item */
  variables?: VariableDefinition[];
  /** Flow item */
  policy?: FlowPolicy;
  /** item */
  meta?: {
    /** item */
    tags?: string[];
    /** item */
    bindings?: FlowBinding[];
  };
}

/**
 *  ID 
 */
export function findNodeById(flow: FlowV3, nodeId: NodeId): NodeV3 | undefined {
  return flow.nodes.find((n) => n.id === nodeId);
}

/**
 * 
 */
export function findEdgesFrom(flow: FlowV3, nodeId: NodeId): EdgeV3[] {
  return flow.edges.filter((e) => e.from === nodeId);
}

/**
 * 
 */
export function findEdgesTo(flow: FlowV3, nodeId: NodeId): EdgeV3[] {
  return flow.edges.filter((e) => e.to === nodeId);
}
