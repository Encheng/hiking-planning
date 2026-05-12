import { describe, it, expect, beforeEach } from 'vitest';
import 'fake-indexeddb/auto';
import { db, resetDb } from '@/db';
import type { Plan } from '@/types';
import { deriveDailyPlansFromLegacy } from '@/services/DailyPlanMigration';

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

describe('Dexie v2 migration', () => {
  it('migrates legacy plan: adds dailyPlans + returnToStart via helper', async () => {
    const legacyPlan = {
      name: 'legacy',
      routeId: 'G02',
      startNodeId: 'n_tataka',
      endNodeId: 'n_yushan_main',
      nodeSequence: ['n_tataka', 'n_paiyun', 'n_yushan_main'],
      paceMultiplier: 1.0,
      startDate: '2026-06-15',
      startTime: '06:00',
      dayBreaks: [{ afterNodeId: 'n_paiyun', type: 'hut' as const, hutId: 'hut_paiyun' }],
      tripType: 'overnight_hut' as const,
      createdAt: '2026-05-09T00:00:00Z',
    };

    // Insert as v1-shaped (cast: type doesn't have dailyPlans yet because optional)
    const id = await db.plans.add(legacyPlan as never);
    // Simulate migration via the helper (Dexie hook is hard to test in isolation)
    const migrated = deriveDailyPlansFromLegacy(legacyPlan);
    await db.plans.update(id, {
      dailyPlans: migrated.dailyPlans,
      returnToStart: migrated.returnToStart,
    } as never);

    const loaded = await db.plans.get(id);
    expect(loaded?.dailyPlans).toHaveLength(2);
    expect(loaded?.returnToStart).toBe(false);
  });
});
