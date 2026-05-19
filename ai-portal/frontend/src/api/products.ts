import request from '@/api/client'

export interface ProductItem {
  id: number
  title: string
  content: string
  category?: string
  is_published: boolean
  created_at: string
  updated_at: string
  cover_image?: string
  author_id?: number
  tags?: string
  summary?: string
}

export const listProducts = (params?: Record<string, any>) => request.get('/v1/products', { params })
export const adminListProducts = (params?: Record<string, any>) => request.get('/v1/products/admin', { params })
export const getProductById = (id: number) => request.get(`/v1/products/${id}`)
export const createProduct = (data: Partial<ProductItem>) => request.post('/v1/products', data)
export const updateProduct = (id: number, data: Partial<ProductItem>) => request.put(`/v1/products/${id}`, data)
export const deleteProduct = (id: number) => request.delete(`/v1/products/${id}`)
