/**
 * 后台管理API - 仅仪表盘、监控、API密钥、日志、系统配置
 * 新增后台功能只需修改此文件，不影响业务模块API
 */
import request from './client'

// 仪表盘
export const getDashboardStats = () =>
  request.get('/v1/admin/stats')

export const getDashboardCharts = () =>
  request.get('/v1/admin/stats/charts')

// 系统监控
export const getMonitor = () =>
  request.get('/v1/admin/monitor')

export const getSystemInfo = () =>
  request.get('/v1/admin/monitor/info')

export const getProcessInfo = () =>
  request.get('/v1/admin/monitor/process')

// API密钥管理
export const getApiKeys = () =>
  request.get('/v1/admin/api-keys')

export const createApiKey = (data: any) =>
  request.post('/v1/admin/api-keys', data)

export const updateApiKey = (id: number, data: any) =>
  request.put(`/v1/admin/api-keys/${id}`, data)

export const deleteApiKey = (id: number) =>
  request.delete(`/v1/admin/api-keys/${id}`)

export const fetchModelsFromApi = (api_key: string, base_url: string, provider: string) =>
  request.post('/v1/admin/api-keys/models', null, { params: { api_key, base_url, provider } })

// 调用日志
export const getApiLogs = (params?: { page?: number; page_size?: number; provider?: string; model_name?: string }) =>
  request.get('/v1/admin/api-logs', { params })

// 系统配置
export const getSystemConfigs = () =>
  request.get('/v1/admin/configs')

export const updateSystemConfig = (key: string, value: string) =>
  request.put(`/v1/admin/configs/${key}`, { value })

// 动态管理
export const getAdminMoments = (params?: { page?: number; page_size?: number; user_id?: number }) =>
  request.get('/v1/admin/moments', { params })

export const deleteAdminMoment = (id: number) =>
  request.delete(`/v1/admin/moments/${id}`)
