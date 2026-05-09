import { describe, it, expect, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import GanttView from '@/components/schedule/GanttView.vue';
import { useRoutesStore } from '@/stores/routesStore';
import { calculateTimes } from '@/services/TimeCalculator';
import g02 from '../../fixtures/G02-test.json';
import type { Plan, Route } from '@/types';

const route = g02 as Route;

beforeEach(() => {
  const pinia = createPinia();
  setActivePinia(pinia);
  const routesStore = useRoutesStore();
  routesStore.routes = [route];
});

const plan: Plan = {
  name: 'test',
  routeId: 'G02',
  startNodeId: 'n_tataka',
  endNodeId: 'n_yushan_main',
  nodeSequence: ['n_tataka', 'n_shang_dongpu', 'n_dietshan', 'n_pailin', 'n_dachienshan', 'n_baimu', 'n_paiyun', 'n_yushan_main'],
  paceMultiplier: 1.0,
  startDate: '2026-06-15',
  startTime: '06:00',
  dayBreaks: [{ afterNodeId: 'n_paiyun', type: 'hut', hutId: 'hut_paiyun' }],
  tripType: 'overnight_hut',
  createdAt: '2026-05-09T00:00:00Z',
};

const segments = calculateTimes({
  route,
  nodeSequence: plan.nodeSequence,
  paceMultiplier: 1.0,
  startDateTime: '2026-06-15T06:00:00',
}).segments;

describe('GanttView', () => {
  it('renders one section per day', () => {
    const wrapper = mount(GanttView, { props: { plan, segments } });
    const sections = wrapper.findAll('section');
    expect(sections.length).toBe(2);
  });

  it('renders bars proportional to adjustedMinutes via flex-grow', () => {
    const wrapper = mount(GanttView, { props: { plan, segments } });
    const bars = wrapper.findAll('section').at(0)!.findAll('[data-segment-bar]');
    expect(bars.length).toBeGreaterThan(0);
    const flexValues = bars.map((b) => Number(b.attributes('style')?.match(/flex:\s*(\d+)/)?.[1] ?? 0));
    expect(flexValues.every((v) => v > 0)).toBe(true);
  });

  it('shows day header with index, date and total time', () => {
    const wrapper = mount(GanttView, { props: { plan, segments } });
    expect(wrapper.text()).toContain('DAY 1');
    expect(wrapper.text()).toContain('2026-06-15');
    expect(wrapper.text()).toContain('DAY 2');
    expect(wrapper.text()).toContain('2026-06-16');
  });

  it('shows start and end node names per day', () => {
    const wrapper = mount(GanttView, { props: { plan, segments } });
    expect(wrapper.text()).toContain('塔塔加遊客中心');
    expect(wrapper.text()).toContain('排雲山莊');
    expect(wrapper.text()).toContain('玉山主峰');
  });
});
