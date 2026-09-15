/**
 * @fileoverview ID 
 * @description  Record-Replay V3  ID 
 */

/** Flow item */
export type FlowId = string;

/** Node item */
export type NodeId = string;

/** Edge item */
export type EdgeId = string;

/** Run item */
export type RunId = string;

/** Trigger item */
export type TriggerId = string;

/** Edge item */
export type EdgeLabel = string;

/** item Edge item */
export const EDGE_LABELS = {
  /** item */
  DEFAULT: 'default',
  /** item */
  ON_ERROR: 'onError',
  /** item */
  TRUE: 'true',
  /** item */
  FALSE: 'false',
} as const;

/** Edge item（item） */
export type EdgeLabelValue = (typeof EDGE_LABELS)[keyof typeof EDGE_LABELS];
