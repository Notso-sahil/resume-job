/**
 * @fileoverview 
 * @description 
 */

import type { TriggerSpec, TriggerKind } from '../../domain/triggers';

/**
 * 
 * @description 
 */
export interface TriggerHandler<K extends TriggerKind = TriggerKind> {
  /** item */
  readonly kind: K;

  /**
   * 
   * @description  chrome API 
   * @param trigger 
   */
  install(trigger: Extract<TriggerSpec, { kind: K }>): Promise<void>;

  /**
   * 
   * @description  chrome API 
   * @param triggerId  ID
   */
  uninstall(triggerId: string): Promise<void>;

  /**
   * 
   * @description 
   */
  uninstallAll(): Promise<void>;

  /**
   *  ID 
   */
  getInstalledIds(): string[];
}

/**
 * 
 * @description TriggerManager  Handler 
 */
export interface TriggerFireCallback {
  /**
   * 
   * @param triggerId  ID
   * @param context 
   */
  onFire(
    triggerId: string,
    context: {
      sourceTabId?: number;
      sourceUrl?: string;
    },
  ): Promise<void>;
}

/**
 * 
 */
export type TriggerHandlerFactory<K extends TriggerKind> = (
  fireCallback: TriggerFireCallback,
) => TriggerHandler<K>;
