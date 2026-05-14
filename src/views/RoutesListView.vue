<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { NCard, NButton, NSpace, NTag } from 'naive-ui';
import { useRoutesStore } from '@/stores/routesStore';
import { usePlanStore } from '@/stores/planStore';
import { useSettingsStore } from '@/stores/settingsStore';
import type { Route, RoutePreset, DailyPlan } from '@/types';
import { resolvePath } from '@/services/PathResolver';

const routesStore = useRoutesStore();
const planStore = usePlanStore();
const settings = useSettingsStore();
const router = useRouter();

const routes = computed(() => routesStore.routes);

function derivePresetDailyPlans(preset: RoutePreset, route: Route): DailyPlan[] {
  function autoVia(start: string, end: string): string[] {
    if (!start || !end || start === end) return [];
    const p = resolvePath({ route, startNodeId: start, endNodeId: end, viaNodeIds: [] });
    if (p.warnings.includes('no_path') || p.forward.length < 2) return [];
    return p.forward.slice(1, -1);
  }

  const breaks = preset.suggestedDayBreaks ?? [];

  // Single-day plan (no break) — leave endNodeId as the user's destination.
  // If preset.roundTrip is true, DailyPlanResolver will append the return path.
  if (breaks.length === 0) {
    return [{
      endNodeId: preset.endNodeId,
      endType: 'manual',
      viaNodeIds: autoVia(preset.startNodeId, preset.endNodeId),
    }];
  }

  // Multi-day with breaks
  const days: DailyPlan[] = [];
  let prevEnd = preset.startNodeId;
  for (const b of breaks) {
    days.push({
      endNodeId: b.atNodeId,
      endType: b.type,
      hutId: route.nodes.find((n) => n.id === b.atNodeId)?.hutId ?? undefined,
      viaNodeIds: autoVia(prevEnd, b.atNodeId),
    });
    prevEnd = b.atNodeId;
  }

  // Last day ends at the preset's endNodeId. Resolver handles return when roundTrip is true.
  days.push({
    endNodeId: preset.endNodeId,
    endType: 'manual',
    viaNodeIds: autoVia(prevEnd, preset.endNodeId),
  });

  return days;
}

function openInPlanner(routeId: string) {
  const route = routesStore.getById(routeId);
  if (!route) return;
  planStore.draft = {
    routeId,
    startNodeId: route.nodes[0]?.id ?? '',
    returnToStart: true,
    dailyPlans: [],
    paceMultiplier: settings.defaultPaceMultiplier,
  };
  router.push({ name: 'map', query: { route: routeId } });
}

function applyPreset(routeId: string, presetId: string) {
  const route = routesStore.getById(routeId);
  if (!route) return;
  const preset = route.presets.find((p) => p.id === presetId);
  if (!preset) return;
  planStore.draft = {
    routeId,
    startNodeId: preset.startNodeId,
    returnToStart: preset.roundTrip !== false,
    dailyPlans: derivePresetDailyPlans(preset, route),
    paceMultiplier: settings.defaultPaceMultiplier,
  };
  router.push({ name: 'map', query: { route: routeId, preset: presetId } });
}
</script>

<template>
  <div class="p-6 max-w-5xl mx-auto">
    <h1 class="text-2xl font-bold mb-4">百岳路線</h1>
    <NSpace vertical size="large">
      <NCard v-for="route in routes" :key="route.id" :title="route.name">
        <template #header-extra>
          <NTag type="success">{{ route.id }}</NTag>
        </template>
        <p class="text-sm text-gray-500 mb-3">{{ route.source }}</p>
        <NSpace>
          <NButton type="primary" @click="openInPlanner(route.id)">在地圖上規劃</NButton>
          <NButton
            v-for="preset in route.presets"
            :key="preset.id"
            secondary
            @click="applyPreset(route.id, preset.id)"
          >
            預設 · {{ preset.name }}
          </NButton>
        </NSpace>
      </NCard>
    </NSpace>
  </div>
</template>
