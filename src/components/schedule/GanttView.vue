<script setup lang="ts">
import { computed } from 'vue';
import type { Plan, SegmentTime } from '@/types';
import { useRoutesStore } from '@/stores/routesStore';
import { groupByDayBreaks } from '@/services/ScheduleGrouper';
import { segmentColor } from '@/services/SegmentColor';

const props = defineProps<{ plan: Plan; segments: SegmentTime[] }>();
const routesStore = useRoutesStore();

const route = computed(() => routesStore.getById(props.plan.routeId));

const days = computed(() => {
  if (!route.value) return [];
  return groupByDayBreaks({ plan: props.plan, route: route.value, segments: props.segments });
});

function fmt(min: number): string {
  const h = Math.floor(min / 60);
  const m = min % 60;
  return m > 0 ? `${h}h${String(m).padStart(2, '0')}` : `${h}h`;
}

function nodeName(id: string): string {
  return route.value?.nodes.find((n) => n.id === id)?.name ?? id;
}

function color(seg: SegmentTime): string {
  return route.value ? segmentColor(seg, route.value) : '#fcd34d';
}
</script>

<template>
  <div v-if="route" class="space-y-6">
    <section v-for="day in days" :key="day.index">
      <h3 class="text-sm font-bold text-emerald-600 mb-2">
        DAY {{ day.index }} · {{ day.date }} · 總計 {{ fmt(day.totalAdjustedMinutes) }}
      </h3>
      <div class="relative h-14">
        <span class="absolute left-0 top-0 text-xs">{{ day.startTime }}</span>
        <span class="absolute right-0 top-0 text-xs">{{ day.endTime }}</span>
        <div class="absolute inset-x-0 top-5 h-5 flex gap-px bg-white">
          <div
            v-for="(seg, idx) in day.daySegments"
            :key="idx"
            data-segment-bar
            :style="{ flex: seg.adjustedMinutes, background: color(seg) }"
            :title="`${nodeName(seg.toNodeId)} +${fmt(seg.adjustedMinutes)}`"
          />
        </div>
        <span class="absolute left-0 top-12 text-xs text-gray-600">{{ day.startNode.name }}</span>
        <span class="absolute right-0 top-12 text-xs text-gray-600">{{ day.endNode.name }}</span>
      </div>
    </section>
  </div>
</template>
