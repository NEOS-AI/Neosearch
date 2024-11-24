import type { Config } from 'tailwindcss';
import animate from 'tailwindcss-animate';
import typography from '@tailwindcss/typography';
import { scopedPreflightStyles, isolateInsideOfContainer } from 'tailwindcss-scoped-preflight';

const config: Config = {
  darkMode: ['class'],
  corePlugins: {
    preflight: false,
  },
  important: '#tidb-ai-widget',
  content: [
    './src/**/*.{ts,tsx}',
    '../../app/src/components/chat/**/*.{ts,tsx}',
    '../../app/src/components/ui/**/*.{ts,tsx}',
    '../../app/src/components/remark-content/**/*.{ts,tsx}',
    '../../app/src/experimental/chat-verify-service/**/*.{ts,tsx}',
  ],
  prefix: '',
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      minHeight: {
        body: 'var(--body-height)',
        content: 'var(--content-height)',
      },
      height: {
        header: 'var(--header-height)',
        body: 'var(--body-height)',
        content: 'var(--content-height)',
      },
      width: {
        side: 'var(--side-width)',
        content: 'var(--content-width)',
      },
      padding: {
        body: 'var(--body-padding)',
        side: 'var(--side-width)',
      },
      margin: {
        side: 'var(--side-width)',
      },
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
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
        'fade-in-right': {
          from: { transform: 'translate3d(30%, 0, 0)', opacity: '0' },
          to: { transform: 'translate3d(0, 0, 0)', opacity: '1' },
        },
        'fade-in-left': {
          from: { transform: 'translate3d(-30%, 0, 0)', opacity: '0' },
          to: { transform: 'translate3d(0, 0, 0)', opacity: '1' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        'fade-in-right': 'fade-in-right 0.5s ease-out',
        'fade-in-left': 'fade-in-left 0.5s ease-out',
      },
    },
  },
  plugins: [
    animate,
    typography({ className: 'tidb-ai-widget#tidb-ai-widget .prose' }),
    scopedPreflightStyles({
      isolationStrategy: isolateInsideOfContainer('#tidb-ai-widget', {
        except: '.no-twp', // optional, to exclude some elements under .twp from being preflighted, like external markup
      }),
    }),
  ],
};

export default config;
