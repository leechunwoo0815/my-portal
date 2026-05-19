import { describe, it, expect, vi } from 'vitest'
import { useCrudAdmin } from '../useCrudAdmin'

const mockFetchList = vi.fn()
const mockCreateItem = vi.fn()
const mockUpdateItem = vi.fn()
const mockDeleteItem = vi.fn()

const defaultForm = () => ({
  title: '',
  content: '',
  category: '',
  tags: '',
  tagsArray: [],
  is_published: true,
})

describe('useCrudAdmin', () => {
  it('initializes with default values', () => {
    const { list, loading, total, page, pageSize, saving, isEdit, dialogVisible } = useCrudAdmin({
      fetchList: mockFetchList,
      createItem: mockCreateItem,
      updateItem: mockUpdateItem,
      deleteItem: mockDeleteItem,
      defaultForm,
    })
    expect(list.value).toEqual([])
    expect(loading.value).toBe(false)
    expect(total.value).toBe(0)
    expect(saving.value).toBe(false)
    expect(isEdit.value).toBe(false)
    expect(dialogVisible.value).toBe(false)
  })

  it('openCreate resets form and opens dialog', () => {
    const { openCreate, dialogVisible, isEdit, form } = useCrudAdmin({
      fetchList: mockFetchList,
      createItem: mockCreateItem,
      updateItem: mockUpdateItem,
      deleteItem: mockDeleteItem,
      defaultForm,
    })
    openCreate()
    expect(dialogVisible.value).toBe(true)
    expect(isEdit.value).toBe(false)
    expect(form.value.title).toBe('')
  })

  it('openEdit sets isEdit and populates form', () => {
    const { openEdit, dialogVisible, isEdit, form } = useCrudAdmin({
      fetchList: mockFetchList,
      createItem: mockCreateItem,
      updateItem: mockUpdateItem,
      deleteItem: mockDeleteItem,
      defaultForm,
    })
    openEdit({ id: 1, title: 'Test', content: 'Hello', category: 'Tech', tags: 'vue,ts', is_published: true })
    expect(dialogVisible.value).toBe(true)
    expect(isEdit.value).toBe(true)
    expect(form.value.id).toBe(1)
  })

  it('handles fetchList with items response', async () => {
    mockFetchList.mockResolvedValueOnce({ items: [{ id: 1, title: 'A' }], total: 1 })
    const { fetchList, list, total } = useCrudAdmin({
      fetchList: mockFetchList,
      createItem: mockCreateItem,
      updateItem: mockUpdateItem,
      deleteItem: mockDeleteItem,
      defaultForm,
    })
    await fetchList()
    expect(list.value.length).toBe(1)
    expect(total.value).toBe(1)
  })

  it('handles fetchList with array response', async () => {
    mockFetchList.mockResolvedValueOnce([{ id: 1, title: 'A' }, { id: 2, title: 'B' }])
    const { fetchList, list, total } = useCrudAdmin({
      fetchList: mockFetchList,
      createItem: mockCreateItem,
      updateItem: mockUpdateItem,
      deleteItem: mockDeleteItem,
      defaultForm,
    })
    await fetchList()
    expect(list.value.length).toBe(2)
    expect(total.value).toBe(2)
  })

  it('prevents double save', async () => {
    mockCreateItem.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))
    const { handleSave, saving } = useCrudAdmin({
      fetchList: mockFetchList,
      createItem: mockCreateItem,
      updateItem: mockUpdateItem,
      deleteItem: mockDeleteItem,
      defaultForm,
    })
    handleSave()
    expect(saving.value).toBe(true)
  })

  it('formatDate returns formatted string', () => {
    const { formatDate } = useCrudAdmin({
      fetchList: mockFetchList,
      createItem: mockCreateItem,
      updateItem: mockUpdateItem,
      deleteItem: mockDeleteItem,
      defaultForm,
    })
    const result = formatDate('2024-01-15T10:30:00')
    expect(result).toContain('2024')
    expect(result).toContain('01')
  })
})
