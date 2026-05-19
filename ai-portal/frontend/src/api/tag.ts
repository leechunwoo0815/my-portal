import api from './client'

export const fetchTags = (params?: Record<string, any>) => api.get('/v1/tag/', { params })
export const fetchPopularTags = (limit?: number) => api.get('/v1/tag/popular', { params: { limit } })
export const createTag = (data: any) => api.post('/v1/tag/', data)
export const updateTag = (id: number, data: any) => api.put(`/v1/tag/${id}/`, data)
export const deleteTag = (id: number) => api.delete(`/v1/tag/${id}/`)
