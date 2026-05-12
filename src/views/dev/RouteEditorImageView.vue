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
</script>

<template>
  <div class="h-full flex flex-col">
    <NTabs v-model:value="activeTab" type="line" size="small" class="flex-shrink-0 px-2 pt-1">
      <NTabPane name="topo" tab="拓撲圖" />
      <NTabPane
        v-for="(img, i) in elevationImages"
        :key="img"
        :name="`elev-${i}`"
        :tab="`高差 ${i + 1}`"
      />
    </NTabs>

    <div class="flex items-center gap-2 px-3 py-1 border-b text-xs">
      <span>縮放</span>
      <NSlider v-model:value="zoom" :min="0.3" :max="3" :step="0.1" style="width: 120px" />
      <span>{{ zoom.toFixed(1) }}x</span>
      <NButton
        size="tiny"
        @click="popout(activeTab === 'topo' ? topoUrl : elevUrl(elevationImages[Number(activeTab.split('-')[1])]))"
      >
        🔗 popout
      </NButton>
    </div>

    <div class="flex-1 overflow-auto bg-gray-50 p-2">
      <img
        v-if="activeTab === 'topo'"
        :src="topoUrl"
        :style="{ transform: `scale(${zoom})`, transformOrigin: 'top left' }"
        alt="上河拓撲圖"
        class="max-w-none"
      />
      <template v-for="(img, i) in elevationImages" :key="img">
        <img
          v-if="activeTab === `elev-${i}`"
          :src="elevUrl(img)"
          :style="{ transform: `scale(${zoom})`, transformOrigin: 'top left' }"
          :alt="`高差圖 ${i + 1}`"
          class="max-w-none"
        />
      </template>
    </div>
  </div>
</template>
