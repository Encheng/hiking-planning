<script setup lang="ts">
import type { Route } from '@/types';
import type { PathOutput } from '@/services/PathResolver';
defineProps<{ path: PathOutput; route: Route }>();
</script>
<template>
  <div class="text-xs text-gray-400 p-2">PathPreview stub — Task 17 will implement</div>
</template>
