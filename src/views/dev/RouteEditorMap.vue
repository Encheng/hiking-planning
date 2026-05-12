<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-gpx';
import type { Route, OsmPoi, NodeCategory } from '@/types';

const props = defineProps<{
  gpxUrl: string;
  pois: OsmPoi[];
  route: Route;
}>();

const mapEl = ref<HTMLDivElement | null>(null);
let map: L.Map | null = null;
let gpxLayer: L.Layer | null = null;
let poiMarkers: L.Marker[] = [];
let nodeMarkers: L.Marker[] = [];
let lastClickMarker: L.Marker | null = null;

const colors: Record<NodeCategory, string> = {
  trailhead: '#22c55e', hut: '#fbbf24', peak: '#dc2626',
  junction: '#a855f7', waypoint: '#3b82f6', water: '#06b6d4',
};

function makePoiIcon(category: string): L.DivIcon {
  const color = (colors as Record<string, string>)[category] ?? '#9ca3af';
  return L.divIcon({
    className: 'osm-poi-marker',
    iconSize: [14, 14],
    iconAnchor: [7, 7],
    html: `<div style="width:14px;height:14px;border-radius:50%;background:${color};opacity:0.6;border:2px solid white;"></div>`,
  });
}

function makeNodeIcon(category: NodeCategory): L.DivIcon {
  const color = colors[category];
  return L.divIcon({
    className: 'route-node-marker',
    iconSize: [22, 22],
    iconAnchor: [11, 11],
    html: `<div style="width:22px;height:22px;border-radius:50%;background:${color};border:3px solid white;box-shadow:0 0 0 1px #000;"></div>`,
  });
}

function renderPois(): void {
  poiMarkers.forEach((m) => m.remove());
  if (!map) return;
  poiMarkers = props.pois.map((poi) => {
    const m = L.marker([poi.lat, poi.lon], { icon: makePoiIcon(poi.tags.category) });
    m.bindTooltip(`${poi.name} (OSM, ${poi.tags.category})`);
    m.addTo(map!);
    return m;
  });
}

function renderNodes(): void {
  nodeMarkers.forEach((m) => m.remove());
  if (!map) return;
  nodeMarkers = props.route.nodes
    .filter((n) => n.lat !== 0 && n.lng !== 0)
    .map((n) => {
      const m = L.marker([n.lat, n.lng], { icon: makeNodeIcon(n.category) });
      m.bindTooltip(`${n.name} (節點, ${n.category})`);
      m.addTo(map!);
      return m;
    });
}

onMounted(() => {
  if (!mapEl.value) return;
  map = L.map(mapEl.value, { center: [23.5, 121], zoom: 12 });
  L.tileLayer('https://wmts.nlsc.gov.tw/wmts/EMAP5/default/GoogleMapsCompatible/{z}/{y}/{x}', {
    attribution: '&copy; 內政部國土測繪中心',
    maxZoom: 18,
  }).addTo(map);

  if (props.gpxUrl) {
    try {
      // @ts-expect-error leaflet-gpx augments L
      gpxLayer = new L.GPX(props.gpxUrl, {
        async: true,
        polyline_options: { color: '#dc2626', weight: 3 },
        markers: { startIcon: null, endIcon: null },
      }).on('loaded', (e: { target: { getBounds: () => L.LatLngBounds } }) => {
        map?.fitBounds(e.target.getBounds());
      }).addTo(map);
    } catch (e) {
      console.warn('GPX load failed:', e);
    }
  }

  renderPois();
  renderNodes();

  map.on('click', (e: L.LeafletMouseEvent) => {
    lastClickMarker?.remove();
    lastClickMarker = L.marker(e.latlng, {
      icon: L.divIcon({
        className: 'click-marker',
        iconSize: [16, 16],
        iconAnchor: [8, 8],
        html: `<div style="width:16px;height:16px;border-radius:50%;background:#000;border:2px solid #fff;"></div>`,
      }),
    }).addTo(map!);
    lastClickMarker.bindTooltip(`點選: ${e.latlng.lat.toFixed(5)}, ${e.latlng.lng.toFixed(5)}`).openTooltip();
    navigator.clipboard?.writeText(`${e.latlng.lat.toFixed(6)}, ${e.latlng.lng.toFixed(6)}`);
  });
});

onBeforeUnmount(() => {
  map?.remove();
});

watch(() => props.pois, renderPois, { deep: true });
watch(() => props.route.nodes, renderNodes, { deep: true });
</script>

<template>
  <div ref="mapEl" class="h-full w-full"></div>
</template>
