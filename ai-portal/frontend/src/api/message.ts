/**
 * 私信API
 */
import api from './client'

export const messageApi = {
  send(receiverId: number, content: string, messageType: string = 'text', imageUrl?: string) {
    return api.post('/v1/message/send', {
      receiver_id: receiverId,
      content,
      message_type: messageType,
      image_url: imageUrl || null,
    })
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
