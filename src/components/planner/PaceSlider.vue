<script setup lang="ts">
import { NSlider } from 'naive-ui';

const props = defineProps<{ modelValue: number }>();
const emit = defineEmits<{ 'update:modelValue': [value: number] }>();

function update(val: number | [number, number]) {
  emit('update:modelValue', Array.isArray(val) ? val[0] : val);
}

const marks = {
  0.8: '0.8x',
  1.0: '上河',
  1.5: '1.5x',
};
</script>

<template>
  <div class="pace-slider w-full">
    <div class="text-right text-sm font-medium text-brand-900 mb-1">{{ props.modelValue.toFixed(2) }}x</div>
    <NSlider
      :value="props.modelValue"
      :min="0.8" :max="1.5" :step="0.05"
      :marks="marks"
      @update:value="update"
    />
  </div>
</template>

<style scoped>
.pace-slider {
  padding-bottom: 1.5rem;
  /* Larger touch target — Naive's default handle is 18px which is below the
     44px WCAG/Apple minimum. Enlarge the handle and the hit area. */
  --handle-size: 28px;
}
.pace-slider :deep(.n-slider-handle) {
  width: var(--handle-size);
  height: var(--handle-size);
  /* Center the larger handle on the rail */
  transform: translate(-50%, -50%);
  top: 50%;
}
.pace-slider :deep(.n-slider-handle::after) {
  /* Invisible expanded hit-box so finger taps register reliably */
  content: '';
  position: absolute;
  inset: -10px;
}
.pace-slider :deep(.n-slider-rail) {
  height: 6px;
}
.pace-slider :deep(.n-slider-dots .n-slider-dot) {
  width: 10px;
  height: 10px;
}
</style>
