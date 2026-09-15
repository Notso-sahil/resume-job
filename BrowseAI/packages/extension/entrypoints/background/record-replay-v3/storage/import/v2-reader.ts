/**
 * @fileoverview V2 
 * @description  V2 （）
 */

/**
 * V2 
 * @description Phase 5+ 
 */
export interface V2Reader {
  /** item V2 Flows */
  readFlows(): Promise<unknown[]>;
  /** item V2 Runs */
  readRuns(): Promise<unknown[]>;
  /** item V2 Triggers */
  readTriggers(): Promise<unknown[]>;
  /** item V2 Schedules */
  readSchedules(): Promise<unknown[]>;
}

/**
 *  NotImplemented  V2Reader
 */
export function createNotImplementedV2Reader(): V2Reader {
  const notImplemented = async () => {
    throw new Error('V2Reader not implemented');
  };

  return {
    readFlows: notImplemented,
    readRuns: notImplemented,
    readTriggers: notImplemented,
    readSchedules: notImplemented,
  };
}
