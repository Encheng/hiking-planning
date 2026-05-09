import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Route, Hut } from '@/types';

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to load ${url}: ${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

export const useRoutesStore = defineStore('routes', () => {
  const routes = ref<Route[]>([]);
  const huts = ref<Hut[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function loadAll() {
    loading.value = true;
    error.value = null;
    try {
      const [routeRes, hutsRes] = await Promise.all([
        fetchJson<Route>('/data/routes/G02-sample.json'),
        fetchJson<Hut[]>('/data/huts.json'),
      ]);
      routes.value = [routeRes];
      huts.value = hutsRes;
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e);
      console.error('[routesStore] loadAll failed:', e);
    } finally {
      loading.value = false;
    }
  }

  const getById = computed(() => (id: string) => routes.value.find((r) => r.id === id));

  return { routes, huts, loading, error, loadAll, getById };
});
