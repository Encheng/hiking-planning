import { describe, it, expect, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import ElevationView from '@/components/schedule/ElevationView.vue';
import { useRoutesStore } from '@/stores/routesStore';
import { calculateTimes } from '@/services/TimeCalculator';
import g02 from '../../fixtures/G02-test.json';
import type { Plan, Route } from '@/types';

const route = g02 as Route;

beforeEach(() => {
  setActivePinia(createPinia());
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

describe('ElevationView', () => {
  it('renders one SVG per day', () => {
    const wrapper = mount(ElevationView, { props: { plan, segments } });
    expect(wrapper.findAll('svg').length).toBe(2);
  });

  it('polyline points count = daySegments.length + 1 (start + each toNode)', () => {
    const wrapper = mount(ElevationView, { props: { plan, segments } });
    const firstSvg = wrapper.findAll('svg').at(0)!;
    const polyline = firstSvg.find('polyline');
    const points = polyline.attributes('points')!.trim().split(/\s+/);
    expect(points.length).toBe(7);
  });

  it('renders peak/hut/trailhead markers as <circle> elements', () => {
    const wrapper = mount(ElevationView, { props: { plan, segments } });
    const firstSvg = wrapper.findAll('svg').at(0)!;
    expect(firstSvg.findAll('circle').length).toBeGreaterThan(0);
  });

  it('shows day header text', () => {
    const wrapper = mount(ElevationView, { props: { plan, segments } });
    expect(wrapper.text()).toContain('DAY 1');
    expect(wrapper.text()).toContain('DAY 2');
  });
});
