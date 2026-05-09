import type { DayBreak, DayBreakType } from './plan';

export interface DailyPlan {
  endNodeId: string;
  endType: DayBreakType;
  hutId?: string;
  viaNodeIds: string[];
}

export interface DayResolution {
  dayIndex: number;
  startNodeId: string;
  pathNodeIds: string[];
  segments: Array<{ from: string; to: string }>;
  warnings: string[];
}

export interface DailyPlanResolveOutput {
  days: DayResolution[];
  nodeSequence: string[];
  dayBreaks: DayBreak[];
  warnings: string[];
}
