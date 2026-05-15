<script setup lang="ts">
import AppIcon from '@/components/common/AppIcon.vue';
import type { RouteNode } from '@/types';

defineProps<{
  node: RouteNode;
  expandedDayIndex: number | null;
}>();

defineEmits<{
  'set-target': [];
  'add-via': [];
}>();
</script>

<template>
  <div class="text-xs min-w-[160px]">
    <p class="font-bold mb-1">{{ node.name }}</p>
    <p class="text-gray-500 mb-2">海拔 {{ node.elevation }}m</p>
    <template v-if="expandedDayIndex">
      <button
        type="button"
        class="flex w-full items-center gap-1 px-2 py-1 mb-1 rounded bg-brand-tint-warning hover:bg-brand-yellow/30 text-left"
        @click="$emit('set-target')"
      >
        <AppIcon name="play" :size="12" class="text-brand-amber flex-shrink-0" />
        <span>當作 Day {{ expandedDayIndex }} 目標</span>
      </button>
      <button
        type="button"
        class="flex w-full items-center gap-1 px-2 py-1 rounded bg-brand-tint-info hover:bg-brand-300/30 text-left"
        @click="$emit('add-via')"
      >
        <AppIcon name="plus" :size="12" class="text-brand-700 flex-shrink-0" />
        <span>加為 Day {{ expandedDayIndex }} 加爬點</span>
      </button>
    </template>
    <p v-else class="text-brand-amber">請先在右側展開要編輯的一天</p>
  </div>
</template>
