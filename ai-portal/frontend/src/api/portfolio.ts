/**
 * 作品集API - 独立模块，新增/修改不影响其他模块
 */
import request from './client'

export const getProjects = (params?: { page?: number; page_size?: number; category?: string }) =>
  request.get('/v1/portfolio/projects', { params })

export const adminListProjects = (params?: { page?: number; page_size?: number; category?: string }) =>
  request.get('/v1/portfolio/admin/projects', { params })

export const getProject = (id: number) =>
  request.get(`/v1/portfolio/projects/${id}`)

export const createProject = (data: any) =>
  request.post('/v1/portfolio/projects', data)

export const updateProject = (id: number, data: any) =>
  request.put(`/v1/portfolio/projects/${id}`, data)

export const deleteProject = (id: number) =>
  request.delete(`/v1/portfolio/projects/${id}`)
