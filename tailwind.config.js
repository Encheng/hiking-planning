/**
 * Tailwind config — design system tokens.
 * Brand palette per project spec; semantic aliases for clarity.
 */
export default {
  content: ['./index.html', './src/**/*.{vue,ts}'],
  theme: {
    extend: {
      colors: {
        brand: {
          // Teals (primary scale)
          900: '#1F4F5B',
          700: '#5F8F95',
          300: '#9ECBD1',
          // Naturals
          sage: '#87AE9E',
          forest: '#6F906A',
          // Neutrals
          gray: '#858C79',
          rose: '#9B8788',
          cream: '#E6E2D6',
          white: '#FFFAFF',
          // Warm scale
          yellow: '#EFC42A',
          gold: '#E0B23E',
          amber: '#D8A13A',
          orange: '#D07B3E',
          rust: '#BE603D',
          danger: '#AB443B',
        },
      },
      // Semantic tinted backgrounds (low-saturation tints of brand colors)
      backgroundColor: {
        'brand-tint-info': '#EAF1F2',
        'brand-tint-success': '#E5EFE9',
        'brand-tint-warning': '#FBF1CE',
        'brand-tint-danger': '#F0DBD3',
        'brand-tint-neutral': '#F1EFE7',
      },
    },
  },
  plugins: [],
};
