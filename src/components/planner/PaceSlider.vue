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

/* Enlarge handle/rail so the touch target meets WCAG/Apple minimum.
   Theme tokens are the only knobs that flow into Naive's positioning math
   (padding around the rail is computed from handleSize). */
const sliderThemeOverrides = {
  handleSize: '24px',
  railHeight: '6px',
  dotHeight: '10px',
  dotWidth: '10px',
};
</script>

<template>
  <div class="pace-slider w-full">
    <div class="text-right text-sm font-medium text-brand-900 mb-1">{{ props.modelValue.toFixed(2) }}x</div>
    <NSlider
      :value="props.modelValue"
      :min="0.8" :max="1.5" :step="0.05"
      :marks="marks"
      :theme-overrides="sliderThemeOverrides"
      @update:value="update"
    />
  </div>
</template>

<style scoped>
.pace-slider {
  padding-bottom: 1.5rem;
}
/* Extra invisible hit-area so finger taps register reliably without
   inflating the visible handle further. */
.pace-slider :deep(.n-slider-handle-wrapper)::after {
  content: '';
  position: absolute;
  inset: -10px;
}
</style>
