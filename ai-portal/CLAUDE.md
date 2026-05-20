# AI Portal — AI 技术门户平台

> 面向 AI 技术社区的综合门户平台，集成博客、新闻、产品展示、解决方案、社交动态、AI 对话、知识库等功能。赛博朋克/终端美学风格。

---

## 1. 项目概述

**项目名称**：AI Portal
**一句话定位**：面向 AI 技术社区的 CSDN 式综合门户平台，集成内容管理、社交互动、AI 对话和知识库。
**目标用户**：AI 技术从业者、研究者、开发者、产品经理
**核心价值**：提供 AI 技术内容发布、社区互动、智能问答一站式服务。

### 业务域划分

| 域 | 职责 | 核心实体 | 对应路由 |
|---|---|---|---|
| 认证域 | 注册/登录/改密 | User | `/api/v1/auth` |
| 用户域 | 个人资料/头像/等级/积分 | User | `/api/v1/user` |
| 内容域 | 博客/新闻/产品/方案/作品集 CRUD | Blog, News, Product, Solution, Project | `/api/v1/blog` 等 |
| 社交域 | 关注/粉丝/好友/动态/评论 | UserFollow, Moment, Comment | `/api/v1/social`, `/api/v1/moment`, `/api/v1/comments` |
| 交互域 | 多态点赞/收藏/分享 | UserLike, UserFavorite | `/api/v1/interaction` |
| 消息域 | 私信/AI 对话/通知 | DirectMessage, Conversation, Notification | `/api/v1/message`, `/api/v1/chat`, `/api/v1/notification` |
| AI 域 | LLM 对话/RAG 知识库/AI 工具 | Conversation, KnowledgeBase | `/api/v1/chat`, `/api/v1/knowledge`, `/api/v1/tools` |
| 游戏化域 | 积分/签到/成就/等级 | PointLog, Checkin, Achievement | `/api/v1/point`, `/api/v1/checkin`, `/api/v1/achievement` |
| 发现域 | 推荐/动态流/搜索 | — | `/api/v1/recommend`, `/api/v1/feed`, `/api/v1/search` |
| 管理域 | 仪表盘/用户管理/系统配置/监控 | SystemConfig, ApiKey, ApiCallLog | `/api/v1/admin` |
| 内容组织域 | 分类/标签/系列/专栏 | Category, Tag, Series | `/api/v1/category`, `/api/v1/tag`, `/api/v1/series` |
| 上传域 | 图片上传（封面+内容） | — | `/api/v1/upload` |

### 核心业务规则

- 5 种内容类型共享 `ContentBase` 基类（title/summary/content/cover_image/category/tags/status/counters）
- 内容状态：`draft` → `published` → `archived`
- 多态交互模式：`target_type` + `target_id` 避免表爆炸
- EventBus 解耦：19 个事件（`blog.published` / `like.created` / `user.followed` 等）触发积分和通知
- 积分体系：12 条规则，10 个等级（LV1 新人 → LV10 至尊王者，LV999 管理员）
- 签到系统：连续签到奖励（7 天/30 天/100 天里程碑）
- 成就系统：20 种成就，4 个阶段（铜/银/金/钻石）
- AI 对话：SSE 流式传输，三层停止机制（AbortController + cancel_event + abort_flag）
- RAG 知识库：ChromaDB + sentence-transformers（384 维向量）

---

## 2. 快速开始

```bash
# 环境要求：Python 3.11+, Node.js 20+

# 1. 配置后端环境变量
cd ai-portal/backend
cp .env.example .env
# 编辑 .env，填入 SECRET_KEY 和 LLM API Key

# 2. 安装后端依赖
pip install -r requirements.txt

# 3. 运行迁移
alembic upgrade head

# 4. 启动后端
python -m uvicorn app.main:app --reload --port 8000

# 5. 安装前端依赖
cd ../frontend
npm install

# 6. 启动前端（开发模式，自动代理 /api 到后端）
npm run dev
# 访问: http://localhost:3000

# 7. 运行测试
cd ../backend
python -m pytest tests/ -v --tb=short

# 8. 前端构建检查
cd ../frontend
npm run build
```

> Redis 为可选依赖。数据库默认使用 SQLite（WAL 模式），可迁移到 PostgreSQL。

---

## 3. 技术栈

| 层 | 技术 | 版本 |
|---|---|---|
| 后端框架 | FastAPI + Uvicorn | 0.111.0 / 0.29.0 |
| ORM | SQLAlchemy | 2.0.30 |
| 迁移 | Alembic | 1.13.1 |
| 数据库 | SQLite (WAL) / PostgreSQL | — |
| 认证 | JWT (python-jose) + bcrypt | 3.3.0 |
| AI 客户端 | httpx (SSE 流式) | 0.27.0 |
| 向量库 | ChromaDB + sentence-transformers | 0.5.0 |
| 前端框架 | Vue 3 (Composition API) | 3.4.27 |
| 语言 | TypeScript | 5.4.5 |
| UI 库 | Element Plus | 2.6.3 |
| 样式 | Tailwind CSS 3.4 + SCSS | — |
| 图表 | ECharts | 5.5.0 |
| Markdown | Milkdown + markdown-it + highlight.js | — |
| 状态管理 | Pinia | 2.1.7 |
| 路由 | Vue Router | 4.3.2 |
| HTTP | Axios | 1.7.2 |
| 构建 | Vite | 5.2.12 |
| 测试 | pytest (后端) + Vitest (前端) | — |
| 限流 | slowapi | 0.1.9+ |

---

## 4. 项目结构

```
ai-portal/
├── backend/
│   ├── app/
│   │   ├── main.py              # 入口：自动发现模块 + 注册路由 + 中间件
│   │   ├── core/
│   │   │   ├── config.py        # pydantic-settings 全局配置
│   │   │   ├── database.py      # SQLAlchemy engine (WAL mode)
│   │   │   ├── security.py      # JWT + bcrypt
│   │   │   ├── deps.py          # 依赖注入（DbDep/CurrentUserDep/AdminUserDep/require_level）
│   │   │   ├── crud.py          # CRUDBase 共享 CRUD 基类
│   │   │   ├── content_base.py  # ContentBase/ContentCreate/ContentUpdate
│   │   │   ├── schemas.py       # PaginatedResponse[T]
│   │   │   ├── events.py        # EventBus 事件定义（19 个事件）
│   │   │   ├── event_handlers.py# 事件处理器注册
│   │   │   ├── exceptions.py    # AppException 统一异常
│   │   │   └── logging_config.py# 结构化日志
│   │   ├── models/              # 27 个 SQLAlchemy 模型
│   │   ├── modules/             # 28 个业务模块（自动注册 /api/v1/{module}）
│   │   └── services/            # LLM/RAG/积分/成就/监控服务
│   ├── tests/                   # 305+ 测试用例
│   ├── alembic/                 # 数据库迁移
│   ├── data/                    # SQLite 数据库 + ChromaDB + 上传文件
│   └── logs/                    # 应用日志
├── frontend/
│   ├── src/
│   │   ├── api/                 # 26 个 API 模块
│   │   ├── stores/              # 7 个 Pinia Store
│   │   ├── composables/         # 12 个 Composable 函数
│   │   ├── components/          # 25+ 可复用组件
│   │   ├── views/               # 17 个视图目录（44 个页面）
│   │   ├── layouts/             # DefaultLayout + AdminLayout
│   │   ├── router/              # 40 个路由（懒加载）
│   │   └── design/              # 赛博朋克设计系统（tokens + theme）
│   ├── vite.config.ts           # Vite 配置（代理 + 分包优化）
│   └── tailwind.config.ts       # Tailwind 自定义主题
└── plans/                       # 开发阶段规划文档
```

### 各目录职责边界

| 目录 | 允许做的事 | 禁止做的事 |
|---|---|---|
| `core/` | 共享基础设施、基类、配置 | 放业务逻辑 |
| `models/` | 定义 ORM 模型 | 放业务逻辑 |
| `modules/` | 路由 + 模块内业务逻辑 | 放通用基础设施 |
| `services/` | 跨模块服务（LLM/RAG/积分） | 直接操作 Request |
| `stores/` | 前端状态管理 | 放 API 调用逻辑 |
| `composables/` | 可复用的组合式函数 | 放全局状态 |
| `components/` | UI 组件 | 放页面级逻辑 |
| `views/` | 页面视图 | 放通用组件 |

---

## 5. 架构约束

### 分层依赖规则

```
View (页面)
  │
  ▼
Store (状态) + Composable (逻辑复用)
  │
  ▼
API Module (HTTP 调用)
  │
  ▼
Router (FastAPI 路由)
  │
  ▼
Module (业务逻辑)
  │
  ▼
CRUDBase / Model (数据访问)
```

### 模块自动发现

```python
# main.py — 后端自动注册路由
for module_info in pkgutil.iter_modules(["app/modules"]):
    module = importlib.import_module(f"app.modules.{module_info.name}.router")
    app.include_router(module.router, prefix=f"/api/v1/{module_info.name}")
```

### EventBus 解耦模式

```python
# 事件定义 (core/events.py)
class EventType(str, Enum):
    BLOG_PUBLISHED = "blog.published"
    LIKE_CREATED = "like.created"
    USER_FOLLOWED = "user.followed"
    # ... 共 19 个事件

# 事件处理器 (core/event_handlers.py)
@event_bus.on(EventType.BLOG_PUBLISHED)
async def on_blog_published(user_id, **kwargs):
    await add_points(user_id, "publish_blog")

@event_bus.on(EventType.LIKE_CREATED)
async def on_like_created(user_id, **kwargs):
    await add_notification(target_user_id, "有人点赞了你的内容")
```

### 多态交互模式

```python
# UserLike / UserFavorite / Comment / Notification 都使用
# target_type (blog/news/product/solution/moment/comment) + target_id
# 避免为每种内容类型创建独立的关联表
```

### 权限体系

| 依赖项 | 说明 |
|---|---|
| `DbDep` | 仅数据库会话，无需认证 |
| `CurrentUserDep` | JWT 必须有效，返回 User 对象 |
| `AdminUserDep` | JWT 有效 + is_admin=True |
| `get_optional_current_user` | 可选认证，未登录返回 None |
| `require_level(n)` | 用户等级 >= n 才可访问 |

### 统一响应格式

```json
// 分页响应
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

### 自定义异常体系

```python
class AppException(Exception):
    def __init__(self, message: str, code: str, status_code: int): ...

class NotFoundException(AppException):    # 404
class ForbiddenException(AppException):   # 403
class ConflictException(AppException):    # 409
class BadRequestException(AppException):  # 400
class UnauthorizedException(AppException):# 401
```

---

## 6. 业务规则详细

### 6.1 认证域

- JWT access_token 24 小时过期，`sub` = user_id
- 密码 bcrypt 哈希存储
- 登录：username + password → bcrypt 验证 → 返回 JWT
- 注册：username + email + password → 创建用户 → 返回 JWT
- 改密：旧密码验证 → bcrypt 更新
- 前端 Axios 拦截器自动注入 `Authorization: Bearer <token>`
- 401 响应自动登出

### 6.2 内容域（5 种类型）

**共享字段（ContentBase）：**
title, slug, content (Markdown), summary, cover_image, category_id, tags, is_published, status, is_top, is_original, source_url, edit_version, view_count, likes_count, favorites_count, comments_count, shares_count

**状态机：**
```
draft ──(用户发布)──→ published ──(用户/管理员)──→ archived
```

**等级门槛：**
- LV3 以下：只能保存草稿，不能发布博客
- LV4 以下：不能发布作品集项目

**内容类型差异：**

| 类型 | 特有字段 | 说明 |
|---|---|---|
| Blog | series_id | 可归属系列/专栏 |
| News | — | 结构与 Blog 相同 |
| Product | features, pricing | 产品特性、定价 |
| Solution | industry, use_case | 行业、用例 |
| Project | tech_stack, demo_url, repo_url | 技术栈、演示、仓库 |

### 6.3 社交域

**关注系统：**
- 关注/取关（单向）
- 好友 = 互相关注（双向检测）
- 移除粉丝
- followers_count / following_count 计数器

**动态（Moment）：**
- 文本 + 图片（最多 9 张）
- 支持转发（repost_id）
- 嵌套评论

**评论：**
- 嵌套/树形结构（parent_id）
- IP 点赞（防重复）

### 6.4 交互域（多态）

```python
# 点赞
target_type: "blog" | "news" | "product" | "solution" | "moment" | "comment"
target_id: str

# 收藏
target_type: "blog" | "news" | "product" | "solution"
target_id: str
```

### 6.5 用户域 — 积分/签到/成就

**积分规则（12 条）：**

| 行为 | 积分 |
|---|---|
| 发布博客 | +10 |
| 发布动态 | +3 |
| 收到点赞 | +2 |
| 收到收藏 | +3 |
| 收到评论 | +2 |
| 每日签到 | +5 |
| 连续 7 天签到 | +20 |
| 连续 30 天签到 | +100 |
| 连续 100 天签到 | +500 |
| 获得成就 | +50 |
| 首次关注 | +5 |
| 被关注 | +3 |

**等级体系（10 级）：**

| 等级 | 名称 | 所需积分 |
|---|---|---|
| LV1 | 新人 | 0 |
| LV2 | 初学者 | 100 |
| LV3 | 进阶者 | 300 |
| LV4 | 资深者 | 900 |
| LV5 | 专家 | 1500 |
| LV6 | 大师 | 3000 |
| LV7 | 宗师 | 5000 |
| LV8 | 传奇 | 10000 |
| LV9 | 王者 | 20000 |
| LV10 | 至尊王者 | 50000 |
| LV999 | 管理员 | — |

**成就系统（20 种，4 阶段）：**
- 铜/银/金/钻石
- 分类：内容/社交/贡献/特殊

### 6.6 消息域

**私信：** 一对一，会话列表，未读计数
**AI 对话：** SSE 流式，多模型支持（DeepSeek/GLM/Qwen/Doubao），会话管理，thinking 标签
**通知：** 系统通知/互动通知（点赞/关注/评论/收藏），已读/未读状态

### 6.7 AI 域

**LLM 对话：**
- SSE 流式传输
- 三层停止：前端 AbortController → 后端 cancel_event → LLM abort_flag
- 多模型切换（DeepSeek/GLM/Qwen/Doubao）
- 每日限额 50 次
- Token 计数

**RAG 知识库：**
- ChromaDB 向量存储（384 维 sentence-transformers）
- 文档上传（.docx/.pdf）
- 分块策略：500 字符/50 字符重叠

**API 密钥管理：**
- Fernet 对称加密存储
- 多厂商支持（10 家）
- BaseURL 自动填充

### 6.8 管理域

18 个管理页面：
- 仪表盘（ECharts 图表）
- 内容管理（博客/新闻/产品/方案/作品集）
- 分类/标签管理
- 评论审核
- 用户管理
- 知识库管理
- API 密钥管理
- API 调用日志
- 系统监控
- 系统配置
- 个人设置
- 个人通知/动态

---

## 7. 数据模型

```
User (1) ──── (*) Blog           # 用户发布博客
User (1) ──── (*) News           # 用户发布新闻
User (1) ──── (*) Product        # 用户发布产品
User (1) ──── (*) Solution       # 用户发布方案
User (1) ──── (*) Project        # 用户发布项目
User (1) ──── (*) Moment         # 用户发布动态
User (1) ──── (*) UserFollow     # 关注关系（follower_id / following_id）
User (1) ──── (*) UserLike       # 多态点赞（target_type + target_id）
User (1) ──── (*) UserFavorite   # 多态收藏（target_type + target_id）
User (1) ──── (*) Comment        # 多态评论（target_type + target_id）
User (1) ──── (*) Notification   # 通知
User (1) ──── (*) DirectMessage  # 私信（sender_id / receiver_id）
User (1) ──── (*) Conversation   # AI 对话
User (1) ──── (*) PointLog       # 积分记录
User (1) ──── (*) Checkin        # 签到记录
User (1) ──── (*) UserAchievement# 用户成就
User (1) ──── (*) ReadingHistory # 阅读历史
Category (1) ── (*) Content      # 分类关联（module_type 区分）
Tag (1) ──── (*) ContentTag      # 标签关联（多态）
Series (1) ── (*) SeriesArticle  # 系列文章
Conversation (1) ── (*) Message  # AI 对话消息
KnowledgeBase (1) ── (*) KnowledgeDocument # 知识库文档
```

**27 个模型：** User, UserFollow, UserLike, UserFavorite, Blog, News, Product, Solution, Project, Category, Tag, ContentTag, Comment, Moment, Conversation, Message, DirectMessage, Notification, KnowledgeBase, KnowledgeDocument, ApiKey, ApiCallLog, SystemConfig, PointLog, Checkin, Achievement, UserAchievement, Series, SeriesArticle, ReadingHistory

---

## 8. API 规范

### 路由自动注册

所有业务 API 以 `/api/v1/{module}` 开头，28 个模块自动注册。

### 认证方式

```bash
# 请求头（可选，公开接口不需要）
Authorization: Bearer <access_token>

# JWT 结构
{
  "sub": "user-uuid",
  "exp": 1234567890
}
```

### 主要端点

| 方法 | 路径 | 认证 | 说明 |
|---|---|---|---|
| POST | `/api/v1/auth/login` | 否 | 登录 |
| POST | `/api/v1/auth/register` | 否 | 注册 |
| GET | `/api/v1/user/{id}` | 否 | 用户公开主页 |
| GET | `/api/v1/blog` | 否 | 博客列表 |
| GET | `/api/v1/blog/{id}` | 否 | 博客详情 |
| POST | `/api/v1/blog` | 是 | 创建博客 |
| POST | `/api/v1/interaction/like` | 是 | 点赞 toggle |
| POST | `/api/v1/interaction/favorite` | 是 | 收藏 toggle |
| POST | `/api/v1/social/follow/{id}` | 是 | 关注 |
| POST | `/api/v1/moment` | 是 | 发布动态 |
| POST | `/api/v1/chat/messages` | 是 | AI 对话（SSE 流式） |
| GET | `/api/v1/notification/unread-count` | 是 | 未读通知数 |
| POST | `/api/v1/checkin` | 是 | 每日签到 |
| GET | `/api/v1/feed` | 否 | 动态流 |
| GET | `/api/v1/search` | 否 | 全文搜索 |
| GET | `/api/v1/recommend` | 否 | 推荐内容 |

---

## 9. 测试策略

```bash
# 后端测试（305+ 用例）
cd ai-portal/backend
python -m pytest tests/ -v --tb=short

# 前端构建检查
cd ai-portal/frontend
npm run build

# 前端类型检查
npx vue-tsc --noEmit
```

---

## 10. 编码规范

### 后端

- 模块自动发现：`app/modules/{module}/router.py` + `models.py`
- 共享 CRUD：继承 `CRUDBase`，不要重复写 get/list/create/update/delete
- 内容类型：继承 `ContentBase`，共享字段不要重复定义
- 事件驱动：跨模块交互通过 `EventBus` 发布/订阅，不要直接 import 其他模块
- 异常处理：使用 `AppException` 子类，不要用 `HTTPException`
- 分页：统一返回 `PaginatedResponse[T]` 格式
- 权限：使用 `CurrentUserDep` / `AdminUserDep` / `require_level(n)` 依赖项

### 前端

- API 调用：使用 `src/api/` 模块，不要在组件中直接 fetch
- 状态管理：全局状态用 Pinia Store，局部状态用 ref/reactive
- 逻辑复用：提取到 `composables/`，不要在组件中重复逻辑
- 组件：通用组件放 `components/`，页面级放 `views/`
- 样式：使用 Tailwind CSS + CSS 变量（`--cyber-*`），不要硬编码颜色

---

## 11. 已知问题 & TODO

### P0 — 功能缺失

| # | 问题 | 说明 |
|---|------|------|
| 1 | 通知端点路径一致性 | 前端请求路径与后端路由需确认完全匹配 |

### P1 — 体验问题

| # | 问题 | 说明 |
|---|------|------|
| 1 | Token 无自动刷新 | 过期后需重新登录，应添加 refresh_token 机制 |
| 2 | 仪表盘图表数据 | 趋势图和饼图数据仍是硬编码 |
| 3 | 列表搜索范围 | 搜索只在当前页生效，应改为后端全文搜索 |

### P2 — 代码质量

| # | 问题 | 说明 |
|---|------|------|
| 1 | 前端类型安全 | 部分 API 返回 `Promise<any>` |
| 2 | 部分 catch 块无日志 | 空 catch 块应记录错误 |
| 3 | `any` 类型使用 | 应逐步替换为具体类型 |

---

## 12. 环境变量

| 变量名 | 用途 | 必填 | 默认值 |
|---|---|---|---|
| `SECRET_KEY` | JWT 签名 + API Key 加密 | ✅ | — |
| `DATABASE_URL` | 数据库连接串 | ❌ | `sqlite:///./ai_portal.db` |
| `DEBUG` | 调试模式 | ❌ | `false` |
| `ALLOWED_ORIGINS` | CORS 来源 | ❌ | `http://localhost:3000` |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | ❌ | — |
| `GLM_API_KEY` | 智谱 GLM 密钥 | ❌ | — |
| `QWEN_API_KEY` | 通义千问密钥 | ❌ | — |
| `DOUBAO_API_KEY` | 豆包密钥 | ❌ | — |
| `DAILY_CHAT_LIMIT` | 每日对话限额 | ❌ | `50` |
| `MAX_TOKENS_PER_REQUEST` | 单次最大 Token | ❌ | `4096` |
| `DEFAULT_MODEL` | 默认 LLM 模型 | ❌ | `deepseek-chat` |
| `CHROMA_PERSIST_DIR` | ChromaDB 存储路径 | ❌ | `./data/chroma` |
| `RAG_CHUNK_SIZE` | RAG 分块大小 | ❌ | `500` |
| `RAG_CHUNK_OVERLAP` | RAG 分块重叠 | ❌ | `50` |

---

## 13. 常用命令

```bash
# 后端
cd ai-portal/backend
python -m uvicorn app.main:app --reload --port 8000  # 启动
python -m pytest tests/ -v --tb=short                 # 测试
alembic upgrade head                                   # 迁移
alembic revision --autogenerate -m "描述"              # 生成迁移

# 前端
cd ai-portal/frontend
npm run dev       # 开发服务器
npm run build     # 生产构建
npx vue-tsc --noEmit  # 类型检查
```

---

## 14. 功能扩展路线图

### Phase P1 — 体验增强 ✅ 已完成

| # | 功能 | 模块 | 说明 | 状态 |
|---|------|------|------|------|
| 1 | Token 自动刷新 | auth | access_token (30min) + refresh_token (30d) 双 Token，rotation | ✅ |
| 2 | 后端全文搜索 | search | SQL 级分页 + title/summary/tags 搜索 + suggest 端点 | ✅ |
| 3 | 仪表盘真实数据 | admin | ECharts 图表从数据库聚合（趋势/模型/内容/活跃度） | ✅ |
| 4 | 私信支持图片 | message | message_type + image_url + 前端图片上传/预览 | ✅ |
| 5 | WebSocket 通知 | notification | 实时推送 + 心跳保活 + 自动重连 + 桌面弹窗 | ✅ |

### Phase P2 — 内容增强

| # | 功能 | 模块 | 说明 |
|---|------|------|------|
| 1 | 文章版本历史 | blog | 编辑历史 + 回滚 |
| 2 | 内容审核工作流 | admin | 敏感词 + 人工审核 |
| 3 | 专栏付费订阅 | series | 付费内容 + 订单 |
| 4 | Markdown 导入/导出 | blog | 批量 .md 导入 |
| 5 | 评论楼中楼 | comments | 知乎式嵌套展示 |

### Phase P3 — 社交增强

| # | 功能 | 模块 | 说明 |
|---|------|------|------|
| 1 | 动态转发 + 引用 | moment | 微博式转发 |
| 2 | 用户时间线 | user | 聚合所有行为 |
| 3 | 私信群聊 | message | 多人群聊 |
| 4 | 内容举报 | interaction | 举报 + 处理流程 |
| 5 | 用户拉黑 | social | 拉黑后不可见 |

### Phase P4 — AI 增强

| # | 功能 | 模块 | 说明 |
|---|------|------|------|
| 1 | AI 写作助手 | chat/blog | 文章生成/续写/润色 |
| 2 | 智能摘要 | recommend | 自动生成文章摘要 |
| 3 | 个性化推荐 | recommend | 协同过滤 + 用户画像 |
| 4 | AI 代码解释器 | tools | 代码执行 + 结果展示 |
| 5 | 知识图谱 | knowledge | 实体关系 + 图谱可视化 |

### Phase P5 — 运维 & 性能

| # | 功能 | 模块 | 说明 |
|---|------|------|------|
| 1 | PostgreSQL 迁移 | database | SQLite → PostgreSQL |
| 2 | Redis 缓存 | cache | 热门内容 + 会话存储 |
| 3 | CDN 图片 | upload | OSS/CDN 图片托管 |
| 4 | Sentry 错误追踪 | core | 前后端错误上报 |
| 5 | N+1 查询审查 | models | 所有列表接口优化 |

---

## 15. 给 Claude 的特殊指令

1. **新功能必须包含**：Router + Model + Schema + Test
2. **使用 CRUDBase 基类**：不要重复写 CRUD 逻辑
3. **跨模块交互用 EventBus**：不要直接 import 其他模块的服务
4. **内容类型继承 ContentBase**：共享字段不要重复定义
5. **前端 API 调用走 src/api/**：不要在组件中直接 fetch
6. **前端状态管理用 Pinia**：全局状态用 Store，局部用 ref
7. **逻辑复用提取到 composables/**：不要在组件中重复逻辑
8. **错误使用 AppException**：不要用 HTTPException
9. **分页统一 PaginatedResponse[T]**
10. **不引入新依赖而不先征询开发者同意**
