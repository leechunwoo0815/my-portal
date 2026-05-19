import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  darkMode: 'class',
  corePlugins: {
    preflight: false,
  },
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: 'var(--cyber-bg)',
          card: 'var(--cyber-card)',
          'card-hover': 'var(--cyber-card-hover)',
          border: 'var(--cyber-border)',
          text: 'var(--cyber-text)',
          muted: 'var(--cyber-muted)',
          neon: 'var(--cyber-neon)',
          'neon-light': 'var(--cyber-neon-light)',
          amber: 'var(--cyber-amber)',
          'amber-light': 'var(--cyber-amber-light)',
          danger: 'var(--cyber-danger)',
          'code-bg': 'var(--cyber-code-bg)',
          'code-text': 'var(--cyber-code-text)',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
        sans: ['Inter', 'Noto Sans SC', 'system-ui', 'sans-serif'],
        pixel: ['Press Start 2P', 'monospace'],
      },
      boxShadow: {
        neon: '0 0 5px var(--cyber-neon), 0 0 20px rgba(0, 212, 170, 0.3)',
        'neon-amber': '0 0 5px var(--cyber-amber), 0 0 20px rgba(240, 180, 41, 0.3)',
        card: 'var(--cyber-shadow)',
        'card-hover': 'var(--cyber-shadow-hover)',
        glow: 'var(--cyber-glow)',
      },
      animation: {
        scanline: 'scanline 8s linear infinite',
        glow: 'glow 2s ease-in-out infinite alternate',
        typing: 'typing 3.5s steps(40, end)',
        blink: 'blink 1s step-end infinite',
        'pulse-neon': 'pulseNeon 2s ease-in-out infinite',
      },
      keyframes: {
        scanline: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px var(--cyber-neon)' },
          '100%': { boxShadow: '0 0 20px var(--cyber-neon), 0 0 40px rgba(0,212,170,0.2)' },
        },
        typing: {
          from: { width: '0' },
          to: { width: '100%' },
        },
        blink: {
          '50%': { borderColor: 'transparent' },
        },
        pulseNeon: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
      },
    },
  },
  plugins: [],
} satisfies Config
