import api from './client'

export const recommendApi = {
  getFeed(page: number = 1, pageSize: number = 20) {
    return api.get('/v1/recommend/feed', { params: { page, page_size: pageSize } })
  },
  getHot(page: number = 1, pageSize: number = 20) {
    return api.get('/v1/recommend/hot', { params: { page, page_size: pageSize } })
  },
  getRelated(contentType: string, contentId: number, pageSize: number = 5) {
    return api.get(`/v1/recommend/related/${contentType}/${contentId}`, { params: { page_size: pageSize } })
  },
  getTrendingTags(limit: number = 20) {
    return api.get('/v1/recommend/trending-tags', { params: { limit } })
  },
}
