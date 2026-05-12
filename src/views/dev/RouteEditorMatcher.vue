<script setup lang="ts">
import type { OsmPoi } from '@/types';
defineProps<{ nodeName: string; pois: OsmPoi[] }>();
defineEmits<{ select: [poi: OsmPoi] }>();
</script>
<template>
  <div class="text-xs text-gray-500">Matcher stub - Task 11</div>
</template>
