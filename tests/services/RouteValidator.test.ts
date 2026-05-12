import { describe, it, expect } from 'vitest';
import { validateRoute } from '@/services/RouteValidator';
import g02 from '../fixtures/G02-test.json';
import type { Route, Hut, RouteEdge } from '@/types';

const baseRoute = g02 as Route;
const baseHuts: Hut[] = [
  {
    id: 'hut_paiyun', name: '排雲山莊', lat: 23.4731, lng: 120.9534,
    elevation: 3402, capacity: 116, type: 'hut',
  },
];

function withEdges(route: Route, edges: RouteEdge[]): Route {
  return { ...route, edges };
}

describe('validateRoute', () => {
  it('valid G02 with confirmed edges → 0 errors', () => {
    const route: Route = {
      ...baseRoute,
      edges: baseRoute.edges.map((e) => ({ ...e, confirmed: true })),
    };
    const report = validateRoute({ route, huts: baseHuts });
    expect(report.errors).toBe(0);
  });

  it('edge references non-existing node → error', () => {
    const route = withEdges(baseRoute, [
      { from: 'n_tataka', to: 'n_nonexistent', minutes_forward: 10, minutes_backward: 10, source: 'x', confirmed: true },
    ]);
    const report = validateRoute({ route, huts: baseHuts });
    expect(report.issues.some((i) => i.type === 'edge_node_missing')).toBe(true);
  });

  it('self-loop edge → error', () => {
    const route = withEdges(baseRoute, [
      { from: 'n_tataka', to: 'n_tataka', minutes_forward: 10, minutes_backward: 10, source: 'x', confirmed: true },
    ]);
    const report = validateRoute({ route, huts: baseHuts });
    expect(report.issues.some((i) => i.type === 'self_loop')).toBe(true);
  });

  it('edge with negative time → error', () => {
    const route = withEdges(baseRoute, [
      { from: 'n_tataka', to: 'n_paiyun', minutes_forward: -5, minutes_backward: 10, source: 'x', confirmed: true },
    ]);
    const report = validateRoute({ route, huts: baseHuts });
    expect(report.issues.some((i) => i.type === 'edge_time_invalid')).toBe(true);
  });

  it('edge confirmed=false → error', () => {
    const route = withEdges(baseRoute, [
      { from: 'n_tataka', to: 'n_shang_dongpu', minutes_forward: 10, minutes_backward: 10, source: 'x', confirmed: false },
    ]);
    const report = validateRoute({ route, huts: baseHuts });
    expect(report.issues.some((i) => i.type === 'edge_unconfirmed')).toBe(true);
  });

  it('node hutId references missing hut → error', () => {
    const route: Route = {
      ...baseRoute,
      nodes: baseRoute.nodes.map((n) =>
        n.id === 'n_paiyun' ? { ...n, hutId: 'hut_missing' } : n,
      ),
      edges: baseRoute.edges.map((e) => ({ ...e, confirmed: true })),
    };
    const report = validateRoute({ route, huts: baseHuts });
    expect(report.issues.some((i) => i.type === 'hut_missing')).toBe(true);
  });

  it('node missing lat/lng → error', () => {
    const route: Route = {
      ...baseRoute,
      nodes: baseRoute.nodes.map((n) =>
        n.id === 'n_tataka' ? { ...n, lat: 0, lng: 0 } : n,
      ),
      edges: baseRoute.edges.map((e) => ({ ...e, confirmed: true })),
    };
    const report = validateRoute({ route, huts: baseHuts });
    expect(report.issues.some((i) => i.type === 'node_missing_coords')).toBe(true);
  });

  it('duplicate node id → error', () => {
    const route: Route = {
      ...baseRoute,
      nodes: [...baseRoute.nodes, { ...baseRoute.nodes[0] }],
      edges: baseRoute.edges.map((e) => ({ ...e, confirmed: true })),
    };
    const report = validateRoute({ route, huts: baseHuts });
    expect(report.issues.some((i) => i.type === 'duplicate_node_id')).toBe(true);
  });

  it('preset references non-existing node → error', () => {
    const route: Route = {
      ...baseRoute,
      presets: [{
        id: 'p1', name: 'broken', startNodeId: 'n_tataka', endNodeId: 'n_does_not_exist',
        viaNodeIds: [],
      }],
      edges: baseRoute.edges.map((e) => ({ ...e, confirmed: true })),
    };
    const report = validateRoute({ route, huts: baseHuts });
    expect(report.issues.some((i) => i.type === 'preset_node_missing')).toBe(true);
  });

  it('preset path unresolvable → error', () => {
    const route: Route = {
      ...baseRoute,
      nodes: [...baseRoute.nodes, {
        id: 'n_island', name: 'island', lat: 0.1, lng: 0.1, elevation: 0, category: 'waypoint',
      }],
      presets: [{
        id: 'p1', name: 'broken', startNodeId: 'n_tataka', endNodeId: 'n_island',
        viaNodeIds: [],
      }],
      edges: baseRoute.edges.map((e) => ({ ...e, confirmed: true })),
    };
    const report = validateRoute({ route, huts: baseHuts });
    expect(report.issues.some((i) => i.type === 'preset_unresolvable')).toBe(true);
  });

  it('disconnected graph → warning', () => {
    const route: Route = {
      ...baseRoute,
      nodes: [...baseRoute.nodes, {
        id: 'n_orphan', name: 'orphan', lat: 23.5, lng: 121, elevation: 1000, category: 'waypoint',
      }],
      edges: baseRoute.edges.map((e) => ({ ...e, confirmed: true })),
    };
    const report = validateRoute({ route, huts: baseHuts });
    expect(report.issues.some((i) => i.type === 'disconnected_graph' && i.severity === 'warning')).toBe(true);
  });

  it('unreasonable speed → warning', () => {
    const route: Route = {
      ...baseRoute,
      edges: baseRoute.edges.map((e, i) => i === 0 ? {
        ...e, minutes_forward: 1, minutes_backward: 1, confirmed: true,
      } : { ...e, confirmed: true }),
    };
    const report = validateRoute({ route, huts: baseHuts });
    expect(report.issues.some((i) => i.type === 'unreasonable_speed' && i.severity === 'warning')).toBe(true);
  });

  it('route with no peak → warning', () => {
    const route: Route = {
      ...baseRoute,
      nodes: baseRoute.nodes.map((n) =>
        n.category === 'peak' ? { ...n, category: 'waypoint' } : n,
      ),
      edges: baseRoute.edges.map((e) => ({ ...e, confirmed: true })),
    };
    const report = validateRoute({ route, huts: baseHuts });
    expect(report.issues.some((i) => i.type === 'missing_categories' && i.severity === 'warning')).toBe(true);
  });
});
