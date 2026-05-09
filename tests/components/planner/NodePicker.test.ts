import { describe, it, expect, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import NodePicker from '@/components/planner/NodePicker.vue';
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
  planStore.draft = { routeId: 'G02' };
});

describe('NodePicker', () => {
  it('renders an NSelect element', () => {
    const wrapper = mount(NodePicker, { props: { value: undefined } });
    expect(wrapper.find('.n-select').exists()).toBe(true);
  });

  it('emits select event when programmatically updated', async () => {
    const wrapper = mount(NodePicker, { props: { value: 'n_tataka' } });
    await wrapper.findComponent({ name: 'NSelect' }).vm.$emit('update:value', 'n_paiyun');
    expect(wrapper.emitted('select')).toEqual([['n_paiyun']]);
  });

  it('groups nodes by category in options prop', () => {
    const wrapper = mount(NodePicker, { props: { value: undefined } });
    const innerSelect = wrapper.findComponent({ name: 'NSelect' });
    const opts = innerSelect.props('options') as Array<{ type: string; label: string; children: unknown[] }>;
    const groupTypes = opts.map((o) => o.type);
    expect(groupTypes).toContain('group');
    const peakGroup = opts.find((o) => o.label.includes('山頭'));
    expect(peakGroup?.children?.length).toBeGreaterThan(0);
  });
});
