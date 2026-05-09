<script setup lang="ts">
import { NMenu } from 'naive-ui';
import { computed, h } from 'vue';
import { RouterLink, useRoute } from 'vue-router';

const route = useRoute();
const activeKey = computed(() => route.name as string);

const options = [
  { key: 'routes', label: () => h(RouterLink, { to: '/routes' }, () => '路線') },
  { key: 'map', label: () => h(RouterLink, { to: '/map' }, () => '地圖規劃') },
  { key: 'plans', label: () => h(RouterLink, { to: '/plans' }, () => '我的行程') },
  { key: 'settings', label: () => h(RouterLink, { to: '/settings' }, () => '設定') },
];
</script>

<template>
  <NMenu :value="activeKey" mode="horizontal" :options="options" />
</template>
