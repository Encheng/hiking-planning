<script setup lang="ts">
import { NMenu, NDrawer, NDrawerContent, NButton } from 'naive-ui';
import { computed, h, ref, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import AppIcon from '@/components/common/AppIcon.vue';

const route = useRoute();
const activeKey = computed(() => route.name as string);
const drawerOpen = ref(false);

// Close drawer whenever route changes so navigation always feels finished
watch(() => route.fullPath, () => { drawerOpen.value = false; });

interface NavItem { key: string; label: string; to: string }
const items: NavItem[] = [
  { key: 'routes', label: '路線', to: '/routes' },
  { key: 'map', label: '地圖規劃', to: '/map' },
  { key: 'plans', label: '我的行程', to: '/plans' },
  { key: 'settings', label: '設定', to: '/settings' },
];

// Desktop horizontal menu uses Naive's render-as-RouterLink trick
const desktopOptions = items.map((it) => ({
  key: it.key,
  label: () => h(RouterLink, { to: it.to }, () => it.label),
}));
</script>

<template>
  <div class="app-nav flex items-center justify-between w-full">
    <!-- Brand mark (shared) -->
    <RouterLink
      to="/"
      class="brand inline-flex items-center gap-2 text-brand-900 font-bold text-base sm:text-lg shrink-0"
    >
      <AppIcon name="mountain" :size="22" />
      <span>百岳排程</span>
    </RouterLink>

    <!-- Desktop nav -->
    <div class="hidden md:block">
      <NMenu :value="activeKey" mode="horizontal" :options="desktopOptions" />
    </div>

    <!-- Mobile hamburger trigger -->
    <NButton
      class="md:hidden"
      quaternary
      circle
      aria-label="開啟選單"
      :aria-expanded="drawerOpen"
      @click="drawerOpen = true"
    >
      <template #icon>
        <AppIcon name="menu" :size="24" />
      </template>
    </NButton>

    <!-- Mobile drawer -->
    <NDrawer v-model:show="drawerOpen" :width="280" placement="right">
      <NDrawerContent title="選單" closable>
        <nav class="flex flex-col gap-1" aria-label="主要導覽">
          <RouterLink
            v-for="it in items"
            :key="it.key"
            :to="it.to"
            class="nav-link"
            :class="{ 'is-active': activeKey === it.key }"
          >
            <span>{{ it.label }}</span>
            <AppIcon name="chevron-right" :size="16" class="opacity-50" />
          </RouterLink>
        </nav>
      </NDrawerContent>
    </NDrawer>
  </div>
</template>

<style scoped>
.nav-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  /* >=44px tap target per Apple HIG / WCAG 2.5.5 */
  min-height: 44px;
  padding: 10px 12px;
  border-radius: 8px;
  color: #1F4F5B;
  font-weight: 500;
  transition: background-color 120ms;
}
.nav-link:hover {
  background: #EAF1F2;
}
.nav-link.is-active {
  background: #1F4F5B;
  color: #FFFAFF;
}
.nav-link.is-active :deep(svg) {
  opacity: 1 !important;
}
</style>
