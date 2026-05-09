<script setup lang="ts">
import { inject, watch, onBeforeUnmount, type Ref } from 'vue';
import L from 'leaflet';
import type { RouteNode, NodeCategory } from '@/types';
import { useMapStore } from '@/stores/mapStore';

const props = defineProps<{ nodes: RouteNode[] }>();
const map = inject<Ref<L.Map | null>>('leaflet-map')!;
const mapStore = useMapStore();

const colors: Record<NodeCategory, string> = {
  trailhead: '#22c55e',
  hut: '#fbbf24',
  peak: '#dc2626',
  junction: '#a855f7',
  waypoint: '#3b82f6',
  water: '#06b6d4',
};

let markers: L.Marker[] = [];

function makeIcon(node: RouteNode, isStart: boolean, isEnd: boolean) {
  const baseColor = colors[node.category];
  const ring = isStart ? '#22c55e' : isEnd ? '#dc2626' : 'white';
  const label = isStart ? '起' : isEnd ? '終' : '';
  return L.divIcon({
    className: 'node-marker',
    iconSize: [22, 22],
    html: `<div style="width:22px;height:22px;border-radius:50%;background:${baseColor};border:3px solid ${ring};display:flex;align-items:center;justify-content:center;color:white;font-size:10px;font-weight:bold;">${label}</div>`,
  });
}

function rebuild() {
  if (!map.value) return;
  markers.forEach((m) => m.remove());
  markers = props.nodes.map((node) => {
    const isStart = mapStore.selectedStartId === node.id;
    const isEnd = mapStore.selectedEndId === node.id;
    const m = L.marker([node.lat, node.lng], { icon: makeIcon(node, isStart, isEnd) });
    m.bindTooltip(`${node.name} (${node.elevation}m)`);
    m.on('click', () => mapStore.pickNode(node.id));
    m.addTo(map.value!);
    return m;
  });
}

watch(map, (m) => { if (m) rebuild(); }, { immediate: true });
watch(() => props.nodes, () => rebuild(), { deep: true });
watch(() => [mapStore.selectedStartId, mapStore.selectedEndId], () => rebuild());

onBeforeUnmount(() => markers.forEach((m) => m.remove()));
</script>

<template><div /></template>
