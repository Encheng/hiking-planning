import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import MapNodePopup from '@/components/planner/MapNodePopup.vue';
import type { RouteNode } from '@/types';

const node: RouteNode = {
  id: 'n_yushan_main',
  name: '玉山主峰',
  lat: 23.4707,
  lng: 120.9572,
  elevation: 3952,
  category: 'peak',
};

describe('MapNodePopup', () => {
  it('shows node name and elevation', () => {
    const wrapper = mount(MapNodePopup, { props: { node, expandedDayIndex: 1 } });
    expect(wrapper.text()).toContain('玉山主峰');
    expect(wrapper.text()).toContain('3952m');
  });

  it('expandedDayIndex set: shows two action buttons', () => {
    const wrapper = mount(MapNodePopup, { props: { node, expandedDayIndex: 2 } });
    expect(wrapper.text()).toContain('當作 Day 2 目標');
    expect(wrapper.text()).toContain('加為 Day 2 加爬點');
  });

  it('expandedDayIndex null: shows hint message', () => {
    const wrapper = mount(MapNodePopup, { props: { node, expandedDayIndex: null } });
    expect(wrapper.text()).toContain('請先展開');
  });

  it('emits set-target on target button click', async () => {
    const wrapper = mount(MapNodePopup, { props: { node, expandedDayIndex: 1 } });
    const btns = wrapper.findAll('button');
    await btns[0].trigger('click');
    expect(wrapper.emitted('set-target')).toBeTruthy();
  });

  it('emits add-via on via button click', async () => {
    const wrapper = mount(MapNodePopup, { props: { node, expandedDayIndex: 1 } });
    const btns = wrapper.findAll('button');
    await btns[1].trigger('click');
    expect(wrapper.emitted('add-via')).toBeTruthy();
  });
});
