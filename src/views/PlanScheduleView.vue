<script setup lang="ts">
import { computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { NCard, NButton, NSpace, NSpin } from 'naive-ui';
import TableView from '@/components/schedule/TableView.vue';
import DayBreakEditor from '@/components/planner/DayBreakEditor.vue';
import TripTypeBadge from '@/components/common/TripTypeBadge.vue';
import { usePlanStore } from '@/stores/planStore';

const props = defineProps<{ planId: string }>();
const planStore = usePlanStore();
const router = useRouter();

onMounted(async () => {
  await planStore.loadPlan(Number(props.planId));
});

watch(() => props.planId, async (id) => {
  await planStore.loadPlan(Number(id));
});

const plan = computed(() => planStore.currentPlan);

function printPage() {
  window.print();
}
</script>

<template>
  <div class="p-6 max-w-5xl mx-auto">
    <NSpin :show="!plan">
      <template v-if="plan">
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
            <NButton @click="router.push({ name: 'gear', params: { planId: plan.id } })">裝備清單</NButton>
            <NButton @click="printPage">列印</NButton>
          </NSpace>
        </header>

        <NSpace vertical size="large">
          <DayBreakEditor />
          <NCard title="行程時刻表 (V2)">
            <TableView :plan="plan" :segments="planStore.computedTimes" />
          </NCard>
        </NSpace>
      </template>
    </NSpin>
  </div>
</template>
