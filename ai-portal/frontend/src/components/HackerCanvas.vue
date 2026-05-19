<template>
  <canvas ref="canvas" class="hacker-canvas" />
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const canvas = ref<HTMLCanvasElement | null>(null)
let animId = 0
let lastTime = 0
let isRunning = false

interface Drop {
  x: number
  y: number
  speed: number
  len: number
  chars: string[]
  color: string
}

const CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%'
const DARK_CHARS = 'アイウエオカキクケコサシスセソタチツテトナニヌネノ'

function initDrops(w: number, isDark: boolean): Drop[] {
  const cols = Math.floor(w / 20)
  const drops: Drop[] = []
  for (let i = 0; i < cols; i++) {
    drops.push({
      x: i * 20 + 10,
      y: Math.random() * canvas.value!.height,
      speed: 1.5 + Math.random() * 2.5,
      len: 4 + Math.floor(Math.random() * 8),
      chars: Array.from({ length: 12 }, () => CHARS[Math.floor(Math.random() * CHARS.length)]),
      color: isDark ? '0,255,180' : '80,120,255',
    })
  }
  return drops
}

let drops: Drop[] = []
let dotPhase = 0

function drawDark(ctx: CanvasRenderingContext2D, drops: Drop[], h: number) {
  ctx.fillStyle = 'rgba(8, 12, 20, 0.08)'
  ctx.fillRect(0, 0, ctx.canvas.width, h)

  ctx.font = '14px monospace'
  ctx.textBaseline = 'top'

  for (const d of drops) {
    for (let i = 0; i < d.len; i++) {
      const cy = d.y - i * 16
      if (cy < -16 || cy > h) continue
      const alpha = i === 0 ? 1 : Math.max(0, 1 - i / d.len * 1.5)
      ctx.fillStyle = i === 0 ? '#00ffcc' : `rgba(0,255,180,${alpha * 0.6})`
      ctx.fillText(d.chars[i % d.chars.length], d.x, cy)
    }
    d.y += d.speed
    if (d.y - d.len * 16 > h) {
      d.y = 0
      for (let j = 0; j < d.chars.length; j++) {
        d.chars[j] = DARK_CHARS[Math.floor(Math.random() * DARK_CHARS.length)]
      }
    }
  }
}

function drawLight(ctx: CanvasRenderingContext2D, w: number, h: number, t: number) {
  ctx.fillStyle = 'rgba(224, 236, 255, 0.5)'
  ctx.fillRect(0, 0, w, h)

  ctx.strokeStyle = 'rgba(100, 160, 255, 0.06)'
  ctx.lineWidth = 1
  for (let x = 0; x < w; x += 60) {
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke()
  }
  for (let y = 0; y < h; y += 60) {
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke()
  }

  const dotCount = 15
  for (let i = 0; i < dotCount; i++) {
    const angle = (i / dotCount) * Math.PI * 2 + t * 0.0004
    const radius = 150 + Math.sin(t * 0.001 + i) * 60
    const cx = w / 2 + Math.cos(angle) * radius
    const cy = h / 2 + Math.sin(angle) * radius
    const size = 2.5 + Math.sin(t * 0.003 + i * 0.5) * 1.5
    ctx.beginPath()
    ctx.arc(cx, cy, size, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(60, 130, 255, ${0.25 + Math.sin(t * 0.001 + i) * 0.15})`
    ctx.fill()
    if (size > 3.5) {
      ctx.beginPath()
      ctx.arc(cx, cy, size + 4, 0, Math.PI * 2)
      ctx.strokeStyle = `rgba(60, 130, 255, ${0.08 + Math.sin(t * 0.002 + i) * 0.05})`
      ctx.lineWidth = 1
      ctx.stroke()
    }
  }

  ctx.beginPath()
  ctx.arc(w / 2, h / 2, 3, 0, Math.PI * 2)
  ctx.fillStyle = 'rgba(60, 130, 255, 0.7)'
  ctx.fill()

  for (let i = 0; i < 6; i++) {
    const angle = (i / 6) * Math.PI * 2 + t * 0.0002
    const r = 220 + Math.sin(t * 0.0008 + i) * 20
    const px = w / 2 + Math.cos(angle) * r
    const py = h / 2 + Math.sin(angle) * r
    ctx.beginPath()
    ctx.arc(px, py, 1.5, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(64, 158, 255, ${0.15 + Math.sin(t * 0.002 + i) * 0.08})`
    ctx.fill()
  }

  for (let i = 0; i < 4; i++) {
    const sx = (Math.sin(t * 0.0003 + i * 1.5) * 0.5 + 0.5) * w
    const sy = (Math.cos(t * 0.0002 + i * 2) * 0.5 + 0.5) * h
    const grd = ctx.createRadialGradient(sx, sy, 0, sx, sy, 200)
    grd.addColorStop(0, 'rgba(100, 180, 255, 0.03)')
    grd.addColorStop(1, 'rgba(100, 180, 255, 0)')
    ctx.fillStyle = grd
    ctx.fillRect(0, 0, w, h)
  }
}

function loop(time: number) {
  const el = canvas.value
  if (!el) return
  const ctx = el.getContext('2d')
  if (!ctx) return
  const isDark = document.documentElement.classList.contains('dark') || false

  if (time - lastTime > 16) {
    lastTime = time
    if (isDark) {
      drawDark(ctx, drops, el.height)
    } else {
      drawLight(ctx, el.width, el.height, time)
    }
  }

  if (isRunning) {
    animId = requestAnimationFrame(loop)
  }
}

function resize() {
  const el = canvas.value
  if (!el) return
  const container = el.parentElement
  if (container) {
    el.width = container.clientWidth
    el.height = container.clientHeight
  }
  const isDark = document.documentElement.classList.contains('dark') || false
  drops = initDrops(el.width, isDark)
}

let observer: IntersectionObserver | null = null

onMounted(() => {
  const el = canvas.value
  if (el) {
    const container = el.parentElement
    if (container) {
      el.width = container.clientWidth
      el.height = container.clientHeight
    }
  }
  resize()
  window.addEventListener('resize', resize)

  observer = new IntersectionObserver(
    (entries) => {
      const entry = entries[0]
      if (entry.isIntersecting) {
        if (!isRunning) {
          isRunning = true
          loop(performance.now())
        }
      } else {
        isRunning = false
        cancelAnimationFrame(animId)
      }
    },
    { threshold: 0.01 }
  )
  if (canvas.value) {
    observer.observe(canvas.value)
  }
})

onUnmounted(() => {
  isRunning = false
  cancelAnimationFrame(animId)
  window.removeEventListener('resize', resize)
  observer?.disconnect()
  observer = null
})
</script>

<style scoped>
.hacker-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}
</style>
