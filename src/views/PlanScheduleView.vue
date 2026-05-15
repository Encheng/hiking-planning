<script setup lang="ts">
import { computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { NCard, NButton, NSpace, NSpin, NTabs, NTabPane, NDropdown } from 'naive-ui';
import AppIcon from '@/components/common/AppIcon.vue';
import TableView from '@/components/schedule/TableView.vue';
import GanttView from '@/components/schedule/GanttView.vue';
import ElevationView from '@/components/schedule/ElevationView.vue';
import PrintLayout from '@/components/schedule/PrintLayout.vue';
import TripTypeBadge from '@/components/common/TripTypeBadge.vue';
import VerificationBanner from '@/components/common/VerificationBanner.vue';
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

import type { TripType } from '@/types';
async function onTripTypeUpdate(tripType: TripType, customLabel?: string) {
  if (!planStore.currentPlan) return;
  const updated = JSON.parse(JSON.stringify(planStore.currentPlan));
  updated.tripType = tripType;
  updated.customTripTypeLabel = customLabel ?? undefined;
  updated.tripTypeOverridden = true;
  await planStore.savePlan(updated);
  planStore.currentPlan = updated;
}
async function onTripTypeReset() {
  if (!planStore.currentPlan) return;
  const updated = JSON.parse(JSON.stringify(planStore.currentPlan));
  updated.customTripTypeLabel = undefined;
  updated.tripTypeOverridden = false;
  // Re-run classifier
  await planStore.savePlan(updated);
  planStore.currentPlan = updated;
  planStore.refreshTripType('current');
  // Save again with auto-classified type
  if (planStore.currentPlan) await planStore.savePlan(planStore.currentPlan);
}

// "More" menu (3-dot) — keeps non-primary actions out of the way on mobile
const moreMenuOptions = computed(() => [
  { key: 'gear', label: '裝備清單' },
  { key: 'print', label: '列印', disabled: !printReady.value },
]);
function onMoreMenuSelect(key: string) {
  if (!plan.value) return;
  if (key === 'gear') router.push({ name: 'gear', params: { planId: plan.value.id } });
  if (key === 'print') printPage();
}
</script>

<template>
  <div class="schedule-page p-6 max-w-5xl mx-auto">
    <NSpin :show="!plan">
      <template v-if="plan && route">
        <div class="screen-only">
          <header class="mb-4 flex justify-between items-start gap-3 flex-wrap">
            <div class="min-w-0 flex-1">
              <h1 class="text-xl sm:text-2xl font-bold text-brand-900 break-words">{{ plan.name }}</h1>
              <NSpace size="small" class="mt-2" :wrap="true">
                <TripTypeBadge
                  :trip-type="plan.tripType"
                  :custom-label="plan.customTripTypeLabel"
                  editable
                  @update="onTripTypeUpdate"
                  @reset="onTripTypeReset"
                />
                <span class="text-sm text-brand-gray">
                  {{ plan.startDate }} {{ plan.startTime }} 出發 · 倍率 {{ plan.paceMultiplier }}x
                </span>
              </NSpace>
            </div>
            <!-- Primary actions (always visible) + overflow menu -->
            <div class="flex gap-2 flex-shrink-0">
              <NButton @click="editPlan">編輯行程</NButton>
              <NButton type="primary" @click="router.push({ name: 'checklist', params: { planId: plan.id } })">
                行前準備
              </NButton>
              <NDropdown
                trigger="click"
                placement="bottom-end"
                :options="moreMenuOptions"
                @select="onMoreMenuSelect"
              >
                <NButton aria-label="更多動作">
                  <template #icon>
                    <AppIcon name="more-vertical" :size="18" />
                  </template>
                </NButton>
              </NDropdown>
            </div>
          </header>

          <NSpace vertical size="large">
            <VerificationBanner :route-id="plan.routeId" />
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
