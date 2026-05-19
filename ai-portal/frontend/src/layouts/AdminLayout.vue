<template>
  <div class="admin-layout">
    <aside class="admin-sidebar">
      <div class="sidebar-header">
        <span class="terminal-prefix">&gt;_</span>
        <span class="sidebar-title">admin</span>
      </div>

      <el-menu
        :default-active="$route.path"
        router
        class="admin-menu"
        background-color="transparent"
        :text-color="themeTextColor"
        :active-text-color="activeColor"
      >
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataLine /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>

        <div class="menu-section-label">// 内容管理</div>

        <el-sub-menu index="/admin/content" :popper-append-to-body="false">
          <template #title>
            <el-icon><FolderOpened /></el-icon>
            <span>{{ authStore.isAdmin ? '内容管理' : '我的内容' }}</span>
          </template>
          <el-menu-item index="/admin/blogs">
            <el-icon><Document /></el-icon>
            <span>博客管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/projects">
            <el-icon><Folder /></el-icon>
            <span>项目管理</span>
          </el-menu-item>
          <el-menu-item v-if="authStore.isAdmin" index="/admin/news">
            <el-icon><Bell /></el-icon>
            <span>新闻管理</span>
          </el-menu-item>
          <el-menu-item v-if="authStore.isAdmin" index="/admin/products">
            <el-icon><Goods /></el-icon>
            <span>产品管理</span>
          </el-menu-item>
          <el-menu-item v-if="authStore.isAdmin" index="/admin/solutions">
            <el-icon><Tools /></el-icon>
            <span>解决方案管理</span>
          </el-menu-item>
          <el-menu-item v-if="authStore.isAdmin" index="/admin/categories">
            <el-icon><Menu /></el-icon>
            <span>分类管理</span>
          </el-menu-item>
          <el-menu-item v-if="authStore.isAdmin" index="/admin/tags">
            <el-icon><PriceTag /></el-icon>
            <span>标签管理</span>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/admin/notifications">
          <el-icon><Bell /></el-icon>
          <span>我的通知</span>
        </el-menu-item>

        <el-menu-item index="/admin/profile">
          <el-icon><User /></el-icon>
          <span>个人设置</span>
        </el-menu-item>

        <template v-if="authStore.isAdmin">
          <div class="menu-section-label">// 互动</div>

          <el-menu-item index="/admin/comments">
            <el-icon><ChatLineRound /></el-icon>
            <span>评论管理</span>
          </el-menu-item>

          <div class="menu-section-label">// 系统</div>

          <el-menu-item index="/admin/knowledge">
            <el-icon><Reading /></el-icon>
            <span>知识库</span>
          </el-menu-item>
          <el-menu-item index="/admin/api-keys">
            <el-icon><Key /></el-icon>
            <span>API密钥</span>
          </el-menu-item>
          <el-menu-item index="/admin/api-logs">
            <el-icon><List /></el-icon>
            <span>调用日志</span>
          </el-menu-item>
          <el-menu-item index="/admin/monitor">
            <el-icon><Monitor /></el-icon>
            <span>系统监控</span>
          </el-menu-item>
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/configs">
            <el-icon><Tickets /></el-icon>
            <span>系统配置</span>
          </el-menu-item>
        </template>

        <div class="menu-section-label">// 个人</div>
        <el-menu-item index="/admin/moments">
          <el-icon><ChatLineRound /></el-icon>
          <span>我的动态</span>
        </el-menu-item>

        <div class="menu-divider" />
        <el-menu-item index="/">
          <el-icon><Back /></el-icon>
          <span>返回前台</span>
        </el-menu-item>
      </el-menu>
    </aside>

    <div class="admin-main">
      <header class="admin-header">
        <div class="breadcrumb-path">
          <span class="path-prefix">~</span>
          <span class="path-segment" v-for="(segment, i) in pathSegments" :key="i">
            <span class="path-slash">/</span>
            <span class="path-text">{{ segment }}</span>
          </span>
        </div>
        <div class="header-actions">
          <ThemeToggle />
          <el-avatar :size="28" :icon="UserFilled" class="admin-avatar" />
          <span class="username">{{ authStore.user?.username }}</span>
          <el-button size="small" text @click="handleLogout" class="logout-btn">
            [exit]
          </el-button>
        </div>
      </header>

      <main class="admin-content">
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'
import {
  Setting, DataLine, Folder, Document, Key, List,
  Reading, Monitor, Back, UserFilled, ChatLineRound,
  Bell, Goods, Tools, FolderOpened, User, Tickets,
  Menu, PriceTag
} from '@element-plus/icons-vue'
import ThemeToggle from '@/components/ThemeToggle.vue'

const route = useRoute()
const themeStore = useThemeStore()
const authStore = useAuthStore()

const themeTextColor = computed(() => themeStore.isDark ? '#8b949e' : '#4a5568')
const activeColor = computed(() => themeStore.isDark ? '#00ff88' : '#00d4aa')

const pathSegments = computed(() => {
  const pathMap: Record<string, string[]> = {
    '/admin/dashboard': ['admin', 'dashboard'],
    '/admin/blogs': ['admin', 'content', 'blogs'],
    '/admin/news': ['admin', 'content', 'news'],
    '/admin/products': ['admin', 'content', 'products'],
    '/admin/solutions': ['admin', 'content', 'solutions'],
    '/admin/projects': ['admin', 'content', 'projects'],
    '/admin/categories': ['admin', 'content', 'categories'],
    '/admin/tags': ['admin', 'content', 'tags'],
    '/admin/comments': ['admin', 'interaction', 'comments'],
    '/admin/users': ['admin', 'system', 'users'],
    '/admin/api-keys': ['admin', 'system', 'api-keys'],
    '/admin/api-logs': ['admin', 'system', 'api-logs'],
    '/admin/monitor': ['admin', 'system', 'monitor'],
    '/admin/knowledge': ['admin', 'system', 'knowledge'],
    '/admin/configs': ['admin', 'system', 'configs'],
    '/admin/notifications': ['admin', 'notifications'],
    '/admin/profile': ['admin', 'profile'],
    '/admin/moments': ['admin', 'moments'],
  }
  return pathMap[route.path] || ['admin', route.path.split('/').pop() || '']
})

const handleLogout = () => {
  authStore.logout()
}
</script>

<style scoped lang="scss">
.admin-layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--cyber-bg);
}

.admin-sidebar {
  width: 220px;
  background-color: var(--cyber-card);
  border-right: 1px solid var(--cyber-border);
  display: flex;
  flex-direction: column;

  .sidebar-header {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 16px 20px;
    border-bottom: 1px solid var(--cyber-border);

    .terminal-prefix {
      font-family: 'JetBrains Mono', monospace;
      color: var(--cyber-neon);
      font-weight: 700;
      font-size: 14px;
    }

    .sidebar-title {
      font-family: 'JetBrains Mono', monospace;
      font-size: 16px;
      font-weight: 600;
      color: var(--cyber-text);
    }
  }

  .admin-menu {
    border-right: none;
    flex: 1;

    .menu-section-label {
      padding: 12px 20px 4px;
      font-size: 11px;
      font-family: 'JetBrains Mono', monospace;
      color: var(--cyber-muted);
      opacity: 0.5;
      letter-spacing: 0.5px;
    }

    .menu-divider {
      height: 1px;
      background: var(--cyber-border);
      margin: 8px 16px;
    }

    :deep(.el-menu-item) {
      height: 44px;
      line-height: 44px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;

      &:hover {
        background-color: var(--cyber-neon-light) !important;
      }

      &.is-active {
        background-color: var(--cyber-neon-light) !important;
        color: var(--cyber-neon) !important;
        border-right: 2px solid var(--cyber-neon);
      }
    }
  }
}

.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 48px;
  padding: 0 20px;
  background-color: var(--cyber-card);
  border-bottom: 1px solid var(--cyber-border);

  .breadcrumb-path {
    display: flex;
    align-items: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;

    .path-prefix {
      color: var(--cyber-neon);
      font-weight: 700;
    }

    .path-slash {
      color: var(--cyber-muted);
      margin: 0 2px;
    }

    .path-text {
      color: var(--cyber-text);
    }
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 10px;

    .admin-avatar {
      border: 1px solid var(--cyber-neon);
    }

    .username {
      color: var(--cyber-muted);
      font-size: 13px;
      font-family: 'JetBrains Mono', monospace;
    }

    .logout-btn {
      font-family: 'JetBrains Mono', monospace;
      color: var(--cyber-danger) !important;
      font-size: 12px;
    }
  }
}

.admin-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .admin-sidebar {
    width: 56px;

    .sidebar-header .sidebar-title {
      display: none;
    }

    .admin-menu :deep(.el-menu-item span),
    .admin-menu :deep(.el-sub-menu span),
    .menu-section-label {
      display: none;
    }
  }
}
</style>
