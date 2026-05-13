<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useMessage } from 'naive-ui';
import RouteEditorImageView from './RouteEditorImageView.vue';
import RouteEditorSidebar from './RouteEditorSidebar.vue';
import RouteEditorMap from './RouteEditorMap.vue';
import type {
  Route, RoutesManifest, RoutesManifestEntry, OsmPoisFile,
} from '@/types';

const route = useRoute();
const message = useMessage();

const routeIdQuery = computed(() => (route.query.route as string) ?? '');
const manifestEntry = ref<RoutesManifestEntry | null>(null);
const osmPois = ref<OsmPoisFile | null>(null);
const editingRoute = ref<Route | null>(null);
const loading = ref(true);

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url} HTTP ${res.status}`);
  return res.json() as Promise<T>;
}

async function load(routeId: string): Promise<void> {
  loading.value = true;
  try {
    const manifest = await fetchJson<RoutesManifest>('/data/routes-manifest.json');
    const entry = manifest.routes.find((r) => r.id === routeId);
    if (!entry) {
      message.error(`Route ${routeId} not in manifest`);
      return;
    }
    manifestEntry.value = entry;

    try {
      osmPois.value = await fetchJson<OsmPoisFile>(`/data/osm-pois/${routeId}.json`);
    } catch {
      osmPois.value = { sourceRelation: 0, fetchedAt: '', pois: [] };
    }

    try {
      editingRoute.value = await fetchJson<Route>(`/data/routes/${routeId}.json`);
    } catch {
      editingRoute.value = {
        id: routeId, name: entry.name, version: '', source: '',
        nodes: [], edges: [], presets: [],
      };
    }
  } catch (e) {
    message.error(`Load failed: ${e instanceof Error ? e.message : e}`);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  if (routeIdQuery.value) load(routeIdQuery.value);
});

function downloadJson() {
  if (!editingRoute.value) return;
  const blob = new Blob([JSON.stringify(editingRoute.value, null, 2)], {
    type: 'application/json',
  });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `${editingRoute.value.id}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
}
</script>

<template>
  <div class="h-screen flex flex-col overflow-hidden">
    <header class="shrink-0 border-b px-3 py-2 flex gap-3 items-center">
      <h1 class="text-lg font-bold">/dev/route-editor</h1>
      <span v-if="manifestEntry" class="text-sm text-gray-600">{{ manifestEntry.id }} · {{ manifestEntry.name }}</span>
      <span v-if="loading" class="text-sm text-gray-400">載入中…</span>
    </header>
    <div class="flex-1 min-h-0 grid grid-cols-[380px_380px_1fr]">
      <!-- Column 1: Image viewer -->
      <div class="h-full min-h-0 overflow-hidden border-r relative">
        <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white/70 z-10">
          <span class="text-sm text-gray-400">載入中…</span>
        </div>
        <RouteEditorImageView
          v-if="manifestEntry"
          :sunriver-image="manifestEntry.sunriverImage"
          :elevation-images="manifestEntry.elevationImages"
        />
      </div>
      <!-- Column 2: Sidebar -->
      <div class="h-full min-h-0 overflow-hidden border-r relative">
        <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white/70 z-10">
          <span class="text-sm text-gray-400">載入中…</span>
        </div>
        <RouteEditorSidebar
          v-if="editingRoute && osmPois"
          :route="editingRoute"
          :osm-pois="osmPois.pois"
          @save="downloadJson"
        />
      </div>
      <!-- Column 3: Map -->
      <div class="h-full min-h-0 overflow-hidden relative">
        <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white/70 z-10">
          <span class="text-sm text-gray-400">載入中…</span>
        </div>
        <RouteEditorMap
          v-if="editingRoute && osmPois && manifestEntry"
          :gpx-url="`/data/gpx/${manifestEntry.id}.gpx`"
          :pois="osmPois.pois"
          :route="editingRoute"
        />
      </div>
    </div>
  </div>
</template>
