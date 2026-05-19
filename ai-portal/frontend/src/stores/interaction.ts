import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useInteractionStore = defineStore('interaction', () => {
  const likedItems = ref<Set<string>>(new Set())
  const favoritedItems = ref<Set<string>>(new Set())

  const key = (type: string, id: number) => `${type}:${id}`

  const setLiked = (type: string, id: number, liked: boolean) => {
    const k = key(type, id)
    if (liked) likedItems.value.add(k)
    else likedItems.value.delete(k)
  }

  const setFavorited = (type: string, id: number, favorited: boolean) => {
    const k = key(type, id)
    if (favorited) favoritedItems.value.add(k)
    else favoritedItems.value.delete(k)
  }

  const isLiked = (type: string, id: number) => likedItems.value.has(key(type, id))
  const isFavorited = (type: string, id: number) => favoritedItems.value.has(key(type, id))

  return { likedItems, favoritedItems, setLiked, setFavorited, isLiked, isFavorited }
})
