import { describe, it, expect, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import PrintLayout from '@/components/schedule/PrintLayout.vue';
import { useRoutesStore } from '@/stores/routesStore';
import { calculateTimes } from '@/services/TimeCalculator';
import g02 from '../../fixtures/G02-test.json';
import type { Plan, Route } from '@/types';
import type { SuggestOutput } from '@/services/GearSuggester';

const route = g02 as Route;

beforeEach(() => {
  setActivePinia(createPinia());
  const routesStore = useRoutesStore();
  routesStore.routes = [route];
});

const plan: Plan = {
  id: 1,
  name: '玉山主峰測試',
  routeId: 'G02',
  startNodeId: 'n_tataka',
  endNodeId: 'n_yushan_main',
  nodeSequence: ['n_tataka', 'n_shang_dongpu', 'n_dietshan', 'n_pailin', 'n_dachienshan', 'n_baimu', 'n_paiyun', 'n_yushan_main'],
  paceMultiplier: 1.2,
  startDate: '2026-06-15',
  startTime: '06:00',
  dayBreaks: [{ afterNodeId: 'n_paiyun', type: 'hut', hutId: 'hut_paiyun' }],
  tripType: 'overnight_hut',
  createdAt: '2026-05-09T00:00:00Z',
};

const segments = calculateTimes({
  route,
  nodeSequence: plan.nodeSequence,
  paceMultiplier: 1.2,
  startDateTime: '2026-06-15T06:00:00',
}).segments;

const gearSuggestion: SuggestOutput = {
  tripType: 'overnight_hut',
  categories: [
    {
      id: 'light_summit',
      name: '輕裝攻頂',
      items: [
        { id: 'i_water_1l', name: '水 1L', categoryId: 'light_summit', source: 'template', essential: true, weight_g: 1000 },
      ],
    },
    {
      id: 'overnight_hut',
      name: '山屋過夜',
      items: [
        { id: 'i_sleeping_bag', name: '睡袋', categoryId: 'overnight_hut', source: 'template', essential: true, weight_g: 1200 },
      ],
    },
  ],
};

describe('PrintLayout', () => {
  it('shows header with plan name and metadata', () => {
    const wrapper = mount(PrintLayout, {
      props: { plan, route, segments, gearSuggestion },
    });
    expect(wrapper.text()).toContain('玉山主峰測試');
    expect(wrapper.text()).toContain('G02');
    expect(wrapper.text()).toContain('2026-06-15');
    expect(wrapper.text()).toContain('1.2');
  });

  it('renders schedule table with header and one row per node', () => {
    const wrapper = mount(PrintLayout, {
      props: { plan, route, segments, gearSuggestion },
    });
    const tables = wrapper.findAll('table');
    expect(tables.length).toBe(1);
    const rows = tables.at(0)!.findAll('tbody tr');
    expect(rows.length).toBe(segments.length + 1);
  });

  it('renders gear checklist with correct number of categories and items', () => {
    const wrapper = mount(PrintLayout, {
      props: { plan, route, segments, gearSuggestion },
    });
    const headings = wrapper.findAll('.print-gear h3');
    expect(headings.length).toBe(2);
    const lis = wrapper.findAll('.print-gear li');
    expect(lis.length).toBe(2);
    expect(wrapper.text()).toContain('☐ 水 1L');
    expect(wrapper.text()).toContain('☐ 睡袋');
  });

  it('footer contains 上河文化 attribution', () => {
    const wrapper = mount(PrintLayout, {
      props: { plan, route, segments, gearSuggestion },
    });
    expect(wrapper.find('.print-footer').text()).toContain('上河文化');
  });

  it('handles null gearSuggestion gracefully', () => {
    const wrapper = mount(PrintLayout, {
      props: { plan, route, segments, gearSuggestion: null },
    });
    expect(wrapper.find('.print-gear').exists()).toBe(true);
    expect(wrapper.findAll('.print-gear h3').length).toBe(0);
  });
});
