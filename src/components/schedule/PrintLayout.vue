<script setup lang="ts">
import { computed } from 'vue';
import type { Plan, Route, RouteNode, SegmentTime, TripType } from '@/types';
import { groupByDayBreaks } from '@/services/ScheduleGrouper';
import type { SuggestOutput } from '@/services/GearSuggester';

const props = defineProps<{
  plan: Plan;
  route: Route;
  segments: SegmentTime[];
  gearSuggestion: SuggestOutput | null;
}>();

const tripTypeLabels: Record<TripType, string> = {
  light_summit: '輕裝攻頂',
  long_day: '長日單攻',
  overnight_hut: '山屋過夜',
  overnight_camp: '紮營過夜',
};

const tripTypeLabel = computed(() => tripTypeLabels[props.plan.tripType]);

const printedAt = computed(() => new Date().toISOString().slice(0, 10));

interface ScheduleRow {
  day: number;
  time: string;
  nodeName: string;
  segmentDuration: string;
  elevation: number;
  cumulative: string;
  isBreak: boolean;
}

function findNode(id: string): RouteNode | undefined {
  return props.route.nodes.find((n) => n.id === id);
}

function fmtMins(min: number): string {
  const h = Math.floor(min / 60);
  const m = min % 60;
  return `${h}:${String(m).padStart(2, '0')}`;
}

const scheduleRows = computed<ScheduleRow[]>(() => {
  const groups = groupByDayBreaks({ plan: props.plan, route: props.route, segments: props.segments });
  const out: ScheduleRow[] = [];
  for (const day of groups) {
    const dayStartCum = day.daySegments[0]
      ? day.daySegments[0].cumulativeMinutes - day.daySegments[0].adjustedMinutes
      : 0;
    if (day.index === 1) {
      out.push({
        day: 1,
        time: `${props.plan.startDate} ${props.plan.startTime}`,
        nodeName: day.startNode.name,
        segmentDuration: '—',
        elevation: day.startNode.elevation,
        cumulative: '0:00',
        isBreak: false,
      });
    }
    for (const seg of day.daySegments) {
      const node = findNode(seg.toNodeId);
      out.push({
        day: day.index,
        time: new Date(seg.arrivalTime).toISOString().slice(0, 16).replace('T', ' '),
        nodeName: node?.name ?? seg.toNodeId,
        segmentDuration: `+${fmtMins(seg.adjustedMinutes)}`,
        elevation: node?.elevation ?? 0,
        cumulative: fmtMins(seg.cumulativeMinutes - dayStartCum),
        isBreak: seg.toNodeId === day.endNode.id && day.index < groups.length,
      });
    }
  }
  return out;
});
</script>

<template>
  <article class="print-only">
    <header class="print-header">
      <h1>{{ plan.name }}</h1>
      <dl>
        <div><dt>路線</dt><dd>{{ route.name }} ({{ route.id }})</dd></div>
        <div><dt>出發</dt><dd>{{ plan.startDate }} {{ plan.startTime }}</dd></div>
        <div><dt>類型</dt><dd>{{ tripTypeLabel }}</dd></div>
        <div><dt>倍率</dt><dd>{{ plan.paceMultiplier }}x</dd></div>
        <div><dt>上河版本</dt><dd>{{ route.version }}</dd></div>
      </dl>
    </header>

    <section class="print-schedule">
      <h2>行程時刻表</h2>
      <table>
        <thead>
          <tr>
            <th>Day</th><th>時刻</th><th>節點</th><th>段落</th><th>海拔</th><th>累計</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, idx) in scheduleRows"
            :key="idx"
            :class="{ 'is-break': row.isBreak }"
          >
            <td>{{ row.day }}</td>
            <td>{{ row.time }}</td>
            <td>{{ row.nodeName }}</td>
            <td>{{ row.segmentDuration }}</td>
            <td>{{ row.elevation }}m</td>
            <td>{{ row.cumulative }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="print-gear">
      <h2>裝備清單（出發前打勾）</h2>
      <template v-if="gearSuggestion">
        <div v-for="cat in gearSuggestion.categories" :key="cat.id">
          <h3>{{ cat.name }}</h3>
          <ul>
            <li v-for="item in cat.items" :key="item.id">
              ☐ {{ item.name }}
              <small v-if="item.weight_g">({{ item.weight_g }}g)</small>
            </li>
          </ul>
        </div>
      </template>
    </section>

    <footer class="print-footer">
      列印於 {{ printedAt }} · 資料來源：上河文化《2020 高山百岳地形圖》（個人使用）
    </footer>
  </article>
</template>
