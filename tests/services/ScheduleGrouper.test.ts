import { describe, it, expect } from 'vitest';
import { groupByDayBreaks } from '@/services/ScheduleGrouper';
import { calculateTimes } from '@/services/TimeCalculator';
import g02 from '../fixtures/G02-test.json';
import type { Route, Plan } from '@/types';

const route = g02 as Route;

function makePlan(overrides: Partial<Plan> = {}): Plan {
  return {
    name: 'test',
    routeId: 'G02',
    startNodeId: 'n_tataka',
    endNodeId: 'n_yushan_main',
    nodeSequence: [],
    paceMultiplier: 1.0,
    startDate: '2026-06-15',
    startTime: '06:00',
    dayBreaks: [],
    tripType: 'overnight_hut',
    createdAt: '2026-05-09T00:00:00Z',
    ...overrides,
  };
}

describe('ScheduleGrouper.groupByDayBreaks', () => {
  it('returns one DayGroup when there are no breaks', () => {
    const plan = makePlan({
      nodeSequence: ['n_tataka', 'n_shang_dongpu', 'n_dietshan'],
    });
    const segments = calculateTimes({
      route,
      nodeSequence: plan.nodeSequence,
      paceMultiplier: 1.0,
      startDateTime: '2026-06-15T06:00:00',
    }).segments;
    const groups = groupByDayBreaks({ plan, route, segments });
    expect(groups).toHaveLength(1);
    expect(groups[0].index).toBe(1);
    expect(groups[0].date).toBe('2026-06-15');
    expect(groups[0].startNode.id).toBe('n_tataka');
    expect(groups[0].endNode.id).toBe('n_dietshan');
    expect(groups[0].daySegments).toHaveLength(2);
  });

  it('splits into two days when one dayBreak is present', () => {
    const plan = makePlan({
      nodeSequence: ['n_tataka', 'n_shang_dongpu', 'n_dietshan', 'n_pailin', 'n_dachienshan', 'n_baimu', 'n_paiyun', 'n_yushan_main'],
      dayBreaks: [{ afterNodeId: 'n_paiyun', type: 'hut', hutId: 'hut_paiyun' }],
    });
    const segments = calculateTimes({
      route,
      nodeSequence: plan.nodeSequence,
      paceMultiplier: 1.0,
      startDateTime: '2026-06-15T06:00:00',
    }).segments;
    const groups = groupByDayBreaks({ plan, route, segments });
    expect(groups).toHaveLength(2);
    expect(groups[0].endNode.id).toBe('n_paiyun');
    expect(groups[0].date).toBe('2026-06-15');
    expect(groups[1].startNode.id).toBe('n_paiyun');
    expect(groups[1].endNode.id).toBe('n_yushan_main');
    expect(groups[1].date).toBe('2026-06-16');
    expect(groups[1].index).toBe(2);
  });

  it('identifies peakNode as the highest elevation toNode in the day', () => {
    const plan = makePlan({
      nodeSequence: ['n_tataka', 'n_shang_dongpu', 'n_dietshan', 'n_pailin', 'n_dachienshan', 'n_baimu', 'n_paiyun', 'n_yushan_main'],
      dayBreaks: [{ afterNodeId: 'n_paiyun', type: 'hut', hutId: 'hut_paiyun' }],
    });
    const segments = calculateTimes({
      route,
      nodeSequence: plan.nodeSequence,
      paceMultiplier: 1.0,
      startDateTime: '2026-06-15T06:00:00',
    }).segments;
    const groups = groupByDayBreaks({ plan, route, segments });
    expect(groups[0].peakNode?.id).toBe('n_paiyun');
    expect(groups[1].peakNode?.id).toBe('n_yushan_main');
  });

  it('handles month boundary in date increment', () => {
    const plan = makePlan({
      startDate: '2026-06-30',
      nodeSequence: ['n_tataka', 'n_paiyun', 'n_yushan_main'],
      dayBreaks: [{ afterNodeId: 'n_paiyun', type: 'hut', hutId: 'hut_paiyun' }],
    });
    const segments = [
      { fromNodeId: 'n_tataka', toNodeId: 'n_paiyun', baseMinutes: 270, adjustedMinutes: 270, arrivalTime: '2026-06-30T10:30:00.000Z', cumulativeMinutes: 270, direction: 'forward' as const },
      { fromNodeId: 'n_paiyun', toNodeId: 'n_yushan_main', baseMinutes: 90, adjustedMinutes: 90, arrivalTime: '2026-07-01T01:30:00.000Z', cumulativeMinutes: 360, direction: 'forward' as const },
    ];
    const groups = groupByDayBreaks({ plan, route, segments });
    expect(groups[1].date).toBe('2026-07-01');
  });

  it('startTime/endTime reflect first and last segment arrival within day', () => {
    const plan = makePlan({
      nodeSequence: ['n_tataka', 'n_shang_dongpu', 'n_dietshan'],
    });
    const segments = calculateTimes({
      route,
      nodeSequence: plan.nodeSequence,
      paceMultiplier: 1.0,
      startDateTime: '2026-06-15T06:00:00',
    }).segments;
    const groups = groupByDayBreaks({ plan, route, segments });
    expect(groups[0].startTime).toBe('06:00');
    expect(groups[0].endTime).toMatch(/^\d{2}:\d{2}$/);
  });
});
