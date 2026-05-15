/**
 * Naive UI global theme override — maps brand palette to Naive semantic colors.
 * Source palette: ["#1F4F5B", "#5F8F95", "#9ECBD1", "#87AE9E", "#6F906A",
 *                  "#858C79", "#9B8788", "#FFFAFF", "#E6E2D6", "#EFC42A",
 *                  "#E0B23E", "#D8A13A", "#D07B3E", "#BE603D", "#AB443B"]
 */
import type { GlobalThemeOverrides } from 'naive-ui';

export const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#1F4F5B',
    primaryColorHover: '#2E6573',
    primaryColorPressed: '#173E48',
    primaryColorSuppl: '#1F4F5B',

    infoColor: '#5F8F95',
    infoColorHover: '#74A1A7',
    infoColorPressed: '#4E7E84',

    successColor: '#6F906A',
    successColorHover: '#82A37D',
    successColorPressed: '#5E7E59',

    warningColor: '#D8A13A',
    warningColorHover: '#E0B23E',
    warningColorPressed: '#C18B2D',

    errorColor: '#AB443B',
    errorColorHover: '#BE603D',
    errorColorPressed: '#94372E',

    textColorBase: '#1F4F5B',
  },
  Button: {
    // Single source of truth for sizes — never override per-instance
    heightTiny: '24px',     // reserved for inline icon buttons; avoid in pages
    heightSmall: '32px',    // inline secondary actions inside cards/rows
    heightMedium: '36px',   // default — page-level actions
    heightLarge: '40px',    // primary submit CTA at form bottom
    fontWeight: '500',
  },
  Tag: {
    fontWeight: '500',
  },
};
