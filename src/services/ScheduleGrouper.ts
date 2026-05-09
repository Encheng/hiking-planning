import type { Plan, Route, RouteNode, SegmentTime } from '@/types';

export interface DayGroup {
  index: number;
  date: string;
  startNode: RouteNode;
  endNode: RouteNode;
  startTime: string;
  endTime: string;
  totalAdjustedMinutes: number;
  daySegments: SegmentTime[];
  peakNode?: RouteNode;
}

export interface GrouperInput {
  plan: Plan;
  route: Route;
  segments: SegmentTime[];
}

function findNode(route: Route, id: string): RouteNode {
  const n = route.nodes.find((x) => x.id === id);
  if (!n) throw new Error(`Node not found: ${id}`);
  return n;
}

function fmtTimeFromIso(iso: string): string {
  const d = new Date(iso);
  return `${String(d.getUTCHours()).padStart(2, '0')}:${String(d.getUTCMinutes()).padStart(2, '0')}`;
}

function addDays(yyyymmdd: string, days: number): string {
  const [y, m, d] = yyyymmdd.split('-').map(Number);
  const date = new Date(Date.UTC(y, m - 1, d));
  date.setUTCDate(date.getUTCDate() + days);
  const yy = date.getUTCFullYear();
  const mm = String(date.getUTCMonth() + 1).padStart(2, '0');
  const dd = String(date.getUTCDate()).padStart(2, '0');
  return `${yy}-${mm}-${dd}`;
}

function pickPeak(route: Route, segs: SegmentTime[]): RouteNode | undefined {
  let best: RouteNode | undefined;
  for (const s of segs) {
    const n = route.nodes.find((x) => x.id === s.toNodeId);
    if (!n) continue;
    if (!best || n.elevation > best.elevation) best = n;
  }
  return best;
}

export function groupByDayBreaks(input: GrouperInput): DayGroup[] {
  const { plan, route, segments } = input;
  if (segments.length === 0) return [];

  const breakSet = new Set(plan.dayBreaks.map((b) => b.afterNodeId));
  const groups: DayGroup[] = [];

  let dayIdx = 1;
  let dayStartIdx = 0;
  let dayStartNodeId = plan.startNodeId;
  let dayStartTime = plan.startTime;

  function flushDay(endIdx: number, endNodeId: string) {
    const daySegments = segments.slice(dayStartIdx, endIdx + 1);
    const totalAdjustedMinutes = daySegments.reduce((s, x) => s + x.adjustedMinutes, 0);
    groups.push({
      index: dayIdx,
      date: addDays(plan.startDate, dayIdx - 1),
      startNode: findNode(route, dayStartNodeId),
      endNode: findNode(route, endNodeId),
      startTime: dayStartTime,
      endTime: fmtTimeFromIso(daySegments[daySegments.length - 1].arrivalTime),
      totalAdjustedMinutes,
      daySegments,
      peakNode: pickPeak(route, daySegments),
    });
  }

  for (let i = 0; i < segments.length; i++) {
    const seg = segments[i];
    if (breakSet.has(seg.toNodeId)) {
      flushDay(i, seg.toNodeId);
      dayIdx += 1;
      dayStartIdx = i + 1;
      dayStartNodeId = seg.toNodeId;
      if (dayStartIdx < segments.length) {
        const segMins = segments[dayStartIdx].adjustedMinutes;
        const arrivalMs = new Date(segments[dayStartIdx].arrivalTime).getTime();
        const startMs = arrivalMs - segMins * 60_000;
        const startD = new Date(startMs);
        dayStartTime = `${String(startD.getUTCHours()).padStart(2, '0')}:${String(startD.getUTCMinutes()).padStart(2, '0')}`;
      } else {
        dayStartTime = '00:00';
      }
    }
  }

  if (dayStartIdx < segments.length) {
    flushDay(segments.length - 1, segments[segments.length - 1].toNodeId);
  }

  return groups;
}
