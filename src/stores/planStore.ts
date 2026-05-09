import { defineStore } from 'pinia';
import { ref, computed, toRaw } from 'vue';
import { db } from '@/db';
import type { Plan, SegmentTime, TripType } from '@/types';
import { calculateTimes } from '@/services/TimeCalculator';
import { resolveDailyPlans } from '@/services/DailyPlanResolver';
import { useRoutesStore } from './routesStore';
import { classifyTripType } from '@/services/GearSuggester';

export const usePlanStore = defineStore('plan', () => {
  const draft = ref<Partial<Plan> | null>(null);
  const plans = ref<Plan[]>([]);
  const currentPlan = ref<Plan | null>(null);

  async function loadAllPlans() {
    plans.value = await db.plans.orderBy('createdAt').reverse().toArray();
  }

  async function loadPlan(id: number) {
    currentPlan.value = (await db.plans.get(id)) ?? null;
  }

  async function savePlan(plan: Plan): Promise<number> {
    const raw = JSON.parse(JSON.stringify(toRaw(plan)));
    if (plan.id) {
      await db.plans.put(raw);
      return plan.id;
    }
    return (await db.plans.add({ ...raw, createdAt: raw.createdAt ?? new Date().toISOString() })) as number;
  }

  async function deletePlan(id: number) {
    await db.plans.delete(id);
    await loadAllPlans();
  }

  const draftResolution = computed(() => {
    if (!draft.value || !draft.value.routeId || !draft.value.startNodeId) return null;
    const routesStore = useRoutesStore();
    const route = routesStore.getById(draft.value.routeId);
    if (!route) return null;
    return resolveDailyPlans({
      route,
      startNodeId: draft.value.startNodeId,
      dailyPlans: draft.value.dailyPlans ?? [],
      returnToStart: draft.value.returnToStart ?? true,
    });
  });

  const currentResolution = computed(() => {
    if (!currentPlan.value) return null;
    const routesStore = useRoutesStore();
    const route = routesStore.getById(currentPlan.value.routeId);
    if (!route) return null;
    return resolveDailyPlans({
      route,
      startNodeId: currentPlan.value.startNodeId,
      dailyPlans: currentPlan.value.dailyPlans ?? [],
      returnToStart: currentPlan.value.returnToStart ?? true,
    });
  });

  const computedTimes = computed<SegmentTime[]>(() => {
    if (!currentPlan.value) return [];
    const routesStore = useRoutesStore();
    const route = routesStore.getById(currentPlan.value.routeId);
    if (!route) return [];
    const sequence = (currentResolution.value?.nodeSequence?.length ?? 0) > 0
      ? currentResolution.value!.nodeSequence
      : currentPlan.value.nodeSequence;
    if (sequence.length < 2) return [];
    try {
      return calculateTimes({
        route,
        nodeSequence: sequence,
        paceMultiplier: currentPlan.value.paceMultiplier,
        startDateTime: `${currentPlan.value.startDate}T${currentPlan.value.startTime}:00`,
      }).segments;
    } catch {
      return [];
    }
  });

  function refreshTripType(target: 'draft' | 'current') {
    const plan = target === 'draft' ? draft.value : currentPlan.value;
    if (!plan) return;
    const dailyPlans = plan.dailyPlans ?? [];
    const totalMins = (target === 'current' ? computedTimes.value : []).reduce((s, x) => s + x.adjustedMinutes, 0);
    const hasOvernight = dailyPlans.length > 1;
    const hasCamping = dailyPlans.some((d) => d.endType === 'camp');
    const tripType: TripType = classifyTripType({
      totalHours: totalMins / 60,
      hasOvernight,
      hasCamping,
    });
    plan.tripType = tripType;
  }

  return {
    draft, plans, currentPlan, computedTimes,
    draftResolution, currentResolution,
    loadAllPlans, loadPlan, savePlan, deletePlan,
    refreshTripType,
  };
});
