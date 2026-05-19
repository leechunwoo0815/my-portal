# AI Portal 架构文档

> 最后更新：2026-05-14

---

## 一、后端架构

### 1.1 目录结构

```
backend/app/
├── main.py                    # 应用入口
│   ├── 模块自动发现 (pkgutil)  # 自动注册 /api/v1/<module> 路由
│   ├── 模型自动发现            # 自动导入 modules/*/models.py
│   ├── CORS 中间件             # ALLOWED_ORIGINS 配置
│   ├── 请求日志中间件          # method, path, status, latency, IP
│   ├── 请求ID中间件            # X-Request-ID header
│   ├── 请求大小限制            # 50MB
│   └── 全局异常处理            # AppException + 未知异常
│
├── core/
│   ├── config.py              # pydantic-settings 全局配置
│   ├── database.py            # SQLAlchemy engine + SessionLocal (WAL mode)
│   ├── security.py            # JWT 生成/验证 + bcrypt 哈希
│   ├── deps.py                # 依赖注入 (get_db, get_current_user, require_admin, require_level)
│   ├── crud.py                # CRUDBase 共享基类 (get/list/create/update/delete)
│   ├── content_base.py        # ContentBase/ContentCreate/ContentUpdate 内容模型基类
│   ├── schemas.py             # 共享 Pydantic Schema (PaginatedResponse[T])
│   ├── events.py              # EventBus 事件定义 (19 个事件)
│   ├── event_handlers.py      # 事件处理器注册
│   ├── exceptions.py          # 自定义异常类 AppException
│   └── logging_config.py      # 结构化日志 (RotatingFileHandler, 请求ID追踪)
│
├── models/                    # 27 个 SQLAlchemy 模型
│   ├── __init__.py            # 统一导出所有模型
│   ├── user.py                # User (认证、等级、积分)
│   ├── user_follow.py         # UserFollow (关注关系)
│   ├── user_like.py           # UserLike (点赞)
│   ├── user_favorite.py       # UserFavorite (收藏)
│   ├── blog.py                # Blog (博客文章)
│   ├── news.py                # News (新闻)
│   ├── products.py            # Product (产品)
│   ├── solutions.py           # Solution (解决方案)
│   ├── project.py             # Project (作品集项目)
│   ├── category.py            # Category (分类)
│   ├── tag.py                 # Tag (标签)
│   ├── content_tag.py         # ContentTag (内容-标签关联)
│   ├── comment.py             # Comment (嵌套评论)
│   ├── moment.py              # Moment (动态)
│   ├── conversation.py        # Conversation (AI 对话)
│   ├── message.py             # Message (对话消息, thinking/duration)
│   ├── direct_message.py      # DirectMessage (私信)
│   ├── notification.py        # Notification (通知)
│   ├── knowledge.py           # KnowledgeBase + KnowledgeDocument (知识库)
│   ├── api_key.py             # ApiKey (LLM API 密钥)
│   ├── api_call_log.py        # ApiCallLog (API 调用日志)
│   ├── system_config.py       # SystemConfig (系统配置)
│   ├── point_log.py           # PointLog (积分记录)
│   ├── checkin.py             # Checkin (签到)
│   ├── achievement.py         # Achievement + UserAchievement (成就)
│   ├── series.py              # Series + SeriesArticle (专栏)
│   └── history.py             # ReadingHistory (阅读历史)
│
├── modules/                   # 28 个业务模块 (自动注册路由)
│   ├── auth/                  # 登录、注册、改密
│   ├── user/                  # 用户资料、头像、个人主页
│   ├── blog/                  # 博客 CRUD + 管理员接口
│   ├── news/                  # 新闻 CRUD + 管理员接口
│   ├── products/              # 产品 CRUD + 管理员接口
│   ├── solutions/             # 方案 CRUD + 管理员接口
│   ├── portfolio/             # 作品集 CRUD + 管理员接口
│   ├── category/              # 分类 CRUD
│   ├── tag/                   # 标签 CRUD
│   ├── comments/              # 嵌套评论 + 点赞
│   ├── interaction/           # 点赞/收藏 toggle
│   ├── social/                # 关注/粉丝/好友/移除粉丝
│   ├── moment/                # 动态发布/删除/列表
│   ├── message/               # 私信
│   ├── notification/          # 通知列表/已读/未读计数
│   ├── chat/                  # AI 对话 (SSE 流式/停止/会话管理)
│   ├── knowledge/             # 知识库 RAG
│   ├── search/                # 全文搜索
│   ├── recommend/             # 推荐算法
│   ├── feed/                  # 动态流
│   ├── point/                 # 积分系统
│   ├── checkin/               # 签到系统
│   ├── achievement/           # 成就系统
│   ├── series/                # 系列/专栏
│   ├── history/               # 阅读历史
│   ├── admin/                 # 管理后台 API (仪表盘/配置/密钥/日志/监控)
│   ├── upload/                # 图片上传 (封面+内容)
│   └── tools/                 # AI 工具集
│
└── services/
    ├── llm_service.py         # LLM 多模型调用 (SSE 流式, abort_flag)
    ├── llm_client.py          # LLM HTTP 客户端
    ├── rag_service.py         # RAG 检索增强 (ChromaDB)
    ├── point_service.py       # 积分规则引擎
    ├── achievement_service.py # 成就检测 + 种子数据
    └── monitor.py             # 系统监控
```

### 1.2 模块自动发现机制

```python
# main.py - 路由自动注册
for _, module_name, _ in pkgutil.iter_modules(modules_pkg.__path__):
    router_module = importlib.import_module(f"app.modules.{module_name}.router")
    app.include_router(router_module.router, prefix=f"/api/v1/{module_name}")

# main.py - 模型自动导入（确保表被创建）
for _, module_name, _ in pkgutil.iter_modules(modules_pkg.__path__):
    importlib.import_module(f"app.modules.{module_name}.models")
```

新增模块只需在 `modules/` 下创建目录，无需修改 `main.py`。

### 1.3 关键抽象

| 抽象 | 位置 | 用途 |
|------|------|------|
| `CRUDRouterFactory` | `modules/*/router.py` | 自动生成标准 CRUD 路由 |
| `CRUDBase` | `core/crud.py` | 共享 CRUD 基类 (get/list/create/update/delete) |
| `ContentBase` | `core/content_base.py` | 统一内容模型基类 |
| `PaginatedResponse[T]` | `core/schemas.py` | 统一分页响应格式 `{items, total, page, page_size, total_pages}` |
| `require_level(n)` | `core/deps.py` | 按等级控制权限 |
| `AppException` | `core/exceptions.py` | 统一业务异常 |
| `EventBus` | `core/events.py` | 事件驱动解耦 (19 个事件) |

### 1.4 API 路由总览

所有模块路由前缀：`/api/v1/<module_name>`

| 模块 | 关键端点 | 认证 |
|------|----------|------|
| auth | `POST /login`, `POST /register`, `POST /change-password` | 无/有 |
| user | `GET /{id}/profile`, `PUT /profile`, `POST /avatar` | 可选/有 |
| blog | `GET /posts`, `GET /posts/{id}`, `POST /posts`, `PUT /posts/{id}` | 可选/有 |
| news | `GET /`, `GET /{id}`, `POST /`, `PUT /{id}` | 可选/有 |
| products | `GET /`, `GET /{id}`, `POST /`, `PUT /{id}` | 可选/有 |
| solutions | `GET /`, `GET /{id}`, `POST /`, `PUT /{id}` | 可选/有 |
| portfolio | `GET /projects`, `GET /projects/{id}` | 可选 |
| social | `POST /follow/{id}`, `GET /followers/{id}`, `GET /following/{id}`, `GET /friends/{id}`, `POST /remove-follower/{id}`, `GET /follow-status/{id}` | 有 |
| comments | `GET /{type}/{id}`, `POST /{type}/{id}` | 可选/有 |
| interaction | `POST /like/{type}/{id}`, `POST /favorite/{type}/{id}` | 有 |
| moment | `GET /`, `POST /`, `DELETE /{id}` | 可选/有 |
| message | `GET /conversations`, `POST /send` | 有 |
| notification | `GET /`, `PUT /{id}/read`, `PUT /read-all`, `GET /unread-count` | 有 |
| chat | `POST /completions`, `POST /completions/cancel/{id}`, `GET /conversations` | 有 |
| knowledge | `GET /bases`, `POST /bases/{id}/documents` | 有 |
| search | `GET /` | 可选 |
| recommend | `GET /` | 可选 |
| feed | `GET /` | 可选 |
| point | `GET /history` | 有 |
| checkin | `POST /`, `GET /status` | 有 |
| achievement | `GET /`, `GET /progress` | 有 |
| series | `GET /`, `GET /{id}`, `POST /`, `PUT /{id}` | 可选/有 |
| history | `GET /`, `POST /`, `DELETE /` | 有 |
| admin | `GET /dashboard`, `POST /api-keys`, `GET /api-keys/models` | admin |
| upload | `POST /image`, `POST /cover` | admin |
| category | `GET /`, `POST /`, `PUT /{id}`, `DELETE /{id}` | 可选/有 |
| tag | `GET /`, `POST /`, `PUT /{id}`, `DELETE /{id}` | 可选/有 |

---

## 二、前端架构

### 2.1 目录结构

```
frontend/src/
├── api/                       # 26 个 API 模块
│   ├── client.ts              # Axios 实例 + 拦截器 (auth token, 错误处理, 401登出)
│   ├── auth.ts                # 登录/注册/改密
│   ├── user.ts                # 用户资料/头像 (UserProfile 接口含 friends_count)
│   ├── blog.ts                # 博客 CRUD + 管理员接口
│   ├── news.ts                # 新闻 CRUD + 管理员接口
│   ├── products.ts            # 产品 CRUD + 管理员接口
│   ├── solutions.ts           # 方案 CRUD + 管理员接口
│   ├── portfolio.ts           # 作品集 CRUD + 管理员接口
│   ├── social.ts              # 关注/粉丝/好友/移除粉丝/关注状态
│   ├── comment.ts             # 评论
│   ├── interaction.ts         # 点赞/收藏
│   ├── moment.ts              # 动态
│   ├── message.ts             # 私信
│   ├── notification.ts        # 通知
│   ├── chat.ts                # AI 对话 (SSE 流式)
│   ├── knowledge.ts           # 知识库
│   ├── search.ts              # 搜索
│   ├── recommend.ts           # 推荐
│   ├── feed.ts                # 动态流
│   ├── achievement.ts         # 成就
│   ├── history.ts             # 阅读历史
│   ├── series.ts              # 系列/专栏
│   ├── category.ts            # 分类
│   ├── tag.ts                 # 标签
│   ├── admin.ts               # 管理后台 API
│   └── upload.ts              # 图片上传
│
├── stores/                    # 7 个 Pinia Store
│   ├── auth.ts                # 认证状态 (user, token, isLoggedIn, isAdmin)
│   ├── chat.ts                # AI 对话状态 (会话/消息/模型/SSE流式)
│   ├── content.ts             # 内容缓存
│   ├── interaction.ts         # 互动状态 (点赞/收藏)
│   ├── models.ts              # LLM 模型列表
│   ├── notification.ts        # 通知状态 (未读计数轮询)
│   └── theme.ts               # 主题切换 (亮色/暗色, CSS 变量注入)
│
├── composables/               # 9 个组合式函数
│   ├── useCrudAdmin.ts        # Admin CRUD 通用逻辑 (fetchList/create/update/delete)
│   ├── useInteraction.ts      # 互动逻辑 (点赞/收藏 toggle)
│   ├── useMarkdown.ts         # Markdown 渲染 (html: false)
│   ├── useMdEditor.ts         # Milkdown 编辑器逻辑
│   ├── useMdEditorUpload.ts   # 编辑器图片上传
│   ├── usePagination.ts       # 分页逻辑
│   ├── useReadingProgress.ts  # 阅读进度条
│   ├── useSearch.ts           # 搜索逻辑
│   └── useToc.ts              # 目录树生成
│
├── components/                # 13 个通用组件
│   ├── BackToTop.vue          # 回到顶部按钮
│   ├── CategoryNav.vue        # 分类导航
│   ├── CommentNode.vue        # 递归评论节点
│   ├── CommentSection.vue     # 评论系统容器
│   ├── ContentCard.vue        # 内容卡片
│   ├── ContributionGraph.vue  # 贡献热力图
│   ├── CoverUpload.vue        # 封面图上传 (URL + 本地上传)
│   ├── FollowDialog.vue       # 关注/粉丝/好友管理弹窗 (3 Tab)
│   ├── HackerCanvas.vue       # 首页背景动画 (Matrix雨/旋转点阵)
│   ├── NotificationPanel.vue  # 通知下拉面板
│   ├── TagList.vue            # 标签列表
│   ├── ThemeToggle.vue        # 主题切换按钮
│   ├── UserCard.vue           # 用户卡片
│   ├── skeleton/              # 骨架屏组件
│   │   ├── ContentCardSkeleton.vue
│   │   ├── DetailSkeleton.vue
│   │   ├── MomentSkeleton.vue
│   │   ├── SearchResultSkeleton.vue
│   │   └── index.ts
│   ├── interaction/           # 互动组件
│   │   ├── FavoriteButton.vue # 收藏按钮 (动效)
│   │   ├── FollowButton.vue   # 关注按钮 (动效)
│   │   ├── LikeButton.vue     # 点赞按钮 (动效)
│   │   └── ShareButton.vue    # 社交分享面板
│   └── editor/
│       └── MilkdownEditor.vue # Markdown WYSIWYG 编辑器 (草稿自动保存)
│
├── views/                     # 17 个视图目录
│   ├── admin/                 # 管理后台 (18 个页面)
│   │   ├── DashboardView.vue  # 仪表盘 (ECharts)
│   │   ├── BlogManage.vue     # 博客管理
│   │   ├── ProjectManage.vue  # 项目管理
│   │   ├── NewsManage.vue     # 新闻管理
│   │   ├── ProductManage.vue  # 产品管理
│   │   ├── SolutionManage.vue # 方案管理
│   │   ├── CommentManage.vue  # 评论管理
│   │   ├── CategoryManage.vue # 分类管理
│   │   ├── TagManage.vue      # 标签管理
│   │   ├── UserManage.vue     # 用户管理
│   │   ├── ApiKeyManage.vue   # API 密钥管理
│   │   ├── ApiLogView.vue     # API 日志
│   │   ├── KnowledgeManage.vue # 知识库管理
│   │   ├── MonitorView.vue    # 系统监控
│   │   ├── ConfigManage.vue   # 系统配置
│   │   ├── MyMoments.vue      # 我的动态
│   │   ├── MyNotifications.vue # 我的通知
│   │   └── ProfileSettings.vue # 个人设置
│   ├── auth/                  # 登录/注册
│   ├── blog/                  # 博客列表/详情
│   ├── chat/                  # AI 对话
│   ├── feed/                  # 动态流
│   ├── history/               # 阅读历史
│   ├── home/                  # 首页
│   ├── message/               # 私信
│   ├── moment/                # 动态广场
│   ├── news/                  # 新闻列表/详情
│   ├── notification/          # 通知
│   ├── portfolio/             # 作品集
│   ├── products/              # 产品列表/详情
│   ├── search/                # 搜索结果
│   ├── series/                # 系列/专栏
│   ├── solutions/             # 方案列表/详情
│   └── user/                  # 用户主页 (UserProfileView)
│
├── layouts/
│   ├── DefaultLayout.vue      # 前台布局 (导航栏+通知轮询+回到顶部+专栏入口)
│   └── AdminLayout.vue        # 管理后台布局 (侧边栏二级菜单)
│
├── router/                    # 路由配置 + 认证守卫
├── design/                    # 设计系统 (Token + 主题)
└── utils/
    └── format.ts              # 格式化工具函数 (formatDate, formatDateTime, extractOptions)
```

### 2.2 Axios 拦截器行为

**重要**：Axios 响应拦截器返回 `response.data`，所有 API 调用拿到的已经是解包后的数据，不需要再 `.data`。

```typescript
// client.ts
api.interceptors.response.use(
  (response) => response.data,  // ← 直接返回解包数据
  (error) => { /* 统一错误处理 */ }
)
```

### 2.3 Vite 代理配置

```typescript
// vite.config.ts
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    configure: (proxy) => {
      // 重写重定向 Location 头，避免 CORS 问题
      proxy.on('proxyRes', (proxyRes) => {
        if ([301,302,307,308].includes(proxyRes.statusCode)) {
          const location = proxyRes.headers.location
          if (location) {
            proxyRes.headers.location = location.replace(/^http:\/\/localhost:8000/, '')
          }
        }
      })
    },
  },
  '/uploads': { target: 'http://localhost:8000', changeOrigin: true },
}
```

**注意**：FastAPI 的 `redirect_slashes` 会在 `/path` 和 `/path/` 之间产生 307 重定向。代理必须重写 Location 头，否则浏览器会直接请求 `localhost:8000` 导致 CORS 错误。

---

## 三、FollowDialog 组件说明

**文件**：`frontend/src/components/FollowDialog.vue`

### 权限逻辑

| 功能 | 自己的主页 | 他人的主页 |
|------|-----------|-----------|
| 关注 Tab | 显示 | 显示 |
| 粉丝 Tab | 显示 | 显示 |
| 好友 Tab | 显示 | **隐藏** |
| 关系标签（好友/已关注/关注你） | 显示 | **隐藏** |
| 移除粉丝按钮 | 显示（粉丝列表） | **隐藏** |
| 关注/取消关注按钮 | 显示 | 显示 |
| 私信按钮 | 显示 | 显示 |

### 关系标签说明

关系标签是相对于**主页所有者**的，不是相对于当前查看者：
- "好友"：主页所有者和该用户互相关注
- "已关注"：主页所有者关注了该用户（主页所有者的关注列表中）
- "关注你"：该用户关注了主页所有者（主页所有者的粉丝列表中）

### API 依赖

- `socialApi.getFollowing(userId, page, pageSize)` — 获取关注列表
- `socialApi.getFollowers(userId, page, pageSize)` — 获取粉丝列表
- `socialApi.getFriends(userId, page, pageSize)` — 获取好友列表（互关）
- `socialApi.toggleFollow(userId)` — 关注/取消关注
- `socialApi.removeFollower(userId)` — 移除粉丝

---

## 四、聊天系统架构

### 4.1 SSE 流式对话

```
前端 sendMessageStream()
  ↓ fetch() + ReadableStream
  ↓ Accept: text/event-stream
后端 event_generator()
  ↓ yield SSE event (data: {...})
  ↓ llm_service.stream_chat(abort_flag=...)
  ↓ 每 chunk 检查 abort_flag()
```

### 4.2 停止生成（三层机制）

| 层级 | 文件 | 机制 |
|------|------|------|
| 前端 | `stores/chat.ts` | `stopGeneration()` → POST `/completions/cancel/{id}` + `abortController.abort()` |
| 后端 | `chat/router.py` | `event_generator()` 每次迭代检查 `cancel_event.is_set()` |
| LLM 层 | `llm_service.py` | 每 chunk 调用 `abort_flag()`，为 true 时直接 return |

### 4.3 消息保存

`_save_assistant_message()` 统一处理三种退出路径：
1. 正常流结束（for 循环自然退出）
2. `cancel_event.set()` → break
3. `asyncio.CancelledError`（客户端断连）→ except 穿透后落到此处

---

## 五、已知限制

| 项目 | 说明 |
|------|------|
| Token 刷新 | 当前无自动刷新机制，token 过期后用户需重新登录 |
| 前端类型安全 | 部分 API 函数返回 `Promise<any>` |
| 数据库 | SQLite 单文件，高并发场景需迁移到 PostgreSQL |
| 通知端点 | 前端 `notification.ts` 路径 `/notification/unread-count` 需确认与后端 `/api/v1/notification/unread-count` 一致 |

---

## 六、新增模块开发指南

### 后端

1. 创建 `backend/app/modules/<name>/` 目录，包含 `__init__.py`, `router.py`, `schemas.py`
2. 如需新模型，在 `backend/app/models/<name>.py` 中定义，并在 `__init__.py` 中导出
3. 路由自动注册，前缀为 `/api/v1/<name>`
4. 使用 `CRUDBase` 或 `CRUDRouterFactory` 减少重复代码
5. 使用 `PaginatedResponse[T]` 统一分页格式
6. 在 `backend/tests/test_<name>.py` 中编写测试

### 前端

1. 在 `frontend/src/api/<name>.ts` 中定义 API 调用
2. 在 `frontend/src/views/<name>/` 中创建页面
3. 在 `frontend/src/router/index.ts` 中添加路由
4. 如需管理页面，使用 `useCrudAdmin` composable
5. 所有颜色使用 `--app-*` CSS 变量，确保主题兼容
