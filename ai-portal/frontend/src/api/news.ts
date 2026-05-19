import request from '@/api/client'

export interface NewsItem {
  id: number
  title: string
  content: string
  category?: string
  is_published: boolean
  created_at: string
  updated_at: string
  cover_image?: string
  author?: string
  tags?: string
  summary?: string
  content_type?: 'markdown' | 'html'
}

export const listNews = (params?: Record<string, any>) => request.get('/v1/news', { params })
export const adminListNews = (params?: Record<string, any>) => request.get('/v1/news/admin', { params })
export const getNewsById = (id: number) => request.get(`/v1/news/${id}`)
export const createNews = (data: Partial<NewsItem>) => request.post('/v1/news', data)
export const updateNews = (id: number, data: Partial<NewsItem>) => request.put(`/v1/news/${id}`, data)
export const deleteNews = (id: number) => request.delete(`/v1/news/${id}`)
