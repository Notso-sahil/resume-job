<template>
  <div>
    <SelectorEditor :node="node" :allowPick="true" title="Drag Origin Selector" targetKey="start" />
    <SelectorEditor :node="node" :allowPick="true" title="Drag Target Selector" targetKey="end" />
    <div class="hint">
      <small>Note: Drag trajectories are automatically recorded during user sessions. Leave blank for direct simulation.</small>
    </div>
  </div>
</template>

<script lang="ts" setup>
/* eslint-disable vue/no-mutating-props */
import type { NodeBase } from '@/entrypoints/background/record-replay/types';
import SelectorEditor from './SelectorEditor.vue';

defineProps<{ node: NodeBase }>();
</script>

<style scoped>
.hint {
  color: #64748b;
  margin-top: 8px;
}
</style>
