<template>
  <div class="form-section">
    <div class="form-group">
      <label class="form-label">Match by URL Contains (Primary)</label>
      <input
        class="form-input"
        v-model="(node as any).config.frame.urlContains"
        placeholder="Frame URL substring"
      />
    </div>
    <div class="form-group">
      <label class="form-label">Match by Frame Index (0-indexed)</label>
      <input class="form-input" v-model="(node as any).config.frame.index" placeholder="Index number" />
    </div>
    <div class="text-xs text-slate-500" style="padding: 0 20px"
      >Accessible frames only; blank for top page</div
    >
  </div>
</template>

<script lang="ts" setup>
/* eslint-disable vue/no-mutating-props */
import type { NodeBase } from '@/entrypoints/background/record-replay/types';
defineProps<{ node: NodeBase }>();
</script>

<style scoped></style>
