/**
 * Vue Router 路由配置
 * 所有页面使用懒加载（() => import()），减少首屏体积
 * 路由守卫：检查登录状态和管理员权限
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

/**
 * 路由配置列表
 * 所有页面组件使用动态导入实现懒加载
 */
const routes = [
  // ========== 前台页面 ==========
  {
    path: '/',
    component: () => import(/* webpackChunkName: "layout" */ '@/layouts/DefaultLayout.vue'),
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import(/* webpackChunkName: "home" */ '@/views/home/HomeView.vue'),
        meta: { title: '个人主页' },
      },
      {
        path: 'portfolio',
        name: 'Portfolio',
        component: () => import(/* webpackChunkName: "portfolio" */ '@/views/portfolio/PortfolioView.vue'),
        meta: { title: 'AI作品集' },
      },
      {
        path: 'portfolio/:id',
        name: 'ProjectDetail',
        component: () => import(/* webpackChunkName: "portfolio" */ '@/views/portfolio/ProjectDetailView.vue'),
        meta: { title: '项目详情' },
      },
      {
        path: 'chat',
        name: 'Chat',
        component: () => import(/* webpackChunkName: "chat" */ '@/views/chat/ChatView.vue'),
        meta: { title: '大模型聊天', requiresAuth: true },
      },
      {
        path: 'user/:id',
        name: 'UserProfile',
        component: () => import(/* webpackChunkName: "user" */ '@/views/user/UserProfileView.vue'),
        meta: { title: '用户主页' },
      },
      {
        path: 'user/:id/content',
        name: 'UserContent',
        component: () => import(/* webpackChunkName: "user" */ '@/views/user/UserContentView.vue'),
        meta: { title: '用户内容' },
      },
      {
        path: 'feed',
        name: 'Feed',
        component: () => import(/* webpackChunkName: "feed" */ '@/views/feed/FeedView.vue'),
        meta: { title: '动态流' },
      },
      {
        path: 'moment',
        name: 'Moment',
        component: () => import(/* webpackChunkName: "moment" */ '@/views/moment/MomentView.vue'),
        meta: { title: '动态广场' },
      },
      {
        path: 'search',
        name: 'Search',
        component: () => import(/* webpackChunkName: "search" */ '@/views/search/SearchView.vue'),
        meta: { title: '搜索' },
      },
      {
        path: 'notifications',
        name: 'Notifications',
        component: () => import(/* webpackChunkName: "notification" */ '@/views/notification/NotificationView.vue'),
        meta: { title: '通知中心', requiresAuth: true },
      },
      {
        path: 'messages',
        name: 'Messages',
        component: () => import(/* webpackChunkName: "message" */ '@/views/message/MessageView.vue'),
        meta: { title: '私信', requiresAuth: true },
      },
      {
        path: 'user/settings',
        redirect: '/admin/profile',
      },
      {
        path: 'blog',
        name: 'BlogList',
        component: () => import(/* webpackChunkName: "blog" */ '@/views/blog/BlogListView.vue'),
        meta: { title: 'AI技术博客' },
      },
      {
        path: 'blog/:id',
        name: 'BlogDetail',
        component: () => import(/* webpackChunkName: "blog" */ '@/views/blog/BlogDetailView.vue'),
        meta: { title: '博客文章' },
      },
      {
        path: 'news',
        name: 'NewsList',
        component: () => import(/* webpackChunkName: "news" */ '@/views/news/NewsListView.vue'),
        meta: { title: 'AI新闻资讯' },
      },
      {
        path: 'news/:id',
        name: 'NewsDetail',
        component: () => import(/* webpackChunkName: "news" */ '@/views/news/NewsDetailView.vue'),
        meta: { title: '新闻详情' },
      },
      {
        path: 'products',
        name: 'ProductsList',
        component: () => import(/* webpackChunkName: "products" */ '@/views/products/ProductsListView.vue'),
        meta: { title: 'AI产品中心' },
      },
      {
        path: 'products/:id',
        name: 'ProductsDetail',
        component: () => import(/* webpackChunkName: "products" */ '@/views/products/ProductsDetailView.vue'),
        meta: { title: '产品详情' },
      },
      {
        path: 'solutions',
        name: 'SolutionsList',
        component: () => import(/* webpackChunkName: "solutions" */ '@/views/solutions/SolutionsListView.vue'),
        meta: { title: 'AI解决方案' },
      },
      {
        path: 'solutions/:id',
        name: 'SolutionsDetail',
        component: () => import(/* webpackChunkName: "solutions" */ '@/views/solutions/SolutionsDetailView.vue'),
        meta: { title: '解决方案详情' },
      },
      {
        path: 'series',
        name: 'SeriesList',
        component: () => import('@/views/series/SeriesListView.vue'),
        meta: { title: '专栏' },
      },
      {
        path: 'series/:id',
        name: 'SeriesDetail',
        component: () => import('@/views/series/SeriesDetailView.vue'),
        meta: { title: '专栏详情' },
      },
      {
        path: 'history',
        name: 'ReadingHistory',
        component: () => import('@/views/history/ReadingHistoryView.vue'),
        meta: { title: '阅读历史', requiresAuth: true },
      },
    ],
  },

  // ========== 登录页 ==========
  {
    path: '/login',
    name: 'Login',
    component: () => import(/* webpackChunkName: "auth" */ '@/views/auth/LoginView.vue'),
    meta: { title: '登录', public: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import(/* webpackChunkName: "auth" */ '@/views/auth/RegisterView.vue'),
    meta: { title: '注册', public: true },
  },

  // ========== 后台管理 ==========
  {
    path: '/admin',
    component: () => import(/* webpackChunkName: "admin-layout" */ '@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard',
      },
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import(/* webpackChunkName: "admin" */ '@/views/admin/DashboardView.vue'),
        meta: { title: '仪表盘', requiresAdmin: true },
      },
      {
        path: 'projects',
        name: 'AdminProjects',
        component: () => import('@/views/admin/ProjectManage.vue'),
        meta: { title: '项目管理', requiresAdmin: true },
      },
      {
        path: 'blogs',
        name: 'AdminBlogs',
        component: () => import('@/views/admin/BlogManage.vue'),
        meta: { title: '博客管理', requiresAdmin: true },
      },
      {
        path: 'api-keys',
        name: 'AdminApiKeys',
        component: () => import(/* webpackChunkName: "admin" */ '@/views/admin/ApiKeyManage.vue'),
        meta: { title: 'API密钥管理', requiresAdmin: true },
      },
      {
        path: 'api-logs',
        name: 'AdminApiLogs',
        component: () => import(/* webpackChunkName: "admin" */ '@/views/admin/ApiLogView.vue'),
        meta: { title: '调用日志', requiresAdmin: true },
      },
      {
        path: 'knowledge',
        name: 'AdminKnowledge',
        component: () => import(/* webpackChunkName: "admin" */ '@/views/admin/KnowledgeManage.vue'),
        meta: { title: '知识库管理', requiresAdmin: true },
      },
      {
        path: 'news',
        name: 'AdminNews',
        component: () => import(/* webpackChunkName: "admin" */ '@/views/admin/NewsManage.vue'),
        meta: { title: '新闻管理', requiresAdmin: true },
      },
      {
        path: 'solutions',
        name: 'AdminSolutions',
        component: () => import(/* webpackChunkName: "admin" */ '@/views/admin/SolutionManage.vue'),
        meta: { title: '解决方案管理', requiresAdmin: true },
      },
      {
        path: 'products',
        name: 'AdminProducts',
        component: () => import(/* webpackChunkName: "admin" */ '@/views/admin/ProductManage.vue'),
        meta: { title: '产品管理', requiresAdmin: true },
      },
      {
        path: 'monitor',
        name: 'AdminMonitor',
        component: () => import(/* webpackChunkName: "admin" */ '@/views/admin/MonitorView.vue'),
        meta: { title: '系统监控', requiresAdmin: true },
      },
      {
        path: 'comments',
        name: 'AdminComments',
        component: () => import(/* webpackChunkName: "admin" */ '@/views/admin/CommentManage.vue'),
        meta: { title: '评论管理', requiresAdmin: true },
      },
      {
        path: 'categories',
        name: 'AdminCategories',
        component: () => import(/* webpackChunkName: "admin" */ '@/views/admin/CategoryManage.vue'),
        meta: { title: '分类管理', requiresAdmin: true },
      },
      {
        path: 'tags',
        name: 'AdminTags',
        component: () => import(/* webpackChunkName: "admin" */ '@/views/admin/TagManage.vue'),
        meta: { title: '标签管理', requiresAdmin: true },
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import(/* webpackChunkName: "admin" */ '@/views/admin/UserManage.vue'),
        meta: { title: '用户管理', requiresAdmin: true },
      },
      {
        path: 'notifications',
        name: 'AdminNotifications',
        component: () => import('@/views/admin/MyNotifications.vue'),
        meta: { title: '我的通知', requiresAuth: true },
      },
      {
        path: 'moments',
        name: 'AdminMoments',
        component: () => import('@/views/admin/MyMoments.vue'),
        meta: { title: '动态管理', requiresAdmin: true },
      },
      {
        path: 'profile',
        name: 'ProfileSettings',
        component: () => import('@/views/admin/ProfileSettings.vue'),
        meta: { title: '个人设置', requiresAuth: true },
      },
      {
        path: 'configs',
        name: 'AdminConfigs',
        component: () => import(/* webpackChunkName: "admin" */ '@/views/admin/ConfigManage.vue'),
        meta: { title: '系统配置', requiresAdmin: true },
      },
    ],
  },

  // ========== 404 ==========
  {
    path: '/:pathMatch(.*)*',
    component: () => import(/* webpackChunkName: "not-found" */ '@/views/NotFoundView.vue'),
  },
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
  // 切换路由时滚动到顶部
  scrollBehavior() {
    return { top: 0 }
  },
})

// ============================================================
// 路由守卫 - 权限检查
// ============================================================
router.beforeEach(async (to, from, next) => {
  const title = to.meta.title as string
  document.title = title ? `${title} - AI技术门户` : 'AI技术门户'

  const authStore = useAuthStore()

  if (authStore.token && !authStore.user) {
    const result = await authStore.fetchUser()
    if (result === false) {
      next('/login')
      return
    }
    if (result === null) {
      ElMessage.warning('网络异常，部分功能可能不可用')
    }
  }

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next('/login')
    return
  }

  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next('/')
    return
  }

  if (to.path === '/login' && authStore.isLoggedIn) {
    next('/')
    return
  }

  next()
})

export default router
