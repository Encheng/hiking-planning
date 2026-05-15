import type { DailyPlan } from './daily';
import type { PreTripChecklist } from './checklist';

export type TripType = 'light_summit' | 'long_day' | 'overnight_hut' | 'overnight_camp';
export type DayBreakType = 'hut' | 'shelter' | 'camp' | 'manual';

export interface DayBreak {
  afterNodeId: string;
  type: DayBreakType;
  hutId?: string;
}

export interface Plan {
  id?: number;
  name: string;
  routeId: string;
  startNodeId: string;
  endNodeId: string;
  nodeSequence: string[];
  paceMultiplier: number;
  startDate: string;
  startTime: string;
  dayBreaks: DayBreak[];
  tripType: TripType;
  notes?: string;
  createdAt: string;

  // Phase 2.5
  dailyPlans?: DailyPlan[];
  returnToStart?: boolean;

  // Phase A: 行前安全
  preTripChecklist?: PreTripChecklist;
}

export interface SegmentTime {
  fromNodeId: string;
  toNodeId: string;
  baseMinutes: number;
  adjustedMinutes: number;
  arrivalTime: string;
  cumulativeMinutes: number;
  direction: 'forward' | 'backward';
}
