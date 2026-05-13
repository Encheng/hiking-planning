<script setup lang="ts">
import { inject, watch, onBeforeUnmount, type Ref } from 'vue';
import L from 'leaflet';
import type { RouteNode, DayBreak } from '@/types';

const props = defineProps<{
  nodes: RouteNode[];
  nodeIds: string[];
  dayBreaks?: DayBreak[];
}>();

const map = inject<Ref<L.Map | null>>('leaflet-map')!;

const DAY_COLORS = ['#2563eb', '#d97706', '#7c3aed', '#059669', '#db2777'];

const layers: L.Layer[] = [];

function clearLayers() {
  layers.forEach((l) => l.remove());
  layers.length = 0;
}

function getBearing(a: L.LatLng, b: L.LatLng): number {
  const dLng = ((b.lng - a.lng) * Math.PI) / 180;
  const lat1 = (a.lat * Math.PI) / 180;
  const lat2 = (b.lat * Math.PI) / 180;
  const y = Math.sin(dLng) * Math.cos(lat2);
  const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLng);
  return (Math.atan2(y, x) * 180) / Math.PI;
}

function midLatLng(a: L.LatLng, b: L.LatLng): L.LatLng {
  return L.latLng((a.lat + b.lat) / 2, (a.lng + b.lng) / 2);
}

function arrowIcon(color: string, angle: number): L.DivIcon {
  // CSS triangle points up by default; rotate by bearing degrees
  return L.divIcon({
    html: `<div style="width:0;height:0;border-left:5px solid transparent;border-right:5px solid transparent;border-bottom:12px solid ${color};transform:rotate(${angle}deg)"></div>`,
    className: '',
    iconSize: [10, 12],
    iconAnchor: [5, 6],
  });
}

function overnightIcon(type: DayBreak['type']): L.DivIcon {
  const emoji = type === 'camp' ? '⛺' : '🏠';
  return L.divIcon({
    html: `<div style="font-size:18px;line-height:1;filter:drop-shadow(0 1px 2px rgba(0,0,0,0.5))">${emoji}</div>`,
    className: '',
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });
}

function splitByDays(nodeIds: string[], dayBreaks: DayBreak[]): string[][] {
  if (!dayBreaks.length) return [nodeIds];
  const days: string[][] = [];
  let start = 0;
  for (const db of dayBreaks) {
    const idx = nodeIds.indexOf(db.afterNodeId, start);
    if (idx === -1 || idx <= start) continue;
    days.push(nodeIds.slice(start, idx + 1));
    start = idx; // overnight node is shared — next day starts here
  }
  days.push(nodeIds.slice(start));
  return days.filter((d) => d.length >= 2);
}

function rebuild(): void {
  clearLayers();
  if (!map.value || props.nodeIds.length < 2) return;

  const nodeMap = new Map(props.nodes.map((n) => [n.id, n]));
  const daySegs = splitByDays(props.nodeIds, props.dayBreaks ?? []);

  daySegs.forEach((seg, dayIdx) => {
    const color = DAY_COLORS[dayIdx % DAY_COLORS.length];
    const latlngs = seg
      .map((id) => nodeMap.get(id))
      .filter((n): n is RouteNode => !!n)
      .map((n) => L.latLng(n.lat, n.lng));

    if (latlngs.length < 2) return;

    const pl = L.polyline(latlngs, {
      color,
      weight: 5,
      opacity: 0.9,
      lineCap: 'round',
      lineJoin: 'round',
    }).addTo(map.value!);
    layers.push(pl);

    // Place arrows: one every ~3 segments, at segment midpoints
    const step = Math.max(1, Math.floor((latlngs.length - 1) / 3));
    for (let i = step - 1; i < latlngs.length - 1; i += step) {
      const a = latlngs[i];
      const b = latlngs[i + 1];
      const bearing = getBearing(a, b);
      const mid = midLatLng(a, b);
      const arrow = L.marker(mid, {
        icon: arrowIcon(color, bearing),
        interactive: false,
        zIndexOffset: 50,
      }).addTo(map.value!);
      layers.push(arrow);
    }

    // Overnight marker at end of each non-final day
    if (dayIdx < daySegs.length - 1) {
      const lastId = seg[seg.length - 1];
      const lastNode = nodeMap.get(lastId);
      const db = (props.dayBreaks ?? []).find((d) => d.afterNodeId === lastId);
      if (lastNode && db) {
        const m = L.marker([lastNode.lat, lastNode.lng], {
          icon: overnightIcon(db.type),
          interactive: false,
          zIndexOffset: 100,
        }).addTo(map.value!);
        layers.push(m);
      }
    }
  });
}

watch(map, (m) => { if (m) rebuild(); }, { immediate: true });
watch(() => props.nodeIds, () => rebuild(), { deep: true });
watch(() => props.nodes, () => rebuild(), { deep: true });
watch(() => props.dayBreaks, () => rebuild(), { deep: true });

onBeforeUnmount(clearLayers);
</script>

<template><div /></template>
