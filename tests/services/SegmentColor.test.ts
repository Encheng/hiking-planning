import { describe, it, expect } from 'vitest';
import { segmentTrend, segmentColor } from '@/services/SegmentColor';
import g02 from '../fixtures/G02-test.json';
import type { Route, SegmentTime } from '@/types';

const route = g02 as Route;

function seg(fromId: string, toId: string, minutes: number): SegmentTime {
  return {
    fromNodeId: fromId,
    toNodeId: toId,
    baseMinutes: minutes,
    adjustedMinutes: minutes,
    arrivalTime: '2026-06-15T06:00:00.000Z',
    cumulativeMinutes: minutes,
    direction: 'forward',
  };
}

describe('segmentTrend', () => {
  it('returns climb when ascent rate > 50 m/h', () => {
    expect(segmentTrend(seg('n_paiyun', 'n_yushan_main', 60), route)).toBe('climb');
  });

  it('returns descent when descent rate > 50 m/h', () => {
    expect(segmentTrend(seg('n_yushan_main', 'n_paiyun', 60), route)).toBe('descent');
  });

  it('returns flat when rate is within +/- 50 m/h', () => {
    expect(segmentTrend(seg('n_shang_dongpu', 'n_tataka', 60), route)).toBe('flat');
  });

  it('returns flat when adjustedMinutes is 0 (degenerate)', () => {
    const degenerate: SegmentTime = { ...seg('n_paiyun', 'n_yushan_main', 0), adjustedMinutes: 0 };
    expect(segmentTrend(degenerate, route)).toBe('flat');
  });

  it('returns flat when nodes not found in route', () => {
    expect(segmentTrend(seg('n_unknown_a', 'n_unknown_b', 60), route)).toBe('flat');
  });
});

describe('segmentColor', () => {
  it('returns climb color #fb923c for climb', () => {
    expect(segmentColor(seg('n_paiyun', 'n_yushan_main', 60), route)).toBe('#fb923c');
  });

  it('returns descent color #86efac for descent', () => {
    expect(segmentColor(seg('n_yushan_main', 'n_paiyun', 60), route)).toBe('#86efac');
  });

  it('returns flat color #fcd34d for flat', () => {
    expect(segmentColor(seg('n_shang_dongpu', 'n_tataka', 60), route)).toBe('#fcd34d');
  });
});
