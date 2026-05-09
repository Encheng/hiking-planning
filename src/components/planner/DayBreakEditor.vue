<script setup lang="ts">
import { computed } from 'vue';
import { NCard, NSelect, NSpace, NButton, NTag } from 'naive-ui';
import { usePlanStore } from '@/stores/planStore';
import { useRoutesStore } from '@/stores/routesStore';

const planStore = usePlanStore();
const routesStore = useRoutesStore();

const route = computed(() => {
  if (!planStore.currentPlan) return null;
  return routesStore.getById(planStore.currentPlan.routeId) ?? null;
});

const nodeOptions = computed(() => {
  if (!route.value || !planStore.currentPlan) return [];
  return planStore.currentPlan.nodeSequence
    .map((id, idx) => {
      const n = route.value!.nodes.find((x) => x.id === id);
      return n ? { label: `${idx + 1}. ${n.name}`, value: n.id } : null;
    })
    .filter((x): x is { label: string; value: string } => x !== null);
});

function changeBreak(idx: number, newNodeId: string) {
  if (!planStore.currentPlan) return;
  const node = route.value?.nodes.find((n) => n.id === newNodeId);
  planStore.currentPlan.dayBreaks[idx] = {
    afterNodeId: newNodeId,
    type: node?.hutId ? 'hut' : 'manual',
    hutId: node?.hutId ?? undefined,
  };
  planStore.refreshTripType();
}

async function applyAuto() {
  planStore.autoSuggestDayBreaks();
  if (planStore.currentPlan) await planStore.savePlan(planStore.currentPlan);
}
</script>

<template>
  <NCard v-if="planStore.currentPlan && planStore.currentPlan.dayBreaks.length > 0" title="多日切點">
    <NSpace vertical size="small">
      <div v-for="(brk, idx) in planStore.currentPlan.dayBreaks" :key="idx" class="flex items-center gap-2">
        <NTag :type="brk.type === 'hut' ? 'warning' : 'default'">第 {{ idx + 1 }} 晚</NTag>
        <NSelect
          :value="brk.afterNodeId"
          :options="nodeOptions"
          @update:value="(v: string) => changeBreak(idx, v)"
          style="flex: 1"
        />
      </div>
      <NButton size="small" @click="applyAuto">重新自動建議</NButton>
    </NSpace>
  </NCard>
</template>
