<script setup lang="ts">
import { computed } from 'vue';
import { NDataTable } from 'naive-ui';
import type { Plan, SegmentTime } from '@/types';
import { useRoutesStore } from '@/stores/routesStore';
import { groupByDayBreaks, type DayGroup } from '@/services/ScheduleGrouper';

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

function formatMins(min: number): string {
  const h = Math.floor(min / 60);
  const m = min % 60;
  return `${h}:${String(m).padStart(2, '0')}`;
}

const rows = computed<Row[]>(() => {
  if (!route.value) return [];
  const groups: DayGroup[] = groupByDayBreaks({
    plan: props.plan,
    route: route.value,
    segments: props.segments,
  });

  const out: Row[] = [];
  for (const day of groups) {
    const dayStartCumulative = day.daySegments[0]
      ? day.daySegments[0].cumulativeMinutes - day.daySegments[0].adjustedMinutes
      : 0;

    if (day.index === 1) {
      out.push({
        day: day.index,
        time: `${props.plan.startDate} ${props.plan.startTime}`,
        nodeName: day.startNode.name,
        segmentDuration: '—',
        elevation: day.startNode.elevation,
        cumulative: '0:00',
        isBreak: false,
      });
    }

    for (const seg of day.daySegments) {
      const node = route.value!.nodes.find((n) => n.id === seg.toNodeId);
      const cumWithinDay = seg.cumulativeMinutes - dayStartCumulative;
      out.push({
        day: day.index,
        time: new Date(seg.arrivalTime).toLocaleString('zh-TW', { hour12: false }),
        nodeName: node?.name ?? seg.toNodeId,
        segmentDuration: `+${formatMins(seg.adjustedMinutes)}`,
        elevation: node?.elevation ?? 0,
        cumulative: formatMins(cumWithinDay),
        isBreak: seg.toNodeId === day.endNode.id && day.index < groups.length,
      });
    }
  }
  return out;
});

const columns = [
  { title: 'Day', key: 'day', width: 56, fixed: 'left' as const, className: 'tabular-nums' },
  { title: '節點', key: 'nodeName', width: 140, fixed: 'left' as const, ellipsis: { tooltip: true } },
  { title: '時刻', key: 'time', width: 160, className: 'tabular-nums' },
  { title: '段落', key: 'segmentDuration', width: 84, className: 'tabular-nums' },
  { title: '海拔', key: 'elevation', width: 84, render: (r: Row) => `${r.elevation}m`, className: 'tabular-nums' },
  { title: '累計', key: 'cumulative', width: 84, className: 'tabular-nums' },
];
</script>

<template>
  <div class="table-view-wrapper relative">
    <NDataTable
      :columns="columns"
      :data="rows"
      :scroll-x="608"
      :row-class-name="(r: Row) => r.isBreak ? 'is-day-break' : ''"
    />
    <!-- Scroll affordance hint (visible on narrow screens) -->
    <div
      class="scroll-hint md:hidden pointer-events-none absolute top-0 bottom-0 right-0 w-6
             bg-gradient-to-l from-brand-white to-transparent"
      aria-hidden="true"
    ></div>
  </div>
</template>

<style scoped>
:deep(.is-day-break) {
  background-color: var(--brand-tint-warning-bg, #FBF1CE);
}
:deep(.tabular-nums) {
  font-variant-numeric: tabular-nums;
}
</style>
