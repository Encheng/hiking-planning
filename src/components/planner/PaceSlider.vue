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
    <div class="text-right text-sm font-medium text-gray-700 mb-1">{{ props.modelValue.toFixed(2) }}x</div>
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
  padding-bottom: 1.25rem;
}
</style>
