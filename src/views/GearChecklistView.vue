<script setup lang="ts">
import { onMounted, watch, computed } from 'vue';
import { NSpace, NSpin, NCard, NButton } from 'naive-ui';
import GearChecklist from '@/components/gear/GearChecklist.vue';
import CustomItemForm from '@/components/gear/CustomItemForm.vue';
import TripTypeBadge from '@/components/common/TripTypeBadge.vue';
import { usePlanStore } from '@/stores/planStore';
import { useGearStore } from '@/stores/gearStore';
import { useRouter } from 'vue-router';

const props = defineProps<{ planId: string }>();
const router = useRouter();
const planStore = usePlanStore();
const gearStore = useGearStore();

async function refresh() {
  const id = Number(props.planId);
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

onMounted(refresh);
watch(() => props.planId, refresh);

const plan = computed(() => planStore.currentPlan);
</script>

<template>
  <div class="p-6 max-w-3xl mx-auto">
    <NSpin :show="!plan || !gearStore.suggestion">
      <template v-if="plan">
        <header class="mb-4 flex justify-between">
          <div>
            <h1 class="text-2xl font-bold">{{ plan.name }} - 裝備清單</h1>
            <TripTypeBadge :trip-type="plan.tripType" :custom-label="plan.customTripTypeLabel" class="mt-2" />
          </div>
          <NButton @click="router.push({ name: 'schedule', params: { planId: plan.id } })">回行程表</NButton>
        </header>
        <NSpace vertical size="large">
          <NCard title="清單">
            <GearChecklist />
          </NCard>
          <CustomItemForm />
        </NSpace>
      </template>
    </NSpin>
  </div>
</template>
