import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // OKLCH色空間を使用したカスタムカラー
        primary: {
          DEFAULT: 'oklch(59.4% 0.238 251.4)',
          50: 'oklch(97% 0.02 251.4)',
          100: 'oklch(93% 0.05 251.4)',
          200: 'oklch(86% 0.1 251.4)',
          300: 'oklch(76% 0.15 251.4)',
          400: 'oklch(66% 0.2 251.4)',
          500: 'oklch(59.4% 0.238 251.4)',
          600: 'oklch(52% 0.25 251.4)',
          700: 'oklch(45% 0.23 251.4)',
          800: 'oklch(38% 0.2 251.4)',
          900: 'oklch(31% 0.15 251.4)',
          950: 'oklch(24% 0.1 251.4)',
        },
        secondary: {
          DEFAULT: 'oklch(49.1% 0.3 275.8)',
          50: 'oklch(97% 0.02 275.8)',
          100: 'oklch(92% 0.06 275.8)',
          200: 'oklch(84% 0.12 275.8)',
          300: 'oklch(72% 0.2 275.8)',
          400: 'oklch(60% 0.26 275.8)',
          500: 'oklch(49.1% 0.3 275.8)',
          600: 'oklch(42% 0.28 275.8)',
          700: 'oklch(35% 0.25 275.8)',
          800: 'oklch(29% 0.2 275.8)',
          900: 'oklch(24% 0.15 275.8)',
          950: 'oklch(19% 0.1 275.8)',
        },
        accent: {
          DEFAULT: 'oklch(71.7% 0.25 332)',
          50: 'oklch(98% 0.02 332)',
          100: 'oklch(95% 0.05 332)',
          200: 'oklch(90% 0.1 332)',
          300: 'oklch(84% 0.15 332)',
          400: 'oklch(77% 0.2 332)',
          500: 'oklch(71.7% 0.25 332)',
          600: 'oklch(65% 0.23 332)',
          700: 'oklch(57% 0.2 332)',
          800: 'oklch(48% 0.17 332)',
          900: 'oklch(39% 0.13 332)',
          950: 'oklch(30% 0.08 332)',
        },
        // システムカラー
        background: 'oklch(99% 0 0)',
        foreground: 'oklch(10% 0 0)',
        card: {
          DEFAULT: 'oklch(100% 0 0)',
          foreground: 'oklch(10% 0 0)',
        },
        popover: {
          DEFAULT: 'oklch(100% 0 0)',
          foreground: 'oklch(10% 0 0)',
        },
        muted: {
          DEFAULT: 'oklch(96% 0.01 250)',
          foreground: 'oklch(45% 0.02 250)',
        },
        destructive: {
          DEFAULT: 'oklch(59% 0.25 29)',
          foreground: 'oklch(98% 0 0)',
        },
        border: 'oklch(90% 0.01 250)',
        input: 'oklch(90% 0.01 250)',
        ring: 'oklch(59.4% 0.238 251.4)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        'slide-in': 'slide-in 0.2s ease-out',
        'slide-out': 'slide-out 0.2s ease-out',
        'fade-in': 'fade-in 0.2s ease-out',
        'fade-out': 'fade-out 0.2s ease-out',
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
        'slide-in': {
          from: { transform: 'translateX(-100%)' },
          to: { transform: 'translateX(0)' },
        },
        'slide-out': {
          from: { transform: 'translateX(0)' },
          to: { transform: 'translateX(-100%)' },
        },
        'fade-in': {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        'fade-out': {
          from: { opacity: '1' },
          to: { opacity: '0' },
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
  plugins: [
    require('tailwindcss-animate'),
  ],
}

export default config