# AI Portal 待办事项

> 最后更新：2026-05-14

---

## 已知问题

### P0 — 功能缺失

| # | 问题 | 说明 |
|---|------|------|
| 1 | 通知端点路径一致性 | 前端 `notification.ts` 请求 `/notification/unread-count`，后端路由为 `/api/v1/notification/unread-count`，需确认代理和路径是否完全匹配 |

### P1 — 体验问题

| # | 问题 | 说明 |
|---|------|------|
| 1 | Token 无自动刷新 | token 过期后用户需重新登录，应添加 refresh token 机制 |
| 2 | 仪表盘图表数据 | 趋势图和饼图数据仍是写死的，需后端提供真实数据源 |
| 3 | 列表搜索范围 | 搜索只在当前页生效（请求 100 条数据），应改为后端全文搜索 |

### P2 — 代码质量

| # | 问题 | 说明 |
|---|------|------|
| 1 | 前端类型安全 | 部分 API 函数返回 `Promise<any>`，应添加泛型 |
| 2 | 前端 `any` 类型 | 多处使用 `any`，应逐步替换为具体类型 |
| 3 | 部分 catch 块无日志 | HomeView 等页面的 catch 块为空 |

---

## 后续优化方向

### 架构改进

- [ ] 将剩余 admin 管理页面迁移到 `useCrudAdmin`
- [ ] 创建 `useFormRules` composable 统一表单校验
- [ ] 为所有 API 添加 Zod 或 Valibot 运行时校验
- [ ] 考虑引入 WebSocket 实现实时通知
- [ ] 添加前端错误上报（Sentry）
- [ ] 数据库从 SQLite 迁移到 PostgreSQL（高并发场景）

### 功能增强

- [ ] 用户关注/粉丝列表分页优化（当前每次加载全部）
- [ ] 动态广场支持图片预览大图
- [ ] 私信支持图片/文件发送
- [ ] 博客支持目录树跳转（TOC 已有，需测试锚点跳转）
- [ ] 成就系统扩展更多成就类型
- [ ] 推荐算法优化（协同过滤、用户画像）

### 性能优化

- [ ] 前端路由懒加载优化
- [ ] 图片上传压缩（前端 canvas 压缩）
- [ ] API 响应缓存策略
- [ ] 数据库查询优化（N+1 问题已部分修复，需全面审查）

---

## 已完成

<details>
<summary>点击展开已完成的历史任务</summary>

### 2026-05-13 — 关注系统增强
- [x] 后端 `friends_count` 动态计算
- [x] 后端 `friends` 和 `remove-follower` 端点
- [x] 前端 `FollowDialog` 组件（3 Tab：关注/粉丝/好友）
- [x] `FollowDialog` 权限控制（好友 Tab 仅所有者可见，关系标签仅所有者显示）
- [x] 个人主页显示关注/粉丝/好友数量
- [x] 端口 3003 CORS 问题修复（代理重写重定向 Location 头）

### 2026-05-10 — 全面修复
- [x] ~161 个 Bug 修复
- [x] 安全修复（SVG XSS、路径穿越、CORS、速率限制等）
- [x] 架构统一（分页格式、异常处理、原子计数、N+1 查询）
- [x] 日志系统改造（结构化日志、请求追踪、前端错误处理）
- [x] 删除 ~20 个无用文件

### 2026-05-08 — 聊天流式功能
- [x] 停止按钮三层机制（前端 abort + 后端 cancel_event + LLM abort_flag）
- [x] 切换会话消息保存（`_save_assistant_message` 统一三种退出路径）
- [x] thinking/duration 字段

### 2026-05-08 — Phase 1-5 基础修复
- [x] 破坏性 Bug（聊天加载、知识库上传、弹窗动画）
- [x] 一致性（Axios 合并、tags 渲染、Pydantic v2）
- [x] 架构优化（自动发现、CRUD 基类、分页、表单验证）
- [x] 深色主题 + 发布状态
- [x] 后台管理 + 首页改版 + API 密钥管理

### 2026-05-07 — 新功能
- [x] 图片本地上传系统（cover + content）
- [x] 首页 HackerCanvas 动画
- [x] 种子数据（博客/新闻/产品/方案/项目）
- [x] 后台日期格式统一
- [x] 分类/标签下拉选择
- [x] CoverUpload 组件

### CSDN 对标升级（5 Phase）
- [x] Phase 1: 博客详情增强（进度条、TOC、代码复制、阅读时间、作者卡片、相关推荐）
- [x] Phase 2: 首页增强（热门排行、作者排行、回到顶部、社交分享、通知轮询）
- [x] Phase 3: 热力图 + 列表增强（贡献图、筛选增强、搜索自动补全）
- [x] Phase 4: 移动端适配
- [x] Phase 5: 系列/专栏、阅读历史、草稿自动保存

### UX 改进
- [x] 加载骨架屏（4 组件 + 10 页面集成）
- [x] 空状态统一
- [x] 危险操作确认
- [x] 互动按钮动效
- [x] 页面过渡动画
- [x] 无障碍修复
- [x] CommentSection 递归重构

</details>

---

## 测试运行

```bash
cd ai-portal/backend
rm -f test.db
python3 -m pytest tests/ -v --tb=short
```

## 前端构建验证

```bash
cd ai-portal/frontend
npm run build
```
