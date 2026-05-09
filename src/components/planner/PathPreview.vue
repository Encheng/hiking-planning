<script setup lang="ts">
import { computed } from 'vue';
import { NCard, NTag } from 'naive-ui';
import type { Route } from '@/types';
import type { PathOutput } from '@/services/PathResolver';
import { calculateTimes } from '@/services/TimeCalculator';
import { useSettingsStore } from '@/stores/settingsStore';
import { usePlanStore } from '@/stores/planStore';

const props = defineProps<{ path: PathOutput; route: Route }>();
const settings = useSettingsStore();
const planStore = usePlanStore();

const totals = computed(() => {
  if (props.path.combined.length < 2) return { totalMinutes: 0, totalAdjustedMinutes: 0 };
  return calculateTimes({
    route: props.route,
    nodeSequence: props.path.combined,
    paceMultiplier: planStore.draft?.paceMultiplier ?? settings.defaultPaceMultiplier,
    startDateTime: '2026-01-01T00:00:00',
  });
});

function fmtH(min: number) {
  const h = Math.floor(min / 60);
  const m = min % 60;
  return `${h}h${m > 0 ? `${m}m` : ''}`;
}
</script>

<template>
  <NCard title="路徑預覽">
    <div v-if="path.warnings.includes('no_path')" class="text-red-600">
      ⚠️ 找不到從起點到終點的路徑，可能是資料缺失。
    </div>
    <template v-else>
      <p class="text-sm mb-2">
        節點數：<strong>{{ path.combined.length }}</strong>
        ・上河時間：<strong>{{ fmtH(totals.totalMinutes) }}</strong>
        ・倍率後：<strong>{{ fmtH(totals.totalAdjustedMinutes) }}</strong>
      </p>
      <div class="text-xs text-gray-500 max-h-40 overflow-auto">
        <NTag v-for="nodeId in path.combined" :key="nodeId" size="small" class="mr-1 mb-1">
          {{ route.nodes.find(n => n.id === nodeId)?.name }}
        </NTag>
      </div>
    </template>
  </NCard>
</template>
