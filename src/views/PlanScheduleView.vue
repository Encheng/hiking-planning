<script setup lang="ts">
import { computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { NCard, NButton, NSpace, NSpin, NTabs, NTabPane } from 'naive-ui';
import TableView from '@/components/schedule/TableView.vue';
import GanttView from '@/components/schedule/GanttView.vue';
import ElevationView from '@/components/schedule/ElevationView.vue';
import PrintLayout from '@/components/schedule/PrintLayout.vue';
import TripTypeBadge from '@/components/common/TripTypeBadge.vue';
import { usePlanStore } from '@/stores/planStore';
import { useRoutesStore } from '@/stores/routesStore';
import { useGearStore } from '@/stores/gearStore';

const props = defineProps<{ planId: string }>();
const planStore = usePlanStore();
const routesStore = useRoutesStore();
const gearStore = useGearStore();
const router = useRouter();

async function loadAll(id: number) {
  await planStore.loadPlan(id);
  if (!planStore.currentPlan) return;
  await gearStore.loadChecklist(id);
  const totalMins = planStore.computedTimes.reduce((s, x) => s + x.adjustedMinutes, 0);
  const dailyPlans = planStore.currentPlan.dailyPlans ?? [];
  const hasOvernight = dailyPlans.length > 1;
  const hasCamping = dailyPlans.some((d) => d.endType === 'camp');
  const lastPlanId = await gearStore.findLastPlanIdOfType(planStore.currentPlan.tripType, id);
  await gearStore.refreshSuggestion({
    totalHours: totalMins / 60,
    hasOvernight,
    hasCamping,
    lastPlanId,
  });
}

onMounted(() => loadAll(Number(props.planId)));
watch(() => props.planId, (id) => loadAll(Number(id)));

const plan = computed(() => planStore.currentPlan);
const route = computed(() => plan.value ? routesStore.getById(plan.value.routeId) ?? null : null);
const printReady = computed(() => !!gearStore.suggestion && !!plan.value && !!route.value);

function printPage() {
  window.print();
}

function editPlan() {
  if (!planStore.currentPlan) return;
  planStore.draft = JSON.parse(JSON.stringify(planStore.currentPlan));
  router.push({ name: 'map', query: { route: planStore.currentPlan.routeId } });
}
</script>

<template>
  <div class="schedule-page p-6 max-w-5xl mx-auto">
    <NSpin :show="!plan">
      <template v-if="plan && route">
        <div class="screen-only">
          <header class="mb-4 flex justify-between items-start">
            <div>
              <h1 class="text-2xl font-bold">{{ plan.name }}</h1>
              <NSpace size="small" class="mt-2">
                <TripTypeBadge :trip-type="plan.tripType" />
                <span class="text-sm text-gray-500">
                  {{ plan.startDate }} {{ plan.startTime }} 出發 · 倍率 {{ plan.paceMultiplier }}x
                </span>
              </NSpace>
            </div>
            <NSpace>
              <NButton @click="editPlan">編輯行程</NButton>
              <NButton @click="router.push({ name: 'gear', params: { planId: plan.id } })">裝備清單</NButton>
              <NButton :disabled="!printReady" @click="printPage">列印</NButton>
            </NSpace>
          </header>

          <NSpace vertical size="large">
            <NCard title="行程時刻表">
              <NTabs default-value="v2" type="line">
                <NTabPane name="v1" tab="V1 Gantt">
                  <GanttView :plan="plan" :segments="planStore.computedTimes" />
                </NTabPane>
                <NTabPane name="v2" tab="V2 表格">
                  <TableView :plan="plan" :segments="planStore.computedTimes" />
                </NTabPane>
                <NTabPane name="v3" tab="V3 海拔">
                  <ElevationView :plan="plan" :segments="planStore.computedTimes" />
                </NTabPane>
              </NTabs>
            </NCard>
          </NSpace>
        </div>

        <PrintLayout
          :plan="plan"
          :route="route"
          :segments="planStore.computedTimes"
          :gear-suggestion="gearStore.suggestion"
        />
      </template>
    </NSpin>
  </div>
</template>
