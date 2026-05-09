<script setup lang="ts">
import { computed } from 'vue';
import GearCategorySection from './GearCategorySection.vue';
import { useGearStore } from '@/stores/gearStore';

const gearStore = useGearStore();
const checked = computed(() => gearStore.currentChecklist?.checkedItemIds ?? []);

async function toggle(itemId: string) {
  gearStore.toggleItem(itemId);
  await gearStore.saveChecklist();
}
</script>

<template>
  <div v-if="gearStore.suggestion">
    <GearCategorySection
      v-for="cat in gearStore.suggestion.categories"
      :key="cat.id"
      :category-id="cat.id"
      :category-name="cat.name"
      :items="cat.items"
      :checked-ids="checked"
      @toggle="toggle"
    />
  </div>
</template>
