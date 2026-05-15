<script setup lang="ts">
import { onMounted } from 'vue';
import { NConfigProvider, NMessageProvider, NLayout, NLayoutHeader, NLayoutContent, zhTW, dateZhTW } from 'naive-ui';
import { themeOverrides } from '@/theme';
import AppNav from '@/components/common/AppNav.vue';
import { useRoutesStore } from '@/stores/routesStore';
import { useGearStore } from '@/stores/gearStore';

onMounted(async () => {
  await Promise.all([
    useRoutesStore().loadAll(),
    useGearStore().loadTemplates(),
    useGearStore().loadCustomItems(),
  ]);
});
</script>

<template>
  <NConfigProvider :locale="zhTW" :date-locale="dateZhTW" :theme-overrides="themeOverrides">
    <NMessageProvider>
      <NLayout style="height: 100vh">
        <NLayoutHeader bordered class="app-header px-3 py-2 sm:px-6 sm:py-3 pt-safe">
          <AppNav />
        </NLayoutHeader>
        <NLayoutContent>
          <RouterView />
        </NLayoutContent>
      </NLayout>
    </NMessageProvider>
  </NConfigProvider>
</template>

<style>
/* Pin header to a known height so views can subtract it from 100dvh.
   Single source of truth for the planner's viewport math. */
.app-header {
  min-height: 56px;
}
</style>
