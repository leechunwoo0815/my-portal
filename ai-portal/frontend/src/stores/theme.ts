import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { applyDesignTokens } from '@/design/theme'

type Theme = 'light' | 'dark'

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref<Theme>('light')

  const initTheme = () => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('theme') as Theme | null
      if (saved === 'light' || saved === 'dark') {
        currentTheme.value = saved
      } else if (window.matchMedia?.('(prefers-color-scheme: dark)').matches) {
        currentTheme.value = 'dark'
      }
    }
    applyTheme()
  }

  const toggleTheme = () => {
    currentTheme.value = currentTheme.value === 'light' ? 'dark' : 'light'
    saveTheme()
    applyTheme()
  }

  const setTheme = (theme: Theme) => {
    currentTheme.value = theme
    saveTheme()
    applyTheme()
  }

  const saveTheme = () => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('theme', currentTheme.value)
    }
  }

  const applyTheme = () => {
    applyDesignTokens(currentTheme.value)
  }

  const isDark = computed(() => currentTheme.value === 'dark')
  const isLight = computed(() => currentTheme.value === 'light')

  return { currentTheme, isDark, isLight, toggleTheme, setTheme, applyTheme, initTheme }
})
