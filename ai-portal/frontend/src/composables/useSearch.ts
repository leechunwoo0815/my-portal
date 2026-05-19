import { ref } from 'vue'
import { searchContent } from '@/api/search'

export function useSearch() {
  const keyword = ref('')
  const results = ref<any[]>([])
  const loading = ref(false)
  const total = ref(0)

  const doSearch = async (params?: { target_type?: string; page?: number; page_size?: number }) => {
    if (!keyword.value.trim()) return
    loading.value = true
    try {
      const res: any = await searchContent({
        keyword: keyword.value.trim(),
        ...params,
      })
      results.value = res.items || []
      total.value = res.total || 0
    } catch {
      results.value = []
      total.value = 0
    } finally {
      loading.value = false
    }
  }

  const clear = () => {
    keyword.value = ''
    results.value = []
    total.value = 0
  }

  return { keyword, results, loading, total, doSearch, clear }
}
