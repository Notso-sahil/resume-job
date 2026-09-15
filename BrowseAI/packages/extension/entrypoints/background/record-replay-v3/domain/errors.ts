/**
 * @fileoverview 
 * @description  Record-Replay V3 
 */

import type { JsonValue } from './json';

/** item */
export const RR_ERROR_CODES = {
  // =====  =====
  /** item */
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  /** item */
  UNSUPPORTED_NODE: 'UNSUPPORTED_NODE',
  /** DAG item */
  DAG_INVALID: 'DAG_INVALID',
  /** DAG item */
  DAG_CYCLE: 'DAG_CYCLE',

  // =====  =====
  /** item */
  TIMEOUT: 'TIMEOUT',
  /** Tab item */
  TAB_NOT_FOUND: 'TAB_NOT_FOUND',
  /** Frame item */
  FRAME_NOT_FOUND: 'FRAME_NOT_FOUND',
  /** target elementitem */
  TARGET_NOT_FOUND: 'TARGET_NOT_FOUND',
  /** item */
  ELEMENT_NOT_VISIBLE: 'ELEMENT_NOT_VISIBLE',
  /** item */
  NAVIGATION_FAILED: 'NAVIGATION_FAILED',
  /** item */
  NETWORK_REQUEST_FAILED: 'NETWORK_REQUEST_FAILED',

  // ===== / =====
  /** item */
  SCRIPT_FAILED: 'SCRIPT_FAILED',
  /** item */
  PERMISSION_DENIED: 'PERMISSION_DENIED',
  /** item */
  TOOL_ERROR: 'TOOL_ERROR',

  // =====  =====
  /** Run item */
  RUN_CANCELED: 'RUN_CANCELED',
  /** Run item */
  RUN_PAUSED: 'RUN_PAUSED',

  // =====  =====
  /** item */
  INTERNAL: 'INTERNAL',
  /** item */
  INVARIANT_VIOLATION: 'INVARIANT_VIOLATION',
} as const;

/** item */
export type RRErrorCode = (typeof RR_ERROR_CODES)[keyof typeof RR_ERROR_CODES];

/**
 * Record-Replay 
 * @description ，
 */
export interface RRError {
  /** item */
  code: RRErrorCode;
  /** item */
  message: string;
  /** item */
  data?: JsonValue;
  /** item */
  retryable?: boolean;
  /** item（item） */
  cause?: RRError;
}

/**
 *  RRError Factory functions
 */
export function createRRError(
  code: RRErrorCode,
  message: string,
  options?: { data?: JsonValue; retryable?: boolean; cause?: RRError },
): RRError {
  return {
    code,
    message,
    ...(options?.data !== undefined && { data: options.data }),
    ...(options?.retryable !== undefined && { retryable: options.retryable }),
    ...(options?.cause !== undefined && { cause: options.cause }),
  };
}
