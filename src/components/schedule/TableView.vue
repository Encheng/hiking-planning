<script setup lang="ts">
import { computed } from 'vue';
import { NDataTable } from 'naive-ui';
import type { Plan, SegmentTime } from '@/types';
import { useRoutesStore } from '@/stores/routesStore';

const props = defineProps<{ plan: Plan; segments: SegmentTime[] }>();
const routesStore = useRoutesStore();

const route = computed(() => routesStore.getById(props.plan.routeId));

interface Row {
  day: number;
  time: string;
  nodeName: string;
  segmentDuration: string;
  elevation: number;
  cumulative: string;
  isBreak: boolean;
}

const rows = computed<Row[]>(() => {
  if (!route.value) return [];
  const out: Row[] = [];
  let day = 1;
  let dayStartCumulative = 0;
  const breaksByNodeId = new Map(props.plan.dayBreaks.map((b) => [b.afterNodeId, b]));

  const startNode = route.value.nodes.find((n) => n.id === props.plan.startNodeId);
  out.push({
    day,
    time: `${props.plan.startDate} ${props.plan.startTime}`,
    nodeName: startNode?.name ?? props.plan.startNodeId,
    segmentDuration: '—',
    elevation: startNode?.elevation ?? 0,
    cumulative: '0:00',
    isBreak: false,
  });

  for (const seg of props.segments) {
    const node = route.value.nodes.find((n) => n.id === seg.toNodeId);
    const cumMin = seg.cumulativeMinutes - dayStartCumulative;
    out.push({
      day,
      time: new Date(seg.arrivalTime).toLocaleString('zh-TW', { hour12: false }),
      nodeName: node?.name ?? seg.toNodeId,
      segmentDuration: `+${formatMins(seg.adjustedMinutes)}`,
      elevation: node?.elevation ?? 0,
      cumulative: formatMins(cumMin),
      isBreak: breaksByNodeId.has(seg.toNodeId),
    });
    if (breaksByNodeId.has(seg.toNodeId)) {
      day += 1;
      dayStartCumulative = seg.cumulativeMinutes;
    }
  }
  return out;
});

function formatMins(min: number): string {
  const h = Math.floor(min / 60);
  const m = min % 60;
  return `${h}:${String(m).padStart(2, '0')}`;
}

const columns = [
  { title: 'Day', key: 'day', width: 60 },
  { title: '時刻', key: 'time' },
  { title: '節點', key: 'nodeName' },
  { title: '段落', key: 'segmentDuration', width: 80 },
  { title: '海拔', key: 'elevation', width: 80, render: (r: Row) => `${r.elevation}m` },
  { title: '累計', key: 'cumulative', width: 80 },
];
</script>

<template>
  <NDataTable :columns="columns" :data="rows" :row-class-name="(r: Row) => r.isBreak ? 'bg-yellow-50' : ''" />
</template>
