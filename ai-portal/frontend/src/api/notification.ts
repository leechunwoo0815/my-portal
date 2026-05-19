import api from './client'

export const fetchNotifications = (params?: Record<string, any>) => api.get('/v1/user/notifications', { params })
export const markNotificationRead = (id: number) => api.put(`/v1/user/notifications/${id}/read`)
export const markAllNotificationsRead = () => api.put('/v1/user/notifications/read-all')
export const getUnreadCount = () => api.get('/v1/user/notifications/unread-count')
