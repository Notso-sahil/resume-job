export const COMMAND_NAME = 'nexus-bridge';
export const EXTENSION_ID = 'ijmgdinpcbmgfmefblpgbcoacnbkiokj';
export const ALLOWED_EXTENSION_IDS = [
  'ijmgdinpcbmgfmefblpgbcoacnbkiokj',
  'hbdgbgagpkpjffpklnamcljpakneikee',
];
export const HOST_NAME = 'com.nexusai.browserhost';
export const DESCRIPTION = 'NexusAI Native Messaging Host for Autonomous Browser Agent';

/**
 * Directory (under the user's home) where `nexus-bridge set-id` persists the
 * user's actual, freshly-loaded-unpacked Extension ID. This survives
 * `pnpm install`/reinstalls without recompiling, unlike ALLOWED_EXTENSION_IDS
 * above, which is a fallback default used only when no config is present.
 */
export const CONFIG_DIR_NAME = '.nexus-bridge';
export const CONFIG_FILE_NAME = 'config.json';
