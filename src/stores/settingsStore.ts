import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import type { TileLayer } from './mapStore';

const STORAGE_KEY = 'hiking-planning-settings';

interface PersistedSettings {
  defaultPaceMultiplier: number;
  defaultTile: TileLayer;
  defaultDailyHours: number;
}

const defaults: PersistedSettings = {
  defaultPaceMultiplier: 1.2,
  defaultTile: 'photo',
  defaultDailyHours: 8,
};

const VALID_TILES: TileLayer[] = ['photo', 'nlsc', 'osm'];

export const useSettingsStore = defineStore('settings', () => {
  const stored = (() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      const parsed = raw ? { ...defaults, ...JSON.parse(raw) } : defaults;
      if (!VALID_TILES.includes(parsed.defaultTile)) {
        parsed.defaultTile = defaults.defaultTile;
      }
      return parsed;
    } catch {
      return defaults;
    }
  })();

  const defaultPaceMultiplier = ref(stored.defaultPaceMultiplier);
  const defaultTile = ref<TileLayer>(stored.defaultTile);
  const defaultDailyHours = ref(stored.defaultDailyHours);

  watch(
    [defaultPaceMultiplier, defaultTile, defaultDailyHours],
    () => {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        defaultPaceMultiplier: defaultPaceMultiplier.value,
        defaultTile: defaultTile.value,
        defaultDailyHours: defaultDailyHours.value,
      }));
    },
    { deep: true },
  );

  return { defaultPaceMultiplier, defaultTile, defaultDailyHours };
});
