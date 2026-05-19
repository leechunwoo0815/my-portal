/**
 * 动态API
 */
import api from './client'

export const momentApi = {
  create(data: { content: string; images?: string[]; is_public?: boolean }) {
    return api.post('/v1/moment', data)
  },
  list(page = 1, pageSize = 20) {
    return api.get('/v1/moment', { params: { page, page_size: pageSize } })
  },
  listFollowing(page = 1, pageSize = 20) {
    return api.get('/v1/moment/following', { params: { page, page_size: pageSize } })
  },
  getMy(page = 1, pageSize = 20) {
    return api.get('/v1/moment/my', { params: { page, page_size: pageSize } })
  },
  getDetail(momentId: number) {
    return api.get(`/v1/moment/${momentId}`)
  },
  delete(momentId: number) {
    return api.delete(`/v1/moment/${momentId}`)
  },
  like(momentId: number) {
    return api.post(`/v1/moment/${momentId}/like`)
  },
  repost(momentId: number, content = '') {
    return api.post(`/v1/moment/${momentId}/repost`, { content })
  },
}

// Named exports for direct import
export const createMoment = momentApi.create
export const listMoments = momentApi.list
