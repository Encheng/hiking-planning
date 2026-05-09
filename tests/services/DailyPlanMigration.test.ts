import { describe, it, expect } from 'vitest';
import { deriveDailyPlansFromLegacy } from '@/services/DailyPlanMigration';
import { resolveDailyPlans } from '@/services/DailyPlanResolver';
import g02 from '../fixtures/G02-test.json';
import type { Route, DayBreak } from '@/types';

const route = g02 as Route;

describe('deriveDailyPlansFromLegacy', () => {
  it('legacy plan with no dayBreaks → 1 dailyPlan with viaNodeIds=[]', () => {
    const result = deriveDailyPlansFromLegacy({
      startNodeId: 'n_tataka',
      endNodeId: 'n_paiyun',
      nodeSequence: ['n_tataka', 'n_shang_dongpu', 'n_dietshan', 'n_pailin', 'n_dachienshan', 'n_baimu', 'n_paiyun'],
      dayBreaks: [],
    });
    expect(result.dailyPlans).toHaveLength(1);
    expect(result.dailyPlans[0].endNodeId).toBe('n_paiyun');
    expect(result.dailyPlans[0].viaNodeIds).toEqual([]);
    expect(result.returnToStart).toBe(false);
  });

  it('legacy plan with 1 dayBreak → 2 dailyPlans', () => {
    const dayBreaks: DayBreak[] = [{ afterNodeId: 'n_paiyun', type: 'hut', hutId: 'hut_paiyun' }];
    const result = deriveDailyPlansFromLegacy({
      startNodeId: 'n_tataka',
      endNodeId: 'n_yushan_main',
      nodeSequence: ['n_tataka', 'n_shang_dongpu', 'n_dietshan', 'n_pailin', 'n_dachienshan', 'n_baimu', 'n_paiyun', 'n_yushan_main'],
      dayBreaks,
    });
    expect(result.dailyPlans).toHaveLength(2);
    expect(result.dailyPlans[0].endNodeId).toBe('n_paiyun');
    expect(result.dailyPlans[0].endType).toBe('hut');
    expect(result.dailyPlans[0].hutId).toBe('hut_paiyun');
    expect(result.dailyPlans[1].endNodeId).toBe('n_yushan_main');
    expect(result.returnToStart).toBe(false);
  });

  it('legacy plan ending at startNodeId → returnToStart=true', () => {
    const dayBreaks: DayBreak[] = [{ afterNodeId: 'n_paiyun', type: 'hut', hutId: 'hut_paiyun' }];
    const result = deriveDailyPlansFromLegacy({
      startNodeId: 'n_tataka',
      endNodeId: 'n_tataka',
      nodeSequence: ['n_tataka', 'n_shang_dongpu', 'n_paiyun', 'n_yushan_main', 'n_paiyun', 'n_shang_dongpu', 'n_tataka'],
      dayBreaks,
    });
    expect(result.dailyPlans).toHaveLength(2);
    expect(result.dailyPlans[1].endNodeId).toBe('n_tataka');
    expect(result.returnToStart).toBe(true);
  });

  it('round-trip safety: migrated plan re-resolved produces correct endpoints', () => {
    const dayBreaks: DayBreak[] = [{ afterNodeId: 'n_paiyun', type: 'hut', hutId: 'hut_paiyun' }];
    const original = {
      startNodeId: 'n_tataka',
      endNodeId: 'n_yushan_main',
      nodeSequence: ['n_tataka', 'n_shang_dongpu', 'n_dietshan', 'n_pailin', 'n_dachienshan', 'n_baimu', 'n_paiyun', 'n_yushan_main'],
      dayBreaks,
    };
    const { dailyPlans, returnToStart } = deriveDailyPlansFromLegacy(original);
    const resolved = resolveDailyPlans({
      route, startNodeId: original.startNodeId, dailyPlans, returnToStart,
    });
    expect(resolved.nodeSequence[0]).toBe('n_tataka');
    expect(resolved.nodeSequence[resolved.nodeSequence.length - 1]).toBe('n_yushan_main');
  });

  it('legacy plan with empty nodeSequence falls back gracefully', () => {
    const result = deriveDailyPlansFromLegacy({
      startNodeId: 'n_tataka',
      endNodeId: 'n_tataka',
      nodeSequence: [],
      dayBreaks: [],
    });
    expect(result.dailyPlans).toHaveLength(1);
    expect(result.dailyPlans[0].endNodeId).toBe('n_tataka');
    expect(result.returnToStart).toBe(true);
  });
});
