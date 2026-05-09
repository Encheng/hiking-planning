<script setup lang="ts">
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
        class="block w-full px-2 py-1 mb-1 rounded bg-amber-100 hover:bg-amber-200 text-left"
        @click="$emit('set-target')"
      >
        ▶ 當作 Day {{ expandedDayIndex }} 目標
      </button>
      <button
        type="button"
        class="block w-full px-2 py-1 rounded bg-blue-100 hover:bg-blue-200 text-left"
        @click="$emit('add-via')"
      >
        + 加為 Day {{ expandedDayIndex }} 加爬點
      </button>
    </template>
    <p v-else class="text-amber-600">請先在右側展開要編輯的一天</p>
  </div>
</template>
