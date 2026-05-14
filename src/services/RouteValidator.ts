import type { Route, Hut, ValidationIssue, ValidationReport, RouteNode } from '@/types';
import { resolvePath } from './PathResolver';

export interface ValidateInput {
  route: Route;
  huts: Hut[];
}

function haversineKm(a: RouteNode, b: RouteNode): number {
  const R = 6371;
  const dLat = ((b.lat - a.lat) * Math.PI) / 180;
  const dLon = ((b.lng - a.lng) * Math.PI) / 180;
  const aa =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((a.lat * Math.PI) / 180) *
      Math.cos((b.lat * Math.PI) / 180) *
      Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(aa), Math.sqrt(1 - aa));
}

function nodeIndex(route: Route): Map<string, RouteNode> {
  return new Map(route.nodes.map((n) => [n.id, n]));
}

function findConnectedGroups(route: Route): number {
  const adj = new Map<string, Set<string>>();
  for (const n of route.nodes) adj.set(n.id, new Set());
  for (const e of route.edges) {
    adj.get(e.from)?.add(e.to);
    adj.get(e.to)?.add(e.from);
  }
  const visited = new Set<string>();
  let groups = 0;
  for (const n of route.nodes) {
    if (visited.has(n.id)) continue;
    groups++;
    const queue = [n.id];
    while (queue.length) {
      const cur = queue.shift()!;
      if (visited.has(cur)) continue;
      visited.add(cur);
      for (const next of adj.get(cur) ?? []) {
        if (!visited.has(next)) queue.push(next);
      }
    }
  }
  return groups;
}

export function validateRoute(input: ValidateInput): ValidationReport {
  const { route, huts } = input;
  const issues: ValidationIssue[] = [];
  const nodesById = nodeIndex(route);
  const hutIds = new Set(huts.map((h) => h.id));

  for (const e of route.edges) {
    if (!nodesById.has(e.from) || !nodesById.has(e.to)) {
      issues.push({
        severity: 'error', route: route.id, type: 'edge_node_missing',
        message: `Edge ${e.from} → ${e.to} references non-existing node`,
        ref: `${e.from}__${e.to}`,
      });
    }
    if (e.from === e.to) {
      issues.push({
        severity: 'error', route: route.id, type: 'self_loop',
        message: `Edge ${e.from} → ${e.to} is a self-loop`,
        ref: `${e.from}__${e.to}`,
      });
    }
    if (e.minutes_forward < 0 || e.minutes_backward < 0) {
      issues.push({
        severity: 'error', route: route.id, type: 'edge_time_invalid',
        message: `Edge ${e.from} → ${e.to} has negative time`,
        ref: `${e.from}__${e.to}`,
      });
    }
    if (e.confirmed === false) {
      issues.push({
        severity: 'error', route: route.id, type: 'edge_unconfirmed',
        message: `Edge ${e.from} → ${e.to} not confirmed`,
        ref: `${e.from}__${e.to}`,
      });
    }
  }

  const seenIds = new Set<string>();
  for (const n of route.nodes) {
    if (seenIds.has(n.id)) {
      issues.push({
        severity: 'error', route: route.id, type: 'duplicate_node_id',
        message: `Duplicate node id ${n.id}`,
        ref: n.id,
      });
    }
    seenIds.add(n.id);
    if (n.lat === 0 && n.lng === 0) {
      issues.push({
        severity: 'error', route: route.id, type: 'node_missing_coords',
        message: `Node ${n.id} missing lat/lng`,
        ref: n.id,
      });
    }
    if (n.hutId && !hutIds.has(n.hutId)) {
      issues.push({
        severity: 'error', route: route.id, type: 'hut_missing',
        message: `Node ${n.id} references missing hut ${n.hutId}`,
        ref: n.id,
      });
    }
    if (n.elevation === undefined || n.elevation === null) {
      issues.push({
        severity: 'warning', route: route.id, type: 'missing_elevation',
        message: `Node ${n.id} missing elevation`,
        ref: n.id,
      });
    }
  }

  for (const p of route.presets) {
    const referenced = [p.startNodeId, p.endNodeId, ...(p.viaNodeIds ?? [])];
    for (const nid of referenced) {
      if (!nodesById.has(nid)) {
        issues.push({
          severity: 'error', route: route.id, type: 'preset_node_missing',
          message: `Preset "${p.name}" references missing node ${nid}`,
          ref: p.id,
        });
      }
    }
    const pathResult = resolvePath({
      route, startNodeId: p.startNodeId, endNodeId: p.endNodeId,
      viaNodeIds: p.viaNodeIds ?? [],
    });
    if (pathResult.warnings.includes('no_path')) {
      issues.push({
        severity: 'error', route: route.id, type: 'preset_unresolvable',
        message: `Preset "${p.name}" cannot resolve path from ${p.startNodeId} to ${p.endNodeId}`,
        ref: p.id,
      });
    }
  }

  const groups = findConnectedGroups(route);
  if (groups > 1) {
    issues.push({
      severity: 'warning', route: route.id, type: 'disconnected_graph',
      message: `Graph has ${groups} disconnected components`,
    });
  }

  for (const e of route.edges) {
    if (e.transport === 'vehicle') continue;  // vehicle drives have road speed, not hiking speed
    const from = nodesById.get(e.from);
    const to = nodesById.get(e.to);
    if (!from || !to) continue;
    const km = haversineKm(from, to);
    if (km <= 0 || e.minutes_forward <= 0) continue;
    const speed = km / (e.minutes_forward / 60);
    if (speed > 10 || speed < 0.1) {
      issues.push({
        severity: 'warning', route: route.id, type: 'unreasonable_speed',
        message: `Edge ${e.from} → ${e.to}: ${e.minutes_forward}min for ${km.toFixed(2)}km (${speed.toFixed(1)}km/h)`,
        ref: `${e.from}__${e.to}`,
      });
    }
  }

  const cats = new Set(route.nodes.map((n) => n.category));
  if (!cats.has('trailhead') || !cats.has('peak')) {
    issues.push({
      severity: 'warning', route: route.id, type: 'missing_categories',
      message: `Route lacks trailhead or peak nodes`,
    });
  }

  return {
    errors: issues.filter((i) => i.severity === 'error').length,
    warnings: issues.filter((i) => i.severity === 'warning').length,
    issues,
  };
}
