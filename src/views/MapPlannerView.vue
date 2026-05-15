<script setup lang="ts">
import { computed, onMounted, ref, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { NButton, NCard, NDatePicker, NSpace, NTimePicker, useMessage } from 'naive-ui';
import PaceSlider from '@/components/planner/PaceSlider.vue';
import L from 'leaflet';
import MapCanvas from '@/components/map/MapCanvas.vue';
import TileSwitcher from '@/components/map/TileSwitcher.vue';
import PlannedRouteLayer from '@/components/map/PlannedRouteLayer.vue';
import NodeMarkerLayer from '@/components/map/NodeMarkerLayer.vue';
import DailyPlanEditor from '@/components/planner/DailyPlanEditor.vue';
import MapNodePopup from '@/components/planner/MapNodePopup.vue';
import VerificationBanner from '@/components/common/VerificationBanner.vue';
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
const popupContainerSeq = ref(0);
const popupContainerId = computed(() => `map-node-popup-mount-${popupContainerSeq.value}`);
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
const plannedDayBreaks = computed(() => resolution.value?.dayBreaks ?? []);
// editor.expandedDayIndex is 1-based; PlannedRouteLayer wants 0-based (null = no highlight)
const activeDayIndex = computed(() =>
  editor.expandedDayIndex != null ? editor.expandedDayIndex - 1 : null,
);

const canSave = computed(() => {
  if (!planStore.draft || !planStore.draft.startNodeId) return false;
  if ((planStore.draft.dailyPlans?.length ?? 0) === 0) return false;
  if ((planStore.draft.dailyPlans ?? []).some((d) => !d.endNodeId)) return false;
  if ((resolution.value?.warnings.length ?? 0) > 0) return false;
  return true;
});

// Mobile bottom-drawer state: peek (collapsed) → half (map+edit visible) → full
type DrawerState = 'peek' | 'half' | 'full';
// Default to 'half' on mobile so user sees the editor immediately on entry.
// Desktop layout ignores this state entirely (md+ uses static side-by-side).
const mobileDrawerState = ref<DrawerState>('half');

const DRAWER_LABELS: Record<DrawerState, string> = {
  peek: '收合',
  half: '半開',
  full: '展開',
};
const drawerLabel = computed(() => DRAWER_LABELS[mobileDrawerState.value]);

function cycleDrawerState() {
  const order: DrawerState[] = ['peek', 'half', 'full'];
  const idx = order.indexOf(mobileDrawerState.value);
  mobileDrawerState.value = order[(idx + 1) % order.length];
}

const daySummary = computed(() => {
  const dayCount = planStore.draft?.dailyPlans?.length ?? 0;
  const nodeCount = highlightedNodeIds.value.length;
  if (dayCount === 0) return '尚未規劃';
  return `${dayCount} 天 · ${nodeCount} 節點`;
});

// Auto-open drawer to half when a node is picked from map
watch(() => editor.expandedDayIndex, (v) => {
  if (v != null && mobileDrawerState.value === 'peek') {
    mobileDrawerState.value = 'half';
  }
});

const startDateTs = computed({
  get: () => {
    const date = planStore.draft?.startDate;
    if (!date) return Date.now();
    return new Date(`${date}T00:00:00`).getTime();
  },
  set: (ms: number) => {
    if (!planStore.draft) return;
    planStore.draft.startDate = new Date(ms).toISOString().slice(0, 10);
  },
});

const startTimeTs = computed({
  get: () => {
    const time = planStore.draft?.startTime ?? '06:00';
    const [h, m] = time.split(':').map(Number);
    const d = new Date();
    d.setHours(h, m, 0, 0);
    return d.getTime();
  },
  set: (ms: number) => {
    if (!planStore.draft) return;
    const d = new Date(ms);
    const hh = String(d.getHours()).padStart(2, '0');
    const mm = String(d.getMinutes()).padStart(2, '0');
    planStore.draft.startTime = `${hh}:${mm}`;
  },
});

const paceMultiplier = computed({
  get: () => planStore.draft?.paceMultiplier ?? settings.defaultPaceMultiplier,
  set: (val: number) => {
    if (planStore.draft) planStore.draft.paceMultiplier = val;
  },
});

onMounted(() => {
  if (!currentRoute.value) {
    message.error(`找不到路線 ${routeId.value}`);
    return;
  }
  if (!planStore.draft || planStore.draft.routeId !== routeId.value) {
    const today = new Date().toISOString().slice(0, 10);
    planStore.draft = {
      routeId: routeId.value,
      startNodeId: currentRoute.value.nodes[0]?.id ?? '',
      returnToStart: true,
      dailyPlans: [],
      paceMultiplier: settings.defaultPaceMultiplier,
      startDate: today,
      startTime: '06:00',
    };
  } else {
    // Fill in defaults if missing
    if (!planStore.draft.startDate) planStore.draft.startDate = new Date().toISOString().slice(0, 10);
    if (!planStore.draft.startTime) planStore.draft.startTime = '06:00';
    if (!planStore.draft.paceMultiplier) planStore.draft.paceMultiplier = settings.defaultPaceMultiplier;
  }
});

const center = computed<[number, number]>(() => {
  const nodes = currentRoute.value?.nodes ?? [];
  if (nodes.length === 0) return [23.5, 121];
  const sumLat = nodes.reduce((s, n) => s + n.lat, 0);
  const sumLng = nodes.reduce((s, n) => s + n.lng, 0);
  return [sumLat / nodes.length, sumLng / nodes.length];
});

async function onNodeClick({ node, latlng }: { node: RouteNode; latlng: L.LatLng }) {
  const map = (window as unknown as { __leafletMap?: L.Map }).__leafletMap;
  if (!map) return;

  // 1. Unmount old Teleport state
  popupOpen.value = false;
  popupNode.value = null;

  // 2. Remove old Leaflet popup (without firing handler)
  if (activeLeafletPopup) {
    activeLeafletPopup.off('remove');
    activeLeafletPopup.remove();
    activeLeafletPopup = null;
  }

  await nextTick();

  // 3. Increment counter so new mount div has unique ID
  popupContainerSeq.value++;

  // 4. Create new Leaflet popup with the new ID
  activeLeafletPopup = L.popup({ closeButton: true, autoClose: false, minWidth: 180 })
    .setLatLng(latlng)
    .setContent(`<div id="${popupContainerId.value}"></div>`)
    .openOn(map);
  activeLeafletPopup.on('remove', () => {
    popupOpen.value = false;
    popupNode.value = null;
  });

  await nextTick();

  // 5. Mount new Teleport into the new mount div
  popupNode.value = node;
  popupOpen.value = true;
}

function onPopupSetTarget() {
  if (!popupNode.value || editor.expandedDayIndex === null) return;
  const idx = editor.expandedDayIndex - 1;
  const dailyPlans = planStore.draft?.dailyPlans;
  if (!dailyPlans || !dailyPlans[idx]) return;
  dailyPlans[idx].endNodeId = popupNode.value.id;
  closePopup();
  // On mobile, lift drawer so user can confirm the edit
  if (mobileDrawerState.value === 'peek') mobileDrawerState.value = 'half';
}

function onPopupAddVia() {
  if (!popupNode.value || editor.expandedDayIndex === null) return;
  const idx = editor.expandedDayIndex - 1;
  const dailyPlans = planStore.draft?.dailyPlans;
  if (!dailyPlans || !dailyPlans[idx]) return;
  dailyPlans[idx].viaNodeIds.push(popupNode.value.id);
  closePopup();
  if (mobileDrawerState.value === 'peek') mobileDrawerState.value = 'half';
}

function closePopup() {
  if (activeLeafletPopup) {
    // Detach the remove handler first so it doesn't fire during .remove()
    // and cause a double-reset of popupOpen/popupNode.
    activeLeafletPopup.off('remove');
    activeLeafletPopup.remove();
    activeLeafletPopup = null;
  }
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

  const planPayload: Parameters<typeof planStore.savePlan>[0] = {
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
    createdAt: draft.createdAt ?? new Date().toISOString(),
    dailyPlans,
    returnToStart: draft.returnToStart ?? true,
  };
  if (draft.id) planPayload.id = draft.id;
  const id = await planStore.savePlan(planPayload);
  planStore.draft = null;
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
  <div class="planner-root md:flex md:h-[calc(100vh-65px)]">
    <!-- Map: full-screen on mobile (behind drawer), left pane on desktop -->
    <div class="map-pane relative h-[calc(100vh-65px)] md:flex-1 md:h-auto">
      <MapCanvas v-if="currentRoute" :center="center" :zoom="13">
        <TileSwitcher />
        <PlannedRouteLayer
          :nodes="currentRoute.nodes"
          :node-ids="highlightedNodeIds"
          :day-breaks="plannedDayBreaks"
          :active-day-index="activeDayIndex"
        />
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

    <!-- Sidebar / Bottom drawer -->
    <aside
      class="planner-sidebar bg-brand-white flex flex-col
             md:w-[420px] md:border-l md:border-brand-cream md:static md:rounded-none md:shadow-none md:translate-y-0
             md:overflow-hidden md:h-auto"
      :class="[
        mobileDrawerState === 'full'
          ? 'mobile-drawer-full'
          : mobileDrawerState === 'half'
            ? 'mobile-drawer-half'
            : 'mobile-drawer-peek',
      ]"
      :aria-expanded="mobileDrawerState !== 'peek'"
    >
      <!-- Drawer handle (mobile only). Tap to cycle peek → half → full → peek -->
      <div class="md:hidden flex flex-col items-center pt-2 pb-1 bg-brand-white rounded-t-2xl">
        <span
          class="block w-10 h-1.5 bg-brand-gray/40 rounded-full mb-1"
          aria-hidden="true"
        ></span>
      </div>
      <button
        type="button"
        class="md:hidden flex items-center justify-between gap-3 px-4 pb-3 border-b border-brand-cream w-full bg-brand-white select-none"
        :aria-label="`切換編輯面板 (目前: ${drawerLabel})`"
        @click="cycleDrawerState"
      >
        <span class="font-medium text-brand-900">編輯行程</span>
        <div class="flex items-center gap-2 text-xs text-brand-gray flex-shrink-0">
          <span>{{ daySummary }}</span>
          <span class="text-brand-700" aria-hidden="true">
            {{ mobileDrawerState === 'peek' ? '▲ 展開' : mobileDrawerState === 'half' ? '▲ 全開' : '▼ 收合' }}
          </span>
        </div>
      </button>

      <!-- Scrollable content -->
      <div class="planner-content flex-1 overflow-y-auto overflow-x-hidden p-4 pb-24 md:pb-4">
        <NSpace vertical size="medium">
          <VerificationBanner :route-id="planStore.draft?.routeId" />
          <NCard size="small" title="行程設定">
            <NSpace vertical size="small">
              <div>
                <label class="text-xs text-brand-gray block mb-1">出發日期</label>
                <NDatePicker v-model:value="startDateTs" type="date" style="width: 100%" />
              </div>
              <div>
                <label class="text-xs text-brand-gray block mb-1">出發時間</label>
                <NTimePicker v-model:value="startTimeTs" format="HH:mm" style="width: 100%" />
              </div>
              <div>
                <label class="text-xs text-brand-gray block mb-1">腳程倍率</label>
                <PaceSlider v-model="paceMultiplier" />
              </div>
            </NSpace>
          </NCard>
          <NCard size="small" title="行程編輯">
            <DailyPlanEditor v-if="planStore.draft" />
          </NCard>
          <NButton type="primary" block :disabled="!canSave" @click="savePlan">
            儲存行程
          </NButton>
        </NSpace>
      </div>
    </aside>
  </div>
</template>

<style scoped>
@media (max-width: 767px) {
  .planner-sidebar {
    position: fixed;
    inset-inline: 0;
    bottom: 0;
    z-index: 30;
    height: 88vh;
    border-top: 1px solid var(--brand-cream, #E6E2D6);
    border-top-left-radius: 1rem;
    border-top-right-radius: 1rem;
    box-shadow: 0 -8px 24px rgba(31, 79, 91, 0.12);
    transition: transform 220ms cubic-bezier(0.16, 1, 0.3, 1);
    /* Respect iOS notch / home indicator */
    padding-bottom: env(safe-area-inset-bottom);
  }
  .mobile-drawer-peek {
    transform: translateY(calc(88vh - 56px));
  }
  .mobile-drawer-half {
    transform: translateY(50vh);
  }
  .mobile-drawer-full {
    transform: translateY(0);
  }
}
</style>
