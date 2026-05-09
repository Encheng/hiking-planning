import type { Route, DailyPlan, DayBreak, DayResolution, DailyPlanResolveOutput } from '@/types';
import { resolvePath } from './PathResolver';

export interface ResolveInput {
  route: Route;
  startNodeId: string;
  dailyPlans: DailyPlan[];
  returnToStart: boolean;
}

function makeSegments(pathNodeIds: string[]): Array<{ from: string; to: string }> {
  const segs: Array<{ from: string; to: string }> = [];
  for (let i = 0; i < pathNodeIds.length - 1; i++) {
    segs.push({ from: pathNodeIds[i], to: pathNodeIds[i + 1] });
  }
  return segs;
}

export function resolveDailyPlans(input: ResolveInput): DailyPlanResolveOutput {
  const { route, startNodeId, dailyPlans, returnToStart } = input;

  const days: DayResolution[] = [];
  const dayBreaks: DayBreak[] = [];
  const allNodes: string[] = [];
  const allWarnings: string[] = [];

  if (dailyPlans.length === 0) {
    return { days: [], nodeSequence: [], dayBreaks: [], warnings: [] };
  }

  let dayStart = startNodeId;

  for (let i = 0; i < dailyPlans.length; i++) {
    const daily = dailyPlans[i];
    let effectiveEnd = daily.endNodeId;
    let effectiveVia = daily.viaNodeIds;

    const isLast = i === dailyPlans.length - 1;
    if (isLast && returnToStart && daily.endNodeId !== startNodeId) {
      effectiveEnd = startNodeId;
      effectiveVia = [...daily.viaNodeIds, daily.endNodeId];
    }

    const path = resolvePath({
      route,
      startNodeId: dayStart,
      endNodeId: effectiveEnd,
      viaNodeIds: effectiveVia,
    });

    if (path.warnings.includes('no_path')) {
      allWarnings.push(`day_${i + 1}_unreachable`);
      days.push({
        dayIndex: i + 1,
        startNodeId: dayStart,
        pathNodeIds: [],
        segments: [],
        warnings: ['no_path'],
      });
      continue;
    }

    const pathIds = path.forward;
    days.push({
      dayIndex: i + 1,
      startNodeId: dayStart,
      pathNodeIds: pathIds,
      segments: makeSegments(pathIds),
      warnings: [],
    });

    if (allNodes.length === 0) {
      allNodes.push(...pathIds);
    } else if (allNodes[allNodes.length - 1] === pathIds[0]) {
      allNodes.push(...pathIds.slice(1));
    } else {
      allNodes.push(...pathIds);
      allWarnings.push(`day_${i + 1}_disjoint`);
    }

    if (!isLast) {
      dayBreaks.push({
        afterNodeId: effectiveEnd,
        type: daily.endType,
        hutId: daily.hutId,
      });
    }

    dayStart = effectiveEnd;
  }

  return { days, nodeSequence: allNodes, dayBreaks, warnings: allWarnings };
}
