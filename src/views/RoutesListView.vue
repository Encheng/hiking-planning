<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { NCard, NButton, NSpace, NTag } from 'naive-ui';
import { useRoutesStore } from '@/stores/routesStore';
import { useMapStore } from '@/stores/mapStore';
import { usePlanStore } from '@/stores/planStore';
import { useSettingsStore } from '@/stores/settingsStore';

const routesStore = useRoutesStore();
const mapStore = useMapStore();
const planStore = usePlanStore();
const settings = useSettingsStore();
const router = useRouter();

const routes = computed(() => routesStore.routes);

function openInPlanner(routeId: string) {
  mapStore.reset();
  router.push({ name: 'map', query: { route: routeId } });
}

function applyPreset(routeId: string, presetId: string) {
  const route = routesStore.getById(routeId);
  if (!route) return;
  const preset = route.presets.find((p) => p.id === presetId);
  if (!preset) return;
  mapStore.selectedStartId = preset.startNodeId;
  mapStore.selectedEndId = preset.endNodeId;
  planStore.draft = {
    routeId,
    startNodeId: preset.startNodeId,
    endNodeId: preset.endNodeId,
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
