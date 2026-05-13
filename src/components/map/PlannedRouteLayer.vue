<script setup lang="ts">
import { inject, watch, onBeforeUnmount, type Ref } from 'vue';
import L from 'leaflet';
import type { RouteNode } from '@/types';

const props = defineProps<{
  nodes: RouteNode[];
  nodeIds: string[];
}>();

const map = inject<Ref<L.Map | null>>('leaflet-map')!;

let polyline: L.Polyline | null = null;

function rebuild(): void {
  if (!map.value) return;
  polyline?.remove();
  polyline = null;

  if (props.nodeIds.length < 2) return;
  const nodeMap = new Map(props.nodes.map((n) => [n.id, n]));
  const points: L.LatLngExpression[] = props.nodeIds
    .map((id) => nodeMap.get(id))
    .filter((n): n is RouteNode => !!n)
    .map((n) => [n.lat, n.lng]);

  if (points.length < 2) return;

  polyline = L.polyline(points, {
    color: '#dc2626',
    weight: 5,
    opacity: 0.9,
    lineCap: 'round',
    lineJoin: 'round',
  }).addTo(map.value);
}

watch(map, (m) => { if (m) rebuild(); }, { immediate: true });
watch(() => props.nodeIds, () => rebuild(), { deep: true });
watch(() => props.nodes, () => rebuild(), { deep: true });

onBeforeUnmount(() => polyline?.remove());
</script>

<template><div /></template>
