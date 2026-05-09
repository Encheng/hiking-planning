import { describe, it, expect } from 'vitest';
import { suggestGear, classifyTripType } from '@/services/GearSuggester';
import gearTemplatesData from '../../public/data/gear-templates.json';
import type { GearTemplates, CustomItem, GearChecklist } from '@/types';

const templates = gearTemplatesData as GearTemplates;

describe('classifyTripType', () => {
  it('returns light_summit for short, no-overnight trips', () => {
    expect(classifyTripType({ totalHours: 3, hasOvernight: false, hasCamping: false })).toBe('light_summit');
  });
  it('returns long_day for longer day trips', () => {
    expect(classifyTripType({ totalHours: 9, hasOvernight: false, hasCamping: false })).toBe('long_day');
  });
  it('returns overnight_hut for hut stays', () => {
    expect(classifyTripType({ totalHours: 14, hasOvernight: true, hasCamping: false })).toBe('overnight_hut');
  });
  it('returns overnight_camp for camping stays', () => {
    expect(classifyTripType({ totalHours: 14, hasOvernight: true, hasCamping: true })).toBe('overnight_camp');
  });
});

describe('suggestGear', () => {
  it('union categories: overnight_camp includes light_summit, long_day, overnight_hut, overnight_camp', () => {
    const result = suggestGear({
      templates,
      totalHours: 14,
      hasOvernight: true,
      hasCamping: true,
      customItems: [],
    });
    expect(result.tripType).toBe('overnight_camp');
    const ids = result.categories.map((c) => c.id);
    expect(ids).toEqual(expect.arrayContaining(['light_summit', 'long_day', 'overnight_hut', 'overnight_camp']));
  });

  it('appends custom items to matching categories', () => {
    const customItems: CustomItem[] = [
      { id: 1, name: '我的乳膠手套', defaultCategories: ['overnight_camp'] },
    ];
    const result = suggestGear({
      templates,
      totalHours: 14,
      hasOvernight: true,
      hasCamping: true,
      customItems,
    });
    const camp = result.categories.find((c) => c.id === 'overnight_camp')!;
    const customItem = camp.items.find((i) => i.name === '我的乳膠手套');
    expect(customItem?.source).toBe('custom');
  });

  it('marks last-trip items as last_trip source', () => {
    const lastChecklist: GearChecklist = {
      planId: 1,
      checkedItemIds: ['i_water_1l', 'custom_2'],
      removedTemplateIds: [],
    };
    const result = suggestGear({
      templates,
      totalHours: 3,
      hasOvernight: false,
      hasCamping: false,
      customItems: [],
      lastChecklist,
    });
    const light = result.categories.find((c) => c.id === 'light_summit')!;
    const water = light.items.find((i) => i.id === 'i_water_1l')!;
    expect(water.source).toBe('last_trip');
  });
});
