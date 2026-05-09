<script setup lang="ts">
import { ref } from 'vue';
import { NInput, NInputNumber, NCheckboxGroup, NCheckbox, NButton, NCard, NSpace } from 'naive-ui';
import { useGearStore } from '@/stores/gearStore';
import type { TripType } from '@/types';

const gearStore = useGearStore();
const name = ref('');
const weight = ref<number | null>(null);
const categories = ref<TripType[]>([]);

async function submit() {
  if (!name.value.trim()) return;
  await gearStore.addCustomItem({
    name: name.value.trim(),
    weightGrams: weight.value ?? undefined,
    defaultCategories: categories.value,
  });
  name.value = '';
  weight.value = null;
  categories.value = [];
}
</script>

<template>
  <NCard title="新增自訂物品" size="small">
    <NSpace vertical size="small">
      <NInput v-model:value="name" placeholder="物品名稱" />
      <NInputNumber v-model:value="weight" placeholder="重量 (g)" :min="0" />
      <NCheckboxGroup v-model:value="categories">
        <NSpace>
          <NCheckbox value="light_summit">輕裝</NCheckbox>
          <NCheckbox value="long_day">長日</NCheckbox>
          <NCheckbox value="overnight_hut">山屋</NCheckbox>
          <NCheckbox value="overnight_camp">紮營</NCheckbox>
        </NSpace>
      </NCheckboxGroup>
      <NButton type="primary" size="small" :disabled="!name.trim()" @click="submit">新增</NButton>
    </NSpace>
  </NCard>
</template>
