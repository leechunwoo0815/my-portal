<template>
  <transition name="back-to-top-fade">
    <div
      v-show="visible"
      class="back-to-top"
      role="button"
      tabindex="0"
      aria-label="回到顶部"
      @click="scrollToTop"
      @keydown.enter="scrollToTop"
    >
      <el-icon :size="20"><CaretTop /></el-icon>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { CaretTop } from '@element-plus/icons-vue'

const visible = ref(false)
let ticking = false

const handleScroll = () => {
  if (!ticking) {
    requestAnimationFrame(() => {
      visible.value = window.scrollY > 300
      ticking = false
    })
    ticking = true
  }
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => window.addEventListener('scroll', handleScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', handleScroll))
</script>

<style scoped>
.back-to-top {
  position: fixed;
  right: 32px;
  bottom: 90px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--cyber-card, #fff);
  border: 1px solid var(--cyber-border, #ddd);
  color: var(--cyber-neon, #00d4aa);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 90;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.back-to-top:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 212, 170, 0.2);
  border-color: var(--cyber-neon, #00d4aa);
}

.back-to-top-fade-enter-active,
.back-to-top-fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}
.back-to-top-fade-enter-from,
.back-to-top-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

@media (max-width: 768px) {
  .back-to-top {
    right: 20px;
    bottom: 76px;
    width: 36px;
    height: 36px;
  }
}
</style>
