import { ref, computed } from 'vue'

export function usePagination(defaultPageSize = 20) {
  const page = ref(1)
  const pageSize = ref(defaultPageSize)
  const total = ref(0)

  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))
  const hasNext = computed(() => page.value < totalPages.value)
  const hasPrev = computed(() => page.value > 1)

  const setPage = (p: number) => { page.value = p }
  const nextPage = () => { if (hasNext.value) page.value++ }
  const prevPage = () => { if (hasPrev.value) page.value-- }
  const reset = () => { page.value = 1; total.value = 0 }

  return { page, pageSize, total, totalPages, hasNext, hasPrev, setPage, nextPage, prevPage, reset }
}
