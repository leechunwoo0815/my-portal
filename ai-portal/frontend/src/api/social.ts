/**
 * 社交关系API
 */
import api from './client'

export const socialApi = {
  toggleFollow(userId: number) {
    return api.post(`/v1/social/follow/${userId}`)
  },
  getFollowStatus(userId: number) {
    return api.get(`/v1/social/follow-status/${userId}`)
  },
  getFollowers(userId: number, page = 1, pageSize = 20) {
    return api.get(`/v1/social/followers/${userId}`, { params: { page, page_size: pageSize } })
  },
  getFollowing(userId: number, page = 1, pageSize = 20) {
    return api.get(`/v1/social/following/${userId}`, { params: { page, page_size: pageSize } })
  },
  getFriends(userId: number, page = 1, pageSize = 20) {
    return api.get(`/v1/social/friends/${userId}`, { params: { page, page_size: pageSize } })
  },
  removeFollower(userId: number) {
    return api.post(`/v1/social/remove-follower/${userId}`)
  },
}
