<script setup lang="ts">
import { NSlider, NSpace } from 'naive-ui';

const props = defineProps<{ modelValue: number }>();
const emit = defineEmits<{ 'update:modelValue': [value: number] }>();

function update(val: number | [number, number]) {
  emit('update:modelValue', Array.isArray(val) ? val[0] : val);
}

const marks = {
  0.8: '0.8x',
  1.0: '上河',
  1.2: '1.2x',
  1.5: '1.5x',
};
</script>

<template>
  <NSpace vertical size="small">
    <div class="flex justify-between">
      <span class="text-sm text-gray-600">腳程倍率</span>
      <span class="text-sm font-medium">{{ props.modelValue.toFixed(2) }}x</span>
    </div>
    <NSlider
      :value="props.modelValue"
      :min="0.8" :max="1.5" :step="0.05"
      :marks="marks"
      @update:value="update"
    />
  </NSpace>
</template>
