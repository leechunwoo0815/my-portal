import { lightTokens, darkTokens } from './tokens'

export type ThemeMode = 'light' | 'dark'

export function applyDesignTokens(mode: ThemeMode) {
  if (typeof document === 'undefined') return

  const html = document.documentElement
  const isDark = mode === 'dark'
  html.classList.toggle('dark', isDark)

  const tokens = isDark ? darkTokens : lightTokens
  for (const [key, val] of Object.entries(tokens)) {
    html.style.setProperty(key, val)
  }

  html.style.setProperty('--el-color-primary', isDark ? '#00ff88' : '#00d4aa')
  html.style.setProperty('--el-color-primary-light-3', isDark ? '#33ff9f' : '#33deb8')
  html.style.setProperty('--el-color-primary-light-5', isDark ? '#66ffb3' : '#66e5cc')
  html.style.setProperty('--el-color-primary-light-7', isDark ? '#99ffc7' : '#99ecd9')
  html.style.setProperty('--el-color-primary-light-8', isDark ? '#b3ffd4' : '#b3f2e3')
  html.style.setProperty('--el-color-primary-light-9', isDark ? '#ccffe0' : '#ccf8ee')
  html.style.setProperty('--el-color-primary-dark-2', isDark ? '#00cc6d' : '#00aa88')

  html.style.setProperty('--el-bg-color', isDark ? '#161b22' : '#ffffff')
  html.style.setProperty('--el-bg-color-page', isDark ? '#0d1117' : '#f0f2f5')
  html.style.setProperty('--el-bg-color-overlay', isDark ? '#1c2333' : '#ffffff')
  html.style.setProperty('--el-text-color-primary', isDark ? '#e6edf3' : '#1a1a2e')
  html.style.setProperty('--el-text-color-regular', isDark ? '#c9d1d9' : '#4a5568')
  html.style.setProperty('--el-text-color-secondary', isDark ? '#8b949e' : '#6b7280')
  html.style.setProperty('--el-text-color-placeholder', isDark ? '#6b7280' : '#9ca3af')
  html.style.setProperty('--el-border-color', isDark ? '#30363d' : '#d0d7de')
  html.style.setProperty('--el-border-color-light', isDark ? '#374151' : '#e5e7eb')
  html.style.setProperty('--el-border-color-lighter', isDark ? '#4b5563' : '#f3f4f6')
  html.style.setProperty('--el-fill-color', isDark ? '#1c2333' : '#f0f2f5')
  html.style.setProperty('--el-fill-color-light', isDark ? '#21262d' : '#f8f9fa')
  html.style.setProperty('--el-fill-color-lighter', isDark ? '#30363d' : '#fafafa')
  html.style.setProperty('--el-fill-color-blank', isDark ? '#161b22' : '#ffffff')
  html.style.setProperty('--el-fill-color-dark', isDark ? '#0d1117' : '#e5e7eb')

  html.style.setProperty('--el-color-success', isDark ? '#3fb950' : '#22c55e')
  html.style.setProperty('--el-color-warning', isDark ? '#d29922' : '#f59e0b')
  html.style.setProperty('--el-color-danger', isDark ? '#ff6b81' : '#ff4757')
  html.style.setProperty('--el-color-info', isDark ? '#8b949e' : '#6b7280')

  html.style.setProperty('--el-box-shadow', isDark ? '0 2px 12px rgba(0,0,0,0.3)' : '0 2px 12px rgba(0,0,0,0.08)')
  html.style.setProperty('--el-box-shadow-light', isDark ? '0 2px 4px rgba(0,0,0,0.2)' : '0 2px 4px rgba(0,0,0,0.04)')

  html.style.setProperty('--app-bg', isDark ? '#0d1117' : '#f5f7fa')
  html.style.setProperty('--app-bg-card', isDark ? '#161b22' : '#ffffff')
  html.style.setProperty('--app-bg-secondary', isDark ? '#1c2333' : '#f0f2f5')
  html.style.setProperty('--app-text', isDark ? '#e6edf3' : '#1a1a2e')
  html.style.setProperty('--app-text-secondary', isDark ? '#8b949e' : '#4a5568')
  html.style.setProperty('--app-border', isDark ? '#30363d' : '#e5e7eb')
}
