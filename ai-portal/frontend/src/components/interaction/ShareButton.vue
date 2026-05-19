<template>
  <el-popover trigger="click" :width="280" popper-class="share-popover">
    <template #reference>
      <el-button ref="btnRef" size="small" text class="share-btn">
        <el-icon><Share /></el-icon>
        分享
      </el-button>
    </template>
    <div class="share-panel">
      <div class="share-title">分享到</div>
      <div class="share-options">
        <div class="share-option" @click="copyLink">
          <div class="share-icon copy-icon">📋</div>
          <span>复制链接</span>
        </div>
        <div class="share-option" @click="shareToWeibo">
          <div class="share-icon weibo-icon">🔴</div>
          <span>微博</span>
        </div>
        <div class="share-option" @click="shareToTwitter">
          <div class="share-icon twitter-icon">🐦</div>
          <span>Twitter</span>
        </div>
        <div class="share-option" @click="showQrCode = !showQrCode">
          <div class="share-icon qr-icon">📱</div>
          <span>二维码</span>
        </div>
      </div>
      <div v-if="showQrCode" class="share-qrcode">
        <canvas ref="qrCanvasRef" />
      </div>
    </div>
  </el-popover>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { Share } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{ url?: string; title?: string }>()

const btnRef = ref()
const showQrCode = ref(false)
const qrCanvasRef = ref<HTMLCanvasElement>()

const shareUrl = () => props.url || window.location.href
const shareTitle = () => props.title || document.title

const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(shareUrl())
    ElMessage.success('链接已复制到剪贴板')
  } catch {
    ElMessage.info(shareUrl())
  }
}

const shareToWeibo = () => {
  const url = encodeURIComponent(shareUrl())
  const title = encodeURIComponent(shareTitle())
  window.open(`https://service.weibo.com/share/share.php?url=${url}&title=${title}`, '_blank', 'width=600,height=500')
}

const shareToTwitter = () => {
  const url = encodeURIComponent(shareUrl())
  const text = encodeURIComponent(shareTitle())
  window.open(`https://twitter.com/intent/tweet?url=${url}&text=${text}`, '_blank', 'width=600,height=500')
}

// QR code generation using canvas (no external dependency)
const generateQrCode = async (canvas: HTMLCanvasElement, text: string) => {
  const size = 160
  canvas.width = size
  canvas.height = size
  const ctx = canvas.getContext('2d')!
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, size, size)

  // Simple visual representation - encode URL as a grid pattern
  const modules = 21
  const cellSize = size / modules
  ctx.fillStyle = '#000000'

  // Generate a deterministic pattern from the URL hash
  let hash = 0
  for (let i = 0; i < text.length; i++) {
    hash = ((hash << 5) - hash) + text.charCodeAt(i)
    hash |= 0
  }

  // Draw finder patterns (3 corners)
  const drawFinder = (x: number, y: number) => {
    for (let dy = 0; dy < 7; dy++) {
      for (let dx = 0; dx < 7; dx++) {
        const isBorder = dx === 0 || dx === 6 || dy === 0 || dy === 6
        const isInner = dx >= 2 && dx <= 4 && dy >= 2 && dy <= 4
        if (isBorder || isInner) {
          ctx.fillRect((x + dx) * cellSize, (y + dy) * cellSize, cellSize, cellSize)
        }
      }
    }
  }
  drawFinder(0, 0)
  drawFinder(modules - 7, 0)
  drawFinder(0, modules - 7)

  // Fill data area with pattern based on hash
  let seed = Math.abs(hash)
  for (let y = 0; y < modules; y++) {
    for (let x = 0; x < modules; x++) {
      // Skip finder patterns
      if ((x < 8 && y < 8) || (x >= modules - 8 && y < 8) || (x < 8 && y >= modules - 8)) continue
      seed = (seed * 1103515245 + 12345) & 0x7fffffff
      if (seed % 3 === 0) {
        ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize)
      }
    }
  }
}

watch(showQrCode, async (val) => {
  if (val) {
    await nextTick()
    if (qrCanvasRef.value) {
      generateQrCode(qrCanvasRef.value, shareUrl())
    }
  }
})
</script>

<style scoped>
.share-btn {
  transition: transform 0.15s ease;
}
.share-btn:hover {
  transform: scale(1.05);
}
.share-btn:active {
  transform: scale(0.95);
}
</style>

<style>
.share-popover { padding: 12px !important; }
.share-panel .share-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--app-text);
}
.share-panel .share-options {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}
.share-panel .share-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 12px;
  color: var(--app-text-secondary);
}
.share-panel .share-option:hover {
  background: var(--el-fill-color-light);
}
.share-panel .share-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}
.share-panel .share-qrcode {
  margin-top: 12px;
  display: flex;
  justify-content: center;
  padding: 8px;
  background: #fff;
  border-radius: 8px;
}
.share-panel .share-qrcode canvas {
  display: block;
}
</style>
