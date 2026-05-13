<script setup lang="ts">
import { computed, ref } from 'vue';
import { NInput, NRadio, NRadioGroup, NTag } from 'naive-ui';
import { matchPoisToNode } from '@/services/OsmPoiMatcher';
import type { OsmPoi } from '@/types';

const props = defineProps<{
  nodeName: string;
  pois: OsmPoi[];
}>();

const emit = defineEmits<{ select: [poi: OsmPoi] }>();

const searchTerm = ref('');
const selectedPoiId = ref<string | null>(null);

const candidates = computed(() => {
  if (searchTerm.value) {
    return props.pois
      .filter((p) => p.name.toLowerCase().includes(searchTerm.value.toLowerCase()))
      .slice(0, 10)
      .map((poi) => ({ poi, similarity: 1.0 }));
  }
  return matchPoisToNode(props.nodeName, props.pois).slice(0, 6);
});

function pick(poi: OsmPoi): void {
  selectedPoiId.value = poi.id;
  emit('select', poi);
}
</script>

<template>
  <div class="border-t pt-2 mt-2">
    <div class="text-xs text-gray-500 mb-1">OSM POI 匹配候選</div>
    <NInput v-model:value="searchTerm" placeholder="搜尋 OSM POI" size="small" />
    <NRadioGroup v-if="candidates.length > 0" :value="selectedPoiId" class="block mt-2">
      <NRadio
        v-for="c in candidates"
        :key="c.poi.id"
        :value="c.poi.id"
        @change="pick(c.poi)"
      >
        <span class="text-xs">{{ c.poi.name }}</span>
        <NTag size="tiny" class="ml-1">{{ (c.similarity * 100).toFixed(0) }}%</NTag>
        <span class="text-xs text-gray-400 ml-1">
          {{ c.poi.lat.toFixed(4) }}, {{ c.poi.lon.toFixed(4) }}
        </span>
      </NRadio>
    </NRadioGroup>
    <p v-else class="text-xs text-gray-400 mt-2">無候選（試試搜尋）</p>
  </div>
</template>
