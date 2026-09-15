/**
 * Chrome Extension i18n utility
 * Provides safe access to chrome.i18n.getMessage with fallbacks
 */

// Fallback messages for when Chrome APIs aren't available (English)
const fallbackMessages: Record<string, string> = {
  // Extension metadata
  extensionName: 'NexusAI Browser Agent',
  extensionDescription: 'Autonomous browser automation runtime connecting Antigravity to web environments',

  // Section headers
  nativeServerConfigLabel: 'Bridge Connection Gateway',
  semanticEngineLabel: 'Neural Vector Engine',
  embeddingModelLabel: 'Transformer Model Runtime',
  indexDataManagementLabel: 'Vector Index & Storage',
  modelCacheManagementLabel: 'Model Cache Storage',
  mcpServerConfigLabel: 'Fastify MCP Protocol Specification',

  // Status labels
  statusLabel: 'Operational State',
  runningStatusLabel: 'Service Health',
  connectionStatusLabel: 'Gateway Connection Link',
  lastUpdatedLabel: 'Last Heartbeat:',

  // Connection states
  connectButton: 'Connect Runtime',
  disconnectButton: 'Disconnect Runtime',
  connectingStatus: 'Synchronizing link...',
  connectedStatus: 'Online & Linked',
  disconnectedStatus: 'Standby / Offline',
  detectingStatus: 'Probing bridge host...',

  // Server states
  serviceRunningStatus: 'NexusAI Bridge Active (Port: {0})',
  serviceNotConnectedStatus: 'Bridge service unreachable',
  connectedServiceNotStartedStatus: 'Native host linked; awaiting MCP daemon',

  // Configuration labels
  connectionPortLabel: 'Bridge Service Port',
  refreshStatusButton: 'Probe Status',
  copyConfigButton: 'Copy MCP Configuration',

  // Action buttons
  retryButton: 'Retry Directive',
  cancelButton: 'Abort',
  confirmButton: 'Confirm Directive',
  saveButton: 'Save Preferences',
  closeButton: 'Dismiss',
  resetButton: 'Restore Defaults',

  // Progress states
  initializingStatus: 'Bootstrapping...',
  processingStatus: 'Executing instruction...',
  loadingStatus: 'Loading telemetry...',
  clearingStatus: 'Purging records...',
  cleaningStatus: 'Evicting stale entries...',
  downloadingStatus: 'Streaming model assets...',

  // Semantic engine states
  semanticEngineReadyStatus: 'Neural vector pipeline operational',
  semanticEngineInitializingStatus: 'Spinning up local vector engine...',
  semanticEngineInitFailedStatus: 'Neural engine initialization failed',
  semanticEngineNotInitStatus: 'Neural engine dormant',
  initSemanticEngineButton: 'Activate Neural Pipeline',
  reinitializeButton: 'Reboot Engine',

  // Model states
  downloadingModelStatus: 'Downloading transformer weights: {0}%',
  switchingModelStatus: 'Reallocating model weights...',
  modelLoadedStatus: 'Weights loaded into memory',
  modelFailedStatus: 'Weight allocation failed',

  // Model descriptions
  lightweightModelDescription: 'High-throughput multilingual transformer',
  betterThanSmallDescription: 'Enhanced semantic balance with superior accuracy',
  multilingualModelDescription: 'Deep multilingual semantic representations',

  // Performance levels
  fastPerformance: 'Maximum Speed',
  balancedPerformance: 'Balanced Latency',
  accuratePerformance: 'High Precision',

  // Error messages
  networkErrorMessage: 'Bridge connection lost. Ensure nexus-bridge is active on port 12307.',
  modelCorruptedErrorMessage: 'Cached neural weights failed validation. Re-downloading required.',
  unknownErrorMessage: 'Encountered unexpected browser execution fault.',
  permissionDeniedErrorMessage: 'Target operation blocked by Chrome permission boundaries.',
  timeoutErrorMessage: 'Execution timed out waiting for browser DOM response.',

  // Data statistics
  indexedPagesLabel: 'Indexed Webpages',
  indexSizeLabel: 'Vector Store Size',
  activeTabsLabel: 'Monitored Tabs',
  vectorDocumentsLabel: 'Embedded Nodes',
  cacheSizeLabel: 'Allocated Cache Size',
  cacheEntriesLabel: 'Cached Node Entries',

  // Data management
  clearAllDataButton: 'Purge Vector Database',
  clearAllCacheButton: 'Evict Model Cache',
  cleanExpiredCacheButton: 'Prune Stale Artifacts',
  exportDataButton: 'Export Index Dump',
  importDataButton: 'Import Index Dump',

  // Dialog titles
  confirmClearDataTitle: 'Confirm Index Purge',
  settingsTitle: 'Agent Runtime Preferences',
  aboutTitle: 'About NexusAI Browser Agent',
  helpTitle: 'Documentation & Diagnostics',

  // Dialog messages
  clearDataWarningMessage: 'This operation will completely purge all indexed browser DOM data and semantic vectors:',
  clearDataList1: 'Cached text content & accessibility trees',
  clearDataList2: 'Local HNSW vector embeddings and similarity index',
  clearDataList3: 'Action execution history and telemetry logs',
  clearDataIrreversibleWarning: 'Notice: This action cannot be reversed. Web pages must be revisited to reconstruct semantic vectors.',
  confirmClearButton: 'Confirm Purge',

  // Cache states
  cacheDetailsLabel: 'Cache Telemetry',
  noCacheDataMessage: 'No resident cache artifacts found.',
  loadingCacheInfoStatus: 'Inspecting cache telemetry...',
  processingCacheStatus: 'Executing cache maintenance...',
  expiredLabel: 'Stale / Expired',

  // Browser integration
  bookmarksBarLabel: 'Bookmarks Navigation',
  newTabLabel: 'New Browser Context',
  currentPageLabel: 'Active Viewport',

  // Accessibility
  menuLabel: 'Agent Menu',
  navigationLabel: 'Workspace Navigation',
  mainContentLabel: 'Agent Workspace',

  // Telemetry & Settings
  languageSelectorLabel: 'Language Environment',
  themeLabel: 'Visual Theme',
  lightTheme: 'Daylight',
  darkTheme: 'Obsidian Dark',
  autoTheme: 'System Sync',
  advancedSettingsLabel: 'Advanced Diagnostics',
  debugModeLabel: 'Diagnostic Trace Logging',
  verboseLoggingLabel: 'Verbose Protocol Output',

  // Notifications
  successNotification: 'Directive executed successfully.',
  warningNotification: 'Attention: Review parameter requirements.',
  infoNotification: 'Telemetry update available.',
  configCopiedNotification: 'MCP server configuration copied to clipboard.',
  dataClearedNotification: 'All vector index records have been pruned.',

  // Units
  bytesUnit: 'bytes',
  kilobytesUnit: 'KB',
  megabytesUnit: 'MB',
  gigabytesUnit: 'GB',
  itemsUnit: 'nodes',
  pagesUnit: 'documents',

  // Aliases for backwards compatibility with legacy UI bindings
  nativeServerConfig: 'Bridge Connection Gateway',
  runningStatus: 'Service Health',
  refreshStatus: 'Probe Status',
  lastUpdated: 'Last Heartbeat:',
  mcpServerConfig: 'Fastify MCP Protocol Specification',
  connectionPort: 'Bridge Service Port',
  connecting: 'Synchronizing link...',
  disconnect: 'Disconnect Runtime',
  connect: 'Connect Runtime',
  semanticEngine: 'Neural Vector Engine',
  embeddingModel: 'Transformer Model Runtime',
  retry: 'Retry Directive',
  indexDataManagement: 'Vector Index & Storage',
  clearing: 'Purging records...',
  clearAllData: 'Purge Vector Database',
  copyConfig: 'Copy MCP Configuration',
  serviceRunning: 'NexusAI Bridge Active (Port: {0})',
  connectedServiceNotStarted: 'Native host linked; awaiting MCP daemon',
  serviceNotConnected: 'Bridge service unreachable',
  detecting: 'Probing bridge host...',
  lightweightModel: 'High-throughput multilingual transformer',
  betterThanSmall: 'Enhanced semantic balance with superior accuracy',
  multilingualModel: 'Deep multilingual semantic representations',
  fast: 'Maximum Speed',
  balanced: 'Balanced Latency',
  accurate: 'High Precision',
  semanticEngineReady: 'Neural vector pipeline operational',
  semanticEngineInitializing: 'Spinning up local vector engine...',
  semanticEngineInitFailed: 'Neural engine initialization failed',
  semanticEngineNotInit: 'Neural engine dormant',
  downloadingModel: 'Downloading transformer weights: {0}%',
  switchingModel: 'Reallocating model weights...',
  networkError: 'Bridge connection lost. Ensure nexus-bridge is active on port 12307.',
  modelCorrupted: 'Cached neural weights failed validation. Re-downloading required.',
  unknownError: 'Encountered unexpected browser execution fault.',
  reinitialize: 'Reboot Engine',
  initializing: 'Bootstrapping...',
  initSemanticEngine: 'Activate Neural Pipeline',
  indexedPages: 'Indexed Webpages',
  indexSize: 'Vector Store Size',
  activeTabs: 'Monitored Tabs',
  vectorDocuments: 'Embedded Nodes',
  confirmClearData: 'Confirm Index Purge',
  clearDataWarning: 'This operation will completely purge all indexed browser DOM data and semantic vectors:',
  clearDataIrreversible: 'Notice: This action cannot be reversed. Web pages must be revisited to reconstruct semantic vectors.',
  confirmClear: 'Confirm Purge',
  cancel: 'Abort',
  confirm: 'Confirm Directive',
  processing: 'Executing instruction...',
  modelCacheManagement: 'Model Cache Storage',
  cacheSize: 'Allocated Cache Size',
  cacheEntries: 'Cached Node Entries',
  cacheDetails: 'Cache Telemetry',
  noCacheData: 'No resident cache artifacts found.',
  loadingCacheInfo: 'Inspecting cache telemetry...',
  processingCache: 'Executing cache maintenance...',
  cleaning: 'Evicting stale entries...',
  cleanExpiredCache: 'Prune Stale Artifacts',
  clearAllCache: 'Evict Model Cache',
  expired: 'Stale / Expired',
  bookmarksBar: 'Bookmarks Navigation',
};

/**
 * Safe i18n message getter with fallback support
 * @param key Message key
 * @param substitutions Optional substitution values
 * @returns Localized message or fallback
 */
export function getMessage(key: string, substitutions?: string[]): string {
  try {
    // Check if Chrome extension APIs are available
    if (typeof chrome !== 'undefined' && chrome.i18n && chrome.i18n.getMessage) {
      const message = chrome.i18n.getMessage(key, substitutions);
      if (message) {
        return message;
      }
    }
  } catch (error) {
    console.warn(`Failed to get i18n message for key "${key}":`, error);
  }

  // Fallback to English messages
  let fallback = fallbackMessages[key] || key;

  // Handle substitutions in fallback messages
  if (substitutions && substitutions.length > 0) {
    substitutions.forEach((value, index) => {
      fallback = fallback.replace(`{${index}}`, value);
    });
  }

  return fallback;
}

/**
 * Check if Chrome extension i18n APIs are available
 */
export function isI18nAvailable(): boolean {
  try {
    return (
      typeof chrome !== 'undefined' && chrome.i18n && typeof chrome.i18n.getMessage === 'function'
    );
  } catch {
    return false;
  }
}
