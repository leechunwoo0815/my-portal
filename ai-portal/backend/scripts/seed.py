"""
AI Portal 统一种子数据脚本
用法: cd backend && python -m scripts.seed [--reset]
"""
import sys
import os
import random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone, timedelta, date
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models import (
    User, Blog, Project, News, Product, Solution,
    Comment, Moment, UserLike, UserFavorite, UserFollow,
    Notification, PointLog, CheckinRecord,
    Category, Tag, ContentTag,
)
from app.models.series import Series, SeriesArticle
from app.models.history import ReadingHistory

Base.metadata.create_all(bind=engine)

HASHED_PW = get_password_hash("123456")
ADMIN_PW = get_password_hash("admin123")

# ─── 用户数据 ───────────────────────────────────────────────
USERS = [
    {"username": "admin", "email": "admin@aiportal.local", "hashed_password": ADMIN_PW,
     "is_admin": True, "level": 10, "points": 50000, "total_points": 50000,
     "nickname": "站长大大", "bio": "AI Portal 创始人，全栈工程师，热爱开源。",
     "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=admin",
     "gender": "male", "location": "北京", "website": "https://aiportal.dev",
     "github": "https://github.com/aiportal"},
    {"username": "alice_ml", "email": "alice@example.com", "nickname": "Alice 算法实验室",
     "bio": "机器学习博士，研究方向：CV / 多模态。Google Scholar 2000+ 引用。",
     "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=alice",
     "gender": "female", "location": "上海", "github": "https://github.com/alice-ml",
     "level": 8, "points": 12000, "total_points": 15000},
    {"username": "bob_frontend", "email": "bob@example.com", "nickname": "Bob 前端日记",
     "bio": "Vue / React 双修选手，Element Plus 贡献者，CSS 动画爱好者。",
     "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=bob",
     "gender": "male", "location": "深圳", "website": "https://bobfe.dev",
     "level": 7, "points": 8000, "total_points": 10000},
    {"username": "charlie_ops", "email": "charlie@example.com", "nickname": "Charlie 运维笔记",
     "bio": "K8s / Docker / CI-CD 老兵，维护 500+ 节点集群。",
     "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=charlie",
     "gender": "male", "location": "杭州", "level": 6, "points": 5000, "total_points": 6000},
    {"username": "diana_nlp", "email": "diana@example.com", "nickname": "Diana NLP 世界",
     "bio": "NLP 研究员，专注大模型微调与 RAG 应用落地。",
     "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=diana",
     "gender": "female", "location": "成都", "level": 8, "points": 9000, "total_points": 11000},
    {"username": "eve_data", "email": "eve@example.com", "nickname": "Eve 数据洞察",
     "bio": "数据分析师，擅长 Python 可视化与 BI 报表。",
     "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=eve",
     "gender": "female", "location": "广州", "level": 5, "points": 3000, "total_points": 4000},
    {"username": "frank_go", "email": "frank@example.com", "nickname": "Frank Go 后端",
     "bio": "Go 语言爱好者，微服务架构师，开源项目 Maintainer。",
     "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=frank",
     "gender": "male", "location": "南京", "github": "https://github.com/frank-go",
     "level": 6, "points": 6000, "total_points": 7500},
    {"username": "grace_ai", "email": "grace@example.com", "nickname": "Grace AI 产品",
     "bio": "AI 产品经理，关注 AIGC 与 AI Agent 落地场景。",
     "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=grace",
     "gender": "female", "location": "北京", "level": 5, "points": 3500, "total_points": 4500},
    {"username": "henry_sec", "email": "henry@example.com", "nickname": "Henry 安全实验室",
     "bio": "网络安全工程师，渗透测试 / 代码审计 / DevSecOps。",
     "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=henry",
     "gender": "male", "location": "武汉", "level": 6, "points": 5500, "total_points": 7000},
    {"username": "ivy_design", "email": "ivy@example.com", "nickname": "Ivy 设计工坊",
     "bio": "UI/UX 设计师，Figma 达人，关注设计系统与无障碍。",
     "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=ivy",
     "gender": "female", "location": "厦门", "level": 3, "points": 2000, "total_points": 2500},
    {"username": "jack_rust", "email": "jack@example.com", "nickname": "Jack Rust 之旅",
     "bio": "Rust 系统编程爱好者，WebAssembly 布道师。",
     "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=jack",
     "gender": "male", "location": "西安", "level": 4, "points": 4000, "total_points": 5000},
]

# ─── 分类数据 ───────────────────────────────────────────────
BLOG_CATS = ["深度学习", "前端开发", "后端开发", "机器学习", "NLP", "运维部署", "AI应用", "数据科学", "网络安全", "系统编程"]
NEWS_CATS = ["行业动态", "产品发布", "融资并购", "政策法规", "技术突破", "学术进展"]
PRODUCT_CATS = ["AI工具", "SaaS平台", "智能硬件", "数据分析", "聊天机器人", "图像生成"]
SOLUTION_CATS = ["医疗健康", "教育培训", "金融保险", "智能制造", "智慧城市", "零售电商"]
PROJECT_CATS = ["企业官网", "电商系统", "AI应用", "管理系统", "移动应用", "数据平台"]

TAGS_POOL = [
    "Transformer", "Vue3", "FastAPI", "PyTorch", "LangChain", "Docker",
    "TypeScript", "React", "NLP", "K8s", "MLOps", "Security",
    "Deep Learning", "RAG", "LLM", "GPT", "Rust", "Go", "Python",
    "WebAssembly", "GraphQL", "Redis", "PostgreSQL", "MongoDB",
    "TailwindCSS", "Next.js", "Svelte", "Flutter", "Swift", "Kotlin",
]

# ─── 博客内容模板（丰富 Markdown）─────────────────────────────
BLOG_TEMPLATES = [
    {
        "title": "从零搭建 RAG 系统：架构设计与实战",
        "category": "AI应用", "tags": "RAG,LLM,LangChain,Python",
        "summary": "手把手教你搭建生产级 RAG 系统，涵盖文档解析、向量检索、重排序与生成。",
        "content": """# 从零搭建 RAG 系统：架构设计与实战

> RAG（Retrieval-Augmented Generation）是当前 LLM 应用最主流的架构模式。本文将从架构设计到代码实现，带你完整走一遍。

## 为什么需要 RAG？

大语言模型存在以下问题：

1. **知识截止**：训练数据有时间截止点
2. **幻觉问题**：可能生成看似合理但错误的内容
3. **缺乏私域知识**：无法访问企业内部文档

RAG 通过检索外部知识库来增强生成质量。

## 系统架构

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  用户提问    │────▶│  检索模块     │────▶│  生成模块    │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                    ┌──────────────┐
                    │  向量数据库   │
                    └──────────────┘
```

## 核心代码

```python
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

class RAGService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = Chroma(
            embedding_function=self.embeddings,
            persist_directory="./chroma_db"
        )

    def retrieve(self, query: str, k: int = 5):
        return self.vectorstore.similarity_search(query, k=k)

    def generate(self, query: str, context: list[str]) -> str:
        prompt = f\"\"\"基于以下上下文回答问题：
{chr(10).join(context)}

问题：{query}\"\"\"
        return self.llm.generate(prompt)
```

## 性能优化要点

| 优化项 | 方案 | 效果 |
|--------|------|------|
| 向量检索 | HNSW 索引 | 10x 加速 |
| 重排序 | Cross-Encoder | 准确率 +15% |
| 分块策略 | 递归分块 512 token | 召回率最优 |
| 缓存 | Redis 缓存热门查询 | 延迟 -60% |

## 总结

RAG 系统的核心在于 **检索质量**。好的检索策略比更大的模型更有效。

---

*如果觉得有帮助，欢迎点赞收藏 👍*
""",
    },
    {
        "title": "Vue 3.5 新特性深度解析：Vapor Mode 来了",
        "category": "前端开发", "tags": "Vue3,TypeScript,前端",
        "summary": "Vue 3.5 带来了 Vapor Mode、useId()、useTemplateRef() 等重大更新。",
        "content": """# Vue 3.5 新特性深度解析

## Vapor Mode

Vue 3.5 最重磅的更新就是 **Vapor Mode**——一种编译时优化模式，可以将 Vue 组件编译为接近原生 DOM 操作的代码。

```vue
<script setup vapor>
import { ref } from 'vue'

const count = ref(0)
const increment = () => count.value++
</script>

<template>
  <button @click="increment">
    Count: {{ count }}
  </button>
</template>
```

> 加上 `vapor` 属性，组件就会以 Vapor 模式编译。

## useId()

解决 SSR hydration ID 不匹配问题：

```typescript
const id = useId()
// 输出: ":r1:"  (服务端和客户端一致)
```

## useTemplateRef()

新的模板引用 API，更符合直觉：

```typescript
const inputRef = useTemplateRef('myInput')

onMounted(() => {
  inputRef.value?.focus()
})
```

## 性能对比

- **Vapor Mode**: 比标准模式快 **30-50%**
- **内存占用**: 减少约 **20%**
- **Bundle Size**: 减少约 **15%**

## 迁移建议

1. 新组件优先使用 Vapor Mode
2. 逐步替换 `ref()` 为 `useTemplateRef()`
3. 使用 `useId()` 解决 SSR 问题
""",
    },
    {
        "title": "FastAPI + SQLAlchemy 异步实战指南",
        "category": "后端开发", "tags": "FastAPI,Python,PostgreSQL",
        "summary": "深入讲解 FastAPI 与 SQLAlchemy 2.0 的异步集成最佳实践。",
        "content": """# FastAPI + SQLAlchemy 异步实战指南

## 环境准备

```bash
pip install fastapi uvicorn sqlalchemy[asyncio] asyncpg
```

## 数据库配置

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)
```

## 模型定义

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
```

## 依赖注入

```python
from fastapi import Depends

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
```

## 关键注意事项

- 使用 `asyncpg` 而非 `psycopg2`
- 所有数据库操作都需要 `await`
- 避免在 async 函数中使用同步 ORM 方法
- 使用 `select()` 而非 `query()`
""",
    },
    {
        "title": "Transformer 注意力机制完全图解",
        "category": "深度学习", "tags": "Transformer,Deep Learning,PyTorch",
        "summary": "用可视化方式彻底理解 Self-Attention、Multi-Head Attention 和位置编码。",
        "content": """# Transformer 注意力机制完全图解

## Self-Attention 直觉

> 想象你在读一句话：「猫坐在垫子上，因为**它**很累」。人类自然知道「它」指「猫」。Self-Attention 就是让模型学会这种关联。

## 计算步骤

### 1. QKV 投影

```
Q = X × W_Q    (查询)
K = X × W_K    (键)
V = X × W_V    (值)
```

### 2. 注意力分数

$$Attention(Q, K, V) = softmax(\\frac{QK^T}{\\sqrt{d_k}})V$$

### 3. PyTorch 实现

```python
import torch
import torch.nn as nn

class SelfAttention(nn.Module):
    def __init__(self, d_model, n_heads):
        super().__init__()
        self.n_heads = n_heads
        self.d_k = d_model // n_heads

        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

    def forward(self, x):
        B, L, D = x.shape
        Q = self.W_q(x).view(B, L, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_k(x).view(B, L, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_v(x).view(B, L, self.n_heads, self.d_k).transpose(1, 2)

        scores = torch.matmul(Q, K.transpose(-2, -1)) / (self.d_k ** 0.5)
        attn = torch.softmax(scores, dim=-1)
        out = torch.matmul(attn, V)

        out = out.transpose(1, 2).contiguous().view(B, L, D)
        return self.W_o(out)
```

## Multi-Head Attention

多个注意力头并行，捕获不同维度的关系：

| 头 | 关注模式 |
|----|----------|
| Head 1 | 语法关系（主谓宾） |
| Head 2 | 指代消解（它→猫） |
| Head 3 | 位置邻近词 |
| Head 4 | 语义相似词 |

## 总结

Attention 的本质是 **动态加权平均**，权重由内容相似度决定。
""",
    },
    {
        "title": "Docker 多阶段构建实战：镜像缩小 90%",
        "category": "运维部署", "tags": "Docker,K8s,MLOps",
        "summary": "通过多阶段构建将 Node.js 应用镜像从 1.2GB 缩小到 120MB。",
        "content": """# Docker 多阶段构建实战

## 问题

一个简单的 Node.js 应用，单阶段构建的镜像：

```bash
$ docker images myapp
REPOSITORY   TAG       SIZE
myapp        latest    1.2GB   # 😱
```

## 解决方案：多阶段构建

```dockerfile
# ===== 阶段 1: 构建 =====
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --production=false
COPY . .
RUN npm run build

# ===== 阶段 2: 运行 =====
FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./

EXPOSE 3000
CMD ["node", "dist/main.js"]
```

## 效果对比

| 方案 | 镜像大小 | 构建时间 |
|------|----------|----------|
| 单阶段 | 1.2 GB | 45s |
| 多阶段 | 180 MB | 50s |
| 多阶段 + distroless | 120 MB | 52s |

## 进阶技巧

### 使用缓存挂载加速构建

```dockerfile
RUN --mount=type=cache,target=/root/.npm npm ci
```

### 安全扫描

```bash
docker scout cves myapp:latest
```

## 总结

多阶段构建是容器化的 **必备技能**，生产环境请始终使用。
""",
    },
    {
        "title": "PyTorch 2.0 torch.compile 性能实测",
        "category": "深度学习", "tags": "PyTorch,Deep Learning,MLOps",
        "summary": "实测 torch.compile 在不同模型上的加速效果，最高提速 3 倍。",
        "content": """# PyTorch 2.0 torch.compile 性能实测

## torch.compile 是什么？

PyTorch 2.0 引入的 JIT 编译器，一行代码即可获得显著加速：

```python
import torch

model = MyModel()
optimized_model = torch.compile(model)  # 就这一行！
```

## 实测环境

- GPU: NVIDIA A100 80GB
- PyTorch: 2.1.0
- CUDA: 12.1

## 测试结果

| 模型 | 原始 (img/s) | compiled (img/s) | 加速比 |
|------|-------------|------------------|--------|
| ResNet-50 | 1,200 | 2,800 | 2.3x |
| BERT-base | 450 | 980 | 2.2x |
| Stable Diffusion | 12 | 28 | 2.3x |
| LLaMA-7B (生成) | 45 tok/s | 135 tok/s | 3.0x |

## 常见问题

### Q: 编译时间很长怎么办？

```python
# 使用 reduce-overhead 模式
model = torch.compile(model, mode="reduce-overhead")
```

### Q: 某些算子不支持？

```python
# 使用 eager 回退
model = torch.compile(model, backend="eager")
```

## 结论

`torch.compile` 是 **免费的性能提升**，强烈建议在生产环境开启。
""",
    },
    {
        "title": "CSS Container Queries 终极指南",
        "category": "前端开发", "tags": "CSS,前端,TailwindCSS",
        "summary": "Container Queries 让组件真正实现响应式，不再依赖视口宽度。",
        "content": """# CSS Container Queries 终极指南

## 传统 Media Query 的痛点

```css
/* 基于视口，不是组件！ */
@media (max-width: 768px) {
  .card { flex-direction: column; }
}
```

卡片在侧边栏里可能不需要变成列布局。

## Container Query 解法

```css
.card-container {
  container-type: inline-size;
  container-name: card;
}

@container card (max-width: 400px) {
  .card { flex-direction: column; }
  .card-title { font-size: 14px; }
}
```

## 实战：自适应组件

```css
/* 定义容器 */
.sidebar { container: sidebar / inline-size; }

/* 组件自适应 */
@container sidebar (min-width: 300px) {
  .widget { grid-template-columns: 1fr 1fr; }
}

@container sidebar (max-width: 299px) {
  .widget { grid-template-columns: 1fr; }
}
```

## 浏览器支持

| 浏览器 | 支持版本 |
|--------|----------|
| Chrome | 105+ |
| Firefox | 110+ |
| Safari | 16+ |
| Edge | 105+ |

## 总结

Container Queries 是 CSS 近年 **最重要的特性之一**，让组件驱动的响应式设计成为现实。
""",
    },
    {
        "title": "LLM 微调实战：LoRA vs QLoRA 深度对比",
        "category": "NLP", "tags": "LLM,Deep Learning,PyTorch",
        "summary": "对比 LoRA 和 QLoRA 在不同硬件、不同模型规模下的微调效果与成本。",
        "content": """# LLM 微调实战：LoRA vs QLoRA 深度对比

## 背景

全参数微调 7B 模型需要 **4×A100 80GB**，成本高昂。参数高效微调（PEFT）是更实际的选择。

## LoRA 原理

在原始权重旁边插入低秩矩阵：

$$W' = W + BA$$

其中 $B \\in \\mathbb{R}^{d \\times r}$，$A \\in \\mathbb{R}^{r \\times d}$，$r \\ll d$。

```python
from peft import LoraConfig, get_peft_model

config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    task_type="CAUSAL_LM"
)

model = get_peft_model(base_model, config)
model.print_trainable_parameters()
# trainable params: 4,194,304 || all params: 6,742,609,920 || trainable%: 0.062%
```

## QLoRA：4-bit 量化 + LoRA

```python
from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)
```

## 性能对比

| 方法 | GPU 显存 | 训练速度 | 效果 |
|------|----------|----------|------|
| 全量微调 | 120 GB | 1x | 基准 |
| LoRA (r=16) | 48 GB | 1.2x | -0.5% |
| QLoRA (4-bit) | 18 GB | 0.8x | -1.2% |

## 推荐选择

- **有充足 GPU**：LoRA
- **单卡消费级**：QLoRA
- **追求极致效果**：全量微调
""",
    },
    {
        "title": "TypeScript 5.4 类型体操：递归类型实战",
        "category": "前端开发", "tags": "TypeScript,前端",
        "summary": "深入 TypeScript 类型系统，手写 DeepPartial、PathKeys 等高级工具类型。",
        "content": """# TypeScript 5.4 类型体操：递归类型实战

## DeepPartial

```typescript
type DeepPartial<T> = T extends object
  ? { [P in keyof T]?: DeepPartial<T[P]> }
  : T

// 使用
interface Config {
  db: { host: string; port: number }
  cache: { ttl: number }
}

const config: DeepPartial<Config> = {
  db: { host: "localhost" }  // port 可选 ✓
}
```

## PathKeys：获取嵌套对象的所有路径

```typescript
type PathKeys<T, K = keyof T> = K extends string
  ? T[K] extends object
    ? `${K}` | `${K}.${PathKeys<T[K]>}`
    : `${K}`
  : never

interface User {
  name: string
  address: {
    city: string
    zip: string
  }
}

type UserPaths = PathKeys<User>
// "name" | "address" | "address.city" | "address.zip"
```

## 条件类型 + infer

```typescript
type ReturnOf<T> = T extends (...args: any[]) => infer R ? R : never
type AsyncReturn<T> = T extends Promise<infer U> ? U : T

// 提取 Promise 内部类型
type Result = AsyncReturn<Promise<string>>  // string
```

## 实用工具类型

```typescript
// 必填字段
type RequiredKeys<T> = {
  [K in keyof T]-?: undefined extends T[K] ? never : K
}[keyof T]

// 只读深度冻结
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K]
}
```

## 总结

TypeScript 的类型系统是 **图灵完备的**，善用它可以极大提升代码安全性。
""",
    },
    {
        "title": "Kubernetes Pod 调度策略完全指南",
        "category": "运维部署", "tags": "K8s,Docker,MLOps",
        "summary": "详解 K8s 调度器工作原理：亲和性、反亲和性、污点容忍与优先级。",
        "content": """# Kubernetes Pod 调度策略完全指南

## 调度器工作流程

```
Pod 创建 → 过滤(Filter) → 打分(Score) → 绑定(Bind)
```

## Node Affinity

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-pod
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: gpu-type
            operator: In
            values: ["a100", "v100"]
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 80
        preference:
          matchExpressions:
          - key: zone
            operator: In
            values: ["us-east-1a"]
```

## Pod Anti-Affinity（分散部署）

```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchExpressions:
        - key: app
          operator: In
          values: ["web"]
      topologyKey: kubernetes.io/hostname
```

## Taints & Tolerations

```bash
# 给节点打污点
kubectl taint nodes node1 gpu=true:NoSchedule

# Pod 添加容忍
tolerations:
- key: "gpu"
  operator: "Equal"
  value: "true"
  effect: "NoSchedule"
```

## PriorityClass

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: critical
value: 1000000
globalDefault: false
description: "关键业务 Pod"
```

## 最佳实践

1. 生产服务使用 anti-affinity 分散
2. GPU 工作负载用 node affinity 固定
3. 设置合理的 resource requests
4. 使用 PriorityClass 保障核心服务
""",
    },
    {
        "title": "Rust 所有权系统深入理解",
        "category": "系统编程", "tags": "Rust,系统编程",
        "summary": "彻底搞懂 Rust 的所有权、借用与生命周期，告别编译器报错。",
        "content": """# Rust 所有权系统深入理解

## 核心规则

1. 每个值有且仅有一个 **所有者**
2. 所有者离开作用域时，值被 **drop**
3. 同一时间只能有一个 **可变引用** 或多个 **不可变引用**

## 所有权转移

```rust
fn main() {
    let s1 = String::from("hello");
    let s2 = s1;        // s1 的所有权转移到 s2
    // println!("{}", s1); // ❌ 编译错误：s1 已失效
    println!("{}", s2);    // ✅
}
```

## 借用与引用

```rust
fn calculate_length(s: &String) -> usize {  // 不可变借用
    s.len()
}

fn append(s: &mut String) {  // 可变借用
    s.push_str(" world");
}
```

## 生命周期

```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

## 常见陷阱

| 陷阱 | 原因 | 解决方案 |
|------|------|----------|
| use after move | 值已转移 | 使用 `.clone()` 或引用 |
| multiple mutable borrows | 同时多个可变引用 | 限制作用域 |
| dangling reference | 返回局部变量引用 | 返回所有权 |

## 总结

Rust 的所有权系统是 **零成本抽象** 的基石，理解它是写好 Rust 的关键。
""",
    },
    {
        "title": "Prometheus + Grafana 监控实战",
        "category": "运维部署", "tags": "MLOps,Docker,K8s",
        "summary": "从零搭建微服务监控体系：指标采集、告警规则、可视化大盘。",
        "content": """# Prometheus + Grafana 监控实战

## 架构

```
应用 (metrics endpoint)
    │
    ▼
Prometheus (拉取 + 存储)
    │
    ▼
Grafana (可视化)
    │
    ▼
Alertmanager (告警)
```

## 应用暴露指标

```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('http_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Request latency')

@app.middleware("http")
async def metrics_middleware(request, call_next):
    with REQUEST_LATENCY.time():
        response = await call_next(request)
    REQUEST_COUNT.labels(request.method, request.url.path).inc()
    return response
```

## Prometheus 配置

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ai-portal'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
```

## 告警规则

```yaml
groups:
  - name: ai-portal
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "错误率超过 10%"
```

## 总结

监控三板斧：**Metrics + Logs + Traces**，Prometheus 负责第一项。
""",
    },
    {
        "title": "LangChain Agent 从入门到实战",
        "category": "AI应用", "tags": "LangChain,LLM,Python",
        "summary": "用 LangChain 构建能使用工具的 AI Agent：搜索、计算、代码执行。",
        "content": """# LangChain Agent 从入门到实战

## 什么是 Agent？

Agent 是 LLM + 工具调用的组合，让模型能够 **自主决策** 使用哪些工具完成任务。

## 基础 Agent

```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")

tools = [
    Tool(name="Search", func=search_fn, description="搜索互联网"),
    Tool(name="Calculator", func=calc_fn, description="数学计算"),
    Tool(name="Python", func=python_fn, description="执行 Python 代码"),
]

agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

result = executor.invoke({"input": "2024年诺贝尔物理学奖得主是谁？"})
```

## 自定义工具

```python
from langchain.tools import tool

@tool
def query_database(sql: str) -> str:
    # 执行 SQL 查询数据库
    result = db.execute(sql)
    return str(result.fetchall())
```

## ReAct 循环

```
Thought: 我需要搜索 2024 诺贝尔奖信息
Action: Search("2024 Nobel Prize Physics")
Observation: John Hopfield 和 Geoffrey Hinton...
Thought: 我已经找到答案了
Final Answer: 2024年诺贝尔物理学奖得主是...
```

## 注意事项

1. 工具描述要清晰，直接影响 Agent 决策
2. 设置 `max_iterations` 防止死循环
3. 生产环境需要做输入校验和沙箱隔离
""",
    },
    {
        "title": "PostgreSQL 性能优化：查询调优实战",
        "category": "后端开发", "tags": "PostgreSQL,Python,后端",
        "summary": "通过 EXPLAIN ANALYZE、索引优化、查询重写将慢查询提速 100 倍。",
        "content": """# PostgreSQL 性能优化：查询调优实战

## EXPLAIN ANALYZE

```sql
EXPLAIN ANALYZE
SELECT u.username, COUNT(b.id) as blog_count
FROM users u
LEFT JOIN blogs b ON b.author_id = u.id
WHERE u.is_active = true
GROUP BY u.username
ORDER BY blog_count DESC
LIMIT 10;
```

输出：
```
Limit  (cost=1234.56..1234.78 rows=10) (actual time=45.2..45.5 rows=10 loops=1)
  ->  Sort  (cost=1234.56..1260.00 rows=10176) (actual time=45.1..45.3 rows=10)
        Sort Key: count(b.id) DESC
        ->  HashAggregate  (cost=980.00..1081.76 rows=10176) (actual time=40.2..42.1 rows=10176)
              ->  Hash Left Join  (cost=340.00..880.00 rows=10176) (actual time=12.5..35.8)
```

## 索引优化

```sql
-- 复合索引
CREATE INDEX idx_blogs_author_published
ON blogs (author_id, is_published)
WHERE is_published = true;

-- 覆盖索引（INCLUDE）
CREATE INDEX idx_blogs_covering
ON blogs (author_id)
INCLUDE (title, created_at, view_count);
```

## 查询重写技巧

### 避免 N+1

```sql
-- ❌ N+1
SELECT * FROM users;
-- 对每个 user:
SELECT COUNT(*) FROM blogs WHERE author_id = ?;

-- ✅ 一次查询
SELECT u.*, b.blog_count
FROM users u
LEFT JOIN (
  SELECT author_id, COUNT(*) as blog_count
  FROM blogs GROUP BY author_id
) b ON b.author_id = u.id;
```

## 性能对比

| 场景 | 优化前 | 优化后 |
|------|--------|--------|
| 用户列表+博客数 | 2.3s | 23ms |
| 全文搜索 | 1.8s | 15ms |
| 分页查询(第100页) | 5.2s | 8ms |

## 总结

**80% 的性能问题来自缺少合适的索引**，先 EXPLAIN 再优化。
""",
    },
    {
        "title": "React Server Components 深度解析",
        "category": "前端开发", "tags": "React,Next.js,TypeScript",
        "summary": "理解 RSC 的工作原理、使用场景和与客户端组件的协作方式。",
        "content": """# React Server Components 深度解析

## 核心概念

Server Components 在服务端渲染，**不会发送到客户端**：

```tsx
// 这个组件只在服务端运行
async function BlogList() {
  const posts = await db.query('SELECT * FROM posts')
  return (
    <ul>
      {posts.map(post => (
        <li key={post.id}>
          <h3>{post.title}</h3>
          <p>{post.summary}</p>
        </li>
      ))}
    </ul>
  )
}
```

## Server vs Client 组件

| 特性 | Server Component | Client Component |
|------|-----------------|------------------|
| 运行环境 | 服务端 | 客户端 |
| 能访问数据库 | ✅ | ❌ |
| 能用 useState | ❌ | ✅ |
| 能用浏览器 API | ❌ | ✅ |
| Bundle 大小 | 0 (不发送到客户端) | 正常 |

## 混合使用

```tsx
// Server Component
async function Page() {
  const data = await fetchData()
  return (
    <div>
      <h1>{data.title}</h1>
      <InteractiveButton />  {/* Client Component */}
    </div>
  )
}

// Client Component
'use client'
function InteractiveButton() {
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>
}
```

## 最佳实践

1. 默认用 Server Component
2. 只在需要交互时加 `'use client'`
3. 将 `'use client'` 边界尽量推到叶子节点
4. 通过 props 传递 Server Component 到 Client Component
""",
    },
    {
        "title": "Go 并发模式：从 goroutine 到 channel",
        "category": "系统编程", "tags": "Go,系统编程,后端",
        "summary": "掌握 Go 并发编程的核心模式：Fan-in、Fan-out、Pipeline、Worker Pool。",
        "content": """# Go 并发模式

## 基础：goroutine + channel

```go
func main() {
    ch := make(chan string)

    go func() {
        ch <- "hello from goroutine"
    }()

    msg := <-ch
    fmt.Println(msg)
}
```

## Worker Pool

```go
func worker(id int, jobs <-chan int, results chan<- int) {
    for j := range jobs {
        fmt.Printf("worker %d processing job %d\\n", id, j)
        time.Sleep(time.Second)
        results <- j * 2
    }
}

func main() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)

    // 启动 3 个 worker
    for w := 1; w <= 3; w++ {
        go worker(w, jobs, results)
    }

    // 发送任务
    for j := 1; j <= 9; j++ {
        jobs <- j
    }
    close(jobs)

    // 收集结果
    for r := 1; r <= 9; r++ {
        fmt.Println(<-results)
    }
}
```

## Fan-out / Fan-in

```go
func fanIn(inputs ...<-chan string) <-chan string {
    var wg sync.WaitGroup
    merged := make(chan string)

    for _, ch := range inputs {
        wg.Add(1)
        go func(c <-chan string) {
            defer wg.Done()
            for v := range c {
                merged <- v
            }
        }(ch)
    }

    go func() { wg.Wait(); close(merged) }()
    return merged
}
```

## select 多路复用

```go
select {
case msg := <-ch1:
    fmt.Println("from ch1:", msg)
case msg := <-ch2:
    fmt.Println("from ch2:", msg)
case <-time.After(3 * time.Second):
    fmt.Println("timeout")
}
```

## 总结

Go 的并发哲学：**Don't communicate by sharing memory; share memory by communicating.**
""",
    },
    {
        "title": "WebAssembly 入门：用 Rust 写前端",
        "category": "系统编程", "tags": "Rust,WebAssembly,前端",
        "summary": "用 Rust + wasm-pack 将高性能计算带到浏览器。",
        "content": """# WebAssembly 入门：用 Rust 写前端

## 为什么用 Rust + WASM？

| 场景 | JS | Rust+WASM |
|------|-----|-----------|
| 图像处理 | 120ms | 8ms |
| JSON 解析 | 45ms | 3ms |
| 加密计算 | 200ms | 12ms |

## 项目搭建

```bash
cargo install wasm-pack
wasm-pack new wasm-demo --template no-modules
```

## Rust 代码

```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn fibonacci(n: u32) -> u32 {
    match n {
        0 => 0,
        1 => 1,
        _ => fibonacci(n - 1) + fibonacci(n - 2),
    }
}

#[wasm_bindgen]
pub fn process_image(data: &[u8], width: u32, height: u32) -> Vec<u8> {
    // 图像处理逻辑（比 JS 快 15 倍）
    data.iter().map(|&p| 255 - p).collect()  // 简单反转
}
```

## 前端调用

```javascript
import init, { fibonacci, process_image } from './pkg/wasm_demo.js';

async function main() {
    await init();
    console.log(fibonacci(40));  // 极快！
}
```

## 适用场景

1. **图像/视频处理**：滤镜、编码解码
2. **加密算法**：哈希、加密解密
3. **游戏引擎**：物理计算
4. **科学计算**：矩阵运算

## 注意

WASM 不能直接操作 DOM，需要通过 JS 桥接。
""",
    },
    {
        "title": "设计系统构建实战：从 Token 到组件",
        "category": "前端开发", "tags": "TypeScript,CSS,TailwindCSS",
        "summary": "如何构建一套可维护的设计系统：Design Token、组件库、文档站。",
        "content": """# 设计系统构建实战

## Design Token

```typescript
// tokens.ts
export const tokens = {
  color: {
    primary: { 50: '#f0f9ff', 500: '#3b82f6', 900: '#1e3a5f' },
    neutral: { 50: '#fafafa', 500: '#737373', 900: '#171717' },
    semantic: {
      success: '#22c55e',
      warning: '#f59e0b',
      error: '#ef4444',
    }
  },
  spacing: { xs: '4px', sm: '8px', md: '16px', lg: '24px', xl: '32px' },
  radius: { sm: '4px', md: '8px', lg: '12px', full: '9999px' },
  typography: {
    fontFamily: { sans: 'Inter, system-ui', mono: 'JetBrains Mono' },
    fontSize: { sm: '14px', base: '16px', lg: '18px', xl: '24px' },
  }
}
```

## CSS 变量注入

```css
:root {
  --color-primary: #3b82f6;
  --color-bg: #ffffff;
  --color-text: #171717;
  --spacing-md: 16px;
  --radius-md: 8px;
}

[data-theme="dark"] {
  --color-bg: #0a0a0a;
  --color-text: #e5e5e5;
}
```

## 组件设计原则

1. **单一职责**：每个组件只做一件事
2. **可组合**：通过 slot/children 组合
3. **无障碍**：aria 属性 + 键盘导航
4. **主题感知**：使用 token 而非硬编码

## 文档站

```bash
# 使用 Storybook
npx storybook@latest init

# 或使用 VitePress
npm init vitepress
```

## 总结

设计系统的价值在于 **一致性** 和 **效率**。
""",
    },
    {
        "title": "机器学习特征工程实战手册",
        "category": "数据科学", "tags": "机器学习,Python,数据分析",
        "summary": "覆盖数值、类别、文本、时间序列特征的处理方法与代码示例。",
        "content": """# 机器学习特征工程实战手册

## 数值特征

### 标准化 & 归一化

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 对数变换（处理长尾分布）
import numpy as np
X_log = np.log1p(X)
```

### 分箱

```python
from sklearn.preprocessing import KBinsDiscretizer

binner = KBinsDiscretizer(n_bins=5, encode='ordinal', strategy='quantile')
X_binned = binner.fit_transform(X[['age']])
```

## 类别特征

```python
# One-Hot
pd.get_dummies(df, columns=['city'])

# Target Encoding
from category_encoders import TargetEncoder
encoder = TargetEncoder()
X_encoded = encoder.fit_transform(X['category'], y)
```

## 文本特征

```python
from sklearn.feature_extraction.text import TfidfVectorizer

tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
X_text = tfidf.fit_transform(df['text'])

# 更好的方案：Sentence Embeddings
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(df['text'].tolist())
```

## 时间特征

```python
df['hour'] = df['timestamp'].dt.hour
df['day_of_week'] = df['timestamp'].dt.dayofweek
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
df['month'] = df['timestamp'].dt.month
```

## 特征选择

```python
from sklearn.feature_selection import mutual_info_classif

mi_scores = mutual_info_classif(X, y)
top_features = np.argsort(mi_scores)[-20:]  # 取前 20
```

## 总结

**特征决定上限，模型只是逼近上限**。花 80% 时间在特征工程上。
""",
    },
    {
        "title": "网络安全入门：Web 渗透测试基础",
        "category": "网络安全", "tags": "Security,Python,后端",
        "summary": "常见 Web 漏洞类型、检测方法与防御措施（仅供授权测试）。",
        "content": """# 网络安全入门：Web 渗透测试基础

> ⚠️ 本文仅用于 **授权安全测试** 和 **教育目的**。未经授权的渗透测试是违法行为。

## OWASP Top 10

| 排名 | 漏洞类型 | 危险等级 |
|------|----------|----------|
| 1 | Broken Access Control | 🔴 高 |
| 2 | Cryptographic Failures | 🔴 高 |
| 3 | Injection | 🔴 高 |
| 4 | Insecure Design | 🟡 中 |
| 5 | Security Misconfiguration | 🟡 中 |

## SQL 注入防御

```python
# ❌ 危险
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ 参数化查询
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

## XSS 防御

```python
# 输出编码
from markupsafe import escape
safe_html = escape(user_input)

# CSP Header
response.headers['Content-Security-Policy'] = "default-src 'self'"
```

## CSRF 防御

```python
from fastapi_csrf_protect import CsrfProtect

@app.post("/api/action")
async def action(csrf_protect: CsrfProtect = Depends()):
    await csrf_protect.validate_csrf(request)
```

## 安全检查清单

- [ ] 所有输入做验证和消毒
- [ ] 使用参数化查询
- [ ] 启用 HTTPS
- [ ] 设置安全响应头
- [ ] 实施速率限制
- [ ] 密码使用 bcrypt/argon2 哈希
- [ ] 敏感操作需要二次验证

## 总结

安全不是功能，是 **基础属性**。从第一行代码就要考虑。
""",
    },
]

# ─── 新闻内容模板 ────────────────────────────────────────────
NEWS_TEMPLATES = [
    {"title": "OpenAI 发布 GPT-5：多模态能力再进化",
     "category": "产品发布", "tags": "AI,GPT,OpenAI",
     "summary": "GPT-5 支持原生图像、音频、视频输入，推理能力大幅提升。",
     "content": """# GPT-5 正式发布

## 核心升级

- **原生多模态**：支持图像、音频、视频输入
- **推理能力**：数学推理提升 40%，代码生成提升 25%
- **上下文窗口**：扩展到 256K tokens
- **价格**：与 GPT-4 Turbo 持平

## 行业影响

GPT-5 的发布标志着 AI 进入 **全能模型** 时代。多个行业将受到冲击：

1. 翻译行业
2. 客服行业
3. 初级编程岗位

> "这是 AGI 之路的重要里程碑" —— Sam Altman
"""},
    {"title": "DeepSeek-V3 开源：国产大模型新突破",
     "category": "技术突破", "tags": "DeepSeek,LLM,开源",
     "summary": "DeepSeek-V3 在多项基准测试中超越 GPT-4，完全开源。",
     "content": """# DeepSeek-V3 开源发布

## 亮点

- **参数量**：671B MoE（激活 37B）
- **训练成本**：仅 $5.57M（2048 GPU，2个月）
- **性能**：MMLU 88.5，HumanEval 89.0

## 开源内容

| 组件 | 开源 |
|------|------|
| 模型权重 | ✅ |
| 训练代码 | ✅ |
| 数据处理 | ✅ |
| 评估套件 | ✅ |

## 对行业的影响

DeepSeek 证明了 **开源可以与闭源竞争**，这对整个 AI 生态是重大利好。
"""},
    {"title": "欧盟 AI 法案正式生效：影响几何？",
     "category": "政策法规", "tags": "AI,政策,欧盟",
     "summary": "欧盟 AI 法案（AI Act）正式生效，对高风险 AI 系统提出严格要求。",
     "content": """# 欧盟 AI 法案解读

## 核心要点

### 风险分级

| 风险等级 | 要求 | 示例 |
|----------|------|------|
| 不可接受 | 禁止 | 社会信用评分 |
| 高风险 | 严格监管 | 医疗诊断 AI |
| 有限风险 | 透明义务 | 聊天机器人 |
| 最小风险 | 无限制 | 垃圾邮件过滤 |

### 对大模型的影响

- 必须披露训练数据来源
- 需要进行安全评估
- 生成内容必须标注 AI 生成

## 企业应对建议

1. 盘点现有 AI 系统
2. 进行风险评估
3. 建立合规流程
4. 准备技术文档
"""},
    {"title": "Anthropic 完成 50 亿美元融资",
     "category": "融资并购", "tags": "Anthropic,融资,AI",
     "summary": "Anthropic 完成新一轮融资，估值达到 600 亿美元。",
     "content": """# Anthropic 融资 50 亿美元

## 融资详情

- **金额**：50 亿美元
- **估值**：600 亿美元
- **领投**：Google, Salesforce
- **用途**：Claude 模型研发、算力建设

## Claude 模型进展

| 模型 | 发布时间 | 特点 |
|------|----------|------|
| Claude 3 Opus | 2024.03 | 最强推理 |
| Claude 3.5 Sonnet | 2024.06 | 性价比之王 |
| Claude 4 | 2025.11 | 多模态原生 |

## 行业格局

AI 赛道持续火热，头部公司融资不断。竞争格局：

- **OpenAI** ↔ **Anthropic** ↔ **Google** 三足鼎立
- 开源阵营 **Meta** + **Mistral** + **DeepSeek** 紧追不舍
"""},
    {"title": "ICLR 2026 最佳论文揭晓",
     "category": "学术进展", "tags": "学术,机器学习,Deep Learning",
     "summary": "ICLR 2026 最佳论文关注高效训练与模型对齐。",
     "content": """# ICLR 2026 最佳论文

## 获奖论文

### 最佳论文

**Efficient Training of Language Models with Linear Attention**

- 提出线性注意力新架构
- 训练速度提升 3x，效果不降
- 已开源实现

### 最佳论文亚军

**Constitutional AI: Better Alignment through Self-Improvement**

- 模型自我改进对齐方法
- 减少人工标注需求 90%

## 趋势观察

1. **效率优化**成为主流
2. **对齐研究**持续升温
3. **多模态**论文数量翻倍
"""},
    {"title": "GitHub Copilot 月活突破 2000 万",
     "category": "行业动态", "tags": "GitHub,AI,开发工具",
     "summary": "GitHub Copilot 用户数持续增长，AI 编程助手成为开发者标配。",
    "content": """# GitHub Copilot 里程碑

## 关键数据

- **月活用户**：2000 万+
- **企业客户**：10 万+
- **代码接受率**：35%
- **生产力提升**：55%（GitHub 官方数据）

## 新功能

1. **Copilot Workspace**：从 issue 到 PR 全流程
2. **Copilot Chat**：代码问答
3. **Copilot CLI**：命令行助手

## 开发者调查

| 使用场景 | 占比 |
|----------|------|
| 代码补全 | 78% |
| 写测试 | 45% |
| 代码解释 | 52% |
| Debug | 38% |
"""},
    {"title": "NVIDIA H200 量产交付：AI 算力再升级",
     "category": "产品发布", "tags": "NVIDIA,硬件,AI",
     "summary": "NVIDIA H200 GPU 开始量产，141GB HBM3e 显存成为新标杆。",
    "content": """# NVIDIA H200 量产

## 规格对比

| 参数 | H100 | H200 |
|------|------|------|
| 显存 | 80GB HBM3 | 141GB HBM3e |
| 带宽 | 3.35 TB/s | 4.8 TB/s |
| FP16 算力 | 989 TFLOPS | 989 TFLOPS |
| 功耗 | 700W | 700W |

## 对大模型训练的影响

- **LLaMA-70B**：可在单节点（8卡）完成推理
- **训练成本**：降低约 20%
- **推理吞吐**：提升 45%

## 价格与供应

- 单卡售价：约 $30,000
- 交货周期：6-8 周
- 主要客户：云厂商、大模型公司
"""},
    {"title": "斯坦福发布 2026 AI 指数报告",
     "category": "学术进展", "tags": "AI,学术,报告",
     "summary": "斯坦福大学发布年度 AI 发展报告，中国 AI 论文数量全球第一。",
    "content": """# 斯坦福 2026 AI 指数报告

## 核心发现

### 论文数量

| 国家 | 占比 |
|------|------|
| 中国 | 28% |
| 美国 | 22% |
| 欧盟 | 18% |

### 投资趋势

- 2025 年全球 AI 投资：**$1800 亿**
- 同比增长：**45%**
- 最大单笔：OpenAI $100 亿

### 关键趋势

1. **多模态模型**成为主流
2. **AI Agent** 框架爆发
3. **开源模型**性能追平闭源
4. **AI 安全**研究投入翻倍
"""},
    {"title": "百度文心一言 4.0 发布",
     "category": "产品发布", "tags": "百度,LLM,AI",
     "summary": "百度发布文心一言 4.0，中文能力全面超越 GPT-4。",
    "content": """# 文心一言 4.0 发布

## 核心升级

- **参数规模**：万亿级
- **中文理解**：超越 GPT-4
- **代码生成**：HumanEval 85.0
- **数学推理**：GSM8K 92.0

## 特色能力

1. **中文古文理解**：准确率 95%+
2. **方言识别**：支持 20+ 种方言
3. **中国法律知识**：专业级水平

## API 定价

| 模型 | 输入 | 输出 |
|------|------|------|
| 文心 4.0 | ¥0.12/千tokens | ¥0.12/千tokens |
| 文心 3.5 | ¥0.008/千tokens | ¥0.008/千tokens |

## 生态

- 开发者数量：200 万+
- 应用数量：10 万+
"""},
    {"title": "AI 芯片创业公司 Cerebras 上市",
     "category": "融资并购", "tags": "AI,芯片,IPO",
     "summary": "AI 芯片公司 Cerebras 在纳斯达克上市，首日市值突破 100 亿美元。",
    "content": """# Cerebras IPO

## 上市详情

- **交易所**：纳斯达克
- **股票代码**：CBRS
- **发行价**：$42
- **首日收盘**：$68（+62%）
- **市值**：$120 亿

## 核心产品

WSE-3（晶圆级引擎）：
- **芯片面积**：46,225 mm²（比 GPU 大 56 倍）
- **核心数**：900,000
- **内存**：44GB SRAM

## 市场前景

AI 芯片市场预计 2027 年达到 $800 亿，Cerebras 的差异化路线获得资本市场认可。
"""},
    {"title": "Meta 开源 LLaMA-4：405B 参数",
     "category": "技术突破", "tags": "Meta,LLM,开源",
     "summary": "Meta 开源 LLaMA-4 系列模型，405B 版本性能媲美 GPT-4。",
    "content": """# LLaMA-4 开源

## 模型规格

| 版本 | 参数 | 许可 |
|------|------|------|
| LLaMA-4-8B | 8B | 开源 |
| LLaMA-4-70B | 70B | 开源 |
| LLaMA-4-405B | 405B | 开源 |

## 性能表现

- MMLU：89.3（GPT-4: 88.7）
- HumanEval：87.5（GPT-4: 86.6）
- GSM8K：95.2（GPT-4: 94.8）

## 社区反响

> "这是开源 AI 的历史性时刻" —— Yann LeCun

## 使用方式

```python
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-4-405b",
    device_map="auto",
    torch_dtype=torch.bfloat16
)
```
"""},
    {"title": "2026 年 AI 开发者薪资报告",
     "category": "行业动态", "tags": "AI,职业,薪资",
     "summary": "AI 工程师平均年薪突破 50 万，大模型方向薪资最高。",
    "content": """# 2026 AI 开发者薪资报告

## 薪资分布（年薪，万元）

| 方向 | 初级 | 中级 | 高级 |
|------|------|------|------|
| 大模型研发 | 30-50 | 50-80 | 80-150 |
| AI 应用开发 | 20-35 | 35-60 | 60-100 |
| 数据工程 | 18-30 | 30-50 | 50-80 |
| MLOps | 20-35 | 35-55 | 55-90 |

## 热门技能

1. **LLM 微调与部署**：需求增长 200%
2. **RAG 系统开发**：需求增长 180%
3. **AI Agent 开发**：需求增长 300%
4. **多模态模型**：需求增长 150%

## 求职建议

- 掌握至少一个主流框架（LangChain / LlamaIndex）
- 有开源项目经验加分明显
- 关注 AI 安全与对齐方向
"""},
    {"title": "特斯拉 Optimus 机器人开始量产",
     "category": "行业动态", "tags": "机器人,AI,特斯拉",
     "summary": "特斯拉人形机器人 Optimus 开始小批量量产，售价 2 万美元。",
    "content": """# Optimus 量产

## 产品规格

- **身高**：1.72m
- **体重**：57kg
- **负载**：20kg
- **续航**：5 小时
- **售价**：$20,000

## 应用场景

1. 工厂搬运
2. 仓储物流
3. 家庭服务（未来）

## 技术亮点

- 基于 FSD 的视觉系统
- 端到端神经网络控制
- 自然语言交互

## 市场预期

马斯克预计 2027 年产能达到 10 万台/年。
"""},
    {"title": "Claude 4 发布：Anthropic 的王牌",
     "category": "产品发布", "tags": "Anthropic,Claude,AI",
     "summary": "Anthropic 发布 Claude 4，在编程和推理任务上全面领先。",
    "content": """# Claude 4 发布

## 核心能力

- **上下文窗口**：500K tokens
- **编程能力**：SWE-bench 72.0%
- **推理能力**：GPQA 65.0%

## 与竞品对比

| 基准 | Claude 4 | GPT-5 | Gemini Ultra |
|------|----------|-------|--------------|
| MMLU | 90.1 | 89.5 | 90.4 |
| HumanEval | 92.0 | 90.5 | 88.0 |
| SWE-bench | 72.0 | 68.0 | 65.0 |

## 定价

- **输入**：$15/百万 tokens
- **输出**：$75/百万 tokens
- **Haiku 版本**：性价比之选

## API 使用

```python
import anthropic

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-4",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)
```
"""},
    {"title": "中国 AI 产业规模突破万亿",
     "category": "行业动态", "tags": "AI,产业,中国",
     "summary": "2025 年中国 AI 产业规模达到 1.2 万亿元，同比增长 35%。",
    "content": """# 中国 AI 产业万亿规模

## 核心数据

- **产业规模**：1.2 万亿元
- **同比增长**：35%
- **企业数量**：4,500+
- **从业人员**：50 万+

## 细分领域

| 领域 | 规模（亿元） | 占比 |
|------|-------------|------|
| AI 芯片 | 2,500 | 21% |
| 大模型 | 1,800 | 15% |
| 智能驾驶 | 2,000 | 17% |
| AI 应用 | 3,500 | 29% |
| 其他 | 2,200 | 18% |

## 政策支持

- 国家级 AI 创新中心：15 个
- AI 产业园区：50+
- 专项基金规模：500 亿+
"""},
    {"title": "Cursor IDE 用户突破 500 万",
     "category": "产品发布", "tags": "开发工具,AI,IDE",
     "summary": "AI 编程 IDE Cursor 用户数突破 500 万，成为最受欢迎的 AI 开发工具。",
    "content": """# Cursor 500 万用户

## 核心功能

- **AI 代码补全**：上下文感知
- **代码编辑**：自然语言描述修改
- **多文件编辑**：跨文件重构
- **Chat**：代码问答

## 用户增长

| 时间 | 用户数 |
|------|--------|
| 2024.01 | 10 万 |
| 2024.06 | 100 万 |
| 2025.01 | 300 万 |
| 2026.01 | 500 万 |

## 定价

- **免费版**：基础功能
- **Pro**：$20/月
- **Business**：$40/月

## 开发者反馈

> "Cursor 让我的编码效率提升了 3 倍" —— 多位开发者
"""},
    {"title": "量子计算突破：1000 逻辑量子比特",
     "category": "技术突破", "tags": "量子计算,科技",
     "summary": "Google 实现 1000 逻辑量子比特里程碑，量子纠错取得重大进展。",
    "content": """# 量子计算里程碑

## 突破详情

- **逻辑量子比特**：1,000
- **错误率**：10^-6
- **相干时间**：10 秒

## 意义

这是量子计算从 **实验** 走向 **实用** 的关键一步：

1. 药物分子模拟变得可行
2. 密码学面临挑战
3. 优化问题求解加速

## 时间表

| 年份 | 目标 |
|------|------|
| 2026 | 1,000 逻辑量子比特 ✅ |
| 2028 | 10,000 逻辑量子比特 |
| 2030 | 实用量子优势 |

## 专家观点

> "我们正在见证量子计算的 iPhone 时刻" —— Google Quantum AI 负责人
"""},
    {"title": "AWS 发布 Trainium3 AI 芯片",
     "category": "产品发布", "tags": "AWS,AI,芯片",
     "summary": "AWS 第三代 AI 训练芯片 Trainium3 性能提升 4 倍。",
     "content": """# AWS Trainium3

## 规格

- 性能：比 Trainium2 快 4 倍
- 能效：提升 2 倍
- 互联：UltraServer 支持 64 芯片互联

## 与竞品对比

| 指标 | Trainium3 | H100 | TPU v5 |
|------|-----------|------|--------|
| FP16 算力 | 1200 TFLOPS | 989 TFLOPS | 459 TFLOPS |
| 显存 | 192GB HBM3e | 80GB HBM3 | 95GB HBM2e |

## 定价

预计比 H100 便宜 30-40%。
"""},
    {"title": "全球 AI 监管趋势报告",
     "category": "政策法规", "tags": "AI,监管,政策",
     "summary": "全球已有 60+ 国家出台 AI 相关法规，监管趋严。",
     "content": """# 全球 AI 监管趋势

## 各国进展

| 国家/地区 | 进展 |
|-----------|------|
| 欧盟 | AI Act 已生效 |
| 美国 | 行政令 + 各州立法 |
| 中国 | 生成式 AI 管理办法 |
| 英国 | 沙盒监管模式 |
| 日本 | 柔性监管 |

## 企业合规建议

1. 建立 AI 伦理委员会
2. 进行算法影响评估
3. 确保数据合规
4. 建立应急预案
"""},
    {"title": "AI Agent 框架大爆发：2026 年生态盘点",
     "category": "技术突破", "tags": "AI,Agent,LangChain",
     "summary": "AutoGPT、CrewAI、LangGraph 等 Agent 框架百花齐放。",
     "content": """# AI Agent 框架生态盘点

## 主流框架

| 框架 | 特点 | GitHub Stars |
|------|------|-------------|
| LangGraph | 图状态机 | 15K+ |
| CrewAI | 多 Agent 协作 | 20K+ |
| AutoGPT | 自主任务执行 | 160K+ |
| MetaGPT | 软件开发 Agent | 40K+ |

## 应用场景

1. 自动化工作流
2. 代码生成与审查
3. 数据分析报告
4. 客户服务

## 未来趋势

- 多模态 Agent
- 长期记忆
- 工具学习
- 安全对齐
"""},
]

# ─── 产品内容模板 ────────────────────────────────────────────
PRODUCT_TEMPLATES = [
    {"title": "DeepChat - 开源 AI 对话助手",
     "category": "聊天机器人", "tags": "AI,聊天机器人,开源",
     "summary": "支持多模型、多轮对话、插件系统的开源 AI 对话平台。",
     "content": """# DeepChat

> 下一代开源 AI 对话助手

## 特性

- 🤖 支持 GPT-4 / Claude / DeepSeek 等多模型
- 🔌 插件系统：联网搜索、代码执行、文件分析
- 💬 多轮对话 + 上下文记忆
- 🎨 自定义主题与人设

## 快速开始

```bash
docker run -p 3000:3000 deepchat/deepchat
```

## 技术栈

- 前端：Next.js + TypeScript
- 后端：FastAPI + Redis
- 数据库：PostgreSQL

## 截图

![DeepChat 界面](https://picsum.photos/seed/deepchat/800/400)

## GitHub

⭐ Star 数：12,000+
"""},
    {"title": "DataFlow - 可视化数据管道",
     "category": "数据分析", "tags": "数据分析,ETL,SaaS",
     "summary": "拖拽式数据管道构建工具，支持 100+ 数据源。",
     "content": """# DataFlow

> 让数据管道构建像搭积木一样简单

## 核心功能

- **可视化编辑器**：拖拽式 DAG 构建
- **100+ 连接器**：数据库、API、文件、云存储
- **实时监控**：数据质量、延迟、成本
- **调度引擎**：Cron + 事件驱动

## 支持的数据源

| 类型 | 数据源 |
|------|--------|
| 数据库 | MySQL, PostgreSQL, MongoDB, Redis |
| 云存储 | S3, GCS, Azure Blob |
| API | REST, GraphQL, gRPC |
| 文件 | CSV, JSON, Parquet, Excel |

## 定价

- **免费版**：5 个管道
- **专业版**：$99/月
- **企业版**：联系销售
"""},
    {"title": "ImageAI - AI 图像生成平台",
     "category": "图像生成", "tags": "AI,图像生成,SaaS",
     "summary": "基于 Stable Diffusion 的图像生成平台，支持文字生成、图像编辑。",
     "content": """# ImageAI

> 一句话生成专业级图像

## 功能

- **文生图**：输入描述，生成图像
- **图生图**：上传参考图，风格迁移
- **局部编辑**：选区编辑，精确控制
- **批量生成**：一次生成 100+ 变体

## 模型支持

| 模型 | 特点 |
|------|------|
| SDXL | 通用高质量 |
| DALL-E 3 | 文字理解强 |
| Midjourney | 艺术风格 |

## API

```python
import imageai

client = imageai.Client("your-api-key")
result = client.generate(
    prompt="一只穿着宇航服的猫在月球上",
    model="sdxl",
    size="1024x1024"
)
result.save("cat_on_moon.png")
```
"""},
    {"title": "CodeReview AI - 自动代码审查",
     "category": "AI工具", "tags": "AI,代码审查,开发工具",
     "summary": "AI 驱动的代码审查工具，自动发现 Bug、安全漏洞和代码异味。",
     "content": """# CodeReview AI

> 让 AI 帮你做 Code Review

## 功能

- **Bug 检测**：空指针、资源泄漏、竞态条件
- **安全扫描**：SQL 注入、XSS、敏感信息泄露
- **代码异味**：重复代码、过长函数、复杂度
- **最佳实践**：命名规范、设计模式建议

## 集成

- GitHub PR 自动评论
- GitLab MR 自动审查
- VS Code 实时提示
- CLI 工具

## 准确率

| 类型 | 准确率 | 召回率 |
|------|--------|--------|
| Bug | 85% | 78% |
| 安全漏洞 | 92% | 85% |
| 代码异味 | 88% | 82% |

## 定价

- **开源项目**：免费
- **个人版**：$15/月
- **团队版**：$50/月/人
"""},
    {"title": "MindMap AI - 智能思维导图",
     "category": "AI工具", "tags": "AI,思维导图,效率工具",
     "summary": "AI 自动生成思维导图，支持文档导入、语音输入。",
     "content": """# MindMap AI

> 从想法到导图，只需一句话

## 核心功能

- **AI 生成**：输入主题，自动生成完整思维导图
- **文档导入**：上传 PDF/Word，自动提取结构
- **语音输入**：说出想法，实时生成节点
- **协作编辑**：多人实时编辑

## 使用场景

1. **头脑风暴**：快速发散思维
2. **知识整理**：构建知识体系
3. **项目规划**：任务分解
4. **会议记录**：自动生成会议纪要导图

## 定价

- **免费版**：3 个导图
- **Pro**：$9.9/月
- **团队**：$29.9/月/人
"""},
    {"title": "ChatBase - 企业级 RAG 平台",
     "category": "SaaS平台", "tags": "AI,RAG,企业服务",
     "summary": "5 分钟搭建企业知识库问答机器人，支持多种文档格式。",
     "content": """# ChatBase

> 企业知识库 + AI 问答 = ChatBase

## 核心价值

- 上传文档 → 自动构建知识库
- 员工提问 → AI 精准回答
- 5 分钟搭建，0 代码

## 支持的文档格式

- PDF, Word, Excel, PPT
- 网页爬取
- Confluence, Notion, SharePoint
- API 数据源

## 技术架构

```
文档上传 → 解析分块 → 向量化 → ChromaDB
用户提问 → 检索 → Rerank → LLM 生成
```

## 客户案例

| 公司 | 场景 | 效果 |
|------|------|------|
| 某银行 | 客服知识库 | 效率 +60% |
| 某医院 | 病历检索 | 准确率 95% |
| 某电商 | 商品问答 | 转化率 +25% |
"""},
    {"title": "VoiceClone - AI 语音克隆",
     "category": "AI工具", "tags": "AI,语音,语音克隆",
     "summary": "5 分钟音频即可克隆任意声音，支持多语言合成。",
     "content": """# VoiceClone

> 你的声音，AI 来演绎

## 功能

- **声音克隆**：5 分钟音频 → 完整声音模型
- **多语言**：支持 20+ 种语言
- **情感控制**：开心、悲伤、愤怒、平静
- **实时合成**：延迟 < 200ms

## 使用场景

1. 有声读物制作
2. 视频配音
3. 客服语音
4. 游戏 NPC

## 技术参数

| 指标 | 数值 |
|------|------|
| 相似度 | 95%+ |
| 采样率 | 48kHz |
| 合成速度 | 50x 实时 |
| 延迟 | < 200ms |

## 定价

- **基础版**：$29/月（10 小时）
- **专业版**：$99/月（100 小时）
- **企业版**：定制
"""},
    {"title": "AutoML Studio - 零代码机器学习",
     "category": "AI工具", "tags": "AI,AutoML,机器学习",
     "summary": "拖拽式机器学习平台，无需编码即可训练和部署模型。",
     "content": """# AutoML Studio

> 不写代码，也能做机器学习

## 功能

- **自动特征工程**：智能特征提取
- **模型选择**：自动比较 20+ 算法
- **超参调优**：贝叶斯优化
- **一键部署**：生成 REST API

## 支持的任务类型

| 类型 | 算法 |
|------|------|
| 分类 | XGBoost, LightGBM, 随机森林 |
| 回归 | 线性回归, SVR, 神经网络 |
| 聚类 | K-Means, DBSCAN |
| 时序 | Prophet, ARIMA, LSTM |

## 定价

- **免费版**：10 次实验
- **Pro**：$49/月
- **企业版**：$199/月/人
"""},
    {"title": "DocAI - 智能文档处理平台",
     "category": "AI工具", "tags": "AI,OCR,文档处理",
     "summary": "AI 驱动的文档识别、提取、分类平台。",
     "content": """# DocAI

> 让文档处理自动化

## 功能

- **OCR 识别**：手写体、印刷体、表格
- **信息提取**：发票、合同、身份证
- **文档分类**：自动归档
- **智能审核**：异常检测

## 准确率

| 文档类型 | 准确率 |
|----------|--------|
| 印刷体 | 99.5% |
| 手写体 | 95.0% |
| 表格 | 98.0% |
| 发票 | 99.0% |

## 集成

- SAP, Oracle, 用友
- 钉钉, 飞书, 企业微信
- 自定义 API

## 定价

- **按量**：¥0.1/页
- **包月**：¥999/月（10,000 页）
"""},
    {"title": "SmartScheduler - AI 排班系统",
     "category": "SaaS平台", "tags": "AI,排班,企业管理",
     "summary": "AI 智能排班，考虑员工偏好、法规合规、业务预测。",
     "content": """# SmartScheduler

> AI 让排班不再是噩梦

## 核心功能

- **智能排班**：考虑 20+ 约束条件
- **需求预测**：基于历史数据预测客流量
- **员工偏好**：员工可提交排班偏好
- **合规检查**：自动检查劳动法合规

## 约束条件

1. 员工可用时间
2. 最大连续工作天数
3. 最小休息间隔
4. 技能匹配
5. 成本优化

## 客户效果

| 指标 | 改善 |
|------|------|
| 排班时间 | -80% |
| 员工满意度 | +35% |
| 人力成本 | -15% |

## 定价

- **基础版**：¥299/月（50 人）
- **专业版**：¥699/月（200 人）
- **企业版**：定制
"""},
    {"title": "翻译猫 - AI 翻译平台",
     "category": "AI工具", "tags": "AI,翻译,NLP",
     "summary": "支持 100+ 种语言的 AI 翻译平台，专业领域翻译准确率 95%。",
     "content": """# 翻译猫

> 超越 Google 翻译的专业级翻译

## 优势

- **专业领域**：法律、医疗、技术文档
- **术语管理**：自定义术语库
- **翻译记忆**：历史翻译复用
- **团队协作**：翻译项目管理

## 支持语言

- 100+ 种语言
- 中英日韩法德西
- 小语种支持

## API

```python
from transcat import Client

client = Client("api-key")
result = client.translate(
    text="Hello World",
    source="en",
    target="zh",
    domain="tech"  # 专业领域
)
```

## 定价

- **免费**：10 万字符/月
- **Pro**：¥99/月
- **企业**：¥499/月
"""},
    {"title": "AI Resume - 智能简历优化",
     "category": "AI工具", "tags": "AI,简历,求职",
     "summary": "AI 分析职位 JD，自动优化简历内容和格式。",
     "content": """# AI Resume

> 让简历脱颖而出

## 功能

- **JD 分析**：提取关键技能和要求
- **简历优化**：匹配 JD 调整内容
- **格式美化**：专业模板库
- **ATS 适配**：确保通过简历筛选系统

## 工作流程

1. 上传简历
2. 粘贴目标职位 JD
3. AI 分析匹配度
4. 生成优化建议
5. 一键导出

## 效果

| 指标 | 改善 |
|------|------|
| 简历通过率 | +60% |
| 面试邀请率 | +40% |
| 匹配度 | 85% → 95% |

## 定价

- **单次**：¥19.9
- **月卡**：¥49.9（无限次）
"""},
    {"title": "DataLabel - AI 数据标注平台",
     "category": "AI工具", "tags": "AI,数据标注,机器学习",
     "summary": "AI 辅助数据标注，支持图像、文本、音频多模态标注。",
     "content": """# DataLabel

> AI 辅助的数据标注平台

## 功能

- **智能预标注**：AI 先标，人工修正
- **多人协作**：标注 + 审核流程
- **质量控制**：一致性检查、抽检
- **多模态**：图像、文本、音频、视频

## 效率对比

| 方案 | 标注速度 | 准确率 |
|------|----------|--------|
| 纯人工 | 100 条/小时 | 95% |
| AI 辅助 | 500 条/小时 | 98% |

## 定价

- **免费版**：1000 条/月
- **Pro**：¥199/月
- **企业**：定制
"""},
    {"title": "FlowBuilder - 低代码工作流平台",
     "category": "SaaS平台", "tags": "低代码,自动化,SaaS",
     "summary": "拖拽式工作流构建，连接 200+ 应用，零代码实现业务自动化。",
     "content": """# FlowBuilder

> 让业务自动化像搭积木

## 功能

- **可视化编辑**：拖拽构建工作流
- **200+ 连接器**：钉钉、飞书、微信、ERP
- **条件分支**：复杂业务逻辑
- **定时触发**：Cron 表达式

## 应用场景

1. 审批流程自动化
2. 数据同步
3. 消息通知
4. 报表生成

## 定价

- **免费版**：5 个工作流
- **Pro**：¥99/月
- **企业**：¥499/月
"""},
    {"title": "API Gateway Pro - API 管理平台",
     "category": "SaaS平台", "tags": "API,网关,微服务",
     "summary": "企业级 API 网关：限流、鉴权、监控、文档一站式管理。",
     "content": """# API Gateway Pro

> 企业级 API 管理

## 功能

- **流量控制**：限流、熔断、降级
- **认证鉴权**：OAuth2、JWT、API Key
- **监控告警**：实时 QPS、延迟、错误率
- **文档管理**：自动生成 API 文档

## 性能

- 延迟：< 5ms
- 吞吐：100K QPS
- 可用性：99.99%

## 定价

- **社区版**：免费
- **企业版**：¥2,999/月
"""},
    {"title": "TestAI - AI 自动化测试平台",
     "category": "AI工具", "tags": "AI,测试,自动化",
     "summary": "AI 驱动的自动化测试：自然语言编写测试用例，自动修复失败用例。",
     "content": """# TestAI

> AI 让测试更简单

## 功能

- **自然语言测试**：用中文描述测试步骤
- **自愈测试**：UI 变更自动适配
- **视觉回归**：截图对比检测 UI 变化
- **API 测试**：自动生成测试数据

## 效率提升

| 指标 | 传统 | TestAI |
|------|------|--------|
| 用例编写 | 2 小时 | 10 分钟 |
| 维护成本 | 高 | 低 |
| 覆盖率 | 60% | 90% |

## 定价

- **免费版**：50 用例
- **Pro**：¥299/月
- **企业**：¥999/月
"""},
    {"title": "CloudIDE - 云端开发环境",
     "category": "SaaS平台", "tags": "IDE,云开发,SaaS",
     "summary": "浏览器内的完整开发环境，预配置 50+ 技术栈。",
     "content": """# CloudIDE

> 随时随地写代码

## 功能

- **即时启动**：3 秒创建开发环境
- **50+ 技术栈**：预配置模板
- **实时协作**：多人同时编辑
- **终端访问**：完整 Linux 环境

## 支持的语言

Python, JavaScript, TypeScript, Go, Rust, Java, C++, Ruby, PHP

## 定价

- **免费版**：2 个环境
- **Pro**：$19/月
- **团队**：$39/月/人
"""},
    {"title": "LogInsight - 智能日志分析平台",
     "category": "数据分析", "tags": "日志,监控,数据分析",
     "summary": "AI 驱动的日志分析：异常检测、根因分析、智能告警。",
     "content": """# LogInsight

> 让日志会说话

## 功能

- **日志采集**：支持 100+ 数据源
- **AI 异常检测**：自动发现异常模式
- **根因分析**：快速定位问题根因
- **智能告警**：减少告警疲劳

## 效果

| 指标 | 改善 |
|------|------|
| 故障发现时间 | -80% |
| 根因定位时间 | -70% |
| 告警噪音 | -60% |

## 定价

- **基础版**：¥499/月
- **专业版**：¥1,499/月
- **企业版**：定制
"""},
    {"title": "FormAI - 智能表单构建器",
     "category": "AI工具", "tags": "AI,表单,SaaS",
     "summary": "AI 生成表单、智能验证、数据分析的表单平台。",
     "content": """# FormAI

> 一句话生成专业表单

## 功能

- **AI 生成**：描述需求，自动生成表单
- **智能验证**：自动设置验证规则
- **数据分析**：实时统计和可视化
- **多端适配**：PC、移动端、小程序

## 模板库

- 调查问卷
- 报名表
- 订单表
- 反馈表

## 定价

- **免费版**：5 个表单
- **Pro**：¥49/月
- **企业**：¥199/月
"""},
    {"title": "MonitorPro - 全栈监控平台",
     "category": "SaaS平台", "tags": "监控,APM,SaaS",
     "summary": "应用性能监控 + 基础设施监控 + 用户体验监控。",
     "content": """# MonitorPro

> 全栈可观测性

## 功能

- **APM**：应用性能追踪
- **基础设施**：服务器、容器、数据库
- **用户体验**：页面加载、JS 错误
- **告警**：多渠道通知

## 支持的技术栈

Java, Python, Go, Node.js, PHP, .NET

## 定价

- **免费版**：5 台主机
- **Pro**：¥99/月/主机
- **企业**：定制
"""},
]

# ─── 方案内容模板 ────────────────────────────────────────────
SOLUTION_TEMPLATES = [
    {"title": "智慧医院 AI 解决方案",
     "category": "医疗健康", "tags": "AI,医疗,智慧医院",
     "summary": "AI 辅助诊断、智能导诊、病历结构化全流程方案。",
     "content": """# 智慧医院 AI 解决方案

## 方案架构

```
患者 → 智能导诊 → AI 辅助诊断 → 电子病历 → 随访管理
```

## 核心模块

### 1. 智能导诊
- 症状描述 → AI 推荐科室
- 准确率：92%

### 2. AI 辅助诊断
- 影像识别：肺结节、骨折
- 病理分析：细胞分类
- 准确率：95%+

### 3. 病历结构化
- 自然语言 → 结构化数据
- 支持中英文病历

## 客户案例

| 医院 | 场景 | 效果 |
|------|------|------|
| 某三甲医院 | 影像诊断 | 效率 +200% |
| 某社区医院 | 辅助诊断 | 误诊率 -40% |
"""},
    {"title": "在线教育 AI 方案",
     "category": "教育培训", "tags": "AI,教育,在线学习",
     "summary": "自适应学习、智能批改、个性化推荐的教育 AI 方案。",
     "content": """# 在线教育 AI 方案

## 核心能力

### 自适应学习
- 知识图谱驱动
- 动态调整学习路径
- 个性化练习推荐

### 智能批改
- 主观题自动评分
- 作文批改 + 点评
- 数学解题过程分析

### 学情分析
- 知识掌握度热力图
- 薄弱知识点定位
- 学习行为分析

## 效果数据

| 指标 | 效果 |
|------|------|
| 学习效率 | +40% |
| 作业批改时间 | -80% |
| 学生参与度 | +55% |
"""},
    {"title": "金融风控 AI 方案",
     "category": "金融保险", "tags": "AI,金融,风控",
     "summary": "实时交易风控、反欺诈检测、信用评估的 AI 方案。",
     "content": """# 金融风控 AI 方案

## 核心模块

### 实时交易风控
- 毫秒级决策
- 1000+ 风控规则
- 准确率 99.5%

### 反欺诈检测
- 设备指纹
- 行为分析
- 关联图谱

### 信用评估
- 多维数据融合
- 机器学习评分
- 实时更新

## 技术架构

```
交易请求 → 特征计算 → 模型推理 → 风控决策 → 结果返回
     ↑                                    ↓
     └──────── 规则引擎 + AI 模型 ────────┘
```

## 客户效果

| 指标 | 改善 |
|------|------|
| 欺诈损失 | -70% |
| 误报率 | -50% |
| 审批速度 | +300% |
"""},
    {"title": "智能制造质检方案",
     "category": "智能制造", "tags": "AI,制造,质检",
     "summary": "AI 视觉质检，替代人工检测，准确率 99.9%。",
     "content": """# 智能制造质检方案

## 痛点

- 人工质检效率低
- 漏检率高
- 成本持续上升

## 方案

### AI 视觉检测
- 工业相机 + AI 模型
- 实时检测，毫秒级响应
- 支持缺陷分类

### 缺陷类型

| 类型 | 检测率 |
|------|--------|
| 划痕 | 99.5% |
| 凹坑 | 99.2% |
| 色差 | 99.8% |
| 尺寸偏差 | 99.9% |

## 部署方式

- 边缘计算：延迟 < 10ms
- 云端训练：模型持续优化

## ROI

- 投资回收期：6 个月
- 年度成本节约：200 万+
"""},
    {"title": "智慧城市交通方案",
     "category": "智慧城市", "tags": "AI,交通,智慧城市",
     "summary": "AI 信号优化、智能停车、交通预测的智慧交通方案。",
     "content": """# 智慧城市交通方案

## 核心模块

### 1. AI 信号优化
- 实时车流感知
- 动态调整信号配时
- 绿波带优化

### 2. 智能停车
- 车位检测
- 自动计费
- 预约系统

### 3. 交通预测
- 短期流量预测
- 拥堵预警
- 事故检测

## 效果

| 指标 | 改善 |
|------|------|
| 平均通行时间 | -25% |
| 停车找位时间 | -60% |
| 交通事故率 | -30% |
"""},
    {"title": "零售 AI 客服方案",
     "category": "零售电商", "tags": "AI,客服,电商",
     "summary": "AI 智能客服 + 人工协同，提升客户满意度。",
     "content": """# 零售 AI 客服方案

## 架构

```
用户咨询 → 意图识别 → 知识库检索 → AI 回答 → 人工兜底
```

## 功能

- **智能问答**：覆盖 80% 常见问题
- **多轮对话**：上下文理解
- **情感分析**：识别负面情绪，转人工
- **工单系统**：自动创建和分配

## 效果

| 指标 | 效果 |
|------|------|
| 自动解决率 | 80% |
| 响应时间 | < 3 秒 |
| 客户满意度 | +30% |
| 人工客服工作量 | -60% |

## 定价

- **基础版**：¥2,999/月
- **专业版**：¥6,999/月
- **企业版**：定制
"""},
    {"title": "AI 写作助手方案",
     "category": "教育培训", "tags": "AI,写作,NLP",
     "summary": "AI 辅助写作：大纲生成、内容扩展、语法检查、风格优化。",
     "content": """# AI 写作助手方案

## 功能模块

### 1. 大纲生成
输入主题 → 自动生成文章大纲

### 2. 内容扩展
选中段落 → AI 扩展丰富内容

### 3. 语法检查
实时检查语法、拼写、标点

### 4. 风格优化
- 学术风格
- 商务风格
- 创意风格

## 使用场景

| 场景 | 效率提升 |
|------|----------|
| 论文写作 | +50% |
| 营销文案 | +80% |
| 技术文档 | +60% |
| 邮件撰写 | +70% |
"""},
    {"title": "供应链预测方案",
     "category": "智能制造", "tags": "AI,供应链,预测",
     "summary": "AI 驱动的需求预测、库存优化、物流规划方案。",
    "content": """# 供应链预测方案

## 核心能力

### 需求预测
- 多维特征融合
- 季节性、趋势性分析
- 准确率 90%+

### 库存优化
- 安全库存计算
- 自动补货建议
- 库存周转率优化

### 物流规划
- 路径优化
- 车辆调度
- 成本最小化

## 效果

| 指标 | 改善 |
|------|------|
| 预测准确率 | +35% |
| 库存成本 | -25% |
| 物流成本 | -15% |
"""},
    {"title": "智慧农业方案",
     "category": "智慧城市", "tags": "AI,农业,IoT",
     "summary": "AI + IoT 智慧农业：精准灌溉、病虫害检测、产量预测。",
    "content": """# 智慧农业方案

## 系统架构

```
传感器 → 数据采集 → AI 分析 → 决策支持 → 自动执行
```

## 核心功能

### 精准灌溉
- 土壤湿度监测
- 天气预报集成
- 自动灌溉控制

### 病虫害检测
- 图像识别
- 早期预警
- 防治建议

### 产量预测
- 卫星遥感
- 历史数据分析
- 产量预估

## 效果

| 指标 | 改善 |
|------|------|
| 水资源利用 | +40% |
| 病虫害损失 | -50% |
| 产量预测准确率 | 90% |
"""},
    {"title": "能源管理 AI 方案",
     "category": "智能制造", "tags": "AI,能源,节能",
     "summary": "AI 驱动的建筑能源管理：负荷预测、设备优化、碳排放监控。",
    "content": """# 能源管理 AI 方案

## 核心功能

### 负荷预测
- 基于天气、人流、历史数据
- 预测准确率 95%

### 设备优化
- 空调、照明、电梯联动
- 分时段策略
- 异常检测

### 碳排放监控
- 实时碳排放计算
- 碳足迹报告
- 减排建议

## 效果

| 指标 | 改善 |
|------|------|
| 能耗 | -30% |
| 碳排放 | -25% |
| 设备故障率 | -40% |
"""},
    {"title": "智慧物流方案",
     "category": "零售电商", "tags": "AI,物流,供应链",
     "summary": "AI 路径规划、智能调度、实时追踪的物流优化方案。",
     "content": """# 智慧物流方案

## 核心功能

### 路径规划
- 实时路况融合
- 多目标优化（时间、成本、碳排放）
- 动态调整

### 智能调度
- 订单-车辆匹配
- 取件-派件优化
- 异常处理

### 实时追踪
- GPS + IoT 传感器
- 预计到达时间
- 异常预警

## 效果

| 指标 | 改善 |
|------|------|
| 配送效率 | +35% |
| 物流成本 | -20% |
| 客户满意度 | +25% |
"""},
    {"title": "智慧养老方案",
     "category": "医疗健康", "tags": "AI,养老,IoT",
     "summary": "AI + IoT 智慧养老：健康监测、跌倒检测、智能照护。",
     "content": """# 智慧养老方案

## 核心功能

### 健康监测
- 心率、血压、血氧
- 睡眠质量分析
- 异常预警

### 跌倒检测
- 视觉 AI 识别
- 可穿戴设备
- 自动报警

### 智能照护
- 用药提醒
- 活动建议
- 亲属通知

## 效果

| 指标 | 改善 |
|------|------|
| 响应时间 | -70% |
| 跌倒检测率 | 95% |
| 家属满意度 | +40% |
"""},
    {"title": "智慧校园方案",
     "category": "教育培训", "tags": "AI,教育,校园",
     "summary": "AI 驱动的智慧校园：智能考勤、行为分析、个性化学习。",
     "content": """# 智慧校园方案

## 核心模块

### 智能考勤
- 人脸识别
- 自动统计
- 异常预警

### 行为分析
- 课堂专注度
- 校园安全
- 消费行为

### 个性化学习
- 学情分析
- 自适应练习
- 智能推荐

## 效果

| 指标 | 改善 |
|------|------|
| 考勤效率 | +90% |
| 安全事件 | -60% |
| 学习效果 | +30% |
"""},
    {"title": "智慧文旅方案",
     "category": "智慧城市", "tags": "AI,旅游,智慧城市",
     "summary": "AI 智慧文旅：客流预测、智能导览、营销推荐。",
     "content": """# 智慧文旅方案

## 核心功能

### 客流预测
- 历史数据分析
- 天气因素融合
- 实时预警

### 智能导览
- AR 导览
- 语音讲解
- 路线推荐

### 营销推荐
- 个性化推荐
- 动态定价
- 精准营销

## 效果

| 指标 | 改善 |
|------|------|
| 游客满意度 | +35% |
| 二次消费 | +45% |
| 运营成本 | -20% |
"""},
    {"title": "智慧能源方案",
     "category": "智能制造", "tags": "AI,能源,IoT",
     "summary": "AI 驱动的能源管理：发电预测、负荷调度、碳排放优化。",
     "content": """# 智慧能源方案

## 核心功能

### 发电预测
- 光伏/风电出力预测
- 准确率 95%+

### 负荷调度
- 需求响应
- 削峰填谷
- 经济调度

### 碳排放优化
- 碳足迹追踪
- 减排路径规划
- 碳交易支持

## 效果

| 指标 | 改善 |
|------|------|
| 新能源消纳率 | +25% |
| 用能成本 | -15% |
| 碳排放 | -30% |
"""},
    {"title": "智慧环保方案",
     "category": "智慧城市", "tags": "AI,环保,监测",
     "summary": "AI 环境监测：空气质量预测、水质监测、污染溯源。",
     "content": """# 智慧环保方案

## 核心功能

### 空气质量预测
- 多源数据融合
- 72 小时预测
- 准确率 90%

### 水质监测
- 实时传感器
- 异常预警
- 趋势分析

### 污染溯源
- 扩散模型
- 源头定位
- 责任追溯

## 效果

| 指标 | 改善 |
|------|------|
| 预警时间 | 提前 24h |
| 监测覆盖 | +80% |
| 执法效率 | +50% |
"""},
    {"title": "智慧社区方案",
     "category": "智慧城市", "tags": "AI,社区,IoT",
     "summary": "AI 智慧社区：安防监控、停车管理、物业服务。",
     "content": """# 智慧社区方案

## 核心功能

### 安防监控
- 人脸识别门禁
- 异常行为检测
- 周界防护

### 停车管理
- 车牌识别
- 车位引导
- 自动计费

### 物业服务
- 报修工单
- 缴费管理
- 社区公告

## 效果

| 指标 | 改善 |
|------|------|
| 安全事件 | -70% |
| 停车效率 | +50% |
| 物业满意度 | +35% |
"""},
    {"title": "智慧农业养殖方案",
     "category": "智能制造", "tags": "AI,养殖,IoT",
     "summary": "AI 智慧养殖：环境监控、疾病预警、精准饲喂。",
     "content": """# 智慧农业养殖方案

## 核心功能

### 环境监控
- 温湿度、氨气、CO2
- 自动调节通风、加热

### 疾病预警
- 行为异常检测
- 体温监测
- 早期预警

### 精准饲喂
- 个体识别
- 按需饲喂
- 饲料优化

## 效果

| 指标 | 改善 |
|------|------|
| 死亡率 | -40% |
| 饲料转化率 | +20% |
| 人工成本 | -50% |
"""},
    {"title": "智慧水利方案",
     "category": "智慧城市", "tags": "AI,水利,IoT",
     "summary": "AI 智慧水利：洪水预警、水资源调度、管网监测。",
     "content": """# 智慧水利方案

## 核心功能

### 洪水预警
- 降雨预测
- 水文模型
- 预警发布

### 水资源调度
- 需求预测
- 优化调度
- 节水管理

### 管网监测
- 泄漏检测
- 压力监测
- 水质监测

## 效果

| 指标 | 改善 |
|------|------|
| 预警时间 | 提前 6h |
| 漏损率 | -30% |
| 水资源利用 | +25% |
"""},
    {"title": "智慧矿山方案",
     "category": "智能制造", "tags": "AI,矿山,安全",
     "summary": "AI 智慧矿山：安全监测、无人采矿、智能调度。",
     "content": """# 智慧矿山方案

## 核心功能

### 安全监测
- 瓦斯浓度
- 顶板压力
- 人员定位

### 无人采矿
- 自动驾驶矿车
- 远程操控
- 智能掘进

### 智能调度
- 生产计划
- 设备调度
- 物流优化

## 效果

| 指标 | 改善 |
|------|------|
| 安全事故 | -80% |
| 生产效率 | +40% |
| 人工成本 | -60% |
"""},
]

# ─── 项目模板 ─────────────────────────────────────────────
PROJECT_TEMPLATES = [
    {"title": "AI Portal - 开源 AI 社区平台",
     "category": "AI应用", "tech_stack": ["Vue3", "FastAPI", "TypeScript", "SQLite", "TailwindCSS"],
     "description": "类 CSDN 的 AI 技术社区平台，支持博客、问答、专栏、动态。",
     "content": """# AI Portal

> 开源 AI 技术社区平台

## 技术栈

- 前端：Vue 3 + TypeScript + Element Plus + Tailwind CSS
- 后端：FastAPI + SQLAlchemy + SQLite
- 特色：赛博朋克 + 终端美学设计

## 功能模块

- 博客系统
- 问答社区
- 专栏/系列文章
- 动态广场
- AI 对话
- 用户系统

## GitHub

⭐ Star: 2,000+
"""},
    {"title": "智能客服系统",
     "category": "AI应用", "tech_stack": ["React", "Node.js", "MongoDB", "Redis", "LangChain"],
     "description": "基于 LLM 的智能客服系统，支持多轮对话和知识库问答。",
     "content": """# 智能客服系统

## 架构

- 前端：React + Ant Design
- 后端：Node.js + Express
- 数据库：MongoDB + Redis
- AI：LangChain + GPT-4

## 功能

- 多轮对话
- 知识库问答
- 人工转接
- 数据分析
"""},
    {"title": "电商数据大屏",
     "category": "数据平台", "tech_stack": ["Vue3", "ECharts", "WebSocket", "Python", "PostgreSQL"],
     "description": "实时电商数据可视化大屏，展示销售、流量、用户行为。",
     "content": """# 电商数据大屏

## 功能

- 实时销售数据
- 用户行为分析
- 商品热力图
- 地域分布

## 技术实现

- WebSocket 实时推送
- ECharts 可视化
- Vue 3 响应式布局
"""},
    {"title": "在线代码编辑器",
     "category": "AI应用", "tech_stack": ["React", "Monaco Editor", "Node.js", "Docker"],
     "description": "支持 10+ 种语言的在线代码编辑器，实时预览。",
     "content": """# 在线代码编辑器

## 功能

- Monaco Editor
- 语法高亮
- 代码补全
- 实时运行
- 多语言支持

## 支持语言

Python, JavaScript, TypeScript, Go, Rust, Java, C++, Ruby
"""},
    {"title": "企业知识库系统",
     "category": "管理系统", "tech_stack": ["Vue3", "FastAPI", "Elasticsearch", "PostgreSQL"],
     "description": "企业级知识库管理系统，支持全文搜索和 AI 问答。",
     "content": """# 企业知识库系统

## 功能

- 文档管理
- 全文搜索
- AI 问答
- 权限管理
- 版本控制

## 技术

- Elasticsearch 全文检索
- FastAPI 后端
- Vue 3 前端
"""},
    {"title": "移动健身 App",
     "category": "移动应用", "tech_stack": ["Flutter", "Firebase", "TensorFlow Lite"],
     "description": "AI 驱动的健身应用，动作识别 + 个性化训练计划。",
     "content": """# 移动健身 App

## 功能

- AI 动作识别
- 个性化训练计划
- 进度追踪
- 社区互动

## 技术

- Flutter 跨平台
- Firebase 后端
- TFLite 动作识别
"""},
    {"title": "智能招聘平台",
     "category": "管理系统", "tech_stack": ["Next.js", "FastAPI", "PostgreSQL", "Redis"],
     "description": "AI 简历匹配 + 智能推荐的招聘平台。",
     "content": """# 智能招聘平台

## 功能

- AI 简历解析
- 职位匹配推荐
- 视频面试
- 数据分析

## 效果

- 匹配准确率：85%
- 招聘周期：-40%
"""},
    {"title": "IoT 设备管理平台",
     "category": "数据平台", "tech_stack": ["React", "Go", "MQTT", "InfluxDB", "Grafana"],
     "description": "百万级 IoT 设备接入和管理平台。",
     "content": """# IoT 设备管理平台

## 功能

- 设备接入
- 数据采集
- 远程控制
- 告警管理
- 可视化

## 性能

- 支持 100 万+ 设备
- 消息延迟 < 100ms
- 数据存储 99.99% 可靠性
"""},
    {"title": "视频会议系统",
     "category": "企业官网", "tech_stack": ["React", "WebRTC", "Node.js", "Redis"],
     "description": "支持百人同时在线的视频会议系统。",
     "content": """# 视频会议系统

## 功能

- 高清视频通话
- 屏幕共享
- 实时字幕
- 会议录制
- 虚拟背景

## 技术

- WebRTC 实时通信
- SFU 架构
- Node.js 信令服务
"""},
    {"title": "电商后台管理系统",
     "category": "电商系统", "tech_stack": ["Vue3", "Element Plus", "FastAPI", "MySQL"],
     "description": "完整的电商后台管理系统：商品、订单、用户、营销。",
     "content": """# 电商后台管理系统

## 功能模块

- 商品管理
- 订单管理
- 用户管理
- 营销活动
- 数据统计

## 技术栈

- Vue 3 + Element Plus
- FastAPI + SQLAlchemy
- MySQL + Redis
"""},
    {"title": "AI 写作助手",
     "category": "AI应用", "tech_stack": ["Next.js", "OpenAI", "Prisma", "PostgreSQL"],
     "description": "AI 辅助写作工具，支持多种文体和风格。",
     "content": """# AI 写作助手

## 功能

- 大纲生成
- 内容扩展
- 风格转换
- 语法检查
- 多语言翻译

## 技术

- Next.js 全栈
- OpenAI API
- Prisma ORM
"""},
    {"title": "智能停车系统",
     "category": "智慧城市", "tech_stack": ["Vue3", "FastAPI", "PostgreSQL", "OpenCV"],
     "description": "车牌识别 + 车位检测 + 自动计费的智能停车系统。",
     "content": """# 智能停车系统

## 功能

- 车牌识别（准确率 99%）
- 车位检测
- 自动计费
- 预约系统
- 数据分析

## 技术

- OpenCV 车牌识别
- FastAPI 后端
- Vue 3 前端
"""},
    {"title": "在线教育平台",
     "category": "管理系统", "tech_stack": ["React", "Node.js", "MongoDB", "Socket.io"],
     "description": "支持直播、录播、作业、考试的在线教育平台。",
     "content": """# 在线教育平台

## 功能

- 直播授课
- 录播课程
- 作业系统
- 在线考试
- 学习分析

## 技术

- React 前端
- Node.js 后端
- Socket.io 实时通信
"""},
    {"title": "医疗影像分析系统",
     "category": "AI应用", "tech_stack": ["Python", "PyTorch", "FastAPI", "DICOM"],
     "description": "AI 辅助医疗影像分析，支持 CT、MRI、X 光。",
     "content": """# 医疗影像分析系统

## 功能

- 影像导入（DICOM）
- AI 病灶检测
- 三维重建
- 报告生成

## 准确率

- 肺结节检测：95%
- 骨折检测：97%
- 脑部异常：93%
"""},
    {"title": "社交媒体分析工具",
     "category": "数据平台", "tech_stack": ["Python", "FastAPI", "PostgreSQL", "Redis"],
     "description": "社交媒体数据采集、分析、舆情监控平台。",
     "content": """# 社交媒体分析工具

## 功能

- 数据采集
- 情感分析
- 舆情监控
- 趋势预测
- 报告生成

## 支持平台

微博、Twitter、小红书、抖音
"""},
    {"title": "智能仓储系统",
     "category": "管理系统", "tech_stack": ["Vue3", "FastAPI", "PostgreSQL", "IoT"],
     "description": "AI 驱动的智能仓储管理：入库、出库、盘点、优化。",
     "content": """# 智能仓储系统

## 功能

- 入库管理
- 出库管理
- 库存盘点
- 路径优化
- 预警系统

## 效果

- 拣货效率：+50%
- 库存准确率：99.9%
- 仓储成本：-20%
"""},
    {"title": "旅游推荐平台",
     "category": "电商系统", "tech_stack": ["Next.js", "FastAPI", "PostgreSQL", "Redis"],
     "description": "AI 个性化旅游推荐，行程规划，景点介绍。",
     "content": """# 旅游推荐平台

## 功能

- 个性化推荐
- 行程规划
- 景点介绍
- 酒店预订
- 用户评价

## AI 能力

- 偏好学习
- 协同过滤
- 内容推荐
"""},
    {"title": "企业 IM 系统",
     "category": "管理系统", "tech_stack": ["React", "Go", "WebSocket", "Redis", "MySQL"],
     "description": "企业级即时通讯系统，支持单聊、群聊、文件传输。",
     "content": """# 企业 IM 系统

## 功能

- 单聊 / 群聊
- 文件传输
- 消息搜索
- 已读回执
- 组织架构

## 性能

- 消息延迟 < 50ms
- 支持 10 万+ 在线用户
- 消息可靠送达
"""},
    {"title": "数据治理平台",
     "category": "数据平台", "tech_stack": ["Vue3", "FastAPI", "PostgreSQL", "Elasticsearch"],
     "description": "企业数据治理：元数据管理、数据质量、数据血缘。",
     "content": """# 数据治理平台

## 功能

- 元数据管理
- 数据质量监控
- 数据血缘追踪
- 数据安全
- 数据目录

## 价值

- 数据质量：+60%
- 数据发现效率：+80%
- 合规风险：-50%
"""},
    {"title": "AI 绘画工作台",
     "category": "AI应用", "tech_stack": ["Next.js", "Stable Diffusion", "Python", "Redis"],
     "description": "在线 AI 绘画工具，支持文生图、图生图、局部编辑。",
     "content": """# AI 绘画工作台

## 功能

- 文生图
- 图生图
- 局部编辑
- 风格迁移
- 批量生成

## 模型

- Stable Diffusion XL
- ControlNet
- LoRA
"""},
]

# ─── 动态内容 ─────────────────────────────────────────────
MOMENT_CONTENTS = [
    "刚看完 Transformer 论文，终于理解了 Attention 的核心思想！🎉",
    "今天用 FastAPI 写了个接口，性能比 Flask 快了 3 倍，推荐大家试试！",
    "Vue 3.5 的 Vapor Mode 太强了，组件渲染速度提升 50%！",
    "分享一个调试技巧：在 Chrome DevTools 里用 `monitor()` 监控函数调用，超好用！",
    "Docker 多阶段构建真的香，镜像从 1.2G 缩到 180M 🚀",
    "今天终于搞懂了 Kubernetes 的 Pod 调度策略，记了篇笔记。",
    "Rust 的所有权系统一开始真的很难，但理解之后写代码太舒服了。",
    "推荐一本书：《设计数据密集型应用》，对理解分布式系统很有帮助。",
    "用 LangChain 搭了个 RAG 系统，效果比预想的好很多！",
    "TypeScript 的类型体操真上头，写了个递归 DeepPartial 工具类型。",
    "PostgreSQL 的 EXPLAIN ANALYZE 是性能优化的神器，强烈推荐学习。",
    "今天把团队的 CI/CD 流水线从 Jenkins 迁移到 GitHub Actions，体验好太多了。",
    "React Server Components 的理念很棒，但学习曲线有点陡。",
    "PyTorch 2.0 的 torch.compile 真的是一行代码提速 3 倍，太香了！",
    "分享一个 CSS 小技巧：container queries 让组件真正响应式了。",
    "刚参加完 AI 技术大会，今年 Agent 是绝对的热门话题。",
    "用 Rust + WebAssembly 重写了图片处理模块，速度提升了 15 倍！",
    "Prometheus + Grafana 的监控组合真的无敌，推荐所有后端开发者学习。",
    "今天代码被 review 了，学到了很多关于错误处理的最佳实践。",
    "周末用 Cursor IDE 写了个小项目，AI 辅助编程效率真的高。",
]

# ─── 评论内容 ─────────────────────────────────────────────
COMMENT_CONTENTS = [
    "写得太棒了，受益匪浅！",
    "请问这个方案在生产环境用过吗？稳定性怎么样？",
    "感谢分享，正好在找这方面的资料。",
    "代码示例很清晰，已经跑通了 👍",
    "有一个疑问：如果数据量很大的情况下，性能如何？",
    "补充一点：还可以用 xxx 方案来优化。",
    "这个思路很新颖，之前没想到可以这样处理。",
    "博主能详细讲讲 xxx 部分吗？",
    "已收藏，准备周末好好研究一下。",
    "和我之前的做法不太一样，学习了！",
    "这个方案有个潜在问题：并发场景下可能会有竞态条件。",
    "太硬核了，需要消化一下。",
    "有没有相关的 benchmark 数据？",
    "实测有效，感谢！",
    "建议加上错误处理的部分会更完善。",
]

REPLY_CONTENTS = [
    "同意，我在生产环境用了半年了，很稳定。",
    "可以参考这篇论文：xxx",
    "谢谢补充，已经更新到文章里了。",
    "并发场景确实需要注意，建议加锁。",
    "可以看看官方文档的这部分：xxx",
    "数据量大的话建议分库分表。",
    "好的，我后续会写一篇专门的文章。",
    "benchmark 数据我放在 GitHub 仓库里了。",
]


def seed_users(db):
    """创建用户"""
    users = []
    for data in USERS:
        u = db.query(User).filter(User.username == data["username"]).first()
        if not u:
            u = User(
                username=data["username"],
                email=data.get("email"),
                hashed_password=data.get("hashed_password", HASHED_PW),
                is_active=True,
                is_admin=data.get("is_admin", False),
                nickname=data.get("nickname"),
                bio=data.get("bio"),
                avatar_url=data.get("avatar_url"),
                gender=data.get("gender"),
                location=data.get("location"),
                website=data.get("website"),
                github=data.get("github"),
                level=data.get("level", 1),
                points=data.get("points", 0),
                total_points=data.get("total_points", 0),
                created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(30, 180)),
            )
            db.add(u)
            db.commit()
            db.refresh(u)
            print(f"  Created user: {u.username}")
        users.append(u)
    return users


def seed_categories(db):
    """创建分类"""
    categories = []
    all_cats = [
        (BLOG_CATS, "blog"), (NEWS_CATS, "news"),
        (PRODUCT_CATS, "product"), (SOLUTION_CATS, "solution"),
    ]
    for cats, module_type in all_cats:
        for i, name in enumerate(cats):
            slug = f"{module_type}-{name.lower().replace(' ', '-')}"
            existing = db.query(Category).filter(Category.slug == slug).first()
            if not existing:
                cat = Category(name=name, slug=slug, module_type=module_type, sort_order=i)
                db.add(cat)
                categories.append(cat)
    db.commit()
    print(f"  Categories: {len(categories)} items")
    return categories


def seed_tags(db):
    """创建标签"""
    tags = []
    for name in TAGS_POOL:
        slug = name.lower().replace(".", "").replace("+", "plus")
        existing = db.query(Tag).filter(Tag.slug == slug).first()
        if not existing:
            t = Tag(name=name, slug=slug, usage_count=random.randint(5, 200))
            db.add(t)
            tags.append(t)
    db.commit()
    print(f"  Tags: {len(tags)} items")
    return tags


def seed_blogs(db, users, now):
    """创建 20 篇博客"""
    blogs = []
    non_admin = [u for u in users if not u.is_admin]
    for i, tmpl in enumerate(BLOG_TEMPLATES):
        author = random.choice(users)
        created = now - timedelta(days=random.randint(1, 90), hours=random.randint(0, 23))
        blog = Blog(
            title=tmpl["title"],
            content=tmpl["content"],
            summary=tmpl["summary"],
            cover_image=f"https://picsum.photos/seed/blog{i}/800/400",
            category=tmpl["category"],
            tags=tmpl["tags"],
            is_published=True,
            author_id=author.id,
            view_count=random.randint(100, 5000),
            likes_count=random.randint(5, 200),
            favorites_count=random.randint(2, 80),
            comments_count=random.randint(0, 30),
            shares_count=random.randint(0, 50),
            created_at=created,
            updated_at=created,
            published_at=created,
        )
        db.add(blog)
        blogs.append(blog)
    db.commit()
    for b in blogs:
        db.refresh(b)
    # 更新用户的 blog_count
    for u in users:
        count = db.query(Blog).filter(Blog.author_id == u.id).count()
        u.blog_count = count
    db.commit()
    print(f"  Blogs: {len(blogs)} items")
    return blogs


def seed_news(db, users, now):
    """创建 20 条新闻"""
    items = []
    for i, tmpl in enumerate(NEWS_TEMPLATES):
        author = random.choice(users)
        created = now - timedelta(days=random.randint(1, 60), hours=random.randint(0, 23))
        item = News(
            title=tmpl["title"],
            content=tmpl["content"],
            summary=tmpl["summary"],
            cover_image=f"https://picsum.photos/seed/news{i}/800/400",
            category=tmpl["category"],
            tags=tmpl["tags"],
            is_published=True,
            author_id=author.id,
            view_count=random.randint(200, 8000),
            shares_count=random.randint(5, 100),
            comments_count=random.randint(0, 25),
            created_at=created,
            updated_at=created,
            published_at=created,
        )
        db.add(item)
        items.append(item)
    db.commit()
    print(f"  News: {len(items)} items")
    return items


def seed_products(db, users, now):
    """创建 20 个产品"""
    items = []
    for i, tmpl in enumerate(PRODUCT_TEMPLATES):
        author = random.choice(users)
        created = now - timedelta(days=random.randint(1, 75), hours=random.randint(0, 23))
        item = Product(
            title=tmpl["title"],
            content=tmpl["content"],
            summary=tmpl["summary"],
            cover_image=f"https://picsum.photos/seed/product{i}/800/400",
            category=tmpl["category"],
            tags=tmpl["tags"],
            is_published=True,
            author_id=author.id,
            view_count=random.randint(300, 12000),
            shares_count=random.randint(10, 150),
            comments_count=random.randint(0, 35),
            created_at=created,
            updated_at=created,
            published_at=created,
        )
        db.add(item)
        items.append(item)
    db.commit()
    print(f"  Products: {len(items)} items")
    return items


def seed_solutions(db, users, now):
    """创建 20 个方案"""
    items = []
    for i, tmpl in enumerate(SOLUTION_TEMPLATES):
        author = random.choice(users)
        created = now - timedelta(days=random.randint(1, 80), hours=random.randint(0, 23))
        item = Solution(
            title=tmpl["title"],
            content=tmpl["content"],
            summary=tmpl["summary"],
            cover_image=f"https://picsum.photos/seed/solution{i}/800/400",
            category=tmpl["category"],
            tags=tmpl["tags"],
            is_published=True,
            author_id=author.id,
            view_count=random.randint(200, 9000),
            shares_count=random.randint(5, 120),
            comments_count=random.randint(0, 20),
            created_at=created,
            updated_at=created,
            published_at=created,
        )
        db.add(item)
        items.append(item)
    db.commit()
    print(f"  Solutions: {len(items)} items")
    return items


def seed_projects(db, users, now):
    """创建 20 个项目"""
    items = []
    for i, tmpl in enumerate(PROJECT_TEMPLATES):
        author = random.choice(users)
        created = now - timedelta(days=random.randint(1, 100), hours=random.randint(0, 23))
        item = Project(
            title=tmpl["title"],
            description=tmpl["description"],
            content=tmpl["content"],
            cover_image=f"https://picsum.photos/seed/project{i}/800/400",
            tech_stack=tmpl["tech_stack"],
            category=tmpl["category"],
            demo_url=f"https://demo.example.com/project{i}",
            repo_url=f"https://github.com/example/project{i}",
            is_published=True,
            author_id=author.id,
            likes_count=random.randint(5, 150),
            favorites_count=random.randint(2, 60),
            shares_count=random.randint(0, 40),
            sort_order=i,
            created_at=created,
            updated_at=created,
        )
        db.add(item)
        items.append(item)
    db.commit()
    print(f"  Projects: {len(items)} items")
    return items


def seed_series(db, users, blogs, now):
    """创建专栏并关联文章"""
    series_data = [
        {"title": "FastAPI 从入门到精通", "desc": "全面介绍 FastAPI 框架的系列教程"},
        {"title": "Vue 3 实战指南", "desc": "Vue 3 + TypeScript + Pinia 实战系列"},
        {"title": "AI 大模型应用开发", "desc": "LLM 应用开发实践系列"},
        {"title": "Docker & K8s 部署实战", "desc": "容器化部署与编排系列教程"},
        {"title": "机器学习算法精讲", "desc": "经典机器学习算法原理与实现"},
    ]
    series_list = []
    blog_idx = 0
    for i, data in enumerate(series_data):
        author = users[i % len(users)]
        created = now - timedelta(days=random.randint(10, 120))
        s = Series(
            title=data["title"],
            description=data["desc"],
            cover_image=f"https://picsum.photos/seed/series{i}/800/400",
            author_id=author.id,
            is_public=True,
            articles_count=0,
            created_at=created,
            updated_at=created,
        )
        db.add(s)
        db.flush()
        # 给每个专栏关联 3-4 篇文章
        count = random.randint(3, 4)
        for j in range(count):
            if blog_idx < len(blogs):
                sa = SeriesArticle(series_id=s.id, blog_id=blogs[blog_idx].id, order=j + 1)
                db.add(sa)
                blog_idx += 1
        s.articles_count = count
        series_list.append(s)
    db.commit()
    print(f"  Series: {len(series_list)} items")
    return series_list


def seed_moments(db, users, now):
    """创建动态"""
    moments = []
    for i, content in enumerate(MOMENT_CONTENTS):
        author = random.choice(users)
        created = now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        m = Moment(
            user_id=author.id,
            content=content,
            likes_count=random.randint(0, 50),
            comments_count=random.randint(0, 15),
            shares_count=random.randint(0, 10),
            created_at=created,
            updated_at=created,
        )
        db.add(m)
        moments.append(m)
    db.commit()
    for m in moments:
        db.refresh(m)
    print(f"  Moments: {len(moments)} items")
    return moments


def seed_comments(db, users, blogs, news, products, solutions, moments):
    """创建评论（含嵌套回复）"""
    comments = []
    targets = (
        [("blog", b) for b in blogs[:15]] +
        [("news", n) for n in news[:10]] +
        [("product", p) for p in products[:8]] +
        [("solution", s) for s in solutions[:5]] +
        [("moment", m) for m in moments[:8]]
    )
    for target_type, target in targets:
        # 每个目标 2-4 条一级评论
        num_comments = random.randint(2, 4)
        for _ in range(num_comments):
            user = random.choice(users)
            content = random.choice(COMMENT_CONTENTS)
            created = target.created_at + timedelta(hours=random.randint(1, 48))
            c = Comment(
                target_type=target_type,
                target_id=target.id,
                user_id=user.id,
                author_name=user.nickname or user.username,
                content=content,
                likes_count=random.randint(0, 20),
                created_at=created,
            )
            db.add(c)
            db.flush()
            comments.append(c)

            # 30% 概率有嵌套回复
            if random.random() < 0.3:
                replier = random.choice([u for u in users if u.id != user.id])
                reply = Comment(
                    target_type=target_type,
                    target_id=target.id,
                    parent_id=c.id,
                    user_id=replier.id,
                    author_name=replier.nickname or replier.username,
                    content=random.choice(REPLY_CONTENTS),
                    likes_count=random.randint(0, 5),
                    created_at=created + timedelta(hours=random.randint(1, 12)),
                )
                db.add(reply)
                comments.append(reply)

    db.commit()
    print(f"  Comments: {len(comments)} items")
    return comments


def seed_likes(db, users, blogs, moments, projects):
    """创建点赞记录"""
    likes = []
    targets = (
        [("blog", b) for b in blogs] +
        [("moment", m) for m in moments] +
        [("project", p) for p in projects]
    )
    for user in users:
        num_likes = random.randint(8, 25)
        sampled = random.sample(targets, min(num_likes, len(targets)))
        for target_type, target in sampled:
            existing = db.query(UserLike).filter(
                UserLike.user_id == user.id,
                UserLike.target_type == target_type,
                UserLike.target_id == target.id,
            ).first()
            if not existing:
                like = UserLike(
                    user_id=user.id,
                    target_type=target_type,
                    target_id=target.id,
                    created_at=target.created_at + timedelta(hours=random.randint(1, 72)),
                )
                db.add(like)
                likes.append(like)
    db.commit()
    print(f"  Likes: {len(likes)} items")
    return likes


def seed_favorites(db, users, blogs, products, solutions, projects):
    """创建收藏记录"""
    favorites = []
    targets = (
        [("blog", b) for b in blogs] +
        [("product", p) for p in products] +
        [("solution", s) for s in solutions] +
        [("project", p) for p in projects]
    )
    for user in users:
        num_favs = random.randint(3, 12)
        sampled = random.sample(targets, min(num_favs, len(targets)))
        for target_type, target in sampled:
            existing = db.query(UserFavorite).filter(
                UserFavorite.user_id == user.id,
                UserFavorite.target_type == target_type,
                UserFavorite.target_id == target.id,
            ).first()
            if not existing:
                fav = UserFavorite(
                    user_id=user.id,
                    target_type=target_type,
                    target_id=target.id,
                    created_at=target.created_at + timedelta(hours=random.randint(1, 96)),
                )
                db.add(fav)
                favorites.append(fav)
    db.commit()
    print(f"  Favorites: {len(favorites)} items")
    return favorites


def seed_follows(db, users):
    """创建关注关系"""
    follows = []
    for user in users:
        num_following = random.randint(2, 6)
        others = [u for u in users if u.id != user.id]
        targets = random.sample(others, min(num_following, len(others)))
        for target in targets:
            existing = db.query(UserFollow).filter(
                UserFollow.follower_id == user.id,
                UserFollow.following_id == target.id,
            ).first()
            if not existing:
                follow = UserFollow(
                    follower_id=user.id,
                    following_id=target.id,
                    created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 60)),
                )
                db.add(follow)
                follows.append(follow)
    db.commit()
    # 更新关注/粉丝计数
    for user in users:
        user.following_count = db.query(UserFollow).filter(UserFollow.follower_id == user.id).count()
        user.followers_count = db.query(UserFollow).filter(UserFollow.following_id == user.id).count()
    db.commit()
    print(f"  Follows: {len(follows)} items")
    return follows


def seed_checkins(db, users, now):
    """创建签到记录"""
    records = []
    for user in users:
        # 每个用户最近 7-30 天的签到
        days = random.randint(7, 30)
        for d in range(days):
            checkin_date = (now - timedelta(days=d)).date()
            existing = db.query(CheckinRecord).filter(
                CheckinRecord.user_id == user.id,
                CheckinRecord.checkin_date == checkin_date,
            ).first()
            if not existing:
                r = CheckinRecord(
                    user_id=user.id,
                    checkin_date=checkin_date,
                    continuous_days=min(d + 1, 30),
                    points_awarded=5 + (10 if (d + 1) % 7 == 0 else 0),
                    created_at=datetime(checkin_date.year, checkin_date.month, checkin_date.day, tzinfo=timezone.utc),
                )
                db.add(r)
                records.append(r)
    db.commit()
    print(f"  Checkins: {len(records)} items")
    return records


def seed_reading_history(db, users, blogs, news, products):
    """创建阅读历史"""
    records = []
    targets = (
        [("blog", b) for b in blogs] +
        [("news", n) for n in news] +
        [("product", p) for p in products]
    )
    for user in users:
        num_reads = random.randint(10, 30)
        sampled = random.sample(targets, min(num_reads, len(targets)))
        for content_type, target in sampled:
            existing = db.query(ReadingHistory).filter(
                ReadingHistory.user_id == user.id,
                ReadingHistory.content_type == content_type,
                ReadingHistory.content_id == target.id,
            ).first()
            if not existing:
                r = ReadingHistory(
                    user_id=user.id,
                    content_type=content_type,
                    content_id=target.id,
                    read_at=target.created_at + timedelta(hours=random.randint(1, 120)),
                )
                db.add(r)
                records.append(r)
    db.commit()
    print(f"  Reading History: {len(records)} items")
    return records


def seed_point_logs(db, users, now):
    """创建积分记录"""
    records = []
    actions = [
        ("daily_login", 5, "每日签到"),
        ("publish_blog", 20, "发布博客"),
        ("receive_like", 2, "获得点赞"),
        ("receive_favorite", 3, "获得收藏"),
        ("receive_follow", 5, "获得关注"),
        ("comment", 2, "发表评论"),
    ]
    for user in users:
        num_logs = random.randint(5, 15)
        for _ in range(num_logs):
            action, points, desc = random.choice(actions)
            r = PointLog(
                user_id=user.id,
                action=action,
                points=points,
                description=desc,
                created_at=now - timedelta(days=random.randint(0, 60), hours=random.randint(0, 23)),
            )
            db.add(r)
            records.append(r)
    db.commit()
    print(f"  Point Logs: {len(records)} items")
    return records


def run(reset=False):
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)

        if reset:
            for model in [
                ReadingHistory, SeriesArticle, Series,
                CheckinRecord, PointLog, Notification,
                UserFollow, UserFavorite, UserLike,
                Comment, Moment,
                Blog, News, Product, Solution, Project,
                ContentTag, Tag, Category,
                User,
            ]:
                db.query(model).delete()
            db.commit()
            print("  Cleared existing data")

        print("\n=== Seeding Users ===")
        users = seed_users(db)

        print("\n=== Seeding Categories & Tags ===")
        seed_categories(db)
        seed_tags(db)

        print("\n=== Seeding Content ===")
        blogs = seed_blogs(db, users, now)
        news = seed_news(db, users, now)
        products = seed_products(db, users, now)
        solutions = seed_solutions(db, users, now)
        projects = seed_projects(db, users, now)
        series = seed_series(db, users, blogs, now)

        print("\n=== Seeding Social ===")
        moments = seed_moments(db, users, now)
        seed_comments(db, users, blogs, news, products, solutions, moments)
        seed_likes(db, users, blogs, moments, projects)
        seed_favorites(db, users, blogs, products, solutions, projects)
        seed_follows(db, users)

        print("\n=== Seeding Activity ===")
        seed_checkins(db, users, now)
        seed_reading_history(db, users, blogs, news, products)
        seed_point_logs(db, users, now)

        print("\n  ✅ Seed complete!")
        print(f"  Users: {len(users)} | Blogs: {len(blogs)} | News: {len(news)}")
        print(f"  Products: {len(products)} | Solutions: {len(solutions)} | Projects: {len(projects)}")
        print(f"  Series: {len(series)} | Moments: {len(moments)}")
    except Exception as e:
        db.rollback()
        print(f"  ❌ Failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    reset = "--reset" in sys.argv
    run(reset=reset)
