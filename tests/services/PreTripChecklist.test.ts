import { describe, it, expect } from 'vitest';
import {
  generateSuggestedItems,
  mergeChecklist,
  checklistStats,
} from '@/services/PreTripChecklist';
import type { ChecklistItem, Plan } from '@/types';

function makePlan(routeId: string, id = 1): Plan {
  return {
    id,
    name: 'test plan',
    routeId,
    startNodeId: 'a',
    endNodeId: 'a',
    nodeSequence: ['a'],
    paceMultiplier: 1,
    startDate: '2026-06-01',
    startTime: '06:00',
    dayBreaks: [],
    tripType: 'overnight_hut',
    createdAt: '2026-05-15T00:00:00Z',
  };
}

describe('generateSuggestedItems', () => {
  it('produces items for G02 with park permit + 排雲山莊 booking', () => {
    const plan = makePlan('G02');
    const items = generateSuggestedItems(plan);
    const titles = items.map((i) => i.title);
    expect(titles).toContain('入山證（警政署）');
    expect(titles).toContain('玉山國家公園入園證');
    expect(titles.some((t) => t.includes('排雲山莊'))).toBe(true);
    expect(titles.some((t) => t.includes('圓峰山屋'))).toBe(true);
  });

  it('produces forestry-only items for G11 (no park permit)', () => {
    const plan = makePlan('G11');
    const items = generateSuggestedItems(plan);
    const titles = items.map((i) => i.title);
    expect(titles).toContain('入山證（警政署）');
    expect(titles).not.toContain('玉山國家公園入園證');
    expect(titles).toContain('林務局申請（古道、林道、保留區）');
  });

  it('always includes safety items', () => {
    const plan = makePlan('G09');
    const items = generateSuggestedItems(plan);
    expect(items.some((i) => i.id === 'safety_custodian')).toBe(true);
    expect(items.some((i) => i.id === 'safety_return_time')).toBe(true);
    expect(items.some((i) => i.id === 'safety_emergency_contacts')).toBe(true);
  });

  it('marks legal/safety items as required', () => {
    const plan = makePlan('G09');
    const items = generateSuggestedItems(plan);
    const mountain = items.find((i) => i.id === 'legal_mountain_permit');
    const custodian = items.find((i) => i.id === 'safety_custodian');
    expect(mountain?.required).toBe(true);
    expect(custodian?.required).toBe(true);
  });

  it('gear_checklist_link points to /gear/:id when plan.id present', () => {
    const plan = makePlan('G02', 42);
    const items = generateSuggestedItems(plan);
    const link = items.find((i) => i.id === 'gear_checklist_link');
    expect(link?.internalRoute).toBe('/gear/42');
  });

  it('returns no regulatory items for unknown route', () => {
    const plan = makePlan('GXX');
    const items = generateSuggestedItems(plan);
    expect(items.find((i) => i.id === 'legal_mountain_permit')).toBeUndefined();
    // But safety/gear/external still present
    expect(items.find((i) => i.id === 'safety_custodian')).toBeDefined();
  });
});

describe('mergeChecklist', () => {
  it('preserves checkedAt on system items by id', () => {
    const generated: ChecklistItem[] = [
      { id: 'a', category: 'legal', title: 'a', required: true, systemSuggested: true },
      { id: 'b', category: 'safety', title: 'b', required: true, systemSuggested: true },
    ];
    const existing: ChecklistItem[] = [
      { id: 'a', category: 'legal', title: 'old title', required: true, systemSuggested: true, checkedAt: '2026-05-10T00:00:00Z' },
    ];
    const merged = mergeChecklist(existing, generated);
    const a = merged.find((i) => i.id === 'a')!;
    expect(a.checkedAt).toBe('2026-05-10T00:00:00Z');
    expect(a.title).toBe('a'); // updated from generated
  });

  it('appends user-added items to the end', () => {
    const generated: ChecklistItem[] = [
      { id: 'sys1', category: 'legal', title: 'sys', required: true, systemSuggested: true },
    ];
    const existing: ChecklistItem[] = [
      { id: 'sys1', category: 'legal', title: 'old', required: true, systemSuggested: true },
      { id: 'user1', category: 'custom', title: 'my custom', required: false, systemSuggested: false, checkedAt: '2026-05-10' },
    ];
    const merged = mergeChecklist(existing, generated);
    expect(merged).toHaveLength(2);
    expect(merged[1].id).toBe('user1');
    expect(merged[1].checkedAt).toBe('2026-05-10');
  });

  it('drops system items no longer in generated', () => {
    const generated: ChecklistItem[] = [
      { id: 'keep', category: 'legal', title: 'keep', required: true, systemSuggested: true },
    ];
    const existing: ChecklistItem[] = [
      { id: 'keep', category: 'legal', title: 'keep', required: true, systemSuggested: true },
      { id: 'drop', category: 'legal', title: 'drop me (stale system item)', required: true, systemSuggested: true },
    ];
    const merged = mergeChecklist(existing, generated);
    expect(merged.find((i) => i.id === 'drop')).toBeUndefined();
  });

  it('handles undefined existing as empty list', () => {
    const generated: ChecklistItem[] = [
      { id: 'a', category: 'legal', title: 'a', required: true, systemSuggested: true },
    ];
    const merged = mergeChecklist(undefined, generated);
    expect(merged).toHaveLength(1);
    expect(merged[0].checkedAt).toBeUndefined();
  });
});

describe('checklistStats', () => {
  it('computes percent and required percent', () => {
    const stats = checklistStats({
      items: [
        { id: '1', category: 'legal', title: 'a', required: true, systemSuggested: true, checkedAt: '2026' },
        { id: '2', category: 'legal', title: 'b', required: true, systemSuggested: true },
        { id: '3', category: 'gear', title: 'c', required: false, systemSuggested: true, checkedAt: '2026' },
        { id: '4', category: 'gear', title: 'd', required: false, systemSuggested: true },
      ],
    });
    expect(stats.total).toBe(4);
    expect(stats.checked).toBe(2);
    expect(stats.required).toBe(2);
    expect(stats.requiredChecked).toBe(1);
    expect(stats.percent).toBe(50);
    expect(stats.requiredPercent).toBe(50);
  });

  it('handles empty checklist', () => {
    const stats = checklistStats({ items: [] });
    expect(stats.total).toBe(0);
    expect(stats.percent).toBe(0);
    expect(stats.requiredPercent).toBe(0);
  });

  it('handles undefined checklist', () => {
    const stats = checklistStats(undefined);
    expect(stats.total).toBe(0);
  });
});
