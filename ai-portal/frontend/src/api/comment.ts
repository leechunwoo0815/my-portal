import api from './client'

export const listComments = (targetType: string, targetId: number) =>
  api.get(`/v1/comments/${targetType}/${targetId}`)

export const createComment = (
  targetType: string, targetId: number,
  data: { content: string; emoji?: string; parent_id?: number }
) => api.post(`/v1/comments/${targetType}/${targetId}`, data)

export const likeComment = (commentId: number) =>
  api.post(`/v1/comments/${commentId}/like`)
