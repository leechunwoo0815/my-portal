<template>
  <div class="default-layout">
    <header class="navbar">
      <div class="navbar-brand">
        <router-link to="/" class="brand-link">
          <span class="terminal-prefix">&gt;_</span>
          <span class="brand-text">AI Portal</span>
          <span class="cursor-blink">█</span>
        </router-link>
      </div>

      <nav class="navbar-nav">
        <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </router-link>
        <router-link to="/blog" class="nav-link" :class="{ active: $route.path.startsWith('/blog') }">
          <el-icon><Document /></el-icon>
          <span>博客</span>
        </router-link>
        <router-link to="/news" class="nav-link" :class="{ active: $route.path.startsWith('/news') }">
          <el-icon><Bell /></el-icon>
          <span>资讯</span>
        </router-link>
        <router-link to="/products" class="nav-link" :class="{ active: $route.path.startsWith('/products') }">
          <el-icon><Goods /></el-icon>
          <span>产品</span>
        </router-link>
        <router-link to="/solutions" class="nav-link" :class="{ active: $route.path.startsWith('/solutions') }">
          <el-icon><Tools /></el-icon>
          <span>方案</span>
        </router-link>
        <router-link to="/series" class="nav-link" :class="{ active: $route.path.startsWith('/series') }">
          <el-icon><Collection /></el-icon>
          <span>专栏</span>
        </router-link>
        <router-link to="/moment" class="nav-link" :class="{ active: $route.path.startsWith('/moment') }">
          <el-icon><ChatLineRound /></el-icon>
          <span>动态</span>
        </router-link>
        <router-link to="/chat" class="nav-link" :class="{ active: $route.path === '/chat' }">
          <el-icon><ChatDotRound /></el-icon>
          <span>AI助手</span>
        </router-link>
      </nav>

      <div class="navbar-actions">
        <div class="search-box">
          <span class="search-prefix">&gt;_</span>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索..."
            size="small"
            clearable
            @keyup.enter="handleSearch"
          />
        </div>

        <ThemeToggle />

        <template v-if="authStore.isLoggedIn">
          <router-link to="/notifications" class="nav-icon" title="通知">
            <el-badge :value="unreadNotifications" :hidden="!unreadNotifications">
              <el-icon :size="20"><Bell /></el-icon>
            </el-badge>
          </router-link>
          <el-dropdown>
            <span class="user-info">
              <el-avatar :size="32" :src="authStore.user?.avatar_url || undefined" class="user-avatar">
                {{ authStore.user?.username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <span class="username">{{ authStore.user?.nickname || authStore.user?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="$router.push(`/user/${authStore.user?.id}`)">
                  <el-icon><User /></el-icon>个人主页
                </el-dropdown-item>
                <el-dropdown-item @click="$router.push('/admin/profile')">
                  <el-icon><Setting /></el-icon>个人设置
                </el-dropdown-item>
                <el-dropdown-item v-if="authStore.isAdmin" @click="$router.push('/admin')">
                  <el-icon><Setting /></el-icon>后台管理
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <el-button size="small" @click="$router.push('/login')">登录</el-button>
          <el-button type="primary" size="small" @click="$router.push('/register')">注册</el-button>
        </template>
      </div>
    </header>

    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <BackToTop />

    <footer class="footer">
      <div class="footer-content">
        <p class="footer-brand">&gt;_ AI Portal · 技术改变世界</p>
        <p class="footer-sub">Built with Vue 3 + FastAPI · Cyberpunk Edition</p>
      </div>
    </footer>

    <div class="mobile-nav" v-if="isMobile">
      <router-link to="/" class="mobile-nav-item" :class="{ active: $route.path === '/' }">
        <el-icon><HomeFilled /></el-icon>
        <span>首页</span>
      </router-link>
      <router-link to="/blog" class="mobile-nav-item" :class="{ active: $route.path.startsWith('/blog') }">
        <el-icon><Document /></el-icon>
        <span>博客</span>
      </router-link>
      <router-link to="/moment" class="mobile-nav-item create-btn">
        <el-icon><Plus /></el-icon>
        <span>发布</span>
      </router-link>
      <router-link to="/notifications" class="mobile-nav-item" :class="{ active: $route.path.startsWith('/notification') }">
        <el-icon><Bell /></el-icon>
        <span>通知</span>
      </router-link>
      <router-link :to="authStore.isLoggedIn ? `/user/${authStore.user?.id}` : '/login'" class="mobile-nav-item">
        <el-icon><User /></el-icon>
        <span>我的</span>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  HomeFilled, ChatDotRound, ChatLineRound,
  ArrowDown, Setting, SwitchButton,
  Document, Bell, Goods, Tools, User, Plus, Collection
} from '@element-plus/icons-vue'
import ThemeToggle from '@/components/ThemeToggle.vue'
import BackToTop from '@/components/BackToTop.vue'
import { getUnreadCount } from '@/api/notification'

const router = useRouter()
const authStore = useAuthStore()
const searchKeyword = ref('')
const unreadNotifications = ref(0)
const windowWidth = ref(window.innerWidth)

const isMobile = computed(() => windowWidth.value < 768)

const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    router.push({ path: '/search', query: { q: searchKeyword.value.trim() } })
  }
}

const loadUnreadCounts = async () => {
  if (!authStore.isLoggedIn) return
  try {
    const notifRes: any = await getUnreadCount()
    unreadNotifications.value = notifRes.unread_count || 0
  } catch {}
}

const handleLogout = () => {
  authStore.logout()
}

const handleResize = () => {
  windowWidth.value = window.innerWidth
}

let notifPollTimer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  loadUnreadCounts()
  window.addEventListener('resize', handleResize)
  if (authStore.isLoggedIn) {
    notifPollTimer = setInterval(loadUnreadCounts, 30000)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (notifPollTimer) { clearInterval(notifPollTimer); notifPollTimer = null }
})
</script>

<style scoped lang="scss">
.default-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--cyber-bg);
}

.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 20px;
  background-color: var(--cyber-card);
  border-bottom: 1px solid var(--cyber-border);
  backdrop-filter: blur(12px);
}

.navbar-brand {
  .brand-link {
    display: flex;
    align-items: center;
    gap: 6px;
    text-decoration: none;
    color: var(--cyber-text);

    .terminal-prefix {
      font-family: 'JetBrains Mono', 'Fira Code', monospace;
      color: var(--cyber-neon);
      font-weight: 700;
      font-size: 16px;
    }

    .brand-text {
      font-family: 'JetBrains Mono', 'Fira Code', monospace;
      font-size: 16px;
      font-weight: 700;
      color: var(--cyber-text);
    }

    .cursor-blink {
      color: var(--cyber-neon);
      animation: blink 1s step-end infinite;
    }
  }
}

@keyframes blink {
  50% { opacity: 0; }
}

.navbar-nav {
  display: flex;
  gap: 2px;

  .nav-link {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 6px 12px;
    border-radius: 6px;
    text-decoration: none;
    color: var(--cyber-muted);
    font-size: 14px;
    transition: all 0.2s;
    white-space: nowrap;
    position: relative;

    &:hover {
      color: var(--cyber-text);
      background-color: var(--cyber-neon-light);
    }

    &.active {
      color: var(--cyber-neon);
      background-color: var(--cyber-neon-light);

      &::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 50%;
        transform: translateX(-50%);
        width: 60%;
        height: 2px;
        background: var(--cyber-neon);
        border-radius: 1px;
        box-shadow: 0 0 8px var(--cyber-neon);
      }
    }
  }
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;

  .search-box {
    display: flex;
    align-items: center;
    gap: 4px;
    width: 200px;

    .search-prefix {
      font-family: 'JetBrains Mono', monospace;
      color: var(--cyber-neon);
      font-size: 12px;
      font-weight: 700;
      flex-shrink: 0;
    }

    :deep(.el-input__wrapper) {
      border-radius: 6px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
    }
  }

  .nav-icon {
    display: flex;
    align-items: center;
    color: var(--cyber-muted);
    cursor: pointer;
    text-decoration: none;
    transition: color 0.2s;
    &:hover { color: var(--cyber-neon); }
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    color: var(--cyber-text);

    .username {
      font-size: 14px;
      font-family: 'JetBrains Mono', monospace;
    }

    .user-avatar {
      border: 2px solid var(--cyber-neon);
      transition: box-shadow 0.2s;
      &:hover {
        box-shadow: 0 0 10px var(--cyber-neon);
      }
    }
  }
}

.main-content {
  flex: 1;
  padding: 24px;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

.footer {
  padding: 24px;
  text-align: center;
  border-top: 1px solid var(--cyber-border);
  background-color: var(--cyber-card);

  .footer-content {
    max-width: 1200px;
    margin: 0 auto;
  }

  .footer-brand {
    font-family: 'JetBrains Mono', monospace;
    color: var(--cyber-neon);
    font-size: 14px;
  }

  .footer-sub {
    margin-top: 4px;
    font-size: 12px;
    color: var(--cyber-muted);
    opacity: 0.6;
  }
}

.mobile-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  display: flex;
  justify-content: space-around;
  align-items: center;
  height: 56px;
  background-color: var(--cyber-card);
  border-top: 1px solid var(--cyber-border);
  backdrop-filter: blur(12px);

  .mobile-nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    text-decoration: none;
    color: var(--cyber-muted);
    font-size: 10px;
    padding: 4px 12px;
    transition: color 0.2s;

    &.active {
      color: var(--cyber-neon);
    }

    &.create-btn {
      color: var(--cyber-neon);
      background-color: var(--cyber-neon-light);
      border-radius: 12px;
      padding: 6px 16px;
    }
  }
}

@media (max-width: 768px) {
  .navbar {
    padding: 0 12px;
  }
  .navbar-nav .nav-link span {
    display: none;
  }
  .navbar-actions .search-box {
    width: 120px;
  }
  .main-content {
    padding: 12px;
    padding-bottom: 72px;
  }
}
</style>

<style>
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
