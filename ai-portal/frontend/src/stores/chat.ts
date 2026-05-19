import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getConversations, createConversation as createConvApi,
  updateConversation as updateConvApi, deleteConversation as deleteConvApi,
  getMessages as getMessagesApi, sendMessageStream,
  pinConversation, unpinConversation,
} from '@/api/chat'
import { useModelsStore } from '@/stores/models'
import { ElMessage } from 'element-plus'

interface Conversation {
  id: number; title: string; model_name: string; system_prompt: string | null
  is_archived: boolean; is_pinned: boolean
  created_at: string; updated_at: string; message_count?: number
}

interface ChatMessage {
  id: number; role: 'user' | 'assistant' | 'system'
  content: string; model_name: string | null; token_count: number | null
  created_at: string
  isStreaming?: boolean; isDone?: boolean; streamContent?: string
  thinking?: string
  insideThinking?: boolean
  prompt_tokens?: number; completion_tokens?: number; total_tokens?: number
  duration?: number
}

export const useChatStore = defineStore('chat', () => {
  const conversations = ref<Conversation[]>([])

  const pinnedCount = computed(() => conversations.value.filter(c => c.is_pinned).length)

  const sortedConversations = computed(() =>
    [...conversations.value].sort((a, b) => {
      if (a.is_pinned !== b.is_pinned) return a.is_pinned ? -1 : 1
      return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    })
  )
  const currentConversationId = ref<number | null>(null)
  const messages = ref<ChatMessage[]>([])
  const isGenerating = ref(false)
  const streamingContent = ref('')

  let abortController: AbortController | null = null
  let _activeConvId: number | null = null

  const currentConversation = computed(() =>
    conversations.value.find(c => c.id === currentConversationId.value)
  )

  const fetchConversations = async () => {
    try { conversations.value = await getConversations() as any }
    catch (e) { (window as any).__LOG?.('error', '获取会话列表失败', e) }
  }

  const createConversation = async (title?: string, model?: string, systemPrompt?: string) => {
    try {
      const res: any = await createConvApi(title, model, systemPrompt)
      conversations.value.unshift(res)
      currentConversationId.value = res.id
      messages.value = []
      return res
    } catch (e) { (window as any).__LOG?.('error', '创建会话失败', e) }
  }

  const selectConversation = async (id: number) => {
    const requestId = id
    // 先停止正在进行的生成
    if (isGenerating.value) stopGeneration()
    if (abortController) { abortController.abort(); abortController = null }
    isGenerating.value = false
    streamingContent.value = ''
    _activeConvId = null

    currentConversationId.value = id
    messages.value = []
    try {
      const res: any = await getMessagesApi(id)
      if (currentConversationId.value !== requestId) return
      messages.value = res.map((m: any) => ({
        ...m, isStreaming: false, isDone: true, streamContent: m.content,
      }))
    } catch (e) { (window as any).__LOG?.('error', '加载消息失败', e); messages.value = [] }
  }

  const deleteConversation = async (id: number) => {
    try {
      await deleteConvApi(id)
      conversations.value = conversations.value.filter(c => c.id !== id)
      if (currentConversationId.value === id) {
        currentConversationId.value = null; messages.value = []
      }
    } catch (e) { (window as any).__LOG?.('error', '删除会话失败', e) }
  }

  const renameConversation = async (id: number, title: string) => {
    try {
      await updateConvApi(id, title)
      const idx = conversations.value.findIndex(c => c.id === id)
      if (idx !== -1) conversations.value.splice(idx, 1, { ...conversations.value[idx], title })
    } catch (e) { (window as any).__LOG?.('error', '重命名会话失败', e) }
  }

  const pinConversationAction = async (id: number) => {
    if (pinnedCount.value >= 5) {
      (window as any).__LOG?.('warn', '置顶会话最多5个')
      return false
    }
    try {
      await pinConversation(id)
      const idx = conversations.value.findIndex(c => c.id === id)
      if (idx !== -1) conversations.value.splice(idx, 1, { ...conversations.value[idx], is_pinned: true })
      return true
    } catch (e) { (window as any).__LOG?.('error', '置顶会话失败', e); return false }
  }

  const unpinConversationAction = async (id: number) => {
    try {
      await unpinConversation(id)
      const idx = conversations.value.findIndex(c => c.id === id)
      if (idx !== -1) conversations.value.splice(idx, 1, { ...conversations.value[idx], is_pinned: false })
    } catch (e) { (window as any).__LOG?.('error', '取消置顶失败', e) }
  }

  const stopGeneration = async () => {
    if (abortController) {
      abortController.abort()
      abortController = null
    }
    const convId = currentConversationId.value
    if (convId && _activeConvId === convId) {
      try {
        const token = localStorage.getItem('access_token') || ''
        await fetch(`/api/v1/chat/completions/cancel/${convId}`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        })
      } catch (_) {}
    }
  }

  const sendMessage = async (content: string) => {
    const modelStore = useModelsStore()
    if (!currentConversationId.value) {
      await createConversation(content.slice(0, 30), modelStore.currentModel)
    }
    if (!currentConversationId.value) {
      ElMessage.error('创建会话失败')
      return
    }
    const convId = currentConversationId.value!
    const uid = Date.now()
    const aid = uid + 1
    _activeConvId = convId

    messages.value.push({
      id: uid, role: 'user', content, model_name: null, token_count: null,
      created_at: new Date().toISOString(), isStreaming: false, isDone: true,
    })

    messages.value.push({
      id: aid, role: 'assistant', content: '', model_name: modelStore.currentModel,
      token_count: null, created_at: new Date().toISOString(),
      isStreaming: true, isDone: false, streamContent: '', thinking: '', insideThinking: false,
    })

    isGenerating.value = true
    streamingContent.value = ''

    let rawContent = ''
    let thinkingRaw = ''
    let seenThink = false
    const startTime = performance.now()

    const updateMsg = (patch: Partial<ChatMessage>) => {
      const idx = messages.value.findIndex(m => m.id === aid)
      if (idx !== -1) messages.value[idx] = { ...messages.value[idx], ...patch }
    }

    abortController = new AbortController()

    await sendMessageStream(
      content, convId, modelStore.currentModel,
      currentConversation.value?.system_prompt || undefined,
      // onChunk
      (chunk) => {
        if (chunk.type === 'thinking') {
          thinkingRaw += chunk.content
          seenThink = true
          updateMsg({
            thinking: thinkingRaw,
            insideThinking: true,
          })
        } else if (chunk.type === 'content') {
          rawContent += chunk.content
          streamingContent.value = rawContent

          // 内容开始到达，思考阶段结束
          const isThinkingNow = seenThink && thinkingRaw && !rawContent.trim() ? true : false

          // 检查 <thinking> 标签（fallback）
          const hasOpen = rawContent.includes('<thinking>')
          const hasClose = rawContent.includes('</thinking>')
          let bootThinking = false
          if (hasOpen && hasClose) {
            const fromOpen = rawContent.indexOf('<thinking>')
            const lastClose = rawContent.lastIndexOf('</thinking>')
            if (lastClose > fromOpen) {
              thinkingRaw = rawContent.slice(fromOpen + 10, lastClose).trim()
              seenThink = true
            } else {
              // 未闭合
              thinkingRaw = rawContent.slice(fromOpen + 10).trim()
              seenThink = true
            }
            bootThinking = rawContent.lastIndexOf('<thinking>') > rawContent.lastIndexOf('</thinking>')
          }

          updateMsg({
            streamContent: rawContent,
            content: rawContent,
            thinking: thinkingRaw || undefined,
            insideThinking: bootThinking || isThinkingNow,
          })
        }
      },
      // onDone
      (result) => {
        const duration = performance.now() - startTime

        if (result?.aborted) {
          updateMsg({
            streamContent: rawContent,
            content: rawContent,
            isStreaming: false, isDone: true,
            insideThinking: false, duration: Math.round(duration),
            thinking: thinkingRaw || undefined,
          })
        } else {
          const pt = result?.prompt_tokens || 0
          const ct = result?.completion_tokens || 0
          const tt = result?.total_tokens || 0

          let finalThinking: string | undefined = thinkingRaw || undefined
          let clean = rawContent
          // 清理内嵌 <thinking> 标签
          const ts = rawContent.indexOf('<thinking>')
          const te = rawContent.lastIndexOf('</thinking>')
          if (ts !== -1 && te !== -1 && te > ts) {
            if (!finalThinking) finalThinking = rawContent.slice(ts + 10, te).trim()
            clean = (rawContent.slice(0, ts) + rawContent.slice(te + 12)).trim()
          } else {
            clean = rawContent.trim()
          }

          updateMsg({
            content: clean,
            streamContent: clean,
            isStreaming: false, isDone: true,
            thinking: finalThinking, insideThinking: false,
            prompt_tokens: pt, completion_tokens: ct, total_tokens: tt,
            duration: Math.round(duration),
          })
        }
        isGenerating.value = false
        streamingContent.value = ''
        abortController = null
        _activeConvId = null
        fetchConversations()
      },
      // onError
      (error) => {
        updateMsg({ content: error, isStreaming: false, isDone: true, insideThinking: false })
        isGenerating.value = false
        abortController = null
        _activeConvId = null
      },
      abortController.signal,
    )
  }

  return {
    conversations: sortedConversations,
    pinnedCount,
    currentConversationId, currentConversation,
    messages, isGenerating, streamingContent,
    fetchConversations, createConversation, selectConversation,
    deleteConversation, renameConversation, sendMessage, stopGeneration,
    pinConversation: pinConversationAction, unpinConversation: unpinConversationAction,
  }
})