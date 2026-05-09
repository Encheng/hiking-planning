import { describe, it, expect } from 'vitest';
import { resolvePath } from '@/services/PathResolver';
import g02 from '../fixtures/G02-test.json';
import type { Route } from '@/types';

const route = g02 as Route;

describe('PathResolver.resolvePath', () => {
  it('finds direct path between connected nodes', () => {
    const result = resolvePath({
      route,
      startNodeId: 'n_tataka',
      endNodeId: 'n_paiyun',
    });
    expect(result.forward).toEqual([
      'n_tataka', 'n_shang_dongpu', 'n_dietshan', 'n_pailin',
      'n_dachienshan', 'n_baimu', 'n_paiyun',
    ]);
    expect(result.warnings).toEqual([]);
  });

  it('auto-generates backward path (round trip)', () => {
    const result = resolvePath({
      route,
      startNodeId: 'n_tataka',
      endNodeId: 'n_yushan_main',
    });
    expect(result.forward[result.forward.length - 1]).toBe('n_yushan_main');
    expect(result.backward[0]).toBe('n_yushan_main');
    expect(result.backward[result.backward.length - 1]).toBe('n_tataka');
    expect(result.combined).toEqual([...result.forward, ...result.backward.slice(1)]);
    expect(result.isLoop).toBe(true);
  });

  it('respects viaNodeIds order', () => {
    const result = resolvePath({
      route,
      startNodeId: 'n_tataka',
      endNodeId: 'n_yushan_main',
      viaNodeIds: ['n_paiyun'],
    });
    expect(result.forward).toContain('n_paiyun');
    const paiyunIdx = result.forward.indexOf('n_paiyun');
    const peakIdx = result.forward.indexOf('n_yushan_main');
    expect(paiyunIdx).toBeLessThan(peakIdx);
  });

  it('warns when nodes are disconnected', () => {
    const isolatedRoute: Route = {
      ...route,
      nodes: [...route.nodes, { id: 'n_island', name: 'Isolated', lat: 0, lng: 0, elevation: 0, category: 'waypoint' }],
    };
    const result = resolvePath({
      route: isolatedRoute,
      startNodeId: 'n_tataka',
      endNodeId: 'n_island',
    });
    expect(result.warnings).toContain('no_path');
    expect(result.forward).toEqual([]);
  });

  it('returns single-node path when start equals end', () => {
    const result = resolvePath({
      route,
      startNodeId: 'n_tataka',
      endNodeId: 'n_tataka',
    });
    expect(result.forward).toEqual(['n_tataka']);
    expect(result.isLoop).toBe(false);
  });
});
