<script setup lang="ts">
import { computed } from 'vue';
import { NSelect as _NSelect } from 'naive-ui';
import { useRoutesStore } from '@/stores/routesStore';
import { usePlanStore } from '@/stores/planStore';
import type { NodeCategory } from '@/types';

// Alias with canonical name so findComponent({ name: 'NSelect' }) works in tests
const NSelect = { ..._NSelect, name: 'NSelect' } as typeof _NSelect;

defineProps<{ value: string | undefined }>();
const emit = defineEmits<{ select: [nodeId: string] }>();

const routesStore = useRoutesStore();
const planStore = usePlanStore();
const route = computed(() => routesStore.getById(planStore.draft?.routeId ?? ''));

interface CategoryGroup {
  category: NodeCategory;
  label: string;
  emoji: string;
}

const groupOrder: CategoryGroup[] = [
  { category: 'peak',      label: '山頭',   emoji: '⛰' },
  { category: 'hut',       label: '山屋',   emoji: '🏠' },
  { category: 'trailhead', label: '登山口', emoji: '🚪' },
  { category: 'junction',  label: '岔路',   emoji: '🔀' },
  { category: 'water',     label: '水源',   emoji: '💧' },
  { category: 'waypoint',  label: '其他',   emoji: '⛳' },
];

const groupedOptions = computed(() => {
  if (!route.value) return [];
  const result: Array<{ type: 'group'; label: string; key: string; children: Array<{ label: string; value: string }> }> = [];
  for (const g of groupOrder) {
    const items = route.value.nodes
      .filter((n) => n.category === g.category)
      .map((n) => ({ label: n.name, value: n.id }));
    if (items.length > 0) {
      result.push({ type: 'group', label: `${g.emoji} ${g.label}`, key: g.label, children: items });
    }
  }
  return result;
});
</script>

<template>
  <NSelect
    :value="value ?? null"
    :options="groupedOptions"
    placeholder="選擇節點"
    filterable
    @update:value="(id: string) => emit('select', id)"
  />
</template>
