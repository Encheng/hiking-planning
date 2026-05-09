import { describe, it, expect } from 'vitest';
import { calculateTimes } from '@/services/TimeCalculator';
import g02 from '../fixtures/G02-test.json';
import type { Route } from '@/types';

const route = g02 as Route;

describe('TimeCalculator.calculateTimes', () => {
  it('uses minutes_forward for forward direction', () => {
    const result = calculateTimes({
      route,
      nodeSequence: ['n_tataka', 'n_shang_dongpu'],
      paceMultiplier: 1.0,
      startDateTime: '2026-06-15T06:00:00',
    });
    expect(result.segments).toHaveLength(1);
    expect(result.segments[0].baseMinutes).toBe(10);
    expect(result.segments[0].adjustedMinutes).toBe(10);
    expect(result.segments[0].direction).toBe('forward');
    expect(result.segments[0].arrivalTime).toBe('2026-06-15T06:10:00.000Z');
  });

  it('uses minutes_backward for reverse direction', () => {
    const result = calculateTimes({
      route,
      nodeSequence: ['n_dietshan', 'n_shang_dongpu'],
      paceMultiplier: 1.0,
      startDateTime: '2026-06-15T06:00:00',
    });
    expect(result.segments[0].baseMinutes).toBe(25);
    expect(result.segments[0].direction).toBe('backward');
  });

  it('applies pace multiplier and rounds to nearest minute', () => {
    const result = calculateTimes({
      route,
      nodeSequence: ['n_tataka', 'n_shang_dongpu'],
      paceMultiplier: 1.5,
      startDateTime: '2026-06-15T06:00:00',
    });
    expect(result.segments[0].adjustedMinutes).toBe(15);
  });

  it('accumulates total time across multiple segments', () => {
    const result = calculateTimes({
      route,
      nodeSequence: ['n_tataka', 'n_shang_dongpu', 'n_dietshan'],
      paceMultiplier: 1.0,
      startDateTime: '2026-06-15T06:00:00',
    });
    expect(result.segments[1].cumulativeMinutes).toBe(30);
    expect(result.totalMinutes).toBe(30);
    expect(result.totalAdjustedMinutes).toBe(30);
  });

  it('rejects unknown node pairs (no edge)', () => {
    expect(() => calculateTimes({
      route,
      nodeSequence: ['n_tataka', 'n_yushan_main'],
      paceMultiplier: 1.0,
      startDateTime: '2026-06-15T06:00:00',
    })).toThrow(/no edge/i);
  });
});
