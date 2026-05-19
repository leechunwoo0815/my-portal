# AI Portal 历史 Bug 修复与架构改进记录

> 本文件记录项目开发过程中的 Bug 修复、架构改进和重大变更。
> 当前状态请参考 `README.md` 和 `ARCHITECTURE.md`。

---

## 一、Phase 1-5 基础修复（2026-05-08）

### Phase 1 — 破坏性 Bug

| Bug | 文件 | 修复方式 |
|-----|------|---------|
| 聊天页无法加载历史会话/模型 | `stores/chat.ts` | 移除 4 处多余的 `.data` 访问（axios 拦截器已解包） |
| 知识库文档上传永远 401 | `views/dashboard/KnowledgeManage.vue` | `token` → `access_token` |
| 博客管理弹窗动画异常 | `views/dashboard/BlogManage.vue` | 移除 `v-if="visible"`（与 `v-model` 冲突） |

### Phase 2 — 一致性和 UX

| Issue | 修复方式 |
|-------|---------|
| 两套重复 Axios 实例 | 合并为单一实例 `api/client.ts` |
| 仪表盘图表数据是假的 | 移除多余的 `res.data` 访问 |
| sendMessage 死代码 + 安全漏洞 | 删除废弃函数，补全 `/api` 前缀 |
| admin 页面 tags 显示原始 JSON | 改用 `el-tag` 循环渲染 |
| 后端 `dict()` → Pydantic v2 | `news.dict()` → `news.model_dump()` |

### Phase 3 — 架构优化

| Issue | 修复方式 |
|-------|---------|
| 模块模型手动 import | 改用 `pkgutil` 自动发现 |
| URL 尾部斜杠不一致 | 移除尾部 `/`（后改为代理重写重定向） |
| updateSystemConfig 用 query 参数 | 改为 body 传值 |
| CRUD 重复代码 | 新增 `CRUDBase` 基类 |
| 管理页无分页/表单验证 | 添加 `el-pagination` + `el-form` rules |

### Phase 4 — 深色主题 + 发布状态

| Bug | 修复方式 |
|-----|---------|
| 深色主题详情页字体看不清 | CSS 硬编码颜色 → CSS 变量 |
| 关闭发布后记录消失 | 新增 `adminListBlogs`/`adminListProjects` 管理员接口 |
| 公开列表显示未发布内容 | 公开端点默认过滤 `is_published=True` |

### Phase 5 — 后台管理 + 首页改版

| Issue | 修复方式 |
|-------|---------|
| 菜单结构不合理 | 内容管理改为二级菜单，系统管理分组 |
| HomeView 布局杂乱 | Hero + 统计条 + 精选项目 + 模块卡片 |
| HackerCanvas 特效过头 | 暗色精简 Matrix 雨，日间改为旋转点阵 |
| API密钥管理 UI 简陋 | 10家厂商下拉 + BaseURL 自动填充 + 获取模型按钮 |

---

## 二、全面修复（2026-05-10）

### 变更统计

| 类别 | 数量 |
|------|------|
| 修复的 Bug | ~161 个 |
| 修改的文件 | ~130 个 |
| 新增的文件 | ~15 个 |
| 删除的文件 | ~20 个 |

### 安全修复

| # | 问题 | 修复 |
|---|------|------|
| 1 | SVG 上传允许存储型 XSS | 移除 `image/svg+xml` |
| 2 | CRUDRouterFactory update 无所有权检查 | 添加 author_id 比较 |
| 3 | 路径穿越漏洞（3处） | `os.path.basename()` + `re.sub` |
| 4 | 默认 SECRET_KEY 不安全 | 启动时警告 |
| 5 | CORS `allow_headers=["*"]` 过于宽松 | 显式列表 |
| 6 | 评论创建无认证 | 添加 `get_current_user` |
| 7 | 评论删除用 author_name 做权限 | 改为 user_id |
| 8 | 速率限制缺失 | slowapi 中间件 |
| 9 | 请求大小无限制 | 50MB 中间件 |

### 架构修复

| # | 问题 | 修复 |
|---|------|------|
| 1 | `count_tokens` 方法不存在 | 添加估算方法 |
| 2 | `extra_data` 用 `Column(Text)` 存 JSON | 改为 `Column(JSON)` |
| 3 | 返回扁平数组 | 统一为 `{items, total, page, page_size, total_pages}` |
| 4 | 所有 Router 使用 `HTTPException` | 统一使用 `AppException` |
| 5 | 竞态条件（计数） | 原子 SQL `UPDATE SET count = count + 1` |
| 6 | N+1 查询 | 批量预查询 + GROUP BY |
| 7 | 数据库缺少索引（8个表） | 添加 `index=True` |

---

## 三、聊天流式功能修复（2026-05-08）

### 停止按钮无效

**根因**：`sendMessageStream()` 调用传了 9 个参数，函数只接受 8 个，`abortController.signal` 被挤到错误位置。

**修复**：删除重复的 error 回调，`signal` 正确作为第 8 参数传入。三层停止机制：前端 abort + 后端 cancel_event + LLM abort_flag。

### 切换会话消息丢失

**根因**：`asyncio.CancelledError` 继承自 `BaseException`，不被 `except Exception` 捕获，`db.commit()` 永远执行不到。

**修复**：`except (Exception, asyncio.CancelledError)` 统一捕获，`_save_assistant_message()` 独立函数处理三种退出路径。

---

## 四、关注系统增强（2026-05-13）

### friends_count 始终为 0

**根因**：后端 `_build_user_profile` 从未计算和返回 `friends_count`。

**修复**：
- 后端 `user/router.py`：添加 `friends_count` 动态子查询
- 后端 `user/schemas.py`：`UserProfilePublic` 添加 `friends_count: int`
- 前端 `api/user.ts`：`UserProfile` 接口添加 `friends_count: number`
- 前端 `UserProfileView.vue`：添加"好友"统计项 + 点击打开 FollowDialog

### FollowDialog 权限问题

**问题**：查看他人主页时，"好友" Tab 不应显示；关系标签（"关注你"）容易引起歧义。

**修复**：
- "好友" Tab 仅对主页所有者显示
- 关系标签（好友/已关注/关注你）仅对主页所有者显示
- 默认 Tab 若为 'friends' 且非所有者，自动回退到 'following'

### 后端新增端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/social/friends/{user_id}` | GET | 互相关注的用户列表（好友） |
| `/api/v1/social/remove-follower/{user_id}` | POST | 移除粉丝 |

---

## 五、端口 3003 CORS 问题（2026-05-13）

### 问题

3000 端口可正常加载所有模块内容，3003 端口只能看到博客列表，其他模块全部为空。

### 根因

FastAPI 的 `redirect_slashes` 行为：请求 `/api/v1/news` 时返回 307 重定向到 `/api/v1/news/`。Vite 代理将 307 响应直接返回给浏览器，浏览器跟随重定向直接请求 `http://localhost:8000/api/v1/news/`，被 CORS 策略阻止（`localhost:3003` 不在 `ALLOWED_ORIGINS` 中）。

### 修复

在 `vite.config.ts` 的代理配置中添加 `configure` 回调，重写重定向 Location 头：

```typescript
configure: (proxy) => {
  proxy.on('proxyRes', (proxyRes) => {
    if ([301,302,307,308].includes(proxyRes.statusCode)) {
      const location = proxyRes.headers.location
      if (location) {
        proxyRes.headers.location = location.replace(/^http:\/\/localhost:8000/, '')
      }
    }
  })
}
```

---

## 六、日志系统改造（2026-05-07）

### 后端

| 组件 | 日志内容 | 级别 |
|------|---------|------|
| 请求中间件 | 全部 HTTP 请求 (method, path, status, latency, IP) | INFO/WARNING |
| 启动生命周期 | 启动/关闭/模块加载 | INFO |
| AppException | 业务异常 | WARNING |
| 未捕获异常 | 服务器内部错误 (含 traceback) | ERROR |
| JWT 验证失败 | Token 校验失败 | WARNING |

### 前端

| 组件 | 日志内容 |
|------|---------|
| Vue errorHandler | Vue 组件异常 |
| window.onerror | JS 运行时错误 |
| onunhandledrejection | Promise 未捕获异常 |
| Axios 拦截器 | 请求 URL + 响应状态码 |
| Chat Store | 6 个 API 的 catch 块 |

---

## 七、删除的无用文件（2026-05-10）

| 文件 | 原因 |
|------|------|
| `frontend/src/types/api.ts` | 从未导入 |
| `frontend/src/api/tools.ts` | 从未调用 |
| `frontend/src/components/UserAvatar.vue` | 从未使用 |
| `frontend/src/components/user/FavoriteList.vue` | 从未使用 |
| `backend/app/modules/news/models.py` | 与 `app/models/news.py` 重复 |
| `backend/app/modules/products/models.py` | 与 `app/models/products.py` 重复 |
| `backend/app/modules/solutions/models.py` | 与 `app/models/solutions.py` 重复 |
| `backend/app/seed.py` | 与 `scripts/seed.py` 重复 |
| `backend/app/models/models.py` | 转发文件，统一导入路径 |
