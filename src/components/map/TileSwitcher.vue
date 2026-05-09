<script setup lang="ts">
import { inject, watch, onBeforeUnmount, onMounted, ref, type Ref } from 'vue';
import L from 'leaflet';
import { useMapStore, type TileLayer } from '@/stores/mapStore';

const map = inject<Ref<L.Map | null>>('leaflet-map')!;
const mapStore = useMapStore();
const containerEl = ref<HTMLDivElement | null>(null);

onMounted(() => {
  if (containerEl.value) {
    L.DomEvent.disableClickPropagation(containerEl.value);
    L.DomEvent.disableScrollPropagation(containerEl.value);
  }
});

const tileUrls: Record<TileLayer, { url: string; attribution: string; maxZoom: number }> = {
  photo: {
    url: 'https://wmts.nlsc.gov.tw/wmts/PHOTO_MIX/default/GoogleMapsCompatible/{z}/{y}/{x}',
    attribution: '&copy; 內政部國土測繪中心 正射影像',
    maxZoom: 18,
  },
  nlsc: {
    url: 'https://wmts.nlsc.gov.tw/wmts/EMAP5/default/GoogleMapsCompatible/{z}/{y}/{x}',
    attribution: '&copy; 內政部國土測繪中心 通用版電子地圖',
    maxZoom: 18,
  },
  osm: {
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; OpenStreetMap',
    maxZoom: 19,
  },
};

let currentLayer: L.TileLayer | null = null;

function applyTile(name: TileLayer) {
  if (!map.value) return;
  if (currentLayer) {
    map.value.removeLayer(currentLayer);
  }
  const cfg = tileUrls[name];
  currentLayer = L.tileLayer(cfg.url, { attribution: cfg.attribution, maxZoom: cfg.maxZoom }).addTo(map.value);
}

watch(map, (m) => {
  if (m) applyTile(mapStore.activeTile);
}, { immediate: true });

watch(() => mapStore.activeTile, (val) => applyTile(val));

onBeforeUnmount(() => {
  if (currentLayer && map.value) map.value.removeLayer(currentLayer);
});
</script>

<template>
  <div ref="containerEl" class="absolute top-3 right-3 z-[1000] bg-white rounded shadow p-2 flex gap-1">
    <button
      v-for="key in (['photo','nlsc','osm'] as const)"
      :key="key"
      class="px-2 py-1 text-xs rounded"
      :class="mapStore.activeTile === key ? 'bg-blue-500 text-white' : 'bg-gray-100'"
      @click="mapStore.activeTile = key"
    >
      {{ key === 'photo' ? '正射影像' : key === 'nlsc' ? '通用版' : 'OSM' }}
    </button>
  </div>
</template>
