import { defineStore } from 'pinia';
import { ref, toRaw } from 'vue';
import { db } from '@/db';
import type { GearChecklist, CustomItem, GearTemplates, TripType } from '@/types';
import { suggestGear, type SuggestOutput } from '@/services/GearSuggester';

export const useGearStore = defineStore('gear', () => {
  const templates = ref<GearTemplates | null>(null);
  const customItems = ref<CustomItem[]>([]);
  const currentChecklist = ref<GearChecklist | null>(null);
  const suggestion = ref<SuggestOutput | null>(null);

  async function loadTemplates() {
    templates.value = await fetch('/data/gear-templates.json').then((r) => r.json());
  }

  async function loadCustomItems() {
    customItems.value = await db.customItems.toArray();
  }

  async function loadChecklist(planId: number) {
    const existing = await db.gearChecklists.where('planId').equals(planId).first();
    currentChecklist.value = existing ?? { planId, checkedItemIds: [], removedTemplateIds: [] };
  }

  async function saveChecklist(): Promise<void> {
    if (!currentChecklist.value) return;
    const raw = toRaw(currentChecklist.value);
    if (raw.id) {
      await db.gearChecklists.put(raw);
    } else {
      const id = await db.gearChecklists.add(raw);
      currentChecklist.value.id = id as number;
    }
  }

  async function refreshSuggestion(input: {
    totalHours: number;
    hasOvernight: boolean;
    hasCamping: boolean;
    lastPlanId?: number;
  }) {
    if (!templates.value) await loadTemplates();
    const lastChecklist = input.lastPlanId
      ? await db.gearChecklists.where('planId').equals(input.lastPlanId).first()
      : undefined;
    suggestion.value = suggestGear({
      templates: templates.value!,
      totalHours: input.totalHours,
      hasOvernight: input.hasOvernight,
      hasCamping: input.hasCamping,
      customItems: customItems.value,
      lastChecklist,
    });
  }

  function toggleItem(itemId: string) {
    if (!currentChecklist.value) return;
    const idx = currentChecklist.value.checkedItemIds.indexOf(itemId);
    if (idx === -1) currentChecklist.value.checkedItemIds.push(itemId);
    else currentChecklist.value.checkedItemIds.splice(idx, 1);
  }

  async function addCustomItem(item: Omit<CustomItem, 'id'>): Promise<number> {
    const id = (await db.customItems.add(item)) as number;
    await loadCustomItems();
    return id;
  }

  async function findLastPlanIdOfType(tripType: TripType, excludePlanId?: number): Promise<number | undefined> {
    const all = await db.plans.orderBy('createdAt').reverse().toArray();
    const match = all.find((p) => p.tripType === tripType && p.id !== excludePlanId);
    return match?.id;
  }

  return {
    templates, customItems, currentChecklist, suggestion,
    loadTemplates, loadCustomItems, loadChecklist, saveChecklist,
    refreshSuggestion, toggleItem, addCustomItem, findLastPlanIdOfType,
  };
});
