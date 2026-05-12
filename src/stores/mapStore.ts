import { defineStore } from 'pinia';
import { ref } from 'vue';

export type TileLayer = 'photo' | 'nlsc' | 'osm';

export const useMapStore = defineStore('map', () => {
  const activeTile = ref<TileLayer>('photo');
  return { activeTile };
});
