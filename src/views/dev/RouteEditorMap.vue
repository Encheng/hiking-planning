<script setup lang="ts">
import type { Route, OsmPoi } from '@/types';
defineProps<{ gpxUrl: string; pois: OsmPoi[]; route: Route }>();
</script>
<template>
  <div class="p-3 text-xs text-gray-500">Map stub - Task 12</div>
</template>
