/**
 * 用户主页API
 */
import api from './client'

export interface UserProfile {
  user_id: number
  username: string
  nickname?: string
  avatar_url?: string
  bio?: string
  level: number
  level_title: string
  points: number
  total_points: number
  followers_count: number
  following_count: number
  friends_count: number
  is_following: boolean
  is_followed_by: boolean
  is_mutual: boolean
  gender?: string
  location?: string
  website?: string
  github?: string
  created_at: string
}

export const userApi = {
  getUserProfile(userId: number): Promise<UserProfile> {
    return api.get(`/v1/user/${userId}`)
  },
  getUserBlogs(userId: number, page = 1, pageSize = 20) {
    return api.get(`/v1/user/${userId}/blogs`, { params: { page, page_size: pageSize } })
  },
  getUserProjects(userId: number, page = 1, pageSize = 20) {
    return api.get(`/v1/user/${userId}/projects`, { params: { page, page_size: pageSize } })
  },
  getUserMoments(userId: number, page = 1, pageSize = 20) {
    return api.get(`/v1/user/${userId}/moments`, { params: { page, page_size: pageSize } })
  },
}
