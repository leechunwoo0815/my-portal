<template>
  <div class="md-editor-wrapper" :class="{ fullscreen: isFullscreen }">
    <!-- 工具栏 -->
    <div class="md-toolbar">
      <div class="toolbar-group">
        <button type="button" class="toolbar-btn" title="加粗" @click="insert('**', '**')">
          <b>B</b>
        </button>
        <button type="button" class="toolbar-btn" title="斜体" @click="insert('*', '*')">
          <i>I</i>
        </button>
        <button type="button" class="toolbar-btn" title="删除线" @click="insert('~~', '~~')">
          <s>S</s>
        </button>
        <span class="toolbar-divider" />
        <button type="button" class="toolbar-btn" title="标题1" @click="insertLine('# ')">H1</button>
        <button type="button" class="toolbar-btn" title="标题2" @click="insertLine('## ')">H2</button>
        <button type="button" class="toolbar-btn" title="标题3" @click="insertLine('### ')">H3</button>
        <span class="toolbar-divider" />
        <button type="button" class="toolbar-btn" title="无序列表" @click="insertLine('- ')">•</button>
        <button type="button" class="toolbar-btn" title="有序列表" @click="insertLine('1. ')">1.</button>
        <button type="button" class="toolbar-btn" title="引用" @click="insertLine('> ')">"</button>
        <button type="button" class="toolbar-btn" title="代码块" @click="insert('```\n', '\n```')">
          &lt;/&gt;
        </button>
        <button type="button" class="toolbar-btn" title="行内代码" @click="insert('`', '`')">
          <code>`</code>
        </button>
        <span class="toolbar-divider" />
        <button type="button" class="toolbar-btn" title="链接" @click="insert('[', '](url)')">
          🔗
        </button>
        <button type="button" class="toolbar-btn" title="图片" @click="insert('![alt](', ')')">
          🖼️
        </button>
        <button type="button" class="toolbar-btn" title="表格" @click="insertTable">
          ⊞
        </button>
        <button type="button" class="toolbar-btn" title="分割线" @click="insertLine('---\n')">
          —
        </button>
        <span class="toolbar-divider" />
        <button type="button" class="toolbar-btn" title="上传图片" @click="triggerImageUpload">
          📤
        </button>
      </div>
      <div class="toolbar-group">
        <button
          v-for="mode in (['edit', 'split', 'preview'] as const)"
          :key="mode"
          type="button"
          class="toolbar-btn"
          :class="{ active: viewMode === mode }"
          @click="viewMode = mode"
        >
          {{ mode === 'edit' ? '编辑' : mode === 'split' ? '分屏' : '预览' }}
        </button>
        <button type="button" class="toolbar-btn" @click="toggleFullscreen">
          {{ isFullscreen ? '退出全屏' : '全屏' }}
        </button>
      </div>
    </div>

    <!-- 编辑器主体 -->
    <div class="md-body" :class="`mode-${viewMode}`">
      <!-- 编辑区 -->
      <div v-show="viewMode !== 'preview'" class="md-edit-pane">
        <textarea
          ref="textareaRef"
          v-model="content"
          class="md-textarea"
          :placeholder="placeholder"
          @input="onInput"
          @keydown="onKeydown"
        />
      </div>

      <!-- 预览区 -->
      <div v-show="viewMode !== 'edit'" class="md-preview-pane">
        <div class="md-preview-content" v-html="renderedHtml" />
      </div>
    </div>

    <!-- 隐藏的图片上传 input -->
    <input
      ref="imageInput"
      type="file"
      accept="image/*"
      style="display:none"
      @change="onImageSelected"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import { uploadImage } from '@/api/upload'
import { ElMessage } from 'element-plus'

const props = withDefaults(defineProps<{
  modelValue?: string
  placeholder?: string
  module?: string
}>(), {
  modelValue: '',
  placeholder: '开始写作...',
  module: 'blog',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'change': [value: string]
}>()

const content = ref(props.modelValue || '')
const viewMode = ref<'edit' | 'split' | 'preview'>('split')
const isFullscreen = ref(false)
const textareaRef = ref<HTMLTextAreaElement>()
const imageInput = ref<HTMLInputElement>()

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight(str: string, lang: string) {
    if (lang && hljs.getLanguage(lang)) {
      try { return `<pre class="hljs"><code>${hljs.highlight(str, { language: lang }).value}</code></pre>` } catch {}
    }
    return `<pre class="hljs"><code>${md.utils.escapeHtml(str)}</code></pre>`
  },
})

const renderedHtml = computed(() => md.render(content.value || ''))

watch(() => props.modelValue, (v) => {
  if (v !== content.value) content.value = v || ''
})

// Draft auto-save
const draftKey = computed(() => `draft_${props.module}`)
let draftTimer: ReturnType<typeof setInterval> | null = null

const saveDraft = () => {
  if (content.value.trim()) {
    localStorage.setItem(draftKey.value, content.value)
  }
}

const loadDraft = () => {
  const saved = localStorage.getItem(draftKey.value)
  if (saved && !props.modelValue) {
    content.value = saved
    emit('update:modelValue', saved)
    emit('change', saved)
    ElMessage.info('已恢复未保存的草稿')
  }
}

const clearDraft = () => {
  localStorage.removeItem(draftKey.value)
}

// Clear draft when modelValue is set externally (e.g., after save)
watch(() => props.modelValue, (v, old) => {
  if (v !== content.value) content.value = v || ''
  if (old && !v) clearDraft() // cleared after save
})

onMounted(() => {
  loadDraft()
  draftTimer = setInterval(saveDraft, 30000)
})

onUnmounted(() => {
  if (draftTimer) clearInterval(draftTimer)
})

function onInput() {
  emit('update:modelValue', content.value)
  emit('change', content.value)
}

function getSelection() {
  const ta = textareaRef.value
  if (!ta) return { start: 0, end: 0, text: '' }
  return {
    start: ta.selectionStart,
    end: ta.selectionEnd,
    text: content.value.substring(ta.selectionStart, ta.selectionEnd),
  }
}

function setSelection(start: number, end: number) {
  const ta = textareaRef.value
  if (!ta) return
  ta.focus()
  requestAnimationFrame(() => {
    ta.setSelectionRange(start, end)
  })
}

function insert(before: string, after: string) {
  const { start, end, text } = getSelection()
  const newText = before + text + after
  content.value = content.value.substring(0, start) + newText + content.value.substring(end)
  emit('update:modelValue', content.value)
  emit('change', content.value)
  setSelection(start + before.length, start + before.length + text.length)
}

function insertLine(prefix: string) {
  const { start } = getSelection()
  const before = content.value.substring(0, start)
  const after = content.value.substring(start)
  const needsNewline = before.length > 0 && !before.endsWith('\n')
  content.value = before + (needsNewline ? '\n' : '') + prefix + after
  emit('update:modelValue', content.value)
  emit('change', content.value)
  const newPos = before.length + (needsNewline ? 1 : 0) + prefix.length
  setSelection(newPos, newPos)
}

function insertTable() {
  const table = '\n| 列1 | 列2 | 列3 |\n| --- | --- | --- |\n| 内容 | 内容 | 内容 |\n'
  const { start } = getSelection()
  content.value = content.value.substring(0, start) + table + content.value.substring(start)
  emit('update:modelValue', content.value)
  emit('change', content.value)
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Tab') {
    e.preventDefault()
    const { start, end } = getSelection()
    content.value = content.value.substring(0, start) + '    ' + content.value.substring(end)
    emit('update:modelValue', content.value)
    setSelection(start + 4, start + 4)
  }
}

function toggleFullscreen() {
  isFullscreen.value = !isFullscreen.value
}

function triggerImageUpload() {
  imageInput.value?.click()
}

async function onImageSelected(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return

  if (!file.type.startsWith('image/')) {
    ElMessage.error('请选择图片文件')
    ;(e.target as HTMLInputElement).value = ''
    return
  }
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过10MB')
    ;(e.target as HTMLInputElement).value = ''
    return
  }

  try {
    const res: any = await uploadImage(file, props.module)
    if (res.url) {
      const { start } = getSelection()
      const imgMarkdown = `\n![${file.name}](${res.url})\n`
      content.value = content.value.substring(0, start) + imgMarkdown + content.value.substring(start)
      emit('update:modelValue', content.value)
      emit('change', content.value)
      ElMessage.success('图片上传成功')
    }
  } catch (err: any) {
    console.error('Image upload failed:', err)
    ElMessage.error(err?.message || '图片上传失败')
  }
  ;(e.target as HTMLInputElement).value = ''
}

defineExpose({
  getMarkdown: () => content.value,
})
</script>

<style scoped>
.md-editor-wrapper {
  border: 1px solid var(--el-border-color, #dcdfe6);
  border-radius: 8px;
  overflow: hidden;
  background: var(--el-bg-color, #fff);
  display: flex;
  flex-direction: column;
  height: 550px;
}
.md-editor-wrapper.fullscreen {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 9999;
  border-radius: 0;
  height: 100vh;
}

/* 工具栏 */
.md-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  border-bottom: 1px solid var(--el-border-color-lighter, #e4e7ed);
  background: var(--el-fill-color-lighter, #f5f7fa);
  flex-shrink: 0;
  gap: 8px;
  flex-wrap: wrap;
}
.toolbar-group {
  display: flex;
  align-items: center;
  gap: 2px;
  flex-wrap: wrap;
}
.toolbar-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 28px;
  padding: 0 6px;
  border: 1px solid transparent;
  border-radius: 4px;
  background: transparent;
  color: var(--el-text-color-regular, #606266);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}
.toolbar-btn:hover {
  background: var(--el-fill-color, #f2f3f5);
  border-color: var(--el-border-color, #dcdfe6);
}
.toolbar-btn.active {
  background: var(--el-color-primary, #409eff);
  color: #fff;
  border-color: var(--el-color-primary, #409eff);
}
.toolbar-divider {
  width: 1px;
  height: 20px;
  background: var(--el-border-color-lighter, #e4e7ed);
  margin: 0 4px;
}

/* 编辑器主体 */
.md-body {
  display: flex;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}
.mode-edit .md-edit-pane { flex: 1; }
.mode-split .md-edit-pane { flex: 1; }
.mode-split .md-preview-pane { flex: 1; }
.mode-preview .md-preview-pane { flex: 1; }

.md-edit-pane {
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}
.md-textarea {
  flex: 1;
  width: 100%;
  padding: 16px;
  border: none;
  outline: none;
  resize: none;
  font-family: 'Fira Code', 'JetBrains Mono', Consolas, Monaco, monospace;
  font-size: 14px;
  line-height: 1.7;
  color: var(--el-text-color-primary, #303133);
  background: var(--el-bg-color, #fff);
  tab-size: 4;
}
.md-textarea::placeholder {
  color: var(--el-text-color-placeholder, #a8abb2);
}

.md-preview-pane {
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: auto;
  border-left: 1px solid var(--el-border-color-lighter, #e4e7ed);
}
.md-preview-content {
  padding: 20px 24px;
  line-height: 1.8;
  color: var(--el-text-color-primary, #303133);
  font-size: 15px;
}

/* Markdown 预览样式 */
.md-preview-content h1 { font-size: 28px; margin: 24px 0 16px; font-weight: 700; border-bottom: 2px solid var(--el-border-color-lighter, #e4e7ed); padding-bottom: 8px; }
.md-preview-content h2 { font-size: 22px; margin: 20px 0 12px; font-weight: 700; border-bottom: 1px solid var(--el-border-color-lighter, #e4e7ed); padding-bottom: 6px; }
.md-preview-content h3 { font-size: 18px; margin: 16px 0 10px; font-weight: 600; }
.md-preview-content h4 { font-size: 16px; margin: 14px 0 8px; font-weight: 600; }
.md-preview-content p { margin: 8px 0; }
.md-preview-content ul, .md-preview-content ol { padding-left: 24px; margin: 8px 0; }
.md-preview-content li { margin: 4px 0; }
.md-preview-content blockquote {
  margin: 12px 0; padding: 8px 16px;
  border-left: 4px solid var(--el-color-primary, #409eff);
  background: var(--el-fill-color-lighter, #f5f7fa);
  border-radius: 4px;
}
.md-preview-content code {
  background: var(--el-fill-color, #f2f3f5);
  padding: 2px 6px; border-radius: 4px;
  font-size: 13px;
  font-family: 'Fira Code', Consolas, Monaco, monospace;
}
.md-preview-content pre {
  margin: 12px 0; border-radius: 8px; overflow-x: auto;
}
.md-preview-content pre code {
  display: block; padding: 16px;
  background: #1e1e1e; color: #d4d4d4;
  border-radius: 8px; font-size: 13px; line-height: 1.6;
}
.md-preview-content img { max-width: 100%; border-radius: 8px; margin: 8px 0; }
.md-preview-content table { width: 100%; border-collapse: collapse; margin: 12px 0; }
.md-preview-content th, .md-preview-content td { border: 1px solid var(--el-border-color, #dcdfe6); padding: 8px 12px; text-align: left; }
.md-preview-content th { background: var(--el-fill-color-lighter, #f5f7fa); font-weight: 600; }
.md-preview-content a { color: var(--el-color-primary, #409eff); text-decoration: none; }
.md-preview-content a:hover { text-decoration: underline; }
.md-preview-content hr { border: none; border-top: 1px solid var(--el-border-color-lighter, #e4e7ed); margin: 16px 0; }
</style>
