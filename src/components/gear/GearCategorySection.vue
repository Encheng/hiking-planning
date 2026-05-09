<script setup lang="ts">
import { NCheckbox, NTag, NSpace } from 'naive-ui';
import type { ResolvedGearItem, TripType } from '@/types';

const props = defineProps<{
  categoryName: string;
  categoryId: TripType;
  items: ResolvedGearItem[];
  checkedIds: string[];
}>();
const emit = defineEmits<{ toggle: [itemId: string] }>();

function isChecked(id: string) { return props.checkedIds.includes(id); }
</script>

<template>
  <section class="mb-6">
    <h3 class="font-semibold mb-2 text-base">{{ categoryName }}</h3>
    <ul class="space-y-1">
      <li v-for="item in items" :key="item.id" class="flex items-center gap-2 py-1">
        <NCheckbox :checked="isChecked(item.id)" @update:checked="emit('toggle', item.id)">
          {{ item.name }}
        </NCheckbox>
        <NSpace size="small">
          <NTag v-if="item.essential" type="error" size="small">必要</NTag>
          <NTag v-if="item.source === 'custom'" type="info" size="small">自訂</NTag>
          <NTag v-if="item.source === 'last_trip'" type="success" size="small">上次有勾</NTag>
          <span v-if="item.weight_g" class="text-xs text-gray-500">{{ item.weight_g }}g</span>
        </NSpace>
      </li>
    </ul>
  </section>
</template>
