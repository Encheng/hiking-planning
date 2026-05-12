import { describe, it, expect, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import DailyPlanEditor from '@/components/planner/DailyPlanEditor.vue';
import { useRoutesStore } from '@/stores/routesStore';
import { usePlanStore } from '@/stores/planStore';
import g02 from '../../fixtures/G02-test.json';
import type { Route } from '@/types';

const route = g02 as Route;

beforeEach(() => {
  setActivePinia(createPinia());
  const routesStore = useRoutesStore();
  routesStore.routes = [route];
  const planStore = usePlanStore();
  planStore.draft = {
    routeId: 'G02',
    startNodeId: 'n_tataka',
    returnToStart: true,
    paceMultiplier: 1.0,
    dailyPlans: [
      { endNodeId: 'n_paiyun', endType: 'hut', viaNodeIds: [] },
      { endNodeId: 'n_yushan_main', endType: 'manual', viaNodeIds: [] },
    ],
  };
});

describe('DailyPlanEditor', () => {
  it('renders one DayCard per dailyPlan', () => {
    const wrapper = mount(DailyPlanEditor);
    const dayCards = wrapper.findAllComponents({ name: 'DayCard' });
    expect(dayCards.length).toBe(2);
  });

  it('renders the +加一天 button', () => {
    const wrapper = mount(DailyPlanEditor);
    expect(wrapper.text()).toContain('加一天');
  });

  it('appends a day when +加一天 clicked', async () => {
    const wrapper = mount(DailyPlanEditor);
    const planStore = usePlanStore();
    const beforeLen = planStore.draft!.dailyPlans!.length;
    const addButton = wrapper.findAll('button').find((b) => b.text().includes('加一天'));
    await addButton!.trigger('click');
    expect(planStore.draft!.dailyPlans!.length).toBe(beforeLen + 1);
  });

  it('renders returnToStart checkbox', () => {
    const wrapper = mount(DailyPlanEditor);
    expect(wrapper.text()).toContain('回到起點');
  });

  it('renders the start point picker', () => {
    const wrapper = mount(DailyPlanEditor);
    expect(wrapper.text()).toContain('起點');
  });
});
