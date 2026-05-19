import api from './client'

export const getConversations = () => api.get('/v1/chat/conversations')

export const createConversation = (title?: string, model?: string, systemPrompt?: string) =>
  api.post('/v1/chat/conversations', { title, model, system_prompt: systemPrompt })

export const updateConversation = (id: number, title?: string, isArchived?: boolean) =>
  api.put(`/v1/chat/conversations/${id}`, { title, is_archived: isArchived })

export const deleteConversation = (id: number) =>
  api.delete(`/v1/chat/conversations/${id}`)

export const pinConversation = (id: number) =>
  api.post(`/v1/chat/conversations/${id}/pin`)

export const unpinConversation = (id: number) =>
  api.post(`/v1/chat/conversations/${id}/unpin`)

export const getMessages = (conversationId: number) =>
  api.get(`/v1/chat/conversations/${conversationId}/messages`)

export const sendMessageStream = async (
  message: string,
  conversationId?: number,
  model?: string,
  systemPrompt?: string,
  onChunk?: (chunk: any) => void,
  onDone?: (result: any) => void,
  onError?: (error: string) => void,
  signal?: AbortSignal,
) => {
  const token = localStorage.getItem('access_token')
  let doneCalled = false
  const safeOnDone = (result: any) => {
    if (doneCalled) return
    doneCalled = true
    onDone?.(result)
  }

  try {
    const response = await fetch('/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify({ message, conversation_id: conversationId, model, system_prompt: systemPrompt }),
      signal,
    })

    if (!response.ok) {
      const error = await response.json()
      onError?.(error.detail || '请求失败')
      return
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    if (!reader) { onError?.('无法读取响应'); return }

    while (true) {
      const { done, value } = await reader.read()
      if (done) {
        const line = buffer.trim()
        if (line.startsWith('data: ')) {
          try { onChunk?.(JSON.parse(line.slice(6))) } catch { }
        }
        safeOnDone(null)
        break
      }

      buffer += decoder.decode(value, { stream: true })

      while (true) {
        const pos = buffer.indexOf('\n\n')
        if (pos === -1) break
        const line = buffer.slice(0, pos).trim()
        buffer = buffer.slice(pos + 2)
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.type === 'done') {
              safeOnDone(data)
            } else if (data.type === 'error') {
              if (data.content === 'generation_stopped') {
                safeOnDone({ aborted: true })
              } else {
                onError?.(data.content)
              }
            } else {
              onChunk?.(data)
            }
          } catch { }
        }
      }
    }
  } catch (error: any) {
    if (error?.name === 'AbortError') {
      safeOnDone({ aborted: true })
    } else {
      onError?.(error.message || '网络错误')
    }
  }
}

export const getModels = () => api.get('/v1/chat/models')