import api from './client'

export const searchContent = (params: { keyword: string; target_type?: string; page?: number; page_size?: number }) =>
  api.get('/v1/search/', { params })
