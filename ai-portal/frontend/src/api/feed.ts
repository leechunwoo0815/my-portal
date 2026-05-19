import api from './client'

export const feedApi = {
  getFollowingFeed(page: number = 1, pageSize: number = 20) {
    return api.get('/v1/feed/', { params: { page, page_size: pageSize } })
  },
  getAllFeed(page: number = 1, pageSize: number = 20) {
    return api.get('/v1/feed/all', { params: { page, page_size: pageSize } })
  },
}
