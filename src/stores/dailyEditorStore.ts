import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useDailyEditorStore = defineStore('dailyEditor', () => {
  const expandedDayIndex = ref<number | null>(null);
  const popupNodeId = ref<string | null>(null);

  function toggleExpand(idx: number) {
    expandedDayIndex.value = expandedDayIndex.value === idx ? null : idx;
  }

  function reset() {
    expandedDayIndex.value = null;
    popupNodeId.value = null;
  }

  function openPopup(nodeId: string) {
    popupNodeId.value = nodeId;
  }

  function closePopup() {
    popupNodeId.value = null;
  }

  return { expandedDayIndex, popupNodeId, toggleExpand, reset, openPopup, closePopup };
});
