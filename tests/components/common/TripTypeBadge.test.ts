import { describe, it, expect, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import TripTypeBadge from '@/components/common/TripTypeBadge.vue';

beforeEach(() => {
  setActivePinia(createPinia());
});

describe('TripTypeBadge', () => {
  it('shows the standard label for known trip types', () => {
    const w = mount(TripTypeBadge, { props: { tripType: 'overnight_hut' } });
    expect(w.text()).toContain('山屋過夜');
  });

  it('shows custom label when customLabel prop provided (overrides tripType)', () => {
    const w = mount(TripTypeBadge, {
      props: { tripType: 'overnight_hut', customLabel: 'Y型縱走' },
    });
    expect(w.text()).toContain('Y型縱走');
    expect(w.text()).not.toContain('山屋過夜');
  });

  it('does not show edit affordance when editable is false (default)', () => {
    const w = mount(TripTypeBadge, { props: { tripType: 'overnight_hut' } });
    expect(w.html()).not.toContain('aria-label="編輯行程類型"');
  });

  it('shows edit affordance when editable=true', () => {
    const w = mount(TripTypeBadge, {
      props: { tripType: 'overnight_hut', editable: true },
    });
    expect(w.html()).toContain('aria-label="編輯行程類型"');
  });
});
