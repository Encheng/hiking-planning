import { describe, it, expect, beforeEach } from 'vitest';
import 'fake-indexeddb/auto';
import { db, resetDb } from '@/db';
import type { Plan } from '@/types';

beforeEach(async () => {
  await resetDb();
});

describe('Dexie database', () => {
  it('persists a plan and reads it back', async () => {
    const plan: Plan = {
      name: '玉山主峰',
      routeId: 'G02',
      startNodeId: 'n_tataka',
      endNodeId: 'n_yushan_main',
      nodeSequence: ['n_tataka', 'n_paiyun', 'n_yushan_main'],
      paceMultiplier: 1.2,
      startDate: '2026-06-15',
      startTime: '06:00',
      dayBreaks: [],
      tripType: 'overnight_hut',
      createdAt: '2026-05-09T10:00:00Z',
    };
    const id = await db.plans.add(plan);
    const loaded = await db.plans.get(id);
    expect(loaded?.name).toBe('玉山主峰');
    expect(loaded?.nodeSequence).toEqual(['n_tataka', 'n_paiyun', 'n_yushan_main']);
  });

  it('cascades delete: removes gearChecklist when plan deleted', async () => {
    const planId = await db.plans.add({
      name: 'X', routeId: 'G02', startNodeId: 'a', endNodeId: 'b',
      nodeSequence: [], paceMultiplier: 1, startDate: '', startTime: '',
      dayBreaks: [], tripType: 'light_summit', createdAt: '',
    });
    await db.gearChecklists.add({ planId, checkedItemIds: ['i_water_1l'], removedTemplateIds: [] });
    await db.plans.delete(planId);
    const remaining = await db.gearChecklists.where('planId').equals(planId).toArray();
    expect(remaining).toEqual([]);
  });
});
