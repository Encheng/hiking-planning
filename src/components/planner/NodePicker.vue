<script setup lang="ts">
import { computed, h, type VNodeChild } from 'vue';
import { NSelect as _NSelect } from 'naive-ui';
import AppIcon from '@/components/common/AppIcon.vue';
import { useRoutesStore } from '@/stores/routesStore';
import { usePlanStore } from '@/stores/planStore';
import type { NodeCategory } from '@/types';

// Alias with canonical name so findComponent({ name: 'NSelect' }) works in tests
const NSelect = { ..._NSelect, name: 'NSelect' } as typeof _NSelect;

defineProps<{ value: string | undefined; placeholder?: string }>();
const emit = defineEmits<{ select: [nodeId: string] }>();

const routesStore = useRoutesStore();
const planStore = usePlanStore();
const route = computed(() => routesStore.getById(planStore.draft?.routeId ?? ''));

type IconName =
  | 'mountain'
  | 'home'
  | 'door'
  | 'route'
  | 'droplet'
  | 'flag';

interface CategoryGroup {
  category: NodeCategory;
  label: string;
  icon: IconName;
}

const groupOrder: CategoryGroup[] = [
  { category: 'peak',      label: '山頭',   icon: 'mountain' },
  { category: 'hut',       label: '山屋',   icon: 'home' },
  { category: 'trailhead', label: '登山口', icon: 'door' },
  { category: 'junction',  label: '岔路',   icon: 'route' },
  { category: 'water',     label: '水源',   icon: 'droplet' },
  { category: 'waypoint',  label: '其他',   icon: 'flag' },
];

interface GroupOption {
  type: 'group';
  label: string;
  key: string;
  icon: IconName;
  children: Array<{ label: string; value: string }>;
  [k: string]: unknown;
}

const groupedOptions = computed<GroupOption[]>(() => {
  if (!route.value) return [];
  const result: GroupOption[] = [];
  for (const g of groupOrder) {
    const items = route.value.nodes
      .filter((n) => n.category === g.category)
      .map((n) => ({ label: n.name, value: n.id }));
    if (items.length > 0) {
      result.push({
        type: 'group',
        label: g.label,
        key: g.label,
        icon: g.icon,
        children: items,
      });
    }
  }
  return result;
});

function renderLabel(option: Record<string, unknown>): VNodeChild {
  if (option.type === 'group') {
    return h(
      'span',
      { class: 'inline-flex items-center gap-1.5 font-medium' },
      [
        h(AppIcon, { name: option.icon as IconName, size: 14 }),
        h('span', {}, option.label as string),
      ],
    );
  }
  return option.label as string;
}
</script>

<template>
  <NSelect
    :value="value ?? null"
    :options="groupedOptions"
    :placeholder="placeholder ?? '選擇節點'"
    :render-label="renderLabel"
    filterable
    @update:value="(id: string) => emit('select', id)"
  />
</template>
