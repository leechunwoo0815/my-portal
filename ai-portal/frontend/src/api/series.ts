import api from './client'

export const seriesApi = {
  list(page = 1, pageSize = 20, authorId?: number) {
    return api.get('/v1/series/', { params: { page, page_size: pageSize, ...(authorId ? { author_id: authorId } : {}) } })
  },
  get(id: number) {
    return api.get(`/v1/series/${id}`)
  },
  create(data: { title: string; description?: string; cover_image?: string; is_public?: boolean }) {
    return api.post('/v1/series/', data)
  },
  update(id: number, data: { title?: string; description?: string; cover_image?: string; is_public?: boolean }) {
    return api.put(`/v1/series/${id}`, data)
  },
  delete(id: number) {
    return api.delete(`/v1/series/${id}`)
  },
  addArticle(seriesId: number, blogId: number, order = 0) {
    return api.post(`/v1/series/${seriesId}/articles`, { blog_id: blogId, order })
  },
  removeArticle(seriesId: number, blogId: number) {
    return api.delete(`/v1/series/${seriesId}/articles/${blogId}`)
  },
}
