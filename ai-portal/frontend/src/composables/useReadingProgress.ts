import { ref, onMounted, onUnmounted } from 'vue'

export function useReadingProgress() {
  const progress = ref(0)

  const updateProgress = () => {
    const el = document.documentElement
    const scrollTop = el.scrollTop
    const scrollHeight = el.scrollHeight - el.clientHeight
    if (scrollHeight > 0) {
      progress.value = Math.min(Math.round((scrollTop / scrollHeight) * 100), 100)
    }
  }

  onMounted(() => {
    window.addEventListener('scroll', updateProgress, { passive: true })
  })

  onUnmounted(() => {
    window.removeEventListener('scroll', updateProgress)
  })

  return { progress }
}
