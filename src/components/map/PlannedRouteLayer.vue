<script setup lang="ts">
import { inject, watch, onBeforeUnmount, type Ref } from 'vue';
import L from 'leaflet';
import type { RouteNode, DayBreak } from '@/types';
import { dayColor, dayDashArray } from '@/services/DayColors';

const props = defineProps<{
  nodes: RouteNode[];
  nodeIds: string[];
  dayBreaks?: DayBreak[];
  activeDayIndex?: number | null; // 0-based; null = no day selected
}>();

const map = inject<Ref<L.Map | null>>('leaflet-map')!;

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
  // SVG arrow: tip points up at angle=0 (north); rotated around its center
  const svg = `<svg width="18" height="18" viewBox="0 0 18 18" xmlns="http://www.w3.org/2000/svg">
    <g transform="rotate(${angle},9,9)">
      <polygon points="9,1 17,17 9,12 1,17"
        fill="${color}" stroke="white" stroke-width="2" stroke-linejoin="round"/>
    </g>
  </svg>`;
  return L.divIcon({
    html: svg,
    className: '',
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  });
}

// Lucide-style inline SVG paths for overnight markers (kept inline so Leaflet
// divIcon can render without mounting a Vue tree per marker).
const TENT_SVG_PATH =
  '<path d="M3.5 21 14 3"/><path d="M20.5 21 10 3"/><path d="M15.5 21 12 15l-3.5 6"/><path d="M2 21h20"/>';
const HOME_SVG_PATH =
  '<path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>';

function overnightIcon(type: DayBreak['type']): L.DivIcon {
  const isCamp = type === 'camp';
  const bg = isCamp ? '#BE603D' : '#1F4F5B';
  const inner = isCamp ? TENT_SVG_PATH : HOME_SVG_PATH;
  const html = `
    <div style="display:flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;background:${bg};box-shadow:0 1px 3px rgba(0,0,0,0.4);">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#FFFAFF" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">${inner}</svg>
    </div>`;
  return L.divIcon({
    html,
    className: '',
    iconSize: [24, 24],
    iconAnchor: [12, 12],
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
    start = idx;
  }
  days.push(nodeIds.slice(start));
  return days.filter((d) => d.length >= 2);
}

function rebuild(): void {
  clearLayers();
  if (!map.value || props.nodeIds.length < 2) return;

  const nodeMap = new Map(props.nodes.map((n) => [n.id, n]));
  const daySegs = splitByDays(props.nodeIds, props.dayBreaks ?? []);
  const hasActive = props.activeDayIndex != null;

  daySegs.forEach((seg, dayIdx) => {
    const isActive = !hasActive || dayIdx === props.activeDayIndex;
    const color = dayColor(dayIdx);

    // Style: active = prominent, ghost = faded; no active = all normal
    const weight = hasActive ? (isActive ? 7 : 3) : 5;
    const opacity = hasActive ? (isActive ? 1.0 : 0.2) : 0.9;
    const dash = isActive ? undefined : dayDashArray(dayIdx); // active day always solid

    const latlngs = seg
      .map((id) => nodeMap.get(id))
      .filter((n): n is RouteNode => !!n)
      .map((n) => L.latLng(n.lat, n.lng));

    if (latlngs.length < 2) return;

    const pl = L.polyline(latlngs, {
      color,
      weight,
      opacity,
      lineCap: 'round',
      lineJoin: 'round',
      ...(dash ? { dashArray: dash } : {}),
    }).addTo(map.value!);
    layers.push(pl);

    // Arrows: only draw for active (or all-equal) days to avoid ghost clutter
    if (isActive) {
      const step = Math.max(1, Math.floor((latlngs.length - 1) / 2));
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
watch(() => props.activeDayIndex, () => rebuild());

onBeforeUnmount(clearLayers);
</script>

<template><div /></template>
