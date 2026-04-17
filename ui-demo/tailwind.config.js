/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace']
      },
      colors: {
        bg: 'rgb(var(--bg) / <alpha-value>)',
        surface: 'rgb(var(--surface) / <alpha-value>)',
        'surface-2': 'rgb(var(--surface-2) / <alpha-value>)',
        border: 'rgb(var(--border) / <alpha-value>)',
        text: 'rgb(var(--text) / <alpha-value>)',
        muted: 'rgb(var(--text-muted) / <alpha-value>)',
        accent: 'rgb(var(--accent) / <alpha-value>)',
        sev: {
          info: 'rgb(var(--sev-info) / <alpha-value>)',
          notice: 'rgb(var(--sev-notice) / <alpha-value>)',
          warning: 'rgb(var(--sev-warning) / <alpha-value>)',
          anomaly: 'rgb(var(--sev-anomaly) / <alpha-value>)',
          critical: 'rgb(var(--sev-critical) / <alpha-value>)',
          healthy: 'rgb(var(--sev-healthy) / <alpha-value>)'
        }
      },
      keyframes: {
        'pulse-strong': {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.6', transform: 'scale(1.08)' }
        },
        'slide-in': {
          '0%': { transform: 'translateX(-8px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' }
        },
        'flash': {
          '0%, 100%': { backgroundColor: 'transparent' },
          '20%': { backgroundColor: 'rgb(var(--sev-critical) / 0.2)' }
        }
      },
      animation: {
        'pulse-strong': 'pulse-strong 1.2s ease-in-out infinite',
        'slide-in': 'slide-in 220ms ease-out',
        'flash': 'flash 900ms ease-out'
      }
    }
  },
  plugins: []
};
