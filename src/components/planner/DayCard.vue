<script setup lang="ts">
import { computed, ref } from 'vue';
import { NTag, NButton, NPopconfirm } from 'naive-ui';
import draggable from 'vuedraggable';
import NodePicker from './NodePicker.vue';
import AppIcon from '@/components/common/AppIcon.vue';
import { useRoutesStore } from '@/stores/routesStore';
import { usePlanStore } from '@/stores/planStore';
import { dayColor } from '@/services/DayColors';
import type { DailyPlan } from '@/types';

const props = defineProps<{
  index: number;
  startNodeName: string;
  derivedStartNodeId: string;
  endNodeName: string;
  totalMinutes: number;
  dailyPlan: DailyPlan;
  expanded: boolean;
  isOnly: boolean;
  warnings: string[];
}>();

const emit = defineEmits<{
  'toggle-expand': [];
  'change-start': [nodeId: string];
  'change-target': [nodeId: string];
  'add-via': [nodeId: string];
  'remove-via': [index: number];
  'reorder-via': [from: number, to: number];
  'remove-day': [];
}>();

const routesStore = useRoutesStore();
const planStore = usePlanStore();
const route = computed(() => routesStore.getById(planStore.draft?.routeId ?? ''));

function fmt(min: number): string {
  if (min <= 0) return '—';
  const h = Math.floor(min / 60);
  const m = min % 60;
  return m > 0 ? `${h}h${String(m).padStart(2, '0')}` : `${h}h`;
}

// via search
const viaPickerKey = ref(0);
function onAddVia(nodeId: string) {
  emit('add-via', nodeId);
  viaPickerKey.value++;
}

function nodeName(id: string): string {
  return route.value?.nodes.find((n) => n.id === id)?.name ?? id;
}

const draggableList = computed({
  get: () => props.dailyPlan.viaNodeIds.map((nodeId, idx) => ({
    nodeId,
    _key: `${idx}__${nodeId}`,
  })),
  set: () => { /* manual handling via @end */ },
});

function onDragEnd(e: { oldIndex: number; newIndex: number }) {
  if (e.oldIndex !== e.newIndex) {
    emit('reorder-via', e.oldIndex, e.newIndex);
  }
}
</script>

<template>
  <div class="border rounded mb-1" :class="expanded ? 'bg-white' : 'bg-gray-50'">
    <button
      type="button"
      class="w-full flex justify-between items-center gap-2 px-2 py-3 text-left min-h-[44px]"
      @click="emit('toggle-expand')"
    >
      <span class="text-xs flex-1 min-w-0 truncate flex items-center gap-1">
        <AppIcon
          :name="expanded ? 'chevron-down' : 'chevron-right'"
          :size="14"
          :style="{ color: dayColor(index - 1) }"
        />
        <strong :style="{ color: dayColor(index - 1) }">DAY {{ index }}</strong>
        <span class="ml-1 truncate">· {{ startNodeName }} → {{ endNodeName }}</span>
        <AppIcon
          v-if="warnings.length > 0"
          name="alert-triangle"
          :size="14"
          class="text-brand-danger flex-shrink-0"
        />
      </span>
      <span class="text-xs text-gray-600 shrink-0">{{ fmt(totalMinutes) }}</span>
    </button>

    <div v-if="expanded" data-day-editor class="border-t p-3 space-y-3">
      <div>
        <label class="text-xs text-gray-500 block mb-1">
          起點 <span class="text-gray-400">({{ dailyPlan.startNodeId ? '已自訂' : '自動 = 前日結束' }})</span>
        </label>
        <NodePicker
          :value="dailyPlan.startNodeId ?? derivedStartNodeId"
          @select="(id) => emit('change-start', id)"
        />
      </div>

      <div>
        <label class="text-xs text-gray-500 block mb-1">當日目標</label>
        <NodePicker :value="dailyPlan.endNodeId" @select="(id) => emit('change-target', id)" />
      </div>

      <div>
        <label class="text-xs text-gray-500 block mb-1">中途加爬（可拖曳排序）</label>
        <draggable
          :model-value="draggableList"
          item-key="_key"
          @end="onDragEnd"
        >
          <template #item="{ element, index: i }">
            <NTag
              closable
              type="info"
              class="mr-1 mb-1"
              @close="emit('remove-via', i)"
            >
              {{ i + 1 }}. {{ nodeName(element.nodeId) }}
            </NTag>
          </template>
        </draggable>
        <div class="mt-2">
          <NodePicker :key="viaPickerKey" :value="undefined" placeholder="搜尋加入中途點…" @select="onAddVia" />
        </div>
        <p v-if="dailyPlan.viaNodeIds.length === 0" class="text-xs text-gray-400 mt-1">
          從下拉選單搜尋加入，或直接點地圖節點，選「加為加爬點」
        </p>
      </div>

      <NPopconfirm v-if="!isOnly" @positive-click="emit('remove-day')">
        <template #trigger>
          <NButton size="small" type="error" ghost>
            <template #icon>
              <AppIcon name="trash" :size="14" />
            </template>
            移除這天
          </NButton>
        </template>
        確定移除這天？
      </NPopconfirm>
    </div>
  </div>
</template>
