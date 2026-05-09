<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { NCard, NButton, NSpace, NTag } from 'naive-ui';
import { useRoutesStore } from '@/stores/routesStore';
import { usePlanStore } from '@/stores/planStore';
import { useSettingsStore } from '@/stores/settingsStore';
import type { Route, RoutePreset, DailyPlan } from '@/types';

const routesStore = useRoutesStore();
const planStore = usePlanStore();
const settings = useSettingsStore();
const router = useRouter();

const routes = computed(() => routesStore.routes);

function derivePresetDailyPlans(preset: RoutePreset, route: Route): DailyPlan[] {
  const breaks = preset.suggestedDayBreaks ?? [];
  if (breaks.length === 0) {
    return [{
      endNodeId: preset.endNodeId,
      endType: 'manual',
      viaNodeIds: preset.viaNodeIds ?? [],
    }];
  }
  const days: DailyPlan[] = breaks.map((b) => ({
    endNodeId: b.atNodeId,
    endType: b.type,
    hutId: route.nodes.find((n) => n.id === b.atNodeId)?.hutId ?? undefined,
    viaNodeIds: [],
  }));
  const usedVias = new Set(breaks.map((b) => b.atNodeId));
  const remainingVias = (preset.viaNodeIds ?? []).filter((v) => !usedVias.has(v));
  days.push({
    endNodeId: preset.endNodeId,
    endType: 'manual',
    viaNodeIds: remainingVias,
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
    returnToStart: true,
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
