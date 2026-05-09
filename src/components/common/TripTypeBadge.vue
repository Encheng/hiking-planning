<script setup lang="ts">
import { NTag } from 'naive-ui';
import type { TripType } from '@/types';

const props = defineProps<{ tripType: TripType }>();

const labels: Record<TripType, { text: string; type: 'default' | 'success' | 'warning' | 'error' }> = {
  light_summit: { text: '輕裝攻頂', type: 'success' },
  long_day: { text: '長日單攻', type: 'warning' },
  overnight_hut: { text: '山屋過夜', type: 'warning' },
  overnight_camp: { text: '紮營過夜', type: 'error' },
};
</script>

<template>
  <NTag :type="labels[props.tripType].type">{{ labels[props.tripType].text }}</NTag>
</template>
