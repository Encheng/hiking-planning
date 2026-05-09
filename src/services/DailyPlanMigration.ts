import type { DailyPlan, DayBreak } from '@/types';

export interface LegacyPlanShape {
  startNodeId: string;
  endNodeId: string;
  nodeSequence: string[];
  dayBreaks: DayBreak[];
}

export interface MigrationOutput {
  dailyPlans: DailyPlan[];
  returnToStart: boolean;
}

export function deriveDailyPlansFromLegacy(legacy: LegacyPlanShape): MigrationOutput {
  const dailyPlans: DailyPlan[] = [];

  for (const brk of legacy.dayBreaks) {
    dailyPlans.push({
      endNodeId: brk.afterNodeId,
      endType: brk.type,
      hutId: brk.hutId,
      viaNodeIds: [],
    });
  }

  const finalEnd = legacy.nodeSequence.length > 0
    ? legacy.nodeSequence[legacy.nodeSequence.length - 1]
    : legacy.endNodeId;

  dailyPlans.push({
    endNodeId: finalEnd,
    endType: 'manual',
    viaNodeIds: [],
  });

  const returnToStart = finalEnd === legacy.startNodeId;

  return { dailyPlans, returnToStart };
}
