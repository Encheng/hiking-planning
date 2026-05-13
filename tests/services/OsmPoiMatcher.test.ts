import { describe, it, expect } from 'vitest';
import { normalizeName, matchPoisToNode } from '@/services/OsmPoiMatcher';
import type { OsmPoi } from '@/types';

function poi(id: string, name: string): OsmPoi {
  return {
    id,
    name,
    lat: 23.5,
    lon: 121,
    elevation: 3000,
    tags: { category: 'waypoint', raw: {} },
  };
}

describe('normalizeName', () => {
  it('removes common suffixes', () => {
    expect(normalizeName('排雲山莊')).toBe('排雲');
    expect(normalizeName('玉山步道')).toBe('玉山');
    expect(normalizeName('塔塔加登山口')).toBe('塔塔加');
  });

  it('lowercases latin', () => {
    expect(normalizeName('Yushan')).toBe('yushan');
  });

  it('treats arabic digits and chinese digits equivalently', () => {
    expect(normalizeName('369')).toBe(normalizeName('三六九'));
  });

  it('normalizes full-width to half-width', () => {
    expect(normalizeName('ＡＢＣ')).toBe('abc');
  });
});

describe('matchPoisToNode', () => {
  const pois: OsmPoi[] = [
    poi('p1', '排雲山莊'),
    poi('p2', '369 山屋'),
    poi('p3', '玉山主峰'),
    poi('p4', '完全無關'),
  ];

  it('exact match has similarity 1.0', () => {
    const result = matchPoisToNode('排雲山莊', pois);
    expect(result[0].poi.id).toBe('p1');
    expect(result[0].similarity).toBe(1.0);
  });

  it('similar names get high similarity', () => {
    const result = matchPoisToNode('三六九山屋', pois);
    expect(result[0].poi.id).toBe('p2');
    expect(result[0].similarity).toBeGreaterThan(0.7);
  });

  it('returns candidates sorted by descending similarity', () => {
    const result = matchPoisToNode('排雲', pois);
    for (let i = 1; i < result.length; i++) {
      expect(result[i].similarity).toBeLessThanOrEqual(result[i - 1].similarity);
    }
  });

  it('filters out matches below 0.5 threshold', () => {
    const result = matchPoisToNode('排雲', pois);
    expect(result.every((r) => r.similarity > 0.5)).toBe(true);
    expect(result.find((r) => r.poi.id === 'p4')).toBeUndefined();
  });
});
