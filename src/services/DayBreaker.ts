import type { Route, Hut, SegmentTime, DayBreak } from '@/types';

export interface BreakInput {
  route: Route;
  segments: SegmentTime[];
  huts: Hut[];
  maxDailyHours: number;
  preferredBreakType: 'hut' | 'shelter' | 'auto';
}

const HUT_LOOKBACK_MINUTES = 60;

function nodeIsHut(route: Route, nodeId: string, huts: Hut[]): { hut: Hut } | null {
  const node = route.nodes.find((n) => n.id === nodeId);
  if (!node || !node.hutId) return null;
  const hut = huts.find((h) => h.id === node.hutId);
  return hut ? { hut } : null;
}

export function suggestBreaks(input: BreakInput): DayBreak[] {
  const { route, segments, huts, maxDailyHours } = input;
  const limit = maxDailyHours * 60;
  const breaks: DayBreak[] = [];
  let dailyMinutes = 0;
  let lastBreakIndex = -1;

  for (let i = 0; i < segments.length; i++) {
    dailyMinutes += segments[i].adjustedMinutes;
    if (dailyMinutes <= limit) continue;

    let chosenIdx = -1;
    // Look back for a hut node. The lookback window is HUT_LOOKBACK_MINUTES
    // measured as the time BEFORE the daily limit was reached (not from the
    // overflow point). A break at segment j is acceptable if the daily minutes
    // accumulated up to segments[j].toNodeId is within [limit - HUT_LOOKBACK_MINUTES, limit].
    // We walk backwards from the overflow segment until the candidate node's
    // cumulative daily time falls below (limit - HUT_LOOKBACK_MINUTES).
    let trailingMinutes = 0; // minutes counted back from end of segment i
    for (let j = i; j > lastBreakIndex; j--) {
      const candidateDailyMinutes = dailyMinutes - trailingMinutes;
      // If this candidate's arrival is more than HUT_LOOKBACK_MINUTES before
      // the limit, stop looking back.
      if (candidateDailyMinutes < limit - HUT_LOOKBACK_MINUTES) break;
      const candidate = nodeIsHut(route, segments[j].toNodeId, huts);
      if (candidate) {
        chosenIdx = j;
        break;
      }
      trailingMinutes += segments[j].adjustedMinutes;
    }

    if (chosenIdx !== -1) {
      const seg = segments[chosenIdx];
      const hutInfo = nodeIsHut(route, seg.toNodeId, huts)!;
      breaks.push({
        afterNodeId: seg.toNodeId,
        type: 'hut',
        hutId: hutInfo.hut.id,
      });
      dailyMinutes = segments.slice(chosenIdx + 1, i + 1).reduce((s, x) => s + x.adjustedMinutes, 0);
      lastBreakIndex = chosenIdx;
    } else {
      breaks.push({
        afterNodeId: segments[i].toNodeId,
        type: 'camp',
      });
      dailyMinutes = 0;
      lastBreakIndex = i;
    }
  }

  return breaks;
}
