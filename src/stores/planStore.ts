import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { db } from '@/db';
import type { Plan, SegmentTime, TripType } from '@/types';
import { calculateTimes } from '@/services/TimeCalculator';
import { suggestBreaks } from '@/services/DayBreaker';
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
    if (plan.id) {
      await db.plans.put(plan);
      return plan.id;
    }
    return (await db.plans.add({ ...plan, createdAt: plan.createdAt ?? new Date().toISOString() })) as number;
  }

  async function deletePlan(id: number) {
    await db.plans.delete(id);
    await loadAllPlans();
  }

  const computedTimes = computed<SegmentTime[]>(() => {
    if (!currentPlan.value) return [];
    const routesStore = useRoutesStore();
    const route = routesStore.getById(currentPlan.value.routeId);
    if (!route) return [];
    try {
      return calculateTimes({
        route,
        nodeSequence: currentPlan.value.nodeSequence,
        paceMultiplier: currentPlan.value.paceMultiplier,
        startDateTime: `${currentPlan.value.startDate}T${currentPlan.value.startTime}:00`,
      }).segments;
    } catch {
      return [];
    }
  });

  function autoSuggestDayBreaks(): void {
    if (!currentPlan.value) return;
    const routesStore = useRoutesStore();
    const route = routesStore.getById(currentPlan.value.routeId);
    if (!route) return;
    const segments = computedTimes.value;
    const breaks = suggestBreaks({
      route, segments, huts: routesStore.huts,
      maxDailyHours: 8, preferredBreakType: 'auto',
    });
    currentPlan.value.dayBreaks = breaks;
    refreshTripType();
  }

  function refreshTripType() {
    if (!currentPlan.value) return;
    const totalMins = computedTimes.value.reduce((s, x) => s + x.adjustedMinutes, 0);
    const hasOvernight = currentPlan.value.dayBreaks.length > 0;
    const hasCamping = currentPlan.value.dayBreaks.some((b) => b.type === 'camp');
    const tripType: TripType = classifyTripType({
      totalHours: totalMins / 60, hasOvernight, hasCamping,
    });
    currentPlan.value.tripType = tripType;
  }

  return {
    draft, plans, currentPlan, computedTimes,
    loadAllPlans, loadPlan, savePlan, deletePlan,
    autoSuggestDayBreaks, refreshTripType,
  };
});
