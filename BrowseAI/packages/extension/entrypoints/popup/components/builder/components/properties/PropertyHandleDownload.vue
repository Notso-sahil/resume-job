<template>
  <div class="form-section">
    <div class="form-group">
      <label class="form-label">Filename Pattern (Optional)</label>
      <input
        class="form-input"
        v-model="(node as any).config.filenameContains"
        placeholder="Match filename or source URL"
      />
    </div>
    <div class="form-group">
      <label class="form-label">Timeout (ms)</label>
      <input class="form-input" v-model="(node as any).config.timeoutMs" placeholder="Default: 60000" />
    </div>
    <div class="form-group checkbox-group">
      <label class="checkbox-label"
        ><input type="checkbox" v-model="(node as any).config.waitForComplete" />
        Wait for download completion</label
      >
    </div>
    <div class="form-group">
      <label class="form-label">Save Path to Variable</label>
      <input class="form-input" v-model="(node as any).config.saveAs" placeholder="Default: download" />
    </div>
  </div>
</template>

<script lang="ts" setup>
/* eslint-disable vue/no-mutating-props */
import type { NodeBase } from '@/entrypoints/background/record-replay/types';
defineProps<{ node: NodeBase }>();
</script>

<style scoped></style>
