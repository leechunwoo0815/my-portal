import request from '@/api/client'

export interface BlogItem {
  id: number
  title: string
  content: string
  summary?: string
  category?: string
  tags?: string
  cover_image?: string
  author_id?: number
  view_count?: number
  is_published: boolean
  created_at: string
  updated_at: string
}

export const listBlogs = (params?: Record<string, any>) => request.get('/v1/blog/posts', { params })
export const adminListBlogs = (params?: Record<string, any>) => request.get('/v1/blog/admin/posts', { params })
export const getBlogById = (id: number) => request.get(`/v1/blog/posts/${id}`)
export const createBlog = (data: Partial<BlogItem>) => request.post('/v1/blog/posts', data)
export const updateBlog = (id: number, data: Partial<BlogItem>) => request.put(`/v1/blog/posts/${id}`, data)
export const deleteBlog = (id: number) => request.delete(`/v1/blog/posts/${id}`)
