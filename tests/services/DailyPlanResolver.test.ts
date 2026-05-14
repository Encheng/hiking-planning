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

  it('single-day plan, returnToStart=true: resolver appends return path so trip ends at startNodeId', () => {
    const result = resolveDailyPlans({
      route,
      startNodeId: 'n_tataka',
      dailyPlans: [{ endNodeId: 'n_paiyun', endType: 'hut', viaNodeIds: [] }],
      returnToStart: true,
    });
    expect(result.nodeSequence[0]).toBe('n_tataka');
    // Last node should be back at start
    expect(result.nodeSequence[result.nodeSequence.length - 1]).toBe('n_tataka');
    // 排雲山莊 should appear in the middle (turn-around point)
    expect(result.nodeSequence).toContain('n_paiyun');
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

  it('returnToStart=true on multi-day: resolver appends return on last day, ends at startNodeId', () => {
    const result = resolveDailyPlans({
      route,
      startNodeId: 'n_tataka',
      dailyPlans: [
        { endNodeId: 'n_paiyun', endType: 'hut', viaNodeIds: [] },
        { endNodeId: 'n_yushan_main', endType: 'manual', viaNodeIds: [] },
      ],
      returnToStart: true,
    });
    // Trip ends at start after returning
    expect(result.nodeSequence[result.nodeSequence.length - 1]).toBe('n_tataka');
    // Both peak and hut still in sequence
    expect(result.nodeSequence).toContain('n_yushan_main');
    expect(result.nodeSequence).toContain('n_paiyun');
    // Day breaks unchanged (no break added for return)
    expect(result.dayBreaks).toHaveLength(1);
    expect(result.dayBreaks[0].afterNodeId).toBe('n_paiyun');
  });

  it('returnToStart=true but last endNodeId already equals startNodeId: no double-appending', () => {
    // Backward-compat: old saved plans had viaNodeIds already containing the return.
    // Resolver should NOT add another return in this case.
    const result = resolveDailyPlans({
      route,
      startNodeId: 'n_tataka',
      dailyPlans: [
        { endNodeId: 'n_tataka', endType: 'manual', viaNodeIds: ['n_paiyun'] },
      ],
      returnToStart: true,
    });
    expect(result.nodeSequence[0]).toBe('n_tataka');
    expect(result.nodeSequence[result.nodeSequence.length - 1]).toBe('n_tataka');
    // n_tataka appears at start and end, but n_paiyun only once in the middle
    const paiyunCount = result.nodeSequence.filter((n) => n === 'n_paiyun').length;
    expect(paiyunCount).toBe(1);
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
