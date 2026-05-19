import api from './client'

export const fetchCategories = (params?: Record<string, any>) => api.get('/v1/category/', { params })
export const fetchCategoryTree = (moduleType?: string) => api.get('/v1/category/tree', { params: { module_type: moduleType } })
export const createCategory = (data: any) => api.post('/v1/category/', data)
export const updateCategory = (id: number, data: any) => api.put(`/v1/category/${id}/`, data)
export const deleteCategory = (id: number) => api.delete(`/v1/category/${id}/`)
