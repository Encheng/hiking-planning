<script setup lang="ts">
import { computed, onMounted, watch, toRaw } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { NButton, NCard, NSpace, NTag, useMessage } from 'naive-ui';
import MapCanvas from '@/components/map/MapCanvas.vue';
import TileSwitcher from '@/components/map/TileSwitcher.vue';
import GpxLayer from '@/components/map/GpxLayer.vue';
import NodeMarkerLayer from '@/components/map/NodeMarkerLayer.vue';
import PlanForm from '@/components/planner/PlanForm.vue';
import PathPreview from '@/components/planner/PathPreview.vue';
import { useRoutesStore } from '@/stores/routesStore';
import { useMapStore } from '@/stores/mapStore';
import { usePlanStore } from '@/stores/planStore';
import { useSettingsStore } from '@/stores/settingsStore';
import { resolvePath } from '@/services/PathResolver';

const route = useRoute();
const router = useRouter();
const message = useMessage();
const routesStore = useRoutesStore();
const mapStore = useMapStore();
const planStore = usePlanStore();
const settings = useSettingsStore();

const routeId = computed(() => (route.query.route as string) ?? 'G02');
const currentRoute = computed(() => routesStore.getById(routeId.value));
const startNode = computed(() => currentRoute.value?.nodes.find((n) => n.id === mapStore.selectedStartId));
const endNode = computed(() => currentRoute.value?.nodes.find((n) => n.id === mapStore.selectedEndId));

const resolvedPath = computed(() => {
  if (!currentRoute.value || !mapStore.selectedStartId || !mapStore.selectedEndId) return null;
  return resolvePath({
    route: currentRoute.value,
    startNodeId: mapStore.selectedStartId,
    endNodeId: mapStore.selectedEndId,
  });
});

onMounted(() => {
  if (!currentRoute.value) message.error(`找不到路線 ${routeId.value}`);
});

async function savePlan() {
  if (!currentRoute.value || !mapStore.selectedStartId || !mapStore.selectedEndId || !resolvedPath.value) {
    message.error('請先選擇起點與終點');
    return;
  }
  const today = new Date().toISOString().slice(0, 10);
  const draft = planStore.draft ?? {};
  const id = await planStore.savePlan({
    name: `${startNode.value?.name} → ${endNode.value?.name}`,
    routeId: routeId.value,
    startNodeId: mapStore.selectedStartId,
    endNodeId: mapStore.selectedEndId,
    nodeSequence: toRaw(resolvedPath.value.combined),
    paceMultiplier: draft.paceMultiplier ?? settings.defaultPaceMultiplier,
    startDate: draft.startDate ?? today,
    startTime: draft.startTime ?? '06:00',
    dayBreaks: [],
    tripType: 'overnight_hut',
    createdAt: new Date().toISOString(),
  });
  await planStore.loadPlan(id);
  planStore.autoSuggestDayBreaks();
  await planStore.savePlan(planStore.currentPlan!);
  planStore.draft = null;
  router.push({ name: 'schedule', params: { planId: id } });
}

const center = computed<[number, number]>(() => {
  const nodes = currentRoute.value?.nodes ?? [];
  if (nodes.length === 0) return [23.5, 121];
  const sumLat = nodes.reduce((s, n) => s + n.lat, 0);
  const sumLng = nodes.reduce((s, n) => s + n.lng, 0);
  return [sumLat / nodes.length, sumLng / nodes.length];
});

watch(routeId, () => mapStore.reset());
</script>

<template>
  <div class="flex h-[calc(100vh-65px)]">
    <div class="flex-1 relative">
      <MapCanvas v-if="currentRoute" :center="center" :zoom="13">
        <TileSwitcher />
        <GpxLayer :url="`/data/gpx/${currentRoute.id}-sample.gpx`" />
        <NodeMarkerLayer :nodes="currentRoute.nodes" />
      </MapCanvas>
    </div>
    <aside class="w-96 border-l bg-white overflow-auto p-4">
      <NSpace vertical size="large">
        <NCard title="路線">
          <p class="text-sm">{{ currentRoute?.name }}</p>
        </NCard>
        <NCard title="起終點">
          <NSpace vertical size="small">
            <div>
              <NTag type="success">起</NTag>
              <span class="ml-2">{{ startNode?.name ?? '請點選起點 pin' }}</span>
            </div>
            <div>
              <NTag type="error">終</NTag>
              <span class="ml-2">{{ endNode?.name ?? '請點選終點 pin' }}</span>
            </div>
            <NButton size="small" @click="mapStore.reset()">清除</NButton>
          </NSpace>
        </NCard>
        <PathPreview v-if="resolvedPath && currentRoute" :path="resolvedPath" :route="currentRoute" />
        <PlanForm v-if="resolvedPath" />
        <NButton type="primary" block size="large" :disabled="!resolvedPath" @click="savePlan">
          儲存行程
        </NButton>
      </NSpace>
    </aside>
  </div>
</template>
