/**
 * @fileoverview 
 * @description  Record-Replay V3 、、
 */

import type { EdgeLabel, NodeId } from './ids';
import type { RRErrorCode } from './errors';
import type { UnixMillis } from './json';

/**
 * 
 * @description 
 */
export interface TimeoutPolicy {
  /** item（item） */
  ms: UnixMillis;
  /** item：attempt=item, node=item */
  scope?: 'attempt' | 'node';
}

/**
 * 
 * @description 
 */
export interface RetryPolicy {
  /** item */
  retries: number;
  /** item（item） */
  intervalMs: UnixMillis;
  /** item：none=item, exp=item, linear=item */
  backoff?: 'none' | 'exp' | 'linear';
  /** item（item） */
  maxIntervalMs?: UnixMillis;
  /** item：none=item, full=item */
  jitter?: 'none' | 'full';
  /** item */
  retryOn?: ReadonlyArray<RRErrorCode>;
}

/**
 * 
 * @description 
 */
export type OnErrorPolicy =
  | { kind: 'stop' }
  | { kind: 'continue'; as?: 'warning' | 'error' }
  | {
      kind: 'goto';
      target: { kind: 'edgeLabel'; label: EdgeLabel } | { kind: 'node'; nodeId: NodeId };
    }
  | { kind: 'retry'; override?: Partial<RetryPolicy> };

/**
 * 
 * @description 
 */
export interface ArtifactPolicy {
  /** item：never=item, onFailure=item, always=item */
  screenshot?: 'never' | 'onFailure' | 'always';
  /** item */
  saveScreenshotAs?: string;
  /** item */
  includeConsole?: boolean;
  /** item */
  includeNetwork?: boolean;
}

/**
 * 
 * @description 
 */
export interface NodePolicy {
  /** item */
  timeout?: TimeoutPolicy;
  /** item */
  retry?: RetryPolicy;
  /** item */
  onError?: OnErrorPolicy;
  /** item */
  artifacts?: ArtifactPolicy;
}

/**
 * Flow 
 * @description  Flow 
 */
export interface FlowPolicy {
  /** item */
  defaultNodePolicy?: NodePolicy;
  /** item */
  unsupportedNodePolicy?: OnErrorPolicy;
  /** Run item（item） */
  runTimeoutMs?: UnixMillis;
}

/**
 * 
 * @description  Flow 
 */
export function mergeNodePolicy(
  flowDefault: NodePolicy | undefined,
  nodePolicy: NodePolicy | undefined,
): NodePolicy {
  if (!flowDefault) return nodePolicy ?? {};
  if (!nodePolicy) return flowDefault;

  return {
    timeout: nodePolicy.timeout ?? flowDefault.timeout,
    retry: nodePolicy.retry ?? flowDefault.retry,
    onError: nodePolicy.onError ?? flowDefault.onError,
    artifacts: nodePolicy.artifacts
      ? { ...flowDefault.artifacts, ...nodePolicy.artifacts }
      : flowDefault.artifacts,
  };
}
