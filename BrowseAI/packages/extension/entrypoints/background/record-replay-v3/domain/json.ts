/**
 * @fileoverview JSON 
 * @description  Record-Replay V3  JSON 
 */

/** JSON item */
export type JsonPrimitive = string | number | boolean | null;

/** JSON item */
export interface JsonObject {
  [key: string]: JsonValue;
}

/** JSON item */
export type JsonArray = JsonValue[];

/** item JSON item */
export type JsonValue = JsonPrimitive | JsonObject | JsonArray;

/** ISO 8601 item */
export type ISODateTimeString = string;

/** Unix item */
export type UnixMillis = number;
