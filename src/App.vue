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

<style>
/* Full-viewport flex shell so child views can opt into h-full instead of
   hard-coding header offset. Uses 100dvh on mobile to exclude browser chrome. */
.app-layout {
  height: 100dvh;
  display: flex !important;
  flex-direction: column;
}
.app-content {
  flex: 1 1 auto;
  min-height: 0;
}
.app-content > .n-layout-scroll-container {
  height: 100%;
}
</style>

<template>
  <NConfigProvider :locale="zhTW" :date-locale="dateZhTW" :theme-overrides="themeOverrides">
    <NMessageProvider>
      <NLayout class="app-layout">
        <NLayoutHeader bordered class="px-3 py-2 sm:px-6 sm:py-3 pt-safe">
          <AppNav />
        </NLayoutHeader>
        <NLayoutContent class="app-content" :native-scrollbar="false">
          <RouterView />
        </NLayoutContent>
      </NLayout>
    </NMessageProvider>
  </NConfigProvider>
</template>
