import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Route, Hut } from '@/types';

export const useRoutesStore = defineStore('routes', () => {
  const routes = ref<Route[]>([]);
  const huts = ref<Hut[]>([]);
  const loading = ref(false);

  async function loadAll() {
    loading.value = true;
    try {
      const [routeRes, hutsRes] = await Promise.all([
        fetch('/data/routes/G02-sample.json').then((r) => r.json() as Promise<Route>),
        fetch('/data/huts.json').then((r) => r.json() as Promise<Hut[]>),
      ]);
      routes.value = [routeRes];
      huts.value = hutsRes;
    } finally {
      loading.value = false;
    }
  }

  const getById = computed(() => (id: string) => routes.value.find((r) => r.id === id));

  return { routes, huts, loading, loadAll, getById };
});
