import type { Route, RouteEdge, SegmentTime } from '@/types';

export interface TimeInput {
  route: Route;
  nodeSequence: string[];
  paceMultiplier: number;
  startDateTime: string;
}

export interface TimeOutput {
  segments: SegmentTime[];
  totalMinutes: number;
  totalAdjustedMinutes: number;
}

function findEdge(edges: RouteEdge[], a: string, b: string): { edge: RouteEdge; direction: 'forward' | 'backward' } {
  for (const edge of edges) {
    if (edge.from === a && edge.to === b) return { edge, direction: 'forward' };
    if (edge.from === b && edge.to === a) return { edge, direction: 'backward' };
  }
  throw new Error(`no edge between ${a} and ${b}`);
}

function parseAsUtc(input: string): number {
  // If no timezone marker, treat as UTC for deterministic test behaviour
  if (/Z|[+-]\d\d:?\d\d$/.test(input)) {
    return new Date(input).getTime();
  }
  return new Date(input + 'Z').getTime();
}

export function calculateTimes(input: TimeInput): TimeOutput {
  const { route, nodeSequence, paceMultiplier, startDateTime } = input;
  const segments: SegmentTime[] = [];
  let cumulativeMinutes = 0;
  const startMs = parseAsUtc(startDateTime);

  for (let i = 0; i < nodeSequence.length - 1; i++) {
    const from = nodeSequence[i];
    const to = nodeSequence[i + 1];
    const { edge, direction } = findEdge(route.edges, from, to);
    const baseMinutes = direction === 'forward' ? edge.minutes_forward : edge.minutes_backward;
    const adjustedMinutes = Math.round(baseMinutes * paceMultiplier);
    cumulativeMinutes += adjustedMinutes;
    const arrivalTime = new Date(startMs + cumulativeMinutes * 60_000).toISOString();
    segments.push({
      fromNodeId: from,
      toNodeId: to,
      baseMinutes,
      adjustedMinutes,
      arrivalTime,
      cumulativeMinutes,
      direction,
    });
  }

  const totalMinutes = segments.reduce((s, x) => s + x.baseMinutes, 0);
  const totalAdjustedMinutes = cumulativeMinutes;
  return { segments, totalMinutes, totalAdjustedMinutes };
}
