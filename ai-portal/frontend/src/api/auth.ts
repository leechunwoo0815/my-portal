/**
 * 认证相关API封装
 */
import api from './client'

export const login = (username: string, password: string, rememberMe: boolean = false) => {
  return api.post('/v1/auth/login', { username, password, remember_me: rememberMe })
}

export const getCurrentUser = () => {
  return api.get('/v1/auth/profile')
}

export const register = (data: { username: string; email: string; password: string }) => {
  return api.post('/v1/auth/register', data)
}

export const getProfile = () => {
  return api.get('/v1/auth/profile')
}

export const updateProfile = (data: any) => {
  return api.put('/v1/auth/profile', data)
}

export const uploadAvatar = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/v1/auth/avatar', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const changePassword = (oldPassword: string, newPassword: string) => {
  return api.put('/v1/auth/password', { old_password: oldPassword, new_password: newPassword })
}
