<script setup lang="ts">
import { computed, ref } from 'vue';
import { NTabs, NTabPane, NSlider, NButton } from 'naive-ui';

const props = defineProps<{
  sunriverImage: string;
  elevationImages: string[];
}>();

const activeTab = ref<string>('topo');
const zoom = ref(1);

const SUNRIVER_BASE = 'https://www.sunriver.com.tw/images/hiking/';

const topoUrl = computed(() => `${SUNRIVER_BASE}${props.sunriverImage}`);

function elevUrl(filename: string): string {
  return `${SUNRIVER_BASE}${filename}`;
}

function popout(url: string): void {
  window.open(url, '_blank', 'noopener,noreferrer');
}

function activeImageUrl(): string {
  if (activeTab.value === 'topo') return topoUrl.value;
  const idx = Number(activeTab.value.split('-')[1]);
  return elevUrl(props.elevationImages[idx]);
}
</script>

<template>
  <div class="h-full min-h-0 flex flex-col overflow-hidden">
    <!-- Sticky tab bar -->
    <div class="shrink-0 border-b bg-white">
      <NTabs v-model:value="activeTab" type="line" size="small" class="px-2 pt-1">
        <NTabPane name="topo" tab="拓撲圖" />
        <NTabPane
          v-for="(img, i) in elevationImages"
          :key="img"
          :name="`elev-${i}`"
          :tab="`高差 ${i + 1}`"
        />
      </NTabs>
    </div>

    <!-- Sticky zoom controls -->
    <div class="shrink-0 flex items-center gap-2 px-3 py-1 border-b bg-white text-xs">
      <span class="text-gray-500">縮放</span>
      <NSlider v-model:value="zoom" :min="0.3" :max="3" :step="0.1" style="width: 100px" />
      <span class="w-8 text-gray-600">{{ zoom.toFixed(1) }}x</span>
      <NButton size="tiny" @click="popout(activeImageUrl())">🔗 popout</NButton>
    </div>

    <!-- Scrollable image area -->
    <div class="flex-1 min-h-0 overflow-auto bg-gray-50 p-2">
      <img
        v-if="activeTab === 'topo'"
        :src="topoUrl"
        :style="{ transform: `scale(${zoom})`, transformOrigin: 'top left', display: 'block' }"
        alt="上河拓撲圖"
        class="max-w-none"
      />
      <template v-for="(img, i) in elevationImages" :key="img">
        <img
          v-if="activeTab === `elev-${i}`"
          :src="elevUrl(img)"
          :style="{ transform: `scale(${zoom})`, transformOrigin: 'top left', display: 'block' }"
          :alt="`高差圖 ${i + 1}`"
          class="max-w-none"
        />
      </template>
    </div>
  </div>
</template>
