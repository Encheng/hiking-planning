<script setup lang="ts">
import { ref } from 'vue';
import { NCard, NForm, NFormItem, NSelect, NSpace, NButton, useMessage } from 'naive-ui';
import PaceSlider from '@/components/planner/PaceSlider.vue';
import { useSettingsStore } from '@/stores/settingsStore';
import { db, resetDb } from '@/db';

const settings = useSettingsStore();
const message = useMessage();

const tileOptions = [
  { label: '正射影像 (NLSC PHOTO_MIX)', value: 'photo' },
  { label: '通用版電子地圖 (NLSC EMAP5)', value: 'nlsc' },
  { label: 'OpenStreetMap', value: 'osm' },
];

const usage = ref<string>('—');

async function checkStorage() {
  if (!navigator.storage?.estimate) {
    usage.value = '瀏覽器不支援';
    return;
  }
  const est = await navigator.storage.estimate();
  const usedMB = ((est.usage ?? 0) / 1024 / 1024).toFixed(1);
  const quotaMB = ((est.quota ?? 0) / 1024 / 1024).toFixed(0);
  usage.value = `${usedMB} MB / ${quotaMB} MB`;
}

async function clearAll() {
  await resetDb();
  message.success('已清除所有資料');
}

async function exportBackup() {
  const data = {
    plans: await db.plans.toArray(),
    gearChecklists: await db.gearChecklists.toArray(),
    customItems: await db.customItems.toArray(),
  };
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `hiking-backup-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
}
</script>

<template>
  <div class="p-6 max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold mb-4">設定</h1>
    <NSpace vertical size="large">
      <NCard title="預設值">
        <NForm label-placement="left" label-width="100">
          <NFormItem label="預設倍率">
            <PaceSlider v-model="settings.defaultPaceMultiplier" />
          </NFormItem>
          <NFormItem label="預設底圖">
            <NSelect v-model:value="settings.defaultTile" :options="tileOptions" />
          </NFormItem>
        </NForm>
      </NCard>

      <NCard title="儲存空間">
        <NSpace vertical>
          <p>已用：{{ usage }}</p>
          <NSpace>
            <NButton size="small" @click="checkStorage">檢查使用量</NButton>
            <NButton size="small" @click="exportBackup">匯出備份</NButton>
            <NButton size="small" type="error" ghost @click="clearAll">清除所有資料</NButton>
          </NSpace>
        </NSpace>
      </NCard>
    </NSpace>
  </div>
</template>
