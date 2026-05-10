<script setup lang="ts">
import { computed } from 'vue';
import { NCheckbox, NButton } from 'naive-ui';
import DayCard from './DayCard.vue';
import NodePicker from './NodePicker.vue';
import { usePlanStore } from '@/stores/planStore';
import { useRoutesStore } from '@/stores/routesStore';
import { useDailyEditorStore } from '@/stores/dailyEditorStore';
import { resolvePath } from '@/services/PathResolver';

const planStore = usePlanStore();
const routesStore = useRoutesStore();
const editor = useDailyEditorStore();

const draft = computed(() => planStore.draft!);
const route = computed(() => routesStore.getById(draft.value.routeId ?? ''));
const resolution = computed(() => planStore.draftResolution);

function nodeName(id: string | undefined): string {
  if (!id) return '(未選)';
  return route.value?.nodes.find((n) => n.id === id)?.name ?? id;
}

function getDayStartName(dayIdx: number): string {
  if (dayIdx === 0) return nodeName(draft.value.startNodeId);
  return nodeName(draft.value.dailyPlans?.[dayIdx - 1]?.endNodeId);
}

function getDayTotalMinutes(dayIdx: number): number {
  const day = resolution.value?.days[dayIdx];
  if (!day || !route.value || day.pathNodeIds.length < 2) return 0;
  let total = 0;
  for (let i = 0; i < day.pathNodeIds.length - 1; i++) {
    const from = day.pathNodeIds[i];
    const to = day.pathNodeIds[i + 1];
    const edge = route.value.edges.find(
      (e) => (e.from === from && e.to === to) || (e.from === to && e.to === from),
    );
    if (!edge) continue;
    const isFwd = edge.from === from;
    total += isFwd ? edge.minutes_forward : edge.minutes_backward;
  }
  return Math.round(total * (draft.value.paceMultiplier ?? 1));
}

function changeStart(nodeId: string) {
  if (draft.value) draft.value.startNodeId = nodeId;
}

function addDay() {
  if (!draft.value.dailyPlans) draft.value.dailyPlans = [];
  draft.value.dailyPlans.push({ endNodeId: '', endType: 'manual', viaNodeIds: [] });
  editor.expandedDayIndex = draft.value.dailyPlans.length;
}

function removeDay(idx: number) {
  draft.value.dailyPlans?.splice(idx, 1);
  if (editor.expandedDayIndex === idx + 1) editor.expandedDayIndex = null;
}

function computeAutoViaIds(dayIdx: number, endNodeId: string): string[] {
  if (!route.value || !endNodeId) return [];
  const dayStart = dayIdx === 0
    ? draft.value.startNodeId
    : draft.value.dailyPlans?.[dayIdx - 1]?.endNodeId;
  if (!dayStart) return [];
  const path = resolvePath({
    route: route.value,
    startNodeId: dayStart,
    endNodeId,
    viaNodeIds: [],
  });
  if (path.warnings.includes('no_path') || path.forward.length < 2) return [];
  return path.forward.slice(1, -1);
}

function changeTarget(idx: number, nodeId: string) {
  if (!draft.value.dailyPlans) return;
  draft.value.dailyPlans[idx].endNodeId = nodeId;
  draft.value.dailyPlans[idx].viaNodeIds = computeAutoViaIds(idx, nodeId);
}

function removeVia(idx: number, viaIndex: number) {
  if (!draft.value.dailyPlans) return;
  draft.value.dailyPlans[idx].viaNodeIds.splice(viaIndex, 1);
}

function reorderVia(idx: number, from: number, to: number) {
  if (!draft.value.dailyPlans) return;
  const list = draft.value.dailyPlans[idx].viaNodeIds;
  const [moved] = list.splice(from, 1);
  list.splice(to, 0, moved);
}
</script>

<template>
  <div v-if="draft" class="space-y-2">
    <div class="border rounded p-3 bg-emerald-50">
      <div class="flex justify-between items-center mb-2">
        <span class="text-sm font-medium">起點</span>
        <div class="flex-1 ml-3">
          <NodePicker :value="draft.startNodeId" @select="changeStart" />
        </div>
      </div>
      <NCheckbox v-model:checked="draft.returnToStart">回到起點</NCheckbox>
    </div>

    <DayCard
      v-for="(daily, i) in draft.dailyPlans ?? []"
      :key="i"
      :index="i + 1"
      :start-node-name="getDayStartName(i)"
      :end-node-name="nodeName(daily.endNodeId)"
      :total-minutes="getDayTotalMinutes(i)"
      :daily-plan="daily"
      :expanded="editor.expandedDayIndex === i + 1"
      :is-only="(draft.dailyPlans?.length ?? 0) === 1"
      :warnings="resolution?.days[i]?.warnings ?? []"
      @toggle-expand="editor.toggleExpand(i + 1)"
      @change-target="(id: string) => changeTarget(i, id)"
      @remove-via="(viaIndex: number) => removeVia(i, viaIndex)"
      @reorder-via="(from: number, to: number) => reorderVia(i, from, to)"
      @remove-day="removeDay(i)"
    />

    <NButton dashed block @click="addDay">+ 加一天</NButton>

    <div v-if="resolution?.warnings.length" class="text-xs text-red-600 mt-2">
      ⚠ {{ resolution.warnings.join(', ') }}
    </div>
  </div>
</template>
