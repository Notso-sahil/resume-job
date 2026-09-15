/**
 * @fileoverview 
 * @description  Record-Replay V3 
 */

import type { JsonValue, UnixMillis } from './json';

/** item */
export type VariableName = string;

/** item（item $ item） */
export type PersistentVariableName = `$${string}`;

/** item */
export type VariableScope = 'run' | 'flow' | 'persistent';

/**
 * 
 * @description ， JSON path 
 */
export interface VariablePointer {
  /** item */
  scope: VariableScope;
  /** item */
  name: VariableName;
  /** JSON path（item） */
  path?: ReadonlyArray<string | number>;
}

/**
 * 
 * @description Flow 
 */
export interface VariableDefinition {
  /** item */
  name: VariableName;
  /** item */
  label?: string;
  /** item */
  description?: string;
  /** item（item/item） */
  sensitive?: boolean;
  /** item */
  required?: boolean;
  /** item */
  default?: JsonValue;
  /** item（item persistent，persistent item $ item） */
  scope?: Exclude<VariableScope, 'persistent'>;
}

/**
 * 
 * @description  IndexedDB 
 */
export interface PersistentVarRecord {
  /** item（item $ item） */
  key: PersistentVariableName;
  /** item */
  value: JsonValue;
  /** item */
  updatedAt: UnixMillis;
  /** item（item，item LWW item） */
  version: number;
}

/**
 * 
 */
export function isPersistentVariable(name: string): name is PersistentVariableName {
  return name.startsWith('$');
}

/**
 * 
 * @example "$user.name" -> { scope: 'persistent', name: '$user', path: ['name'] }
 */
export function parseVariablePointer(ref: string): VariablePointer | null {
  if (!ref) return null;

  const parts = ref.split('.');
  const name = parts[0];
  const path = parts.slice(1);

  if (isPersistentVariable(name)) {
    return {
      scope: 'persistent',
      name,
      path: path.length > 0 ? path : undefined,
    };
  }

  //  run 
  return {
    scope: 'run',
    name,
    path: path.length > 0 ? path : undefined,
  };
}
