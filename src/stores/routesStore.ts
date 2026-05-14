import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Route, Hut, RoutesManifest } from '@/types';

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
  const manifest = ref<RoutesManifest | null>(null);

  async function loadAll() {
    loading.value = true;
    error.value = null;
    try {
      const [manifestData, hutsData] = await Promise.all([
        fetchJson<RoutesManifest>('/data/routes-manifest.json'),
        fetchJson<Hut[]>('/data/huts.json'),
      ]);
      manifest.value = manifestData;
      huts.value = hutsData;

      const doneEntries = manifestData.routes.filter((r) => r.status === 'done');
      const routePromises = doneEntries.map((entry) =>
        fetchJson<Route>(`/data/routes/${entry.id}.json`).catch((e) => {
          console.warn(`[routesStore] Failed to load ${entry.id}:`, e);
          return null;
        }),
      );
      const loaded = (await Promise.all(routePromises)).filter(
        (r): r is Route => r !== null,
      );
      routes.value = loaded;
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e);
      console.error('[routesStore] loadAll failed:', e);
    } finally {
      loading.value = false;
    }
  }

  const getById = computed(() => (id: string) => routes.value.find((r) => r.id === id));

  const getVerification = computed(() => (id: string) => {
    return manifest.value?.routes.find((r) => r.id === id)?.verification ?? 'estimated';
  });

  return { routes, huts, loading, error, manifest, loadAll, getById, getVerification };
});
