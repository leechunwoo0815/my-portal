import api from './client'

export const historyApi = {
  record(contentType: string, contentId: number) {
    return api.post('/v1/history/', null, { params: { content_type: contentType, content_id: contentId } })
  },
  list(page = 1, pageSize = 20, contentType?: string) {
    return api.get('/v1/history/', { params: { page, page_size: pageSize, ...(contentType ? { content_type: contentType } : {}) } })
  },
  clear(contentType?: string) {
    return api.delete('/v1/history/', { params: { ...(contentType ? { content_type: contentType } : {}) } })
  },
}
