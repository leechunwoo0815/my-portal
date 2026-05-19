import { ref } from 'vue'
import { toggleLike, toggleFavorite, checkLiked, checkFavorited } from '@/api/interaction'

export function useInteraction(targetType: string, targetId: number) {
  const liked = ref(false)
  const favorited = ref(false)
  const likesCount = ref(0)
  const favoritesCount = ref(0)
  const loading = ref(false)

  const checkStatus = async () => {
    try {
      const [lRes, fRes]: any[] = await Promise.all([
        checkLiked(targetType, targetId),
        checkFavorited(targetType, targetId),
      ])
      liked.value = !!lRes?.liked
      favorited.value = !!fRes?.favorited
    } catch {}
  }

  const doLike = async () => {
    loading.value = true
    try {
      const res: any = await toggleLike({ target_type: targetType, target_id: targetId })
      liked.value = res?.liked ?? !liked.value
      likesCount.value = res?.count ?? likesCount.value + (liked.value ? 1 : -1)
    } finally {
      loading.value = false
    }
  }

  const doFavorite = async () => {
    loading.value = true
    try {
      const res: any = await toggleFavorite({ target_type: targetType, target_id: targetId })
      favorited.value = res?.favorited ?? !favorited.value
      favoritesCount.value = res?.count ?? favoritesCount.value + (favorited.value ? 1 : -1)
    } finally {
      loading.value = false
    }
  }

  return { liked, favorited, likesCount, favoritesCount, loading, checkStatus, doLike, doFavorite }
}
