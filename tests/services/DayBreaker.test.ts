import { describe, it, expect } from 'vitest';
import { suggestBreaks } from '@/services/DayBreaker';
import { calculateTimes } from '@/services/TimeCalculator';
import g02 from '../fixtures/G02-test.json';
import hutsData from '../../public/data/huts.json';
import type { Route, Hut } from '@/types';

const route = g02 as Route;
const huts = hutsData as Hut[];

function segmentsForRoundTrip(multiplier = 1.0) {
  return calculateTimes({
    route,
    nodeSequence: [
      'n_tataka', 'n_shang_dongpu', 'n_dietshan', 'n_pailin',
      'n_dachienshan', 'n_baimu', 'n_paiyun', 'n_yushan_main',
      'n_paiyun', 'n_baimu', 'n_dachienshan', 'n_pailin',
      'n_dietshan', 'n_shang_dongpu', 'n_tataka',
    ],
    paceMultiplier: multiplier,
    startDateTime: '2026-06-15T06:00:00',
  }).segments;
}

describe('DayBreaker.suggestBreaks', () => {
  it('returns no breaks when total time fits in one day', () => {
    const segments = calculateTimes({
      route,
      nodeSequence: ['n_tataka', 'n_shang_dongpu', 'n_dietshan'],
      paceMultiplier: 1.0,
      startDateTime: '2026-06-15T06:00:00',
    }).segments;
    const breaks = suggestBreaks({ route, segments, huts, maxDailyHours: 8, preferredBreakType: 'auto' });
    expect(breaks).toEqual([]);
  });

  it('inserts a break at the nearest hut when daily limit exceeded', () => {
    const segments = segmentsForRoundTrip(1.0);
    const breaks = suggestBreaks({ route, segments, huts, maxDailyHours: 5, preferredBreakType: 'auto' });
    expect(breaks.length).toBeGreaterThan(0);
    expect(breaks[0].afterNodeId).toBe('n_paiyun');
    expect(breaks[0].type).toBe('hut');
    expect(breaks[0].hutId).toBe('hut_paiyun');
  });

  it('falls back to camp when no hut is within 60 min', () => {
    const segments = segmentsForRoundTrip(1.0);
    const breaks = suggestBreaks({ route, segments, huts: [], maxDailyHours: 4, preferredBreakType: 'auto' });
    expect(breaks.length).toBeGreaterThan(0);
    expect(breaks[0].type).toBe('camp');
  });

  it('resets daily counter after a break', () => {
    const segments = segmentsForRoundTrip(2.0);
    const breaks = suggestBreaks({ route, segments, huts, maxDailyHours: 6, preferredBreakType: 'auto' });
    expect(breaks.length).toBeGreaterThanOrEqual(2);
  });
});
