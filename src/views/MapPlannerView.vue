<script setup lang="ts">
import { computed, onMounted, ref, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { NButton, NCard, NSpace, useMessage } from 'naive-ui';
import L from 'leaflet';
import MapCanvas from '@/components/map/MapCanvas.vue';
import TileSwitcher from '@/components/map/TileSwitcher.vue';
import GpxLayer from '@/components/map/GpxLayer.vue';
import NodeMarkerLayer from '@/components/map/NodeMarkerLayer.vue';
import DailyPlanEditor from '@/components/planner/DailyPlanEditor.vue';
import MapNodePopup from '@/components/planner/MapNodePopup.vue';
import { useRoutesStore } from '@/stores/routesStore';
import { usePlanStore } from '@/stores/planStore';
import { useSettingsStore } from '@/stores/settingsStore';
import { useDailyEditorStore } from '@/stores/dailyEditorStore';
import { resolveDailyPlans } from '@/services/DailyPlanResolver';
import type { RouteNode } from '@/types';

const route = useRoute();
const router = useRouter();
const message = useMessage();
const routesStore = useRoutesStore();
const planStore = usePlanStore();
const settings = useSettingsStore();
const editor = useDailyEditorStore();

const routeId = computed(() => (route.query.route as string) ?? 'G02');
const currentRoute = computed(() => routesStore.getById(routeId.value));

const popupNode = ref<RouteNode | null>(null);
const popupOpen = ref(false);
const popupContainerId = 'map-node-popup-mount';
let activeLeafletPopup: L.Popup | null = null;

const resolution = computed(() => {
  if (!currentRoute.value || !planStore.draft || !planStore.draft.startNodeId) return null;
  return resolveDailyPlans({
    route: currentRoute.value,
    startNodeId: planStore.draft.startNodeId,
    dailyPlans: planStore.draft.dailyPlans ?? [],
    returnToStart: planStore.draft.returnToStart ?? true,
  });
});

const highlightedNodeIds = computed(() => resolution.value?.nodeSequence ?? []);

const canSave = computed(() => {
  if (!planStore.draft || !planStore.draft.startNodeId) return false;
  if ((planStore.draft.dailyPlans?.length ?? 0) === 0) return false;
  if ((planStore.draft.dailyPlans ?? []).some((d) => !d.endNodeId)) return false;
  if ((resolution.value?.warnings.length ?? 0) > 0) return false;
  return true;
});

onMounted(() => {
  if (!currentRoute.value) {
    message.error(`找不到路線 ${routeId.value}`);
    return;
  }
  if (!planStore.draft || planStore.draft.routeId !== routeId.value) {
    planStore.draft = {
      routeId: routeId.value,
      startNodeId: currentRoute.value.nodes[0]?.id ?? '',
      returnToStart: true,
      dailyPlans: [],
      paceMultiplier: settings.defaultPaceMultiplier,
    };
  }
});

const center = computed<[number, number]>(() => {
  const nodes = currentRoute.value?.nodes ?? [];
  if (nodes.length === 0) return [23.5, 121];
  const sumLat = nodes.reduce((s, n) => s + n.lat, 0);
  const sumLng = nodes.reduce((s, n) => s + n.lng, 0);
  return [sumLat / nodes.length, sumLng / nodes.length];
});

function onNodeClick({ node, latlng }: { node: RouteNode; latlng: L.LatLng }) {
  popupNode.value = node;
  // Create the Leaflet popup first so #map-node-popup-mount exists in the DOM,
  // then set popupOpen so Teleport has a valid target to mount into.
  const map = (window as unknown as { __leafletMap?: L.Map }).__leafletMap;
  if (!map) return;
  activeLeafletPopup?.remove();
  activeLeafletPopup = L.popup({ closeButton: true, autoClose: false })
    .setLatLng(latlng)
    .setContent(`<div id="${popupContainerId}"></div>`)
    .openOn(map);
  activeLeafletPopup.on('remove', () => {
    popupOpen.value = false;
    popupNode.value = null;
  });
  // Wait one tick for Leaflet to inject the popup HTML into the DOM,
  // then let Vue mount the Teleport into #map-node-popup-mount.
  nextTick(() => {
    popupOpen.value = true;
  });
}

function onPopupSetTarget() {
  if (!popupNode.value || editor.expandedDayIndex === null) return;
  const idx = editor.expandedDayIndex - 1;
  const dailyPlans = planStore.draft?.dailyPlans;
  if (!dailyPlans || !dailyPlans[idx]) return;
  dailyPlans[idx].endNodeId = popupNode.value.id;
  closePopup();
}

function onPopupAddVia() {
  if (!popupNode.value || editor.expandedDayIndex === null) return;
  const idx = editor.expandedDayIndex - 1;
  const dailyPlans = planStore.draft?.dailyPlans;
  if (!dailyPlans || !dailyPlans[idx]) return;
  if (!dailyPlans[idx].viaNodeIds.includes(popupNode.value.id)) {
    dailyPlans[idx].viaNodeIds.push(popupNode.value.id);
  }
  closePopup();
}

function closePopup() {
  activeLeafletPopup?.remove();
  popupOpen.value = false;
  popupNode.value = null;
}

function nodeName(id: string | undefined): string {
  if (!id) return '';
  return currentRoute.value?.nodes.find((n) => n.id === id)?.name ?? id;
}

async function savePlan() {
  if (!currentRoute.value || !planStore.draft || !canSave.value || !resolution.value) {
    message.error('請完成行程規劃（至少設定一天的目標）');
    return;
  }
  const today = new Date().toISOString().slice(0, 10);
  const draft = planStore.draft;
  const lastDay = draft.dailyPlans![draft.dailyPlans!.length - 1];
  const finalEndNodeId = draft.returnToStart && lastDay.endNodeId !== draft.startNodeId
    ? draft.startNodeId!
    : lastDay.endNodeId;
  const dailyPlans = JSON.parse(JSON.stringify(draft.dailyPlans));
  const totalMins = estimateTotalMinutes(resolution.value.nodeSequence);
  const hasOvernight = dailyPlans.length > 1;
  const hasCamping = dailyPlans.some((d: { endType: string }) => d.endType === 'camp');
  const tripType = hasCamping ? 'overnight_camp'
    : hasOvernight ? 'overnight_hut'
    : totalMins / 60 > 4 ? 'long_day' : 'light_summit';

  const id = await planStore.savePlan({
    name: `${nodeName(draft.startNodeId!)} → ${nodeName(lastDay.endNodeId)}`,
    routeId: routeId.value,
    startNodeId: draft.startNodeId!,
    endNodeId: finalEndNodeId,
    nodeSequence: resolution.value.nodeSequence,
    paceMultiplier: draft.paceMultiplier ?? settings.defaultPaceMultiplier,
    startDate: draft.startDate ?? today,
    startTime: draft.startTime ?? '06:00',
    dayBreaks: resolution.value.dayBreaks,
    tripType,
    createdAt: new Date().toISOString(),
    dailyPlans,
    returnToStart: draft.returnToStart ?? true,
  });
  router.push({ name: 'schedule', params: { planId: id } });
}

function estimateTotalMinutes(nodeIds: string[]): number {
  if (!currentRoute.value || nodeIds.length < 2) return 0;
  let total = 0;
  for (let i = 0; i < nodeIds.length - 1; i++) {
    const edge = currentRoute.value.edges.find(
      (e) => (e.from === nodeIds[i] && e.to === nodeIds[i + 1]) ||
             (e.from === nodeIds[i + 1] && e.to === nodeIds[i]),
    );
    if (!edge) continue;
    total += edge.from === nodeIds[i] ? edge.minutes_forward : edge.minutes_backward;
  }
  return Math.round(total * (planStore.draft?.paceMultiplier ?? 1));
}

watch(routeId, () => {
  editor.reset();
  closePopup();
});
</script>

<template>
  <div class="flex h-[calc(100vh-65px)]">
    <div class="flex-1 relative">
      <MapCanvas v-if="currentRoute" :center="center" :zoom="13">
        <TileSwitcher />
        <GpxLayer :url="`/data/gpx/${currentRoute.id}-sample.gpx`" />
        <NodeMarkerLayer
          :nodes="currentRoute.nodes"
          :highlighted-node-ids="highlightedNodeIds"
          @node-click="onNodeClick"
        />
      </MapCanvas>
      <Teleport :to="`#${popupContainerId}`" v-if="popupOpen && popupNode">
        <MapNodePopup
          :node="popupNode"
          :expanded-day-index="editor.expandedDayIndex"
          @set-target="onPopupSetTarget"
          @add-via="onPopupAddVia"
        />
      </Teleport>
    </div>

    <aside class="w-[420px] border-l bg-white overflow-auto p-4">
      <NSpace vertical size="medium">
        <NCard size="small" title="行程編輯">
          <DailyPlanEditor v-if="planStore.draft" />
        </NCard>
        <NButton type="primary" block size="large" :disabled="!canSave" @click="savePlan">
          儲存行程
        </NButton>
      </NSpace>
    </aside>
  </div>
</template>
