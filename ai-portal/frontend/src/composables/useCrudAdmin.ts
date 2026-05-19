import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'

export interface CrudAdminOptions {
  fetchList: (params: Record<string, any>) => Promise<any>
  createItem: (data: any) => Promise<any>
  updateItem: (id: number, data: any) => Promise<any>
  deleteItem: (id: number) => Promise<any>
  defaultForm: () => any
  deleteConfirmMessage?: string
  entityName?: string
  contentField?: string
  openEditTransform?: (row: any) => any
  onBeforeSave?: (payload: any) => void
}

function parseListResponse(res: any): { items: any[]; total: number } {
  if (Array.isArray(res)) {
    return { items: res, total: res.length }
  }
  if (res && typeof res === 'object') {
    const items = res.items ?? res.data ?? res.list ?? res.results ?? null
    if (Array.isArray(items)) {
      const total = res.total ?? res.count ?? items.length
      return { items, total }
    }
  }
  return { items: [], total: 0 }
}

export function useCrudAdmin(options: CrudAdminOptions) {
  const {
    fetchList: apiFetchList,
    createItem,
    updateItem,
    deleteItem,
    defaultForm,
    deleteConfirmMessage = '确定删除？',
    entityName = '记录',
    contentField = 'content',
    openEditTransform,
    onBeforeSave,
  } = options

  const list = ref<any[]>([])
  const loading = ref(false)
  const dialogVisible = ref(false)
  const saving = ref(false)
  const isEdit = ref(false)
  const page = ref(1)
  const pageSize = ref(20)
  const total = ref(0)
  const form = ref<any>(defaultForm())

  const formatDate = (v: string) => {
    if (!v) return '—'
    const d = new Date(v)
    const y = d.getFullYear()
    const m = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    const h = String(d.getHours()).padStart(2, '0')
    const min = String(d.getMinutes()).padStart(2, '0')
    const s = String(d.getSeconds()).padStart(2, '0')
    return `${y}-${m}-${day} ${h}:${min}:${s}`
  }

  const extractOptions = (items: any[]) => {
    const cats = new Set<string>()
    const tags = new Set<string>()
    for (const item of items) {
      if (item.category) cats.add(item.category)
      if (item.tags)
        (item.tags as string)
          .split(',')
          .filter(Boolean)
          .forEach((t: string) => tags.add(t.trim()))
    }
    return {
      categoryOptions: Array.from(cats).sort(),
      tagOptions: Array.from(tags).sort(),
    }
  }

  const fetchList = async (extraParams?: Record<string, any>) => {
    loading.value = true
    try {
      const params: any = {
        page: page.value,
        page_size: pageSize.value,
        ...extraParams,
      }
      const res: any = await apiFetchList(params)
      const { items, total: totalCount } = parseListResponse(res)
      list.value = items
      total.value = totalCount
      return extractOptions(items)
    } catch (e) {
      console.error(e)
      return { categoryOptions: [] as string[], tagOptions: [] as string[] }
    } finally {
      loading.value = false
    }
  }

  const openCreate = () => {
    isEdit.value = false
    form.value = defaultForm()
    dialogVisible.value = true
  }

  const openEdit = (row: any) => {
    isEdit.value = true
    const baseFormData: any = {
      id: row.id,
      title: row.title || '',
      summary: row.summary || '',
      [contentField]: '',
      content_type: row.content_type || 'markdown',
      cover_image: row.cover_image || '',
      category: row.category || '',
      tags: row.tags || '',
      tagsArray: (row.tags || '')
        .split(',')
        .filter(Boolean)
        .map((t: string) => t.trim()),
      is_published: !!row.is_published,
    }

    if (openEditTransform) {
      const extra = openEditTransform(row)
      Object.assign(baseFormData, extra)
    }

    form.value = baseFormData
    dialogVisible.value = true
    nextTick(() => {
      form.value[contentField] = row[contentField] || ''
    })
  }

  const handleSave = async (customBeforeSave?: (payload: any) => void) => {
    if (saving.value) return

    saving.value = true
    const payload = { ...form.value }

    if (payload.tagsArray) {
      payload.tags = (payload.tagsArray || []).join(',')
      delete payload.tagsArray
    }

    if (onBeforeSave) onBeforeSave(payload)
    if (customBeforeSave) customBeforeSave(payload)

    try {
      if (isEdit.value && payload.id) {
        await updateItem(payload.id, payload)
        ElMessage.success('更新成功')
      } else {
        await createItem(payload)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      await fetchList()
    } catch (e: any) {
      const msg = e?.response?.data?.detail || e?.response?.data?.message || e?.message || '操作失败'
      ElMessage.error(typeof msg === 'string' ? msg : JSON.stringify(msg))
    } finally {
      saving.value = false
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await deleteItem(id)
      ElMessage.success('删除成功')
      await fetchList()
    } catch (e) {
      console.error(e)
      ElMessage.error('删除失败')
    }
  }

  const handlePageChange = () => {
    fetchList()
  }

  return {
    list,
    loading,
    total,
    page,
    pageSize,
    dialogVisible,
    saving,
    isEdit,
    form,
    formatDate,
    extractOptions,
    fetchList,
    openCreate,
    openEdit,
    handleSave,
    handleDelete,
    handlePageChange,
  }
}
