<template>
  <div class="chat-view">
    <aside class="chat-sidebar" :class="{ collapsed: sidebarCollapsed, open: mobileSidebarOpen }">
      <div class="sidebar-header">
        <el-button type="primary" size="small" class="new-chat-btn" @click="handleNewChat">
          <el-icon><Plus /></el-icon>
          <span v-show="!sidebarCollapsed">新会话</span>
        </el-button>
        <el-button text :aria-label="sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'" @click="sidebarCollapsed = !sidebarCollapsed">
          <el-icon><Fold v-if="!sidebarCollapsed" /><Expand v-else /></el-icon>
        </el-button>
      </div>
      <div class="conversation-list">
        <div
          v-for="conv in chatStore.conversations" :key="conv.id"
          class="conv-item"
          :class="{ active: chatStore.currentConversationId === conv.id, pinned: conv.is_pinned }"
          @click="chatStore.selectConversation(conv.id); mobileSidebarOpen = false"
        >
          <el-icon v-if="conv.is_pinned" class="pin-icon"><Medal /></el-icon>
          <el-icon v-else><ChatLineRound /></el-icon>
          <span v-show="!sidebarCollapsed" class="conv-title">{{ conv.title }}</span>
          <el-dropdown v-show="!sidebarCollapsed" trigger="click" @command="(c:string)=>handleConvCmd(c,conv.id)">
            <el-icon class="conv-more"><More /></el-icon>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-if="!conv.is_pinned" command="pin">📌 置顶</el-dropdown-item>
                <el-dropdown-item v-else command="unpin">🚫 取消置顶</el-dropdown-item>
                <el-dropdown-item command="rename">✏️ 重命名</el-dropdown-item>
                <el-dropdown-item command="delete" divided>🗑️ 删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </aside>

    <main class="chat-main">
      <header class="chat-header">
        <el-button class="mobile-menu-btn" text @click="mobileSidebarOpen = !mobileSidebarOpen">
          <el-icon :size="20"><Fold v-if="mobileSidebarOpen" /><Expand v-else /></el-icon>
        </el-button>
        <h3>{{ chatStore.currentConversation?.title || '新会话' }}</h3>
        <div class="header-tools">
          <el-select v-model="modelsStore.currentModel" size="small" style="width:220px">
            <el-option-group v-for="group in modelGroups" :key="group.provider" :label="group.label">
              <el-option v-for="m in group.models" :key="m.id" :label="m.name" :value="m.id" />
            </el-option-group>
          </el-select>
        </div>
      </header>

      <div ref="messagesRef" class="messages-container">
        <template v-if="chatStore.messages.length > 0">
          <div v-for="msg in chatStore.messages" :key="msg.id" class="message-row" :class="msg.role">
            <div class="msg-avatar-wrap">
              <div class="msg-name">{{ msg.role === 'user' ? userName : (msg.model_name || 'AI') }}</div>
              <el-avatar :size="34">{{ msg.role === 'user' ? userName[0]?.toUpperCase() : (msg.model_name?.[0]?.toUpperCase() || 'A') }}</el-avatar>
            </div>
            <div class="msg-body">
              <div class="msg-bubble">

                <!-- 思考中 -->
                <div v-if="msg.isStreaming && !msg.streamContent" class="think-pending">
                  <span class="think-label">思考中</span>
                  <span class="think-dot" /><span class="think-dot" /><span class="think-dot" />
                </div>

                <!-- 深度思考块 -->
                <div v-if="msg.insideThinking" class="think-block active">
                  <div class="think-hd">
                    <span class="think-dot" />
                    <span>深度思考</span>
                  </div>
                  <div class="think-bd">{{ msg.thinking || msg.streamContent }}</div>
                </div>

                <!-- 已完成思考可回看 -->
                <div v-else-if="msg.thinking" class="think-block">
                  <div class="think-hd collapsible" role="button" tabindex="0" :aria-expanded="expanded[msg.id] !== false" @click="toggleThink(msg.id)" @keydown.enter="toggleThink(msg.id)">
                    <el-icon><CaretTop v-if="expanded[msg.id] !== false" /><CaretRight v-else /></el-icon>
                    <span>深度思考</span>
                  </div>
                  <div v-show="expanded[msg.id] !== false" class="think-bd" v-html="renderMd(msg.thinking)" />
                </div>

                <!-- 主体内容 -->
                <div v-if="msg.isStreaming && !msg.isDone && !msg.insideThinking" class="stream-text">
                  {{ msg.streamContent }}
                </div>
                <div v-else-if="!msg.insideThinking" class="md-body" v-html="renderFinal(msg.content)" />

                <!-- 底部元信息 -->
                <div v-if="!msg.insideThinking" class="msg-foot">
                  <div v-if="msg.isDone && msg.content" class="foot-left">
                    <el-button text size="small" class="act-btn" aria-label="复制消息" @click="cpy(msg.content, $event)">
                      <el-icon><CopyDocument /></el-icon>
                    </el-button>
                  </div>
                  <div class="foot-right">
                    <span>{{ fmt(msg.created_at) }}</span>
                    <span v-if="msg.model_name">{{ msg.model_name }}</span>
                    <span v-if="msg.duration">· {{ (msg.duration / 1000).toFixed(1) }}s</span>
                    <span v-if="msg.content != null">· {{ msg.total_tokens || Math.max(1, Math.round(msg.content.length * 0.5)) }} tok</span>
                    <span v-if="msg.duration && msg.content">· {{ Math.round(((msg.total_tokens || msg.content.length * 0.5) || 1) / (msg.duration / 1000)) }} tok/s</span>
                    <span v-if="msg.isStreaming" class="dot-grp"><span /><span /><span /></span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
        <div v-else class="empty">
          <el-icon size="56"><ChatDotRound /></el-icon>
          <h3>开始对话</h3>
          <p>选择模型，输入问题</p>
        </div>
      </div>

      <div class="input-area">
        <el-input
          v-model="inputMessage"
          type="textarea" :rows="3"
          placeholder="输入消息，Enter 发送，Shift+Enter 换行"
          resize="none"
          @keydown.enter.exact.prevent="send"
        />
        <div class="inp-actions">
          <el-button type="danger" v-if="chatStore.isGenerating" @click="chatStore.stopGeneration()">
            <el-icon><VideoPause /></el-icon> 停止
          </el-button>
          <el-button v-else type="primary" :disabled="!inputMessage.trim()" @click="send">
            <el-icon><Promotion /></el-icon> 发送
          </el-button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch, reactive, computed } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useModelsStore } from '@/stores/models'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Fold, Expand, ChatLineRound, More, Medal,
  ChatDotRound, Promotion, VideoPause,
  CopyDocument, CaretTop, CaretRight,
} from '@element-plus/icons-vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
dayjs.extend(utc)

const chatStore = useChatStore()
const modelsStore = useModelsStore()
const authStore = useAuthStore()
const inputMessage = ref('')
const sidebarCollapsed = ref(false)
const mobileSidebarOpen = ref(false)
const messagesRef = ref<HTMLElement>()
const expanded = reactive<Record<number, boolean>>({})

const userName = computed(() => authStore.user?.username || 'User')

const providerLabelMap: Record<string, string> = {
  deepseek: 'DeepSeek', openai: 'OpenAI', azure: 'Azure', glm: '智谱 GLM',
  qwen: '通义千问', doubao: '豆包', siliconflow: 'SiliconFlow',
  gemini: 'Gemini', ollama: 'Ollama', anthropic: 'Claude',
  custom: 'SiliconFlow',
}

const modelGroups = computed(() => {
  const map = new Map<string, { provider: string; label: string; models: any[] }>()
  for (const m of modelsStore.models) {
    const p = m.provider || 'other'
    if (!map.has(p)) map.set(p, { provider: p, label: providerLabelMap[p] || p, models: [] })
    map.get(p)!.models.push(m)
  }
  return Array.from(map.values())
})

const md = new MarkdownIt({ html: false, breaks: true, linkify: true,
  highlight: (code: string, lang: string) =>
    (lang && hljs.getLanguage(lang)) ? hljs.highlight(code, { language: lang }).value : hljs.highlightAuto(code).value,
})

const renderMd = (c: string) => (c ? md.render(c) : '')

const renderFinal = (c: string) => {
  if (!c) return ''
  let h = md.render(c)
  h = h.replace(
    /<pre><code class="(?:hljs )?language-(\w+)(?: .*?)?">/g,
    (_: string, lang: string) =>
      `<pre class="code-block"><span class="code-lang">${lang}</span><button class="cp-btn" onclick="window._cp(this)">复制</button><code>`
  )
  return h
}

const fmt = (s: string) => dayjs.utc(s).local().format('HH:mm:ss')
const toggleThink = (id: number) => { expanded[id] = expanded[id] === undefined ? false : !expanded[id] }

const cpy = async (text: string, e: Event) => {
  await navigator.clipboard.writeText(text)
  const btn = e.currentTarget as HTMLElement
  const span = document.createElement('span')
  span.className = 'copy-inline-toast'
  span.textContent = '✓ 已复制'
  btn.parentElement?.appendChild(span)
  const rect = btn.getBoundingClientRect()
  span.style.left = rect.left + 'px'
  span.style.top = (rect.top - 24) + 'px'
  span.style.position = 'fixed'
  setTimeout(() => span.remove(), 1200)
}

const scrollBottom = () => nextTick(() => {
  if (messagesRef.value) messagesRef.value.scrollTop = messagesRef.value.scrollHeight
})

// 跟踪思考内容长度变化以滚动
let lastThinkLen = 0
watch(() => {
  const m = chatStore.messages[chatStore.messages.length - 1]
  return m?.thinking?.length ?? 0
}, (n, o) => {
  if (n !== o) scrollBottom()
})

watch(() => chatStore.streamingContent, scrollBottom)
watch(() => chatStore.messages.length, scrollBottom)

const send = async () => {
  const c = inputMessage.value.trim()
  if (!c || chatStore.isGenerating) return
  inputMessage.value = ''
  await chatStore.sendMessage(c)
  scrollBottom()
}

const handleNewChat = async () => await chatStore.createConversation('新会话')
const handleConvCmd = async (cmd: string, id: number) => {
  if (cmd === 'delete') {
    try {
      await ElMessageBox.confirm('确定删除这个会话？删除后无法恢复。', '删除确认', {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      })
      await chatStore.deleteConversation(id)
    } catch { /* cancelled */ }
  }
  else if (cmd === 'rename') { const t = prompt('新标题：'); if (t) await chatStore.renameConversation(id, t) }
  else if (cmd === 'pin') {
    const ok = await chatStore.pinConversation(id)
    if (!ok) ElMessage.warning('最多置顶5个会话')
  }
  else if (cmd === 'unpin') await chatStore.unpinConversation(id)
}

(window as any)._cp = (btn: HTMLElement) => {
  const code = btn.closest('.code-block')?.querySelector('code')?.innerText || ''
  navigator.clipboard.writeText(code).then(() => {
    btn.textContent = '已复制'
    setTimeout(() => { btn.textContent = '复制' }, 1500)
  })
}

onMounted(async () => {
  await chatStore.fetchConversations()
  await modelsStore.fetchModels()
  if (chatStore.conversations.length > 0 && !chatStore.currentConversationId) {
    await chatStore.selectConversation(chatStore.conversations[0].id)
  }
})

onUnmounted(() => {
  delete (window as any)._cp
})
</script>

<style scoped lang="scss">
.chat-view { display: flex; height: calc(100vh - 108px); margin: -24px; }

.chat-sidebar {
  width: 260px; background: var(--app-bg-secondary); border-right: 1px solid var(--app-border);
  display: flex; flex-direction: column; transition: width .3s;
  &.collapsed { width: 60px; .sidebar-header { flex-direction: column; gap: 8px; } }
  .sidebar-header { display: flex; align-items: center; padding: 10px 12px; border-bottom: 1px solid var(--app-border); gap: 8px; .new-chat-btn { flex: 1; } }
  .conversation-list { flex: 1; overflow-y: auto; padding: 6px;
    .conv-item { display: flex; align-items: center; gap: 8px; padding: 9px 10px; border-radius: 8px; cursor: pointer; color: var(--app-text-secondary); transition: all .15s; position: relative;
      &:hover { background: rgba(64,158,255,.08); color: var(--app-text); .conv-more { opacity: 1; } }
      &.active { background: rgba(64,158,255,.14); color: var(--app-accent); }
      &.pinned { background: rgba(230,180,60,.06); .pin-icon { color: #d4a843; } }
      .pin-icon { font-size: 15px; }
      .conv-title { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 13px; }
      .conv-more { opacity: 0; padding: 4px; }
    }
  }
}

.chat-main { flex: 1; display: flex; flex-direction: column; background: var(--app-bg); min-width: 0; }
.chat-header { display: flex; align-items: center; justify-content: space-between; padding: 10px 20px; border-bottom: 1px solid var(--app-border); h3 { margin: 0; font-size: 15px; color: var(--app-text); } }

.messages-container { flex: 1; overflow-y: auto; overflow-x: hidden; padding: 16px 20px;
  .message-row { display: flex; gap: 10px; margin-bottom: 18px;
    &.user { flex-direction: row-reverse;
      .msg-bubble { background: var(--app-accent); color: #fff; }
      .msg-body { max-width: 70%; }
    }
    &.assistant {
      .msg-bubble { background: var(--app-bg-card); border: 1px solid var(--app-border); }
      .msg-body { flex: 1; max-width: none; }
    }
    .msg-avatar-wrap { flex-shrink: 0; display: flex; flex-direction: column; align-items: center; gap: 4px; width: 54px; }
    .msg-name { font-size: 11px; color: var(--app-text-secondary); text-align: center; line-height: 1.2; word-break: break-all; max-width: 54px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .msg-body { min-width: 0; display: flex; flex-direction: column; overflow: hidden; }
    .msg-bubble { padding: 10px 14px; border-radius: 10px; font-size: 14px; line-height: 1.65;
      width: 100%; max-width: 100%; box-sizing: border-box; overflow: hidden;
      .msg-foot { display: flex; align-items: center; justify-content: space-between; margin-top: 4px;
        .foot-left .act-btn { color: var(--app-text-secondary); font-size: 12px; padding: 2px 4px; &:hover { color: var(--app-text); } }
        .foot-right { font-size: 11px; color: var(--app-text-secondary); display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
        .dot-grp { display: flex; gap: 2px; align-items: center;
          span { width: 4px; height: 4px; border-radius: 50%; background: var(--app-accent); animation: blink 1.2s infinite; &:nth-child(2) { animation-delay: .2s; } &:nth-child(3) { animation-delay: .4s; } }
        }
      }
    }
  }
}

.think-pending { display: flex; gap: 4px; align-items: center; padding: 2px 0;
  .think-label { font-size: 13px; color: var(--app-text-secondary); }
  .think-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--app-accent); animation: blink 1.2s infinite; &:nth-child(2) { animation-delay: .2s; } &:nth-child(3) { animation-delay: .4s; } }
}

.think-block {
  margin-bottom: 8px; border-radius: 8px; overflow: hidden;
  border: 1px solid rgba(230,180,60,.3); background: rgba(230,180,60,.04);
  .think-hd { display: flex; align-items: center; gap: 6px; padding: 6px 10px; background: rgba(230,180,60,.1); border-bottom: 1px solid rgba(230,180,60,.15); font-size: 12px; color: #d4a843;
    &.collapsible { cursor: pointer; user-select: none; }
    .think-dot { width: 6px; height: 6px; border-radius: 50%; background: #d4a843; animation: pulse 1.2s ease-in-out infinite; }
  }
  .think-bd { padding: 8px 10px; font-family: 'Georgia','Noto Serif SC',serif; font-size: 13px; line-height: 1.7; color: #c4a35a; white-space: pre-wrap; word-break: break-word; }
}

.stream-text { white-space: pre-wrap; word-break: break-word; overflow-wrap: break-word; max-width: 100%; }

:deep(.md-body) { word-break: break-word; overflow-wrap: break-word; max-width: 100%;
  p { margin: 0 0 6px; &:last-child { margin: 0; } overflow-wrap: break-word; }
  ul, ol { margin: 6px 0; padding-left: 20px; }
  blockquote { margin: 6px 0; padding: 5px 10px; border-left: 3px solid var(--app-accent); background: rgba(64,158,255,.04); color: var(--app-text-secondary); border-radius: 0 4px 4px 0; }
  table { border-collapse: collapse; margin: 6px 0; width: 100%; overflow-x: auto; display: block; }
  th, td { border: 1px solid var(--app-border); padding: 5px 10px; font-size: 13px; }
  th { background: var(--app-bg-secondary); }

  .code-block { position: relative; margin: 8px 0; border-radius: 8px; background: #282c34; max-width: 100%; box-sizing: border-box; overflow: hidden;
    .code-lang { display: block; padding: 5px 12px 3px; font-size: 11px; color: #7f848e; background: #21252b; border-bottom: 1px solid rgba(255,255,255,.04); font-family: monospace; text-transform: uppercase; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .cp-btn { position: absolute; top: 6px; right: 8px; padding: 2px 8px; font-size: 11px; background: rgba(255,255,255,.07); border: none; border-radius: 3px; color: #7f848e; cursor: pointer; z-index: 2; line-height: 1.6; &:hover { background: rgba(255,255,255,.16); color: #abb2bf; } }
    pre { margin: 0; background: #282c34; overflow-x: auto; overflow-y: hidden; max-width: 100%; display: block; }
    code { display: block; padding: 10px 14px; font-family: 'Fira Code',Consolas,monospace; font-size: 13px; line-height: 1.55; color: #abb2bf; background: #282c34; white-space: pre; }
  }
  code:not(.code-block code) { font-family: 'Fira Code',Consolas,monospace; font-size: .88em; background: rgba(64,158,255,.1); color: #79c0ff; padding: 1px 5px; border-radius: 3px; word-break: break-all; max-width: 100%; display: inline-block; }
}

:deep(.hljs) { color: #abb2bf !important; }
:deep(.hljs-keyword) { color: #c678dd !important; }
:deep(.hljs-string) { color: #98c379 !important; }
:deep(.hljs-number) { color: #d19a66 !important; }
:deep(.hljs-built_in) { color: #e5c07b !important; }
:deep(.hljs-type) { color: #e5c07b !important; }
:deep(.hljs-function) { color: #61afef !important; }
:deep(.hljs-params) { color: #abb2bf !important; }
:deep(.hljs-comment) { color: #5c6370 !important; font-style: italic; }
:deep(.hljs-operator) { color: #56b6c2 !important; }
:deep(.hljs-variable) { color: #e06c75 !important; }
:deep(.hljs-tag) { color: #e06c75 !important; }
:deep(.hljs-attr) { color: #d19a66 !important; }
:deep(.hljs-title) { color: #61afef !important; }
:deep(.hljs-selector-tag) { color: #e06c75 !important; }
:deep(.hljs-literal) { color: #56b6c2 !important; }
:deep(.hljs-meta) { color: #61afef !important; }
:deep(.hljs-section) { color: #61afef !important; }
:deep(.hljs-symbol) { color: #56b6c2 !important; }
:deep(.hljs-regexp) { color: #98c379 !important; }
:deep(.hljs-deletion) { color: #e06c75 !important; }
:deep(.hljs-addition) { color: #98c379 !important; }
:deep(.hljs-punctuation) { color: #abb2bf !important; }
:deep(.hljs-class) { color: #e5c07b !important; }
:deep(.hljs-name) { color: #e06c75 !important; }

:deep(.code-block pre::-webkit-scrollbar) { height: 6px; }
:deep(.code-block pre::-webkit-scrollbar-track) { background: #282c34; }
:deep(.code-block pre::-webkit-scrollbar-thumb) { background: #3e4451; border-radius: 3px; }

.empty { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: var(--app-text-secondary);
  .empty-icon { margin-bottom: 12px; color: var(--app-border); }
  h3 { margin: 0 0 6px; color: var(--app-text); } p { margin: 0; font-size: 13px; }
}

.input-area { padding: 12px 16px; border-top: 1px solid var(--app-border); background: var(--app-bg-card);
  .inp-actions { display: flex; justify-content: flex-end; margin-top: 8px; gap: 8px; }
}

@keyframes blink { 0%,100% { opacity: .3; } 50% { opacity: 1; } }
@keyframes pulse { 0%,100% { opacity: .5; } 50% { opacity: 1; } }
.mobile-menu-btn { display: none; }
@media (max-width: 768px) {
  .chat-sidebar { position: absolute; z-index: 50; height: 100%; transform: translateX(-100%); transition: transform .3s; &.open { transform: translateX(0); } }
  .msg-body { max-width: 88%; }
  .mobile-menu-btn { display: inline-flex; }
}
</style>
<style>
.copy-inline-toast {
  background: #333; color: #fff; font-size: 12px; padding: 3px 8px; border-radius: 4px;
  z-index: 9999; pointer-events: none; white-space: nowrap;
  animation: fadeOut 1.2s ease forwards;
}
@keyframes fadeOut { 0% { opacity: 1; } 70% { opacity: 1; } 100% { opacity: 0; } }
</style>