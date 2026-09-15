<template>
  <div class="form-section">
    <div class="form-group">
      <label class="form-label">Element Selector (Optional)</label>
      <input
        class="form-input"
        v-model="(node as any).config.selector"
        placeholder="Leave blank to capture viewport"
      />
    </div>
    <div class="form-group checkbox-group">
      <label class="checkbox-label"
        ><input type="checkbox" v-model="(node as any).config.fullPage" /> Capture Full Page</label
      >
    </div>
    <div class="form-group">
      <label class="form-label">Save to Variable</label>
      <input
        class="form-input"
        v-model="(node as any).config.saveAs"
        placeholder="Variable name, e.g. screenshotData"
      />
    </div>
  </div>
</template>

<script lang="ts" setup>
/* eslint-disable vue/no-mutating-props */
import type { NodeBase } from '@/entrypoints/background/record-replay/types';
defineProps<{ node: NodeBase }>();
</script>

<style scoped></style>
