import { describe, it, expect, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import DayCard from '@/components/planner/DayCard.vue';
import AppIcon from '@/components/common/AppIcon.vue';
import { useRoutesStore } from '@/stores/routesStore';
import { usePlanStore } from '@/stores/planStore';
import g02 from '../../fixtures/G02-test.json';
import type { Route, DailyPlan } from '@/types';

const route = g02 as Route;

beforeEach(() => {
  setActivePinia(createPinia());
  const routesStore = useRoutesStore();
  routesStore.routes = [route];
  const planStore = usePlanStore();
  planStore.draft = { routeId: 'G02' };
});

const dailyPlan: DailyPlan = {
  endNodeId: 'n_paiyun',
  endType: 'hut',
  hutId: 'hut_paiyun',
  viaNodeIds: [],
};

const baseProps = {
  index: 1,
  startNodeName: '塔塔加遊客中心',
  derivedStartNodeId: 'n_tataka',
  endNodeName: '排雲山莊',
  totalMinutes: 510,
  dailyPlan,
  expanded: false,
  isOnly: false,
  warnings: [],
};

describe('DayCard', () => {
  it('collapsed: shows summary only', () => {
    const wrapper = mount(DayCard, { props: baseProps });
    expect(wrapper.text()).toContain('DAY 1');
    expect(wrapper.text()).toContain('塔塔加遊客中心');
    expect(wrapper.text()).toContain('排雲山莊');
    expect(wrapper.find('[data-day-editor]').exists()).toBe(false);
  });

  it('expanded: shows editor', () => {
    const wrapper = mount(DayCard, { props: { ...baseProps, expanded: true } });
    expect(wrapper.find('[data-day-editor]').exists()).toBe(true);
    expect(wrapper.text()).toContain('當日目標');
    expect(wrapper.text()).toContain('中途加爬');
  });

  it('emits toggle-expand on header click', async () => {
    const wrapper = mount(DayCard, { props: baseProps });
    await wrapper.find('button').trigger('click');
    expect(wrapper.emitted('toggle-expand')).toBeTruthy();
  });

  it('isOnly=true hides remove-day button', () => {
    const wrapper = mount(DayCard, { props: { ...baseProps, expanded: true, isOnly: true } });
    expect(wrapper.text()).not.toContain('移除這天');
  });

  it('shows warning indicator when warnings is non-empty', () => {
    const wrapper = mount(DayCard, { props: { ...baseProps, warnings: ['no_path'] } });
    const hasWarningIcon = wrapper
      .findAllComponents(AppIcon)
      .some((i) => i.props('name') === 'alert-triangle');
    expect(hasWarningIcon).toBe(true);
  });
});
