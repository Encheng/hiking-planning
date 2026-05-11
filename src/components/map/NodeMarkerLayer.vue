<script setup lang="ts">
import { inject, watch, onBeforeUnmount, type Ref } from 'vue';
import L from 'leaflet';
import type { RouteNode, NodeCategory } from '@/types';

const props = defineProps<{
  nodes: RouteNode[];
  highlightedNodeIds?: string[];
}>();

const emit = defineEmits<{
  'node-click': [{ node: RouteNode; latlng: L.LatLng }];
}>();

const map = inject<Ref<L.Map | null>>('leaflet-map')!;

const colors: Record<NodeCategory, string> = {
  trailhead: '#22c55e',
  hut: '#fbbf24',
  peak: '#dc2626',
  junction: '#a855f7',
  waypoint: '#3b82f6',
  water: '#06b6d4',
};

let markers: L.Marker[] = [];

function makeIcon(node: RouteNode, highlighted: boolean) {
  const baseColor = colors[node.category];
  const ring = highlighted ? '#0ea5e9' : 'white';
  return L.divIcon({
    className: 'node-marker',
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    html: `<div style="width:28px;height:28px;border-radius:50%;background:${baseColor};border:3px solid ${ring};box-shadow:0 0 0 1px rgba(0,0,0,0.2);"></div>`,
  });
}

function rebuild() {
  if (!map.value) return;
  markers.forEach((m) => m.remove());
  const highlighted = new Set(props.highlightedNodeIds ?? []);
  markers = props.nodes.map((node) => {
    const m = L.marker([node.lat, node.lng], {
      icon: makeIcon(node, highlighted.has(node.id)),
    });
    m.bindTooltip(`${node.name} (${node.elevation}m)`);
    m.on('click', (e: L.LeafletMouseEvent) => {
      emit('node-click', { node, latlng: e.latlng });
    });
    m.addTo(map.value!);
    return m;
  });
}

watch(map, (m) => { if (m) rebuild(); }, { immediate: true });
watch(() => props.nodes, () => rebuild(), { deep: true });
watch(() => props.highlightedNodeIds, () => rebuild(), { deep: true });

onBeforeUnmount(() => markers.forEach((m) => m.remove()));
</script>

<template><div /></template>
