/**
 * 私信API
 */
import api from './client'

export const messageApi = {
  send(receiverId: number, content: string) {
    return api.post('/v1/message/send', { receiver_id: receiverId, content })
  },
  getConversations() {
    return api.get('/v1/message/conversations')
  },
  getConversationMessages(userId: number) {
    return api.get(`/v1/message/conversations/${userId}`)
  },
  markAsRead(userId: number) {
    return api.put(`/v1/message/read/${userId}`)
  },
  getUnreadCount() {
    return api.get('/v1/message/unread-count')
  },
}
