import { defineStore } from 'pinia';
import { ref } from 'vue';

export type TileLayer = 'rudy' | 'nlsc' | 'osm';

export const useMapStore = defineStore('map', () => {
  const selectedStartId = ref<string | null>(null);
  const selectedEndId = ref<string | null>(null);
  const activeTile = ref<TileLayer>('rudy');

  function pickNode(nodeId: string) {
    if (!selectedStartId.value) {
      selectedStartId.value = nodeId;
    } else if (!selectedEndId.value) {
      selectedEndId.value = nodeId;
    } else {
      selectedStartId.value = nodeId;
      selectedEndId.value = null;
    }
  }

  function reset() {
    selectedStartId.value = null;
    selectedEndId.value = null;
  }

  return { selectedStartId, selectedEndId, activeTile, pickNode, reset };
});
