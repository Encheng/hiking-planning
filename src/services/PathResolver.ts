import type { Route } from '@/types';

export interface PathInput {
  route: Route;
  startNodeId: string;
  endNodeId: string;
  viaNodeIds?: string[];
}

export interface PathOutput {
  forward: string[];
  backward: string[];
  combined: string[];
  isLoop: boolean;
  warnings: string[];
}

function buildAdjacency(route: Route): Map<string, string[]> {
  const adj = new Map<string, string[]>();
  for (const node of route.nodes) adj.set(node.id, []);
  for (const edge of route.edges) {
    adj.get(edge.from)?.push(edge.to);
    adj.get(edge.to)?.push(edge.from);
  }
  return adj;
}

function bfs(adj: Map<string, string[]>, start: string, end: string): string[] {
  if (start === end) return [start];
  const queue: string[][] = [[start]];
  const visited = new Set([start]);
  while (queue.length > 0) {
    const path = queue.shift()!;
    const node = path[path.length - 1];
    for (const next of adj.get(node) ?? []) {
      if (visited.has(next)) continue;
      if (next === end) return [...path, next];
      visited.add(next);
      queue.push([...path, next]);
    }
  }
  return [];
}

function chainSegments(adj: Map<string, string[]>, points: string[]): string[] {
  if (points.length < 2) return points;
  const result: string[] = [points[0]];
  for (let i = 0; i < points.length - 1; i++) {
    const seg = bfs(adj, points[i], points[i + 1]);
    if (seg.length === 0) return [];
    result.push(...seg.slice(1));
  }
  return result;
}

export function resolvePath(input: PathInput): PathOutput {
  const { route, startNodeId, endNodeId, viaNodeIds = [] } = input;
  const adj = buildAdjacency(route);
  const points = [startNodeId, ...viaNodeIds, endNodeId];
  const forward = chainSegments(adj, points);
  const warnings: string[] = [];
  if (forward.length === 0) warnings.push('no_path');

  const isLoop = startNodeId !== endNodeId && forward.length > 0;
  const backward = isLoop ? [...forward].reverse() : [];
  const combined = isLoop ? [...forward, ...backward.slice(1)] : forward;

  return { forward, backward, combined, isLoop, warnings };
}
