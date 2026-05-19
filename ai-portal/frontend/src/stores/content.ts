import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useContentStore = defineStore('content', () => {
  const currentCategory = ref('')
  const currentTag = ref('')
  const searchKeyword = ref('')

  const setCategory = (cat: string) => { currentCategory.value = cat }
  const setTag = (tag: string) => { currentTag.value = tag }
  const setSearchKeyword = (kw: string) => { searchKeyword.value = kw }
  const clearFilters = () => {
    currentCategory.value = ''
    currentTag.value = ''
    searchKeyword.value = ''
  }

  return { currentCategory, currentTag, searchKeyword, setCategory, setTag, setSearchKeyword, clearFilters }
})
