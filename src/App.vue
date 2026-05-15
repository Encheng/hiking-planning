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
        <NLayoutHeader bordered class="px-6 py-3">
          <AppNav />
        </NLayoutHeader>
        <NLayoutContent>
          <RouterView />
        </NLayoutContent>
      </NLayout>
    </NMessageProvider>
  </NConfigProvider>
</template>
