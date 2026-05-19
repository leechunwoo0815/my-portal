import request from '@/api/client'

export interface SolutionItem {
  id: number
  title: string
  description: string
  content: string
  is_published: boolean
  created_at: string
  updated_at: string
  cover_image?: string
  author_id?: number
  category?: string
  tags?: string
  summary?: string
}

export const listSolutions = (params?: Record<string, any>) => request.get('/v1/solutions', { params })
export const adminListSolutions = (params?: Record<string, any>) => request.get('/v1/solutions/admin', { params })
export const getSolutionById = (id: number) => request.get(`/v1/solutions/${id}`)
export const createSolution = (data: Partial<SolutionItem>) => request.post('/v1/solutions', data)
export const updateSolution = (id: number, data: Partial<SolutionItem>) => request.put(`/v1/solutions/${id}`, data)
export const deleteSolution = (id: number) => request.delete(`/v1/solutions/${id}`)
