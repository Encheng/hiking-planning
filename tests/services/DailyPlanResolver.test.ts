import { describe, it, expect } from 'vitest';
import { resolveDailyPlans } from '@/services/DailyPlanResolver';
import g02 from '../fixtures/G02-test.json';
import type { Route } from '@/types';

const route = g02 as Route;

describe('resolveDailyPlans', () => {
  it('single-day plan, returnToStart=false: forward path only', () => {
    const result = resolveDailyPlans({
      route,
      startNodeId: 'n_tataka',
      dailyPlans: [{ endNodeId: 'n_paiyun', endType: 'hut', viaNodeIds: [] }],
      returnToStart: false,
    });
    expect(result.days).toHaveLength(1);
    expect(result.nodeSequence[0]).toBe('n_tataka');
    expect(result.nodeSequence[result.nodeSequence.length - 1]).toBe('n_paiyun');
    expect(result.dayBreaks).toEqual([]);
    expect(result.warnings).toEqual([]);
  });

  it('single-day plan, returnToStart=true is now ignored by resolver: ends at daily.endNodeId', () => {
    // The resolver no longer rewrites the last day. returnToStart auto-fill is done
    // by the DailyPlanEditor toggle (onToggleReturnToStart) before the data reaches here.
    const result = resolveDailyPlans({
      route,
      startNodeId: 'n_tataka',
      dailyPlans: [{ endNodeId: 'n_paiyun', endType: 'hut', viaNodeIds: [] }],
      returnToStart: true,
    });
    expect(result.nodeSequence[0]).toBe('n_tataka');
    expect(result.nodeSequence[result.nodeSequence.length - 1]).toBe('n_paiyun');
  });

  it('single-day plan, returnToStart=true, end == start: no rewrite, returns single-node path', () => {
    const result = resolveDailyPlans({
      route,
      startNodeId: 'n_tataka',
      dailyPlans: [{ endNodeId: 'n_tataka', endType: 'manual', viaNodeIds: [] }],
      returnToStart: true,
    });
    expect(result.nodeSequence).toEqual(['n_tataka']);
    expect(result.warnings).toEqual([]);
  });

  it('two-day plan with via on day 2', () => {
    const result = resolveDailyPlans({
      route,
      startNodeId: 'n_tataka',
      dailyPlans: [
        { endNodeId: 'n_paiyun', endType: 'hut', viaNodeIds: [] },
        { endNodeId: 'n_yushan_main', endType: 'manual', viaNodeIds: [] },
      ],
      returnToStart: false,
    });
    expect(result.days).toHaveLength(2);
    expect(result.dayBreaks).toEqual([{ afterNodeId: 'n_paiyun', type: 'hut', hutId: undefined }]);
    expect(result.days[1].startNodeId).toBe('n_paiyun');
  });

  it('three-day plan: dayStart carries over correctly', () => {
    const result = resolveDailyPlans({
      route,
      startNodeId: 'n_tataka',
      dailyPlans: [
        { endNodeId: 'n_pailin', endType: 'manual', viaNodeIds: [] },
        { endNodeId: 'n_paiyun', endType: 'hut', viaNodeIds: [] },
        { endNodeId: 'n_yushan_main', endType: 'manual', viaNodeIds: [] },
      ],
      returnToStart: false,
    });
    expect(result.days).toHaveLength(3);
    expect(result.days[0].startNodeId).toBe('n_tataka');
    expect(result.days[1].startNodeId).toBe('n_pailin');
    expect(result.days[2].startNodeId).toBe('n_paiyun');
    expect(result.dayBreaks.map((b) => b.afterNodeId)).toEqual(['n_pailin', 'n_paiyun']);
  });

  it('returnToStart=true on multi-day: resolver no longer rewrites, ends at last daily.endNodeId', () => {
    // Resolver is now pass-through; auto-fill is done by DailyPlanEditor.onToggleReturnToStart
    const result = resolveDailyPlans({
      route,
      startNodeId: 'n_tataka',
      dailyPlans: [
        { endNodeId: 'n_paiyun', endType: 'hut', viaNodeIds: [] },
        { endNodeId: 'n_yushan_main', endType: 'manual', viaNodeIds: [] },
      ],
      returnToStart: true,
    });
    expect(result.nodeSequence[result.nodeSequence.length - 1]).toBe('n_yushan_main');
  });

  it('unreachable day: returns warning, still emits other days', () => {
    const isolatedRoute: Route = {
      ...route,
      nodes: [
        ...route.nodes,
        { id: 'n_island', name: 'Isolated', lat: 0, lng: 0, elevation: 0, category: 'waypoint' },
      ],
    };
    const result = resolveDailyPlans({
      route: isolatedRoute,
      startNodeId: 'n_tataka',
      dailyPlans: [
        { endNodeId: 'n_paiyun', endType: 'hut', viaNodeIds: [] },
        { endNodeId: 'n_island', endType: 'manual', viaNodeIds: [] },
      ],
      returnToStart: false,
    });
    expect(result.warnings).toContain('day_2_unreachable');
    expect(result.days[0].pathNodeIds.length).toBeGreaterThan(0);
    expect(result.days[1].pathNodeIds).toEqual([]);
  });

  it('consecutive days with same endNodeId: no warning, nodeSequence does not duplicate', () => {
    const result = resolveDailyPlans({
      route,
      startNodeId: 'n_tataka',
      dailyPlans: [
        { endNodeId: 'n_paiyun', endType: 'hut', viaNodeIds: [] },
        { endNodeId: 'n_paiyun', endType: 'hut', viaNodeIds: [] },
      ],
      returnToStart: false,
    });
    expect(result.warnings).toEqual([]);
    expect(result.nodeSequence[result.nodeSequence.length - 1]).toBe('n_paiyun');
  });

  it('empty dailyPlans: empty nodeSequence, no warning', () => {
    const result = resolveDailyPlans({
      route,
      startNodeId: 'n_tataka',
      dailyPlans: [],
      returnToStart: true,
    });
    expect(result.nodeSequence).toEqual([]);
    expect(result.days).toEqual([]);
  });
});
