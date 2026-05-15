<script setup lang="ts">
import { computed, ref } from 'vue';
import { NTag, NPopover, NSpace, NButton, NInput, NDivider } from 'naive-ui';
import AppIcon from '@/components/common/AppIcon.vue';
import type { TripType } from '@/types';

const props = defineProps<{
  tripType: TripType;
  /** When set, displays this instead of the default tripType label. */
  customLabel?: string;
  /** When true, shows edit affordance (small pencil hint). */
  editable?: boolean;
}>();

const emit = defineEmits<{
  /** Emitted when user picks a standard tripType. customLabel will be cleared. */
  (e: 'update', tripType: TripType, customLabel?: string): void;
  /** Emitted when user clicks "重設為自動判斷". */
  (e: 'reset'): void;
}>();

interface TypeOption {
  value: TripType;
  text: string;
  color: 'default' | 'success' | 'warning' | 'error';
}

const STANDARD_TYPES: TypeOption[] = [
  { value: 'light_summit', text: '輕裝攻頂', color: 'success' },
  { value: 'long_day', text: '長日單攻', color: 'warning' },
  { value: 'overnight_hut', text: '山屋過夜', color: 'warning' },
  { value: 'overnight_camp', text: '紮營過夜', color: 'error' },
];

const displayLabel = computed(() => {
  if (props.customLabel) return props.customLabel;
  return STANDARD_TYPES.find((t) => t.value === props.tripType)?.text ?? props.tripType;
});

const displayColor = computed(() => {
  if (props.customLabel) return 'default'; // custom labels use neutral color
  return STANDARD_TYPES.find((t) => t.value === props.tripType)?.color ?? 'default';
});

const popoverOpen = ref(false);
const customInput = ref('');

function selectStandard(t: TypeOption) {
  emit('update', t.value);
  popoverOpen.value = false;
}

function applyCustom() {
  const v = customInput.value.trim();
  if (!v) return;
  emit('update', props.tripType, v);
  customInput.value = '';
  popoverOpen.value = false;
}

function reset() {
  emit('reset');
  popoverOpen.value = false;
}
</script>

<template>
  <span v-if="!editable" class="inline-flex">
    <NTag :type="displayColor">{{ displayLabel }}</NTag>
  </span>

  <NPopover
    v-else
    v-model:show="popoverOpen"
    trigger="click"
    placement="bottom-start"
    :show-arrow="false"
  >
    <template #trigger>
      <button
        type="button"
        class="inline-flex items-center gap-1 cursor-pointer focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand-700 rounded"
        aria-label="編輯行程類型"
      >
        <NTag :type="displayColor" class="cursor-pointer">{{ displayLabel }}</NTag>
        <AppIcon name="pencil" :size="12" class="text-brand-gray" />
      </button>
    </template>

    <div class="min-w-[260px]">
      <div class="text-xs text-brand-gray mb-2">選擇行程類型</div>
      <NSpace vertical size="small">
        <NButton
          v-for="opt in STANDARD_TYPES"
          :key="opt.value"
          block
          :type="opt.value === tripType && !customLabel ? 'primary' : 'default'"
          @click="selectStandard(opt)"
        >
          {{ opt.text }}
        </NButton>
      </NSpace>

      <NDivider style="margin: 12px 0" />

      <div class="text-xs text-brand-gray mb-2">或自訂標籤</div>
      <div class="flex gap-2">
        <NInput
          v-model:value="customInput"
          placeholder="例如：Y型縱走、O型、探勘…"
          maxlength="12"
          show-count
          aria-label="自訂行程標籤"
          @keyup.enter="applyCustom"
        />
        <NButton type="primary" :disabled="!customInput.trim()" @click="applyCustom">
          套用
        </NButton>
      </div>

      <NDivider style="margin: 12px 0" />

      <NButton block quaternary @click="reset">
        重設為自動判斷
      </NButton>
    </div>
  </NPopover>
</template>
