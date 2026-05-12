<script setup lang="ts">
import type { Route, OsmPoi } from '@/types';
defineProps<{ route: Route; osmPois: OsmPoi[] }>();
defineEmits<{ save: [] }>();
</script>
<template>
  <div class="p-3 text-xs text-gray-500">Sidebar stub - Task 10</div>
</template>
