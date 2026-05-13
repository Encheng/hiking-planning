export const DAY_COLORS = ['#22c55e', '#a855f7', '#ec4899', '#10b981', '#f59e0b'];

// Different dash patterns so overlapping segments stay distinguishable
export const DAY_DASH_ARRAYS: (string | undefined)[] = [
  undefined,    // Day 1: solid
  '10 6',       // Day 2: long dash
  '3 5',        // Day 3: dots
  '12 4 3 4',   // Day 4: dash-dot
  '3 4 10 4',   // Day 5: dot-dash
];

export function dayColor(zeroBasedIndex: number): string {
  return DAY_COLORS[zeroBasedIndex % DAY_COLORS.length];
}

export function dayDashArray(zeroBasedIndex: number): string | undefined {
  return DAY_DASH_ARRAYS[zeroBasedIndex % DAY_DASH_ARRAYS.length];
}
