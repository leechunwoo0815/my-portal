# AI Portal — AI 技术门户

> 类 CSDN 的 AI 技术门户平台，赛博朋克 + 终端美学设计，FastAPI + Vue 3 全栈开发。
> 28 个后端模块、27 个数据模型、20 个测试文件（305+ 测试用例），企业级低耦合插拔式架构。

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 后端框架 | FastAPI + Uvicorn | 0.111.0 |
| ORM | SQLAlchemy + Alembic | 2.0.30 |
| 数据校验 | Pydantic + pydantic-settings | 2.7.1 |
| 数据库 | SQLite（WAL 模式，可扩展 PostgreSQL） | — |
| 认证 | JWT (python-jose) + bcrypt | — |
| AI 服务 | httpx → DeepSeek / 智谱 / 通义 / 豆包 | — |
| 向量数据库 | ChromaDB + sentence-transformers | 0.5.0 |
| 限流 | slowapi | — |
| 前端框架 | Vue 3 + TypeScript | 3.4 / 5.4 |
| UI 组件库 | Element Plus | 2.6 |
| CSS 框架 | Tailwind CSS 3.4 + SCSS | — |
| 图表 | ECharts | 5.5 |
| 编辑器 | Milkdown (Markdown WYSIWYG) | — |
| 状态管理 | Pinia | 2.1 |
| 构建工具 | Vite | 5.2 |

## 项目架构

```
ai-portal/
├── backend/                          FastAPI 后端
│   ├── app/
│   │   ├── main.py                   应用入口 + 模块自动发现 + 中间件
│   │   ├── core/                     配置、依赖注入、安全、数据库、事件总线
│   │   │   ├── config.py             全局配置 (pydantic-settings)
│   │   │   ├── database.py           SQLAlchemy engine + SessionLocal
│   │   │   ├── security.py           JWT + bcrypt
│   │   │   ├── deps.py               依赖注入 (get_db, get_current_user, require_admin)
│   │   │   ├── crud.py               共享 CRUD 基类
│   │   │   ├── content_base.py       内容模型基类
│   │   │   ├── events.py             EventBus 事件定义
│   │   │   ├── event_handlers.py     事件处理器注册
│   │   │   ├── exceptions.py         自定义异常类
│   │   │   ├── schemas.py            共享 Pydantic Schema
│   │   │   └── logging_config.py     结构化日志配置
│   │   ├── models/                   27 个 SQLAlchemy 模型
│   │   ├── modules/                  28 个业务模块（自动注册路由）
│   │   └── services/                 服务层
│   │       ├── llm_service.py        LLM 多模型调用
│   │       ├── llm_client.py         LLM HTTP 客户端
│   │       ├── rag_service.py        RAG 检索增强
│   │       ├── point_service.py      积分系统
│   │       ├── achievement_service.py 成就系统
│   │       └── monitor.py            系统监控
│   ├── alembic/                      数据库迁移
│   ├── tests/                        20 个测试文件 (305+ 用例)
│   ├── scripts/seed.py               种子数据
│   └── data/ai_portal.db             SQLite 数据库
│
├── frontend/                         Vue 3 前端
│   ├── src/
│   │   ├── api/                      26 个 API 模块 + client.ts
│   │   ├── stores/                   7 个 Pinia Store
│   │   ├── composables/              9 个组合式函数
│   │   ├── components/               13 个通用组件
│   │   │   ├── skeleton/             4 个骨架屏组件
│   │   │   ├── interaction/          4 个互动组件 (Like/Fav/Follow/Share)
│   │   │   └── editor/               Milkdown 编辑器
│   │   ├── views/                    17 个视图目录
│   │   ├── layouts/                  DefaultLayout + AdminLayout
│   │   ├── design/                   设计系统 (Token + 主题)
│   │   └── router/                   路由 + 认证守卫
│   └── tailwind.config.ts            Tailwind 赛博朋克配置
│
├── docker-compose.yml                Docker 部署
└── .github/workflows/ci.yml         CI/CD
```

## 快速开始

### 后端（端口 8000）

```bash
cd ai-portal/backend
pip install -r requirements.txt
./start.sh
# 或手动启动：uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 前端（端口 3000，自动代理 /api → 8000）

```bash
cd ai-portal/frontend
npm install
npm run dev
```

### Docker 部署

```bash
cd ai-portal && docker-compose up -d
```

### 默认账号

`admin` / `admin123`

---

## 功能模块

### 内容管理（5 个模块）

| 模块 | 前台 | 后台管理 | 特性 |
|------|------|----------|------|
| 博客 | 列表 + 详情 + Markdown 渲染 | CRUD + 发布控制 | 标签/分类筛选、系列/专栏、阅读历史 |
| 新闻 | 列表 + 详情 | CRUD + 发布控制 | 分类筛选 |
| 产品 | 列表 + 详情 | CRUD + 发布控制 | 产品展示 |
| 方案 | 列表 + 详情 | CRUD + 发布控制 | 解决方案 |
| 作品集 | 列表 + 详情 | CRUD | 项目案例展示 |

### 社交互动（6 个模块）

| 模块 | 功能 | API 端点 |
|------|------|----------|
| 关注系统 | 关注/取关、互关检测、粉丝/关注/好友列表、移除粉丝 | `POST /follow/{id}`, `GET /followers/{id}`, `GET /following/{id}`, `GET /friends/{id}`, `POST /remove-follower/{id}`, `GET /follow-status/{id}` |
| 动态广场 | 发布动态（文字+图片）、转发、删除 | `/moment` |
| 评论系统 | 嵌套回复、IP 点赞 toggle、级联删除 | `/comments` |
| 互动系统 | 点赞、收藏、分享 | `/interaction` |
| 私信 | 用户间私信、未读计数 | `/message` |
| 通知系统 | 互动通知、系统通知、未读计数 | `GET /notification`, `PUT /read-all`, `GET /unread-count` |

### 用户体系（5 个模块）

| 模块 | 功能 | 亮点 |
|------|------|------|
| 认证 | 登录、注册、改密 | JWT + bcrypt |
| 用户资料 | 个人主页、头像上传、密码修改 | 等级进度条 + 成就墙 |
| 积分系统 | 12 条积分规则、10 级等级体系 | EventBus 驱动自动积分 |
| 签到系统 | 每日签到、连续天数、里程碑奖励 | 7天+10 / 30天+50 / 100天+200 |
| 成就系统 | 20 种成就，4 个段位（铜/银/金/钻石） | 进度追踪，秘密成就 |

### 推荐与发现（3 个模块）

| 模块 | 功能 | 算法 |
|------|------|------|
| 推荐 | 个性化推荐流、热门内容、相关推荐 | 加权评分：view×0.1 + likes×2.0 + fav×3.0 + comment×1.5 + 时间衰减 |
| 动态流 | 关注用户动态 + 全站动态 | 按时间排序，支持分页 |
| 搜索 | 全文搜索 + 类型筛选 + 搜索建议 | 标签聚合 |

### AI 能力（3 个模块）

| 模块 | 功能 | 亮点 |
|------|------|------|
| AI 对话 | SSE 流式对话、多模型切换、会话管理 | DeepSeek/智谱/通义/豆包，停止生成 + thinking 展示 |
| 知识库 | RAG 检索增强、文档上传 | ChromaDB + sentence-transformers |
| AI 工具 | AI 工具集 | 扩展接口 |

### 内容组织（3 个模块）

| 模块 | 功能 |
|------|------|
| 分类 | 内容分类管理 |
| 标签 | 标签 CRUD + 内容关联 |
| 系列/专栏 | 博客系列化组织，文章排序 |

### 管理后台（18 个页面）

| 分组 | 页面 |
|------|------|
| 总览 | 仪表盘（ECharts 赛博朋克图表）、系统监控 |
| 内容管理 | 博客、项目、新闻、产品、方案（均有 CRUD + 发布控制） |
| 社区管理 | 评论管理、动态管理（MyMoments）、通知管理 |
| 用户管理 | 用户管理、个人设置（头像上传+密码修改） |
| 系统管理 | 分类管理、标签管理、API 密钥管理、API 日志、知识库管理、系统配置 |

---

## 设计系统

### 赛博朋克 + 终端美学

- **品牌前缀**：`>_` 终端命令行风格
- **字体**：JetBrains Mono（等宽）+ Inter（正文）
- **霓虹绿**：Light `#00d4aa` / Dark `#00ff88`
- **琥珀金**：Light `#f0b429` / Dark `#ffb800`
- **CRT 特效**：扫描线动画、霓虹辉光、脉冲呼吸
- **暗色模式**：GitHub Dark 风格 `#0d1117` 背景

### CSS 变量体系

| 变量名 | Light | Dark | 用途 |
|--------|-------|------|------|
| `--app-bg` | `#eef2f8` | `#0a0a0a` | 页面背景 |
| `--app-bg-card` | `#ffffff` | `#141414` | 卡片背景 |
| `--app-text` | `#333333` | `#e0e0e0` | 主文字 |
| `--app-text-secondary` | `#666666` | `#b0b8c4` | 次要文字 |
| `--app-accent` | `#409eff` | `#626aef` | 强调色 |
| `--app-border` | `#e4e7ed` | `#303133` | 边框 |

---

## EventBus 事件系统

19 个事件订阅，解耦模块间通信：

```
blog.published/created → 积分+通知
comment.created → 积分+通知
like.created → 积分+通知
favorite.created → 积分+通知
user.registered → 欢迎通知
user.followed → 积分+通知
checkin.done → 积分+成就检测
```

---

## 测试

```bash
cd backend && python3 -m pytest tests/ -v
```

| 测试文件 | 覆盖模块 | 测试数 |
|----------|----------|--------|
| test_auth.py | 登录、Token、改密 | 10 |
| test_blog.py | CRUD、权限、分页 | 20 |
| test_category.py | 分类 CRUD | 6 |
| test_chat.py | 会话 CRUD、置顶 | 6 |
| test_comments.py | 嵌套、点赞、级联 | 6 |
| test_events.py | EventBus 事件 | 8 |
| test_full_verification.py | 全模块验证 | 52 |
| test_history.py | 阅读历史记录、列表、清空 | 10 |
| test_news.py | CRUD + 权限 | 7 |
| test_phase4.py | 互动/动态/通知/积分/社交 | 42 |
| test_phase7.py | 成就 + 签到 | 20 |
| test_phase8.py | 推荐 + Feed | 20 |
| test_portfolio.py | CRUD + 权限 | 7 |
| test_products.py | CRUD + 权限 | 7 |
| test_search.py | 搜索、分页、筛选 | 5 |
| test_series.py | 专栏 CRUD + 文章管理 | 16 |
| test_solutions.py | CRUD + 权限 | 7 |
| test_tag.py | 标签 CRUD | 6 |
| test_user_journey.py | 用户旅程集成测试 | 47 |
| **合计** | **20 个文件** | **305+** |

---

## 关键配置

### 后端 .env

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SECRET_KEY` | （随机） | JWT 签名 + API Key 加密 |
| `DEBUG` | `true` | 调试模式 |
| `DATABASE_URL` | `sqlite:///./data/ai_portal.db` | 数据库 |
| `DAILY_CHAT_LIMIT` | `50` | 每日对话限制 |
| `DEFAULT_MODEL` | `deepseek-chat` | 默认模型 |
| `ADMIN_USERNAME` | `admin` | 管理员用户名 |
| `ADMIN_PASSWORD` | `admin123` | 管理员密码 |
| `ALLOWED_ORIGINS` | `http://localhost:3000,http://localhost:5173` | CORS 允许源 |

### 新增 LLM 模型

在 `app/services/llm_service.py` 添加：

```python
MODEL_DISPLAY_NAMES["new-model"] = "显示名称"
_MODEL_ENV_MAP["new-model"] = {"provider": "deepseek"}
```

---

## 新增模块 Checklist

```bash
# 1. 后端：创建模块目录 + router + schemas
mkdir -p backend/app/modules/<name>
touch backend/app/modules/<name>/{__init__,router,schemas}.py

# 2. 后端：创建模型（如需要）
touch backend/app/models/<name>.py
# 并在 backend/app/models/__init__.py 中导出

# 3. 后端：写测试
touch backend/tests/test_<name>.py
python3 -m pytest tests/test_<name>.py -v

# 4. 前端：创建 API + 视图
touch frontend/src/api/<name>.ts
mkdir -p frontend/src/views/<name>

# 5. 前端：添加路由
# 编辑 frontend/src/router/index.ts

# 6. 前端：如需管理页面，使用 useCrudAdmin composable
# 7. 运行全量测试确保无回归
python3 -m pytest tests/ -v
```

## 许可证

MIT
