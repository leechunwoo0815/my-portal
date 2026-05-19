import api from './client'

export const toggleLike = (data: { target_type: string; target_id: number }) =>
  api.post(`/v1/interaction/like/${data.target_type}/${data.target_id}`)

export const toggleFavorite = (data: { target_type: string; target_id: number }) =>
  api.post(`/v1/interaction/favorite/${data.target_type}/${data.target_id}`)

export const checkLiked = (targetType: string, targetId: number) =>
  api.get(`/v1/interaction/like-status/${targetType}/${targetId}`)

export const checkFavorited = (targetType: string, targetId: number) =>
  api.get(`/v1/interaction/favorite-status/${targetType}/${targetId}`)

export const fetchUserFavorites = (params?: Record<string, any>) =>
  api.get('/v1/interaction/favorites', { params })
