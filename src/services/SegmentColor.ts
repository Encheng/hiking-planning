import type { Route, SegmentTime } from '@/types';

export type SegmentTrend = 'climb' | 'descent' | 'flat';

const COLORS: Record<SegmentTrend, string> = {
  climb: '#fb923c',
  descent: '#86efac',
  flat: '#fcd34d',
};

const RATE_THRESHOLD_MPH = 50;

export function segmentTrend(seg: SegmentTime, route: Route): SegmentTrend {
  if (seg.adjustedMinutes <= 0) return 'flat';
  const from = route.nodes.find((n) => n.id === seg.fromNodeId);
  const to = route.nodes.find((n) => n.id === seg.toNodeId);
  if (!from || !to) return 'flat';
  const elevDelta = to.elevation - from.elevation;
  const hours = seg.adjustedMinutes / 60;
  const ratePerHour = elevDelta / hours;
  if (ratePerHour > RATE_THRESHOLD_MPH) return 'climb';
  if (ratePerHour < -RATE_THRESHOLD_MPH) return 'descent';
  return 'flat';
}

export function segmentColor(seg: SegmentTime, route: Route): string {
  return COLORS[segmentTrend(seg, route)];
}
