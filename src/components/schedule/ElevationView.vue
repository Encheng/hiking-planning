<script setup lang="ts">
import { computed } from 'vue';
import AppIcon from '@/components/common/AppIcon.vue';
import type { Plan, RouteNode, SegmentTime } from '@/types';
import { useRoutesStore } from '@/stores/routesStore';
import { groupByDayBreaks, type DayGroup } from '@/services/ScheduleGrouper';

const props = defineProps<{ plan: Plan; segments: SegmentTime[] }>();
const routesStore = useRoutesStore();

const route = computed(() => routesStore.getById(props.plan.routeId));

const SVG_W = 400;
const SVG_H = 80;
const X_LEFT = 20;
const X_RIGHT = 380;
const Y_TOP = 12;
const Y_BOTTOM = 68;

interface MarkerPoint {
  x: number;
  y: number;
  name: string;
  elevation: number;
  time: string;
  type: 'peak' | 'hut' | 'trailhead' | 'waypoint';
}

interface ElevationDay {
  index: number;
  date: string;
  startTime: string;
  endTime: string;
  totalMinutes: number;
  startNode: RouteNode;
  endNode: RouteNode;
  peakNode?: RouteNode;
  polylinePoints: string;
  fillPath: string;
  highlights: MarkerPoint[];
  yMin: number;
  yMax: number;
}

function fmt(min: number): string {
  const h = Math.floor(min / 60);
  const m = min % 60;
  return m > 0 ? `${h}h${String(m).padStart(2, '0')}` : `${h}h`;
}

function dayColor(idx: number): string {
  const palette = ['#3b82f6', '#a855f7', '#ec4899', '#10b981', '#f59e0b'];
  return palette[(idx - 1) % palette.length];
}

function markerColor(type: MarkerPoint['type']): string {
  return { peak: '#dc2626', hut: '#fbbf24', trailhead: '#22c55e', waypoint: '#3b82f6' }[type];
}

function buildDay(day: DayGroup, allNodes: RouteNode[]): ElevationDay {
  const points: { elev: number; cumulative: number; node: RouteNode | undefined; time: string }[] = [];
  points.push({
    elev: day.startNode.elevation,
    cumulative: 0,
    node: day.startNode,
    time: day.startTime,
  });
  let cum = 0;
  for (const seg of day.daySegments) {
    cum += seg.adjustedMinutes;
    const node = allNodes.find((n) => n.id === seg.toNodeId);
    const arr = new Date(seg.arrivalTime);
    const time = `${String(arr.getUTCHours()).padStart(2, '0')}:${String(arr.getUTCMinutes()).padStart(2, '0')}`;
    points.push({ elev: node?.elevation ?? 0, cumulative: cum, node, time });
  }

  const elevations = points.map((p) => p.elev);
  const rawMin = Math.min(...elevations);
  const rawMax = Math.max(...elevations);
  const yMin = Math.floor(rawMin / 100) * 100;
  const yMax = Math.ceil(rawMax / 100) * 100;
  const ySpan = Math.max(1, yMax - yMin);

  const xOf = (cum: number) => X_LEFT + (X_RIGHT - X_LEFT) * (cum / Math.max(1, day.totalAdjustedMinutes));
  const yOf = (elev: number) => Y_BOTTOM - (Y_BOTTOM - Y_TOP) * ((elev - yMin) / ySpan);

  const polylinePoints = points
    .map((p) => `${xOf(p.cumulative).toFixed(1)},${yOf(p.elev).toFixed(1)}`)
    .join(' ');

  const fillSegments = points.map((p) => `${xOf(p.cumulative).toFixed(1)},${yOf(p.elev).toFixed(1)}`).join(' L ');
  const fillPath = `M ${xOf(0).toFixed(1)},${Y_BOTTOM} L ${fillSegments} L ${xOf(day.totalAdjustedMinutes).toFixed(1)},${Y_BOTTOM} Z`;

  const highlights: MarkerPoint[] = points
    .filter((p) => p.node && (p.node.category === 'peak' || p.node.category === 'hut' || p.node.category === 'trailhead'))
    .map((p) => ({
      x: xOf(p.cumulative),
      y: yOf(p.elev),
      name: p.node!.name,
      elevation: p.node!.elevation,
      time: p.time,
      type: p.node!.category as MarkerPoint['type'],
    }));

  return {
    index: day.index,
    date: day.date,
    startTime: day.startTime,
    endTime: day.endTime,
    totalMinutes: day.totalAdjustedMinutes,
    startNode: day.startNode,
    endNode: day.endNode,
    peakNode: day.peakNode,
    polylinePoints,
    fillPath,
    highlights,
    yMin,
    yMax,
  };
}

const days = computed<ElevationDay[]>(() => {
  if (!route.value) return [];
  const groups = groupByDayBreaks({ plan: props.plan, route: route.value, segments: props.segments });
  return groups.map((g) => buildDay(g, route.value!.nodes));
});
</script>

<template>
  <div v-if="route" class="space-y-4">
    <section v-for="day in days" :key="day.index">
      <div
        class="text-xs font-bold mb-1"
        :style="{ color: dayColor(day.index) }"
      >
        DAY {{ day.index }} · {{ day.startTime }} → {{ day.endTime }} · {{ fmt(day.totalMinutes) }}
      </div>
      <svg :viewBox="`0 0 ${SVG_W} ${SVG_H}`" class="w-full h-20" data-testid="elevation-chart">
        <line :x1="X_LEFT" :y1="Y_BOTTOM" :x2="X_RIGHT" :y2="Y_BOTTOM" stroke="#ddd" />
        <path :d="day.fillPath" :fill="dayColor(day.index)" fill-opacity="0.18" />
        <polyline
          :points="day.polylinePoints"
          :stroke="dayColor(day.index)"
          stroke-width="2"
          fill="none"
        />
        <g v-for="h in day.highlights" :key="h.name">
          <circle
            :cx="h.x"
            :cy="h.y"
            r="4"
            :fill="markerColor(h.type)"
            stroke="white"
            stroke-width="1.5"
          />
          <title>{{ h.name }} ({{ h.elevation }}m, {{ h.time }})</title>
        </g>
        <text x="2" y="72" font-size="7" fill="#888">{{ day.yMin }}m</text>
        <text x="2" y="14" font-size="7" fill="#888">{{ day.yMax }}m</text>
      </svg>
      <div class="flex justify-between text-xs text-gray-600 -mt-1">
        <span>{{ day.startNode.name }}</span>
        <span v-if="day.peakNode" class="font-medium inline-flex items-center gap-1">
          <AppIcon name="mountain" :size="12" />
          {{ day.peakNode.name }} {{ day.peakNode.elevation }}m
        </span>
        <span>{{ day.endNode.name }}</span>
      </div>
    </section>
  </div>
</template>
