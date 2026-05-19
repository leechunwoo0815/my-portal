"""
AI Portal 完整种子数据脚本
用法: cd backend && python3 scripts/seed_all.py
"""
import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone, timedelta
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models import (
    User, Blog, News, Product, Solution, Project, Moment, Comment, UserFollow
)


def rt(now: datetime, max_days: int = 90) -> datetime:
    """生成随机过去时间"""
    return now - timedelta(
        days=random.randint(1, max_days),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )


def seed_users(db, now):
    users_data = [
        {"username": "alice", "email": "alice@aiportal.local", "level": 5, "points": 1200,
         "bio": "热爱AI的前端工程师，专注于大模型应用开发", "gender": "female", "location": "北京"},
        {"username": "bob", "email": "bob@aiportal.local", "level": 3, "points": 450,
         "bio": "后端开发者，喜欢折腾各种新框架", "gender": "male", "location": "上海"},
        {"username": "charlie", "email": "charlie@aiportal.local", "level": 7, "points": 3200,
         "bio": "全栈工程师兼技术博主，深耕深度学习多年", "gender": "male", "location": "深圳"},
        {"username": "diana", "email": "diana@aiportal.local", "level": 2, "points": 180,
         "bio": "数据科学爱好者，正在学习LLM相关技术", "gender": "female", "location": "杭州"},
        {"username": "evan", "email": "evan@aiportal.local", "level": 4, "points": 850,
         "bio": "产品经理，关注AI产品落地与用户体验", "gender": "male", "location": "成都"},
    ]
    created_users = []
    for u in users_data:
        existing = db.query(User).filter(User.username == u["username"]).first()
        if existing:
            created_users.append(existing)
            continue
        user = User(
            username=u["username"],
            email=u["email"],
            hashed_password=get_password_hash("password123"),
            is_active=True,
            is_admin=False,
            nickname=u["username"].capitalize(),
            bio=u["bio"],
            gender=u["gender"],
            location=u["location"],
            level=u["level"],
            points=u["points"],
            total_points=u["points"],
            created_at=rt(now, 120),
            updated_at=rt(now, 120),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        created_users.append(user)
    print(f"  Users: {len(created_users)} items")
    return created_users


def seed_follows(db, users):
    name_to_id = {u.username: u.id for u in users}
    follow_pairs = [
        ("alice", "bob"), ("alice", "charlie"),
        ("bob", "charlie"), ("bob", "diana"),
        ("charlie", "alice"), ("charlie", "evan"),
        ("diana", "alice"), ("diana", "charlie"),
        ("evan", "bob"), ("evan", "charlie"),
    ]
    count = 0
    for follower, following in follow_pairs:
        fid = name_to_id[follower]
        tid = name_to_id[following]
        existing = db.query(UserFollow).filter(
            UserFollow.follower_id == fid,
            UserFollow.following_id == tid,
        ).first()
        if not existing:
            db.add(UserFollow(follower_id=fid, following_id=tid))
            count += 1
    db.commit()
    for u in users:
        u.followers_count = db.query(UserFollow).filter(UserFollow.following_id == u.id).count()
        u.following_count = db.query(UserFollow).filter(UserFollow.follower_id == u.id).count()
    db.commit()
    print(f"  Follows: {count} items")


COVER_IMAGES = [
    "/uploads/news/temp_1778147754323.jpg",
    "https://picsum.photos/seed/ai1/800/400",
    "https://picsum.photos/seed/ai2/800/400",
    "https://picsum.photos/seed/ai3/800/400",
    "https://picsum.photos/seed/ai4/800/400",
]

BLOG_CONTENTS = [
    ("DeepSeek-V3技术解读",
     """DeepSeek-V3 是深度求索发布的最新一代大语言模型，在多项评测中表现优异。

## 模型架构

DeepSeek-V3 采用了 MoE（Mixture of Experts）架构，总参数量达 671B，每次前向传播激活 37B 参数。

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "deepseek-ai/DeepSeek-V3"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

inputs = tokenizer("介绍一下DeepSeek-V3", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=256)
print(tokenizer.decode(outputs[0]))
```

## 性能对比

| 模型 | MMLU | GSM8K | HumanEval |
|------|------|-------|-----------|
| DeepSeek-V3 | 88.5 | 90.2 | 92.5 |
| GPT-4o | 88.7 | 89.3 | 90.2 |
| Claude-3.5 | 88.3 | 91.6 | 92.0 |

## 训练成本

据官方披露，DeepSeek-V3 的完整训练成本约为 **557.6万美元**，远低于同类闭源模型。

更多信息请参考 [DeepSeek 官方文档](https://www.deepseek.com/)。
"""),
    ("FastAPI+SQLAlchemy最佳实践",
     """FastAPI 与 SQLAlchemy 是当前 Python Web 开发中最流行的组合之一。本文分享一些实战经验。

## 项目结构

推荐的项目目录结构如下：

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/
│   ├── schemas/
│   └── routers/
├── alembic/
└── tests/
```

## 依赖注入示例

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DbDep = Annotated[Session, Depends(get_db)]
```

## ORM 性能对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| 原生 SQL | 性能最优 | 维护困难 |
| SQLAlchemy ORM | 开发效率高 | 复杂查询性能一般 |
| SQLAlchemy Core | 平衡选择 | 学习曲线较陡 |

## 数据库连接池配置

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)
```
"""),
    ("Vue3 Composition API深入理解",
     """Vue 3 的 Composition API 带来了更灵活的代码组织方式，本文深入探讨其核心概念。

## 核心 API

### ref 与 reactive

```typescript
import { ref, reactive, computed } from 'vue'

// 基本类型用 ref
const count = ref(0)

// 对象用 reactive
const state = reactive({
  name: 'Alice',
  age: 25,
})

const doubleCount = computed(() => count.value * 2)
```

### 生命周期钩子

```typescript
import { onMounted, onUnmounted } from 'vue'

onMounted(() => {
  console.log('组件已挂载')
})

onUnmounted(() => {
  console.log('组件已卸载')
})
```

## 对比 Options API

| 特性 | Options API | Composition API |
|------|-------------|-----------------|
| 代码组织 | 按选项分组 | 按逻辑功能分组 |
| 复用性 | Mixin 易冲突 | Composable 清晰 |
| TypeScript | 支持一般 | 支持优秀 |

## 最佳实践

- 将相关逻辑提取到 composable 函数中
- 优先使用 ref 而不是 reactive
- 合理使用 provide/inject 进行跨层级通信
"""),
    ("RAG系统实战",
     """RAG（Retrieval-Augmented Generation）是当前企业落地大模型最主流的方案。

## 系统架构

```
用户提问 → 向量化 → 向量检索 → 上下文拼接 → LLM生成
```

## 向量检索示例

```python
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-large-zh-v1.5"
)

vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
```

## 关键优化点

1. **分块策略**：根据文档类型选择合适的大小和重叠度
2. **重排序**：使用 cross-encoder 对召回结果重排
3. **查询改写**：对用户问题进行扩展和澄清

推荐阅读 [LangChain 官方文档](https://python.langchain.com/)。
"""),
    ("PyTorch模型部署",
     """将训练好的 PyTorch 模型部署到生产环境有多种方案，本文对比分析各方案的优劣。

## 部署方案对比

| 方案 | 延迟 | 吞吐量 | 复杂度 |
|------|------|--------|--------|
| TorchScript | 低 | 中 | 低 |
| ONNX Runtime | 低 | 高 | 中 |
| TensorRT | 极低 | 极高 | 高 |
| vLLM | 低 | 极高 | 中 |

## TorchServe 示例

```python
from ts.torch_handler.base_handler import BaseHandler

class MyHandler(BaseHandler):
    def preprocess(self, data):
        return torch.tensor(json.loads(data[0]["body"]))

    def inference(self, inputs):
        with torch.no_grad():
            return self.model(inputs)

    def postprocess(self, inference_output):
        return [json.dumps({"result": inference_output.tolist()})]
```

## 性能调优建议

- 使用 `torch.compile` 加速模型（PyTorch 2.0+）
- 启用混合精度推理 `torch.cuda.amp`
- 批量处理请求以提高 GPU 利用率
"""),
    ("Transformer注意力机制可视化",
     """理解 Transformer 的注意力机制是掌握大模型的关键，本文通过代码和可视化帮助理解。

## 自注意力计算

```python
import torch
import torch.nn as nn

class SelfAttention(nn.Module):
    def __init__(self, embed_size, heads):
        super().__init__()
        self.embed_size = embed_size
        self.heads = heads
        self.head_dim = embed_size // heads

        self.values = nn.Linear(embed_size, embed_size)
        self.keys = nn.Linear(embed_size, embed_size)
        self.queries = nn.Linear(embed_size, embed_size)
        self.fc_out = nn.Linear(embed_size, embed_size)

    def forward(self, values, keys, query, mask):
        N = query.shape[0]
        value_len, key_len, query_len = values.shape[1], keys.shape[1], query.shape[1]

        values = self.values(values).view(N, value_len, self.heads, self.head_dim)
        keys = self.keys(keys).view(N, key_len, self.heads, self.head_dim)
        queries = self.queries(query).view(N, query_len, self.heads, self.head_dim)

        energy = torch.einsum("nqhd,nkhd->nhqk", [queries, keys])
        attention = torch.softmax(energy / (self.embed_size ** (1/2)), dim=3)
        out = torch.einsum("nhql,nlhd->nqhd", [attention, values]).reshape(N, query_len, self.heads * self.head_dim)
        return self.fc_out(out)
```

## 注意力模式分析

| 类型 | 用途 | 代表模型 |
|------|------|----------|
| Full Self-Attention | 理解全局上下文 | BERT |
| Causal Masking | 自回归生成 | GPT |
| Cross-Attention | 多模态融合 | T5, Stable Diffusion |

更多可视化工具可参考 [BertViz](https://github.com/jessevig/bertviz)。
"""),
    ("LoRA与QLoRA微调",
     """LoRA（Low-Rank Adaptation）是高效微调大模型的核心技术，QLoRA 进一步降低了显存需求。

## LoRA 原理

LoRA 通过在原始权重矩阵旁路添加低秩矩阵来实现微调：

```python
from peft import LoraConfig, get_peft_model

config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(base_model, config)
model.print_trainable_parameters()
```

## QLoRA 显存优化

| 模型大小 | Full Fine-tune | LoRA | QLoRA |
|----------|----------------|------|-------|
| 7B | 80GB | 20GB | 10GB |
| 13B | 160GB | 35GB | 16GB |
| 70B | 800GB | 150GB | 48GB |

## 训练配置

```python
from transformers import TrainingArguments

training_args = TrainingArguments(
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    learning_rate=2e-4,
    fp16=True,
    optim="paged_adamw_8bit",
)
```
"""),
    ("提示工程进阶CoT与ReAct",
     """提示工程（Prompt Engineering）是发挥大模型能力的基础，CoT 和 ReAct 是两种核心进阶技术。

## Chain-of-Thought (CoT)

通过引导模型逐步推理，显著提升复杂任务的表现：

```python
prompt = '''
问题：一个农场里有鸡和兔子，共有35个头，94只脚。鸡和兔子各有多少只？

请一步一步思考：
1. 设鸡有 x 只，兔子有 y 只
2. 根据头的数量：x + y = 35
3. 根据脚的数量：2x + 4y = 94
4. 从方程1得：x = 35 - y
5. 代入方程2：2(35 - y) + 4y = 94
6. 70 - 2y + 4y = 94
7. 2y = 24，y = 12
8. x = 35 - 12 = 23

答案：鸡23只，兔子12只。
'''
```

## ReAct 模式

ReAct（Reasoning + Acting）让模型交替进行推理和行动：

```python
react_prompt = '''
你可以使用以下工具：
- search[query]: 搜索信息
- calculator[expr]: 计算表达式

问题：2024年诺贝尔文学奖得主是谁？他/她的代表作是什么？

思考1：我需要搜索2024年诺贝尔文学奖的信息。
行动1：search[2024年诺贝尔文学奖得主]
观察1：2024年诺贝尔文学奖授予韩国作家韩江。

思考2：我需要搜索韩江的代表作。
行动2：search[韩江 代表作]
观察2：韩江的代表作包括《素食者》《少年来了》等。

答案：2024年诺贝尔文学奖得主是韩江，代表作有《素食者》等。
'''
```

## 对比总结

| 技术 | 适用场景 | 示例 |
|------|----------|------|
| CoT | 数学推理、逻辑题 | 鸡兔同笼 |
| ReAct | 需要外部工具的任务 | 实时信息查询 |
"""),
    ("数据可视化最佳实践",
     """数据可视化是将抽象数据转化为直观图表的艺术，好的可视化能让数据讲述动人的故事。

## 选择正确的图表类型

| 数据关系 | 推荐图表 | 示例库 |
|----------|----------|--------|
| 时间趋势 | 折线图 | ECharts, D3.js |
| 占比构成 | 饼图/环形图 | Plotly, Matplotlib |
| 分布比较 | 箱线图/小提琴图 | Seaborn |
| 地理数据 | 热力地图 | Mapbox, Leaflet |

## ECharts 快速入门

```javascript
import * as echarts from 'echarts';

const chart = echarts.init(document.getElementById('main'));
const option = {
  title: { text: '月度销售趋势' },
  tooltip: {},
  xAxis: { data: ['1月', '2月', '3月', '4月', '5月'] },
  yAxis: {},
  series: [{
    name: '销售额',
    type: 'line',
    data: [120, 200, 150, 80, 70]
  }]
};
chart.setOption(option);
```

## 配色原则

- 使用品牌色作为主色调
- 避免过多颜色（建议不超过7种）
- 考虑色盲用户的可访问性
- 暗色模式需要降低饱和度
"""),
    ("智慧城市AI应用案例",
     """智慧城市是人工智能落地的重要场景，涵盖了交通、安防、环保等多个领域。

## 典型应用场景

### 智能交通信号控制

通过实时分析路口车流量，AI 系统可以动态调整红绿灯时长，减少拥堵。

| 城市 | 拥堵指数下降 | 平均通行时间缩短 |
|------|--------------|------------------|
| 杭州 | 15% | 12分钟 |
| 深圳 | 18% | 15分钟 |
| 北京 | 10% | 8分钟 |

### 城市安防监控

利用计算机视觉技术实现异常行为检测、人群密度分析等功能。

```python
import cv2

# 加载预训练模型
model = cv2.dnn.readNetFromTensorflow('frozen_inference_graph.pb')

# 检测视频流中的异常行为
cap = cv2.VideoCapture('city_camera_01.mp4')
while True:
    ret, frame = cap.read()
    if not ret:
        break
    # 预处理与推理
    blob = cv2.dnn.blobFromImage(frame, size=(300, 300), swapRB=True)
    model.setInput(blob)
    detections = model.forward()
```

## 更多资源

- [住建部智慧城市试点名单](https://www.mohurd.gov.cn/)
- [阿里云城市大脑解决方案](https://www.aliyun.com/solution/citybrain)
"""),
]


def seed_blogs(db, users, now):
    cats = ["深度学习", "前端开发", "后端开发", "机器学习", "NLP", "运维部署", "AI应用", "数据科学", "大模型"]
    tags_pool = ["Transformer", "Vue3", "FastAPI", "PyTorch", "LangChain", "Docker",
                 "TypeScript", "React", "NLP", "K8s", "MLOps", "Security", "Deep Learning",
                 "RAG", "LoRA", "Prompt Engineering", "ECharts", "智慧城市"]
    blogs = []
    for i, (title, content) in enumerate(BLOG_CONTENTS):
        cat = random.choice(cats)
        tags = ",".join(random.sample(tags_pool, k=random.randint(2, 4)))
        summary = content.split("\n")[0][:200]
        cover = random.choice(COVER_IMAGES) if random.random() > 0.3 else None
        author = random.choice(users)
        created = rt(now, 60)
        blogs.append(Blog(
            title=title,
            content=content,
            summary=summary,
            cover_image=cover,
            category=cat,
            tags=tags,
            is_published=True,
            created_at=created,
            updated_at=created,
            view_count=random.randint(50, 5000),
            likes_count=random.randint(5, 300),
            author_id=author.id,
        ))
    for blog in blogs:
        db.add(blog)
    db.commit()
    for blog in blogs:
        db.refresh(blog)
    print(f"  Blogs: {len(blogs)} items")
    return blogs


NEWS_CONTENTS = [
    ("OpenAI发布GPT-4o多模态大模型",
     """OpenAI 在春季发布会上正式推出了 GPT-4o，这是一个原生多模态大模型，能够同时处理文本、音频和图像输入。

## 核心特性

| 能力 | 描述 | 延迟 |
|------|------|------|
| 语音对话 | 端到端音频处理 | 平均320ms |
| 视觉理解 | 实时图像分析 | 即时 |
| 代码生成 | 支持多语言编程 | 快速 |

## 技术突破

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": [
            {"type": "text", "text": "描述这张图片"},
            {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
        ]}
    ]
)
print(response.choices[0].message.content)
```

## 行业影响

GPT-4o 的发布标志着大模型进入**全模态时代**，详细报道请查看 [OpenAI 官方博客](https://openai.com/blog)。
"""),
    ("Anthropic发布Claude 3.5 Sonnet",
     """Anthropic 发布了 Claude 3.5 Sonnet，在多项基准测试中超越了 GPT-4o，成为当前最强的大语言模型之一。

## 性能基准

| 评测项 | Claude 3.5 | GPT-4o | Gemini 1.5 Pro |
|--------|------------|--------|----------------|
| MMLU | 88.3 | 88.7 | 85.9 |
| HumanEval | 92.0 | 90.2 | 84.1 |
| GSM8K | 91.6 | 89.3 | 87.8 |

## 新功能：Artifacts

Claude 3.5 引入了 Artifacts 功能，可以在侧边栏实时预览代码生成的结果。

```python
# Claude 生成的示例代码
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(8, 4))
plt.plot(x, y, label="sin(x)")
plt.legend()
plt.show()
```

更多信息请参考 [Anthropic 官网](https://www.anthropic.com/)。
"""),
    ("Meta开源Llama 3系列模型",
     """Meta 正式开源了 Llama 3 系列大语言模型，包含 8B 和 70B 两个版本，性能全面超越同规模开源模型。

## 模型亮点

- 训练数据量达 **15T tokens**，是 Llama 2 的7倍
- 支持 **8K 上下文窗口**
- 在代码生成和推理任务上显著提升

## 快速开始

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype="auto")

messages = [
    {"role": "system", "content": "你是一个 helpful assistant。"},
    {"role": "user", "content": "你好！"}
]
```

## 开源生态

| 项目 | 描述 | Star数 |
|------|------|--------|
| ollama | 本地运行大模型 | 70k+ |
| llama.cpp | C++推理引擎 | 50k+ |
| vLLM | 高吞吐服务化 | 20k+ |
"""),
    ("Google I/O 2024 AI产品全览",
     """在 Google I/O 2024 大会上，Google 发布了一系列 AI 产品和更新，全面展示其 AI 战略。

## 重磅发布

### Gemini 1.5 Pro

支持 **200万 token** 超长上下文，可以处理整本书或长视频。

### Veo 视频生成模型

```python
# 使用 Vertex AI 调用 Veo
from google.cloud import aiplatform

aiplatform.init(project="your-project", location="us-central1")

model = aiplatform.Model("veo-001")
response = model.predict(
    prompt="一只柯基在沙滩上奔跑，夕阳背景",
    duration_seconds=8,
    resolution="1080p"
)
```

## 产品矩阵

| 产品 | 类型 | 状态 |
|------|------|------|
| Gemini 1.5 Pro | 多模态LLM | 已发布 |
| Veo | 视频生成 | 内测 |
| Imagen 3 | 图像生成 | 预览 |
| Astra | AI助手 | 概念演示 |

详情访问 [Google AI 博客](https://ai.googleblog.com/)。
"""),
    ("苹果WWDC发布Apple Intelligence",
     """苹果在 WWDC 2024 上正式公布了 Apple Intelligence，将生成式 AI 深度集成到 iOS、iPadOS 和 macOS 中。

## 核心功能

- **Siri 升级**：支持自然语言对话和上下文理解
- **写作工具**：系统级文本重写、校对和摘要
- **Image Playground**：本地生成个性化图像

## 隐私架构

```
用户设备（本地模型）→ 私有云计算（Apple服务器）→ ChatGPT（可选）
```

## 支持的设备

| 设备类型 | 要求 | 代表机型 |
|----------|------|----------|
| iPhone | A17 Pro 及以上 | iPhone 15 Pro |
| iPad | M1 及以上 | iPad Pro M4 |
| Mac | M1 及以上 | MacBook Air M3 |

Apple Intelligence 预计随 iOS 18 正式版推出，更多信息见 [Apple 官网](https://www.apple.com/)。
"""),
    ("马斯克xAI发布Grok-2大模型",
     """埃隆·马斯克旗下的 xAI 公司发布了 Grok-2 大模型，并宣布在 X 平台上向 Premium 用户开放使用。

## 模型特点

- 可以实时访问 X 平台的最新信息
- 支持图像生成（基于 Flux 模型）
- 在数学和推理任务上接近 GPT-4 水平

## 使用方法

```python
import requests

API_KEY = "your_xai_api_key"
response = requests.post(
    "https://api.x.ai/v1/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "model": "grok-2",
        "messages": [{"role": "user", "content": "今天有什么科技新闻？"}]
    }
)
print(response.json()["choices"][0]["message"]["content"])
```

## 定价策略

| 层级 | 月费 | 可用模型 |
|------|------|----------|
| Premium | $8 | Grok-2 |
| Premium+ | $16 | Grok-2 + 优先访问 |
"""),
    ("月之暗面Kimi发布k1.5长思考模型",
     """月之暗面（Moonshot AI）发布了 Kimi k1.5 长思考模型，在数学、代码和推理任务上表现突出。

## 核心能力

Kimi k1.5 采用了 **长思维链（Long CoT）** 技术，能够进行深度推理后再给出答案。

## 代码能力示例

```python
# 请求 Kimi k1.5 API
import openai

client = openai.OpenAI(
    api_key="your_api_key",
    base_url="https://api.moonshot.cn/v1"
)

response = client.chat.completions.create(
    model="kimi-k1.5",
    messages=[
        {"role": "user", "content": "用Python实现一个红黑树"}
    ]
)
print(response.choices[0].message.content)
```

## 与其他模型对比

| 模型 | AIME 2024 | MATH-500 | LiveCodeBench |
|------|-----------|----------|---------------|
| Kimi k1.5 | 60.8 | 96.2 | 47.3 |
| o1-preview | 44.6 | 85.5 | 45.3 |
| Claude 3.5 | 16.0 | 78.3 | 38.9 |

更多详情见 [Moonshot AI 官网](https://www.moonshot.cn/)。
"""),
    ("欧盟AI法案正式生效",
     """欧盟《人工智能法案》（EU AI Act）正式生效，这是全球首部全面监管人工智能的综合性法律。

## 风险分级体系

| 风险等级 | 描述 | 示例 |
|----------|------|------|
| 不可接受风险 | 禁止 | 社会信用评分 |
| 高风险 | 严格监管 | 医疗诊断、招聘筛选 |
| 有限风险 | 透明度要求 | 聊天机器人 |
| 最小风险 | 自愿准则 | 垃圾邮件过滤 |

## 企业合规建议

```python
# AI系统风险评估检查清单
checklist = {
    "数据治理": "是否使用高质量、无偏见的数据？",
    "技术文档": "是否具备完整的技术文档？",
    "透明度": "是否向用户明确告知AI的使用？",
    "人工监督": "是否保留了人工干预的机制？",
    "准确性": "是否达到了宣称的性能指标？",
}

for item, question in checklist.items():
    print(f"{item}: {question}")
```

## 处罚措施

- 违反禁令：最高 **3500万欧元** 或全球年营业额 **7%**
- 违反义务：最高 **1500万欧元** 或全球年营业额 **3%**

详细信息请访问 [欧盟委员会官网](https://commission.europa.eu/)。
"""),
    ("英伟达发布Blackwell架构GPU",
     """英伟达在 GTC 2024 大会上发布了新一代 Blackwell 架构 GPU，专为生成式 AI 和高性能计算设计。

## 技术规格

| 指标 | H100 (Hopper) | B200 (Blackwell) | 提升倍数 |
|------|---------------|------------------|----------|
| 晶体管数量 | 800亿 | 2080亿 | 2.6x |
| FP8 算力 | 3958 TFLOPS | 4500 TFLOPS | 1.14x |
| 训练能效 | 基准 | 提升4倍 | 4x |

## DGX GB200 系统

```bash
# 使用 NVIDIA 容器运行时启动训练
docker run --gpus all \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -v $(pwd):/workspace \
  nvcr.io/nvidia/pytorch:24.03-py3 \
  python train.py --model llama3-70b
```

## 生态影响

Blackwell 的发布将进一步拉大英伟达在 AI 训练芯片领域的领先优势，详细规格请查看 [NVIDIA 官方文档](https://www.nvidia.com/)。
"""),
    ("智谱AI发布GLM-4开源模型",
     """智谱 AI 正式开源了 GLM-4-9B 模型，这是 GLM-4 系列的轻量开源版本，在中文理解和推理任务上表现出色。

## 模型特点

- 9B 参数量，适合消费级显卡部署
- 支持 **128K 长上下文**
- 原生支持 Function Calling 和 All Tools

## 快速体验

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "THUDM/glm-4-9b-chat"
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    trust_remote_code=True,
    torch_dtype="auto"
).cuda()

inputs = tokenizer("请用Python写一个快速排序", return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=512)
print(tokenizer.decode(outputs[0]))
```

## 开源协议

GLM-4-9B 采用宽松的商用授权，允许企业免费用于商业场景。

更多详情访问 [智谱 AI 开源仓库](https://github.com/THUDM/GLM-4)。
"""),
]


def seed_news(db, users, now):
    cats = ["行业动态", "产品发布", "融资并购", "政策法规", "技术突破", "学术进展"]
    items = []
    for i, (title, content) in enumerate(NEWS_CONTENTS):
        cat = random.choice(cats)
        summary = content.split("\n")[0][:200]
        cover = random.choice(COVER_IMAGES) if random.random() > 0.3 else None
        author = random.choice(users)
        created = rt(now, 45)
        items.append(News(
            title=title,
            content=content,
            content_type="markdown",
            summary=summary,
            category=cat,
            cover_image=cover,
            tags=f"AI,新闻,{cat}",
            is_published=True,
            author_id=author.id,
            created_at=created,
            updated_at=created,
            published_at=created,
            view_count=random.randint(100, 8000),
        ))
    for item in items:
        db.add(item)
    db.commit()
    for item in items:
        db.refresh(item)
    print(f"  News: {len(items)} items")
    return items


PRODUCT_CONTENTS = [
    ("DeepSeek-V3 API服务",
     """DeepSeek-V3 API 提供高性价比的大模型调用服务，支持对话、代码生成、推理等多种任务。

## 核心能力

| 功能 | 输入 | 输出 | 价格/百万tokens |
|------|------|------|------------------|
| 对话 | 文本 | 文本 | ¥2 |
| 代码补全 | 代码片段 | 补全建议 | ¥2 |
| FIM补全 | 前缀+后缀 | 中间代码 | ¥2 |

## 快速接入

```python
import openai

client = openai.OpenAI(
    api_key="your_deepseek_api_key",
    base_url="https://api.deepseek.com/v1"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "你好"}]
)
print(response.choices[0].message.content)
```

## 产品优势

- 成本仅为 GPT-4 的 **1/10**
- 支持 **64K 上下文**
- 推理速度可达 **60 tokens/s**
"""),
    ("智谱AI GLM-4企业版",
     """GLM-4 企业版是智谱 AI 面向企业客户推出的全方位大模型解决方案，覆盖对话、知识库、Agent 等场景。

## 产品矩阵

| 产品 | 适用场景 | 部署方式 |
|------|----------|----------|
| GLM-4-Plus | 通用对话 | 公有云API |
| GLM-4-9B | 边缘部署 | 私有化 |
| CodeGeeX | 代码辅助 | IDE插件 |
| CogView | 图像生成 | API/私有化 |

## 企业知识库接入

```python
from zhipuai import ZhipuAI

client = ZhipuAI(api_key="your_api_key")

response = client.chat.completions.create(
    model="glm-4-plus",
    messages=[
        {"role": "system", "content": "你是一位企业知识助手。"},
        {"role": "user", "content": "查询公司今年的OKR目标"}
    ],
    tools=[{
        "type": "retrieval",
        "retrieval": {
            "knowledge_id": "your_knowledge_base_id",
            "prompt_template": "从知识库中检索相关信息\n\n问题：{question}\n\n知识库内容：{knowledge}"
        }
    }]
)
```

## 客户案例

- 金融：某头部券商智能投研系统
- 教育：某在线教育平台 AI 助教
- 医疗：某三甲医院智能导诊助手
"""),
    ("百度文心一言企业版",
     """文心一言企业版（ERNIE Bot Enterprise）是百度基于文心大模型打造的企业级 AI 平台。

## 功能模块

```
┌─────────────────────────────────────┐
│         文心一言企业版               │
├──────────┬──────────┬───────────────┤
│ 智能客服  │ 内容创作  │ 数据分析      │
├──────────┼──────────┼───────────────┤
│ 知识管理  │ 代码助手  │ 办公自动化    │
└──────────┴──────────┴───────────────┘
```

## API 调用示例

```python
import requests

API_KEY = "your_baidu_api_key"
SECRET_KEY = "your_baidu_secret"

# 获取access_token
token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_KEY}&client_secret={SECRET_KEY}"
token = requests.get(token_url).json()["access_token"]

# 调用文心API
url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={token}"
response = requests.post(url, json={
    "messages": [{"role": "user", "content": "你好"}]
})
print(response.json()["result"])
```

## 定价

| 版本 | 月费 | 包含token |
|------|------|-----------|
| 基础版 | ¥5000 | 1000万 |
| 专业版 | ¥20000 | 5000万 |
| 旗舰版 | 定制 | 无限 |
"""),
    ("阿里云通义千问",
     """通义千问（Qwen）是阿里云自主研发的大语言模型系列，开源版本在业界广受好评。

## 模型系列

| 模型 | 参数 | 特点 | 适用场景 |
|------|------|------|----------|
| Qwen-Max | 未公开 | 最强能力 | 复杂任务 |
| Qwen-Plus | 未公开 | 均衡选择 | 通用场景 |
| Qwen-Turbo | 未公开 | 高性价比 | 高频调用 |
| Qwen2-72B | 72B | 开源最强 | 私有化部署 |
| Qwen2-VL | 7B/72B | 视觉理解 | 多模态应用 |

## 阿里云百炼平台接入

```python
from http import HTTPStatus
from dashscope import Generation

result = Generation.call(
    model="qwen-max",
    messages=[{"role": "user", "content": "你好"}]
)
if result.status_code == HTTPStatus.OK:
    print(result.output.text)
else:
    print(result.message)
```

## 开源生态

通义千问开源模型累计下载量超过 **3000万次**，在 HuggingFace 上长期位居中文模型榜首。
"""),
    ("字节跳动豆包大模型",
     """豆包大模型是字节跳动推出的企业级大模型服务平台，依托火山引擎提供稳定高效的推理服务。

## 产品体系

| 模型 | 能力 | 特色 |
|------|------|------|
| Doubao-pro | 通用对话 | 中文理解能力强 |
| Doubao-lite | 轻量对话 | 延迟低、成本低 |
| Doubao-vision | 视觉理解 | 图文混合输入 |
| Doubao-embedding | 文本向量化 | 检索效果好 |
| Doubao-tts | 语音合成 | 音色自然 |

## 快速接入

```python
from volcengine.maas import MaasService

maas = MaasService("ark.cn-beijing.volces.com", "cn-beijing")
maas.set_ak("your_access_key")
maas.set_sk("your_secret_key")

resp = maas.chat(
    model="doubao-pro-32k",
    messages=[{"role": "user", "content": "你好"}]
)
print(resp.choice.message.content)
```

## 应用场景

- 抖音/飞书智能客服
- 内容审核与推荐
- 番茄小说 AI 写作助手
"""),
    ("商汤日日新SenseNova",
     """商汤日日新（SenseNova）是商汤科技打造的大模型体系，包含语言、多模态、文生图、文生视频等多个模型。

## 模型能力

| 模型 | 类型 | 核心能力 |
|------|------|----------|
| 商量 | 语言 | 对话、推理、代码 |
| 秒画 | 图像生成 | 文生图、图生图 |
| 如影 | 数字人 | 视频生成、口型同步 |
| 琼宇 | 3D生成 | 场景重建、物体建模 |
| 格物 | 具身智能 | 机器人控制 |

## 代码示例

```python
import requests

url = "https://api.sensenova.cn/v1/llm/chat-completions"
headers = {
    "Authorization": "Bearer your_api_key",
    "Content-Type": "application/json"
}
data = {
    "model": "SenseChat-5",
    "messages": [{"role": "user", "content": "你好"}]
}
response = requests.post(url, headers=headers, json=data)
print(response.json()["data"]["choices"][0]["message"]["content"])
```

## 行业落地

商汤大模型已在智慧城市、智能驾驶、智慧医疗等领域实现规模化商用。
"""),
    ("讯飞星火认知大模型",
     """讯飞星火认知大模型是科大讯飞推出的新一代 AI 大模型，在中文理解和语音交互方面具有独特优势。

## 核心能力

| 维度 | 能力描述 | 行业排名 |
|------|----------|----------|
| 文本生成 | 公文写作、创意文案 | 第一梯队 |
| 知识问答 | 百科知识、专业领域 | 第一梯队 |
| 逻辑推理 | 数学计算、逻辑分析 | 第一梯队 |
| 多模态 | 语音、图像理解 | 领先 |

## 语音交互示例

```python
from xfyun import SparkApi

appid = "your_appid"
api_secret = "your_api_secret"
api_key = "your_api_key"

# 初始化WebSocket连接
ws_url = SparkApi.create_url(appid, api_key, api_secret)
# 发送语音流并获取实时识别结果
```

## 硬件生态

星火大模型已集成到科大讯飞的学习机、办公本、录音笔等硬件产品中，实现端侧 AI 能力。
"""),
    ("腾讯混元大模型",
     """腾讯混元大模型（Hunyuan）是腾讯自研的通用大语言模型，已广泛应用于微信、腾讯文档、腾讯会议等产品。

## 产品接入矩阵

| 腾讯产品 | 接入功能 | 效果 |
|----------|----------|------|
| 微信读书 | AI问书 | 实时解答书中疑问 |
| 腾讯文档 | AI助手 | 智能写作、表格分析 |
| 腾讯会议 | AI小助手 | 会议纪要、待办提取 |
| 企业微信 | 智能客服 | 自动回复、知识检索 |

## API 调用

```python
import requests

url = "https://hunyuan.tencentcloudapi.com"
headers = {
    "Authorization": "TC3-HMAC-SHA256 your_signature",
    "Content-Type": "application/json"
}
payload = {
    "Model": "hunyuan-lite",
    "Messages": [{"Role": "user", "Content": "你好"}]
}
response = requests.post(url, headers=headers, json=payload)
print(response.json()["Choices"][0]["Message"]["Content"])
```

## 模型版本

- hunyuan-pro：旗舰版，最强能力
- hunyuan-standard：标准版，均衡选择
- hunyuan-lite：轻量版，免费使用
"""),
    ("月之暗面Kimi智能助手",
     """Kimi 是月之暗面（Moonshot AI）推出的智能助手产品，以超长上下文和优秀的文档理解能力著称。

## 核心功能

| 功能 | 描述 | 限制 |
|------|------|------|
| 长文本处理 | 支持整本书、长论文 | 200万字 |
| 文件解析 | PDF、Word、Excel、PPT | 50个文件/次 |
| 网页总结 | 自动提取关键信息 | 无限制 |
| 联网搜索 | 实时信息检索 | 自动触发 |

## 使用示例

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_api_key",
    base_url="https://api.moonshot.cn/v1"
)

# 上传文件
file = client.files.create(file=open("paper.pdf", "rb"), purpose="file-extract")

# 基于文件内容提问
response = client.chat.completions.create(
    model="moonshot-v1-128k",
    messages=[
        {"role": "system", "content": f"基于以下文件内容回答问题：{file.id}"},
        {"role": "user", "content": "这篇论文的主要贡献是什么？"}
    ]
)
print(response.choices[0].message.content)
```

## 产品定位

Kimi 主打 **长文本 + 文件处理** 场景，是学术研究和办公自动化的得力助手。
"""),
    ("MiniMaxabab大模型",
     """MiniMax 是国内领先的通用人工智能科技公司，旗下 abab 系列大模型支持文本、语音、视觉多模态能力。

## 模型家族

| 模型 | 参数规模 | 上下文长度 | 特点 |
|------|----------|------------|------|
| abab6.5 | 万亿级 | 200k | 中文能力强 |
| abab6.5s | 千亿级 | 200k | 高性价比 |
| abab5.5 | 千亿级 | 8k | 稳定成熟 |
| speech-01 | - | - | 语音合成 |
| video-01 | - | - | 视频生成 |

## API接入

```python
import requests

url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
headers = {
    "Authorization": "Bearer your_api_key",
    "Content-Type": "application/json"
}
data = {
    "model": "abab6.5-chat",
    "messages": [{"role": "user", "content": "你好"}]
}
response = requests.post(url, headers=headers, json=data)
print(response.json()["choices"][0]["message"]["content"])
```

## 应用场景

MiniMax 为海螺 AI、星野等 C 端产品提供底层模型能力，日调用量超过数十亿次。
"""),
]


def seed_products(db, users, now):
    cats = ["AI工具", "SaaS平台", "智能硬件", "数据分析", "聊天机器人", "图像生成", "大模型API"]
    items = []
    for i, (title, content) in enumerate(PRODUCT_CONTENTS):
        cat = random.choice(cats)
        summary = content.split("\n")[0][:200]
        cover = random.choice(COVER_IMAGES) if random.random() > 0.3 else None
        author = random.choice(users)
        created = rt(now, 50)
        items.append(Product(
            title=title,
            content=content,
            content_type="markdown",
            summary=summary,
            category=cat,
            cover_image=cover,
            tags=f"AI产品,{cat}",
            is_published=True,
            author_id=author.id,
            created_at=created,
            updated_at=created,
            published_at=created,
            view_count=random.randint(200, 12000),
        ))
    for item in items:
        db.add(item)
    db.commit()
    for item in items:
        db.refresh(item)
    print(f"  Products: {len(items)} items")
    return items


SOLUTION_CONTENTS = [
    ("智慧医疗AI辅助诊断系统",
     """基于深度学习的医疗影像辅助诊断系统，能够自动识别 CT、MRI、X光片中的异常病灶。

## 系统架构

```
影像采集 → 预处理 → AI推理 → 结果展示 → 医生复核
```

## 核心模型

| 模型 | 适用部位 | 准确率 | 数据集规模 |
|------|----------|--------|------------|
| LungNet | 肺部CT | 96.5% | 50,000例 |
| BrainSeg | 脑部MRI | 94.2% | 30,000例 |
| BoneX | 骨折X光 | 92.8% | 80,000例 |
| EyeCheck | 眼底照片 | 98.1% | 120,000例 |

## 部署代码示例

```python
from medical_ai import DiagnosisEngine

engine = DiagnosisEngine(model_path="./models/lungnet_v3.pt")

def diagnose_ct(image_path):
    result = engine.predict(image_path)
    return {
        "finding": result.label,
        "confidence": result.confidence,
        "heatmap": result.attention_map,
        "recommendation": result.suggested_followup
    }
```

## 落地效果

在某三甲医院的实际应用中，该系统帮助放射科医生将阅片效率提升了 **40%**，漏诊率降低了 **25%**。
"""),
    ("智能金融风控平台",
     """面向银行、保险、证券等金融机构的智能风控解决方案，基于机器学习和知识图谱技术实现全方位风险识别。

## 功能模块

| 模块 | 功能 | 技术栈 |
|------|------|--------|
| 反欺诈 | 交易异常检测 | XGBoost + 图神经网络 |
| 信用评估 | 用户画像评分 | 宽深网络 + 特征工程 |
| 合规审查 | 文档智能审核 | BERT + 规则引擎 |
| 舆情监控 | 实时风险预警 | NLP + 流计算 |

## 反欺诈模型示例

```python
import torch
import torch.nn as nn

class FraudGNN(nn.Module):
    def __init__(self, in_dim, hidden_dim, out_dim):
        super().__init__()
        self.conv1 = GraphConv(in_dim, hidden_dim)
        self.conv2 = GraphConv(hidden_dim, hidden_dim)
        self.classifier = nn.Linear(hidden_dim, out_dim)

    def forward(self, g, features):
        h = torch.relu(self.conv1(g, features))
        h = torch.relu(self.conv2(g, h))
        return self.classifier(h)
```

## 业务价值

- 欺诈识别准确率：**99.2%**
- 误报率降低至 **0.3%**
- 信贷审批效率提升 **10倍**
"""),
    ("智能制造质量检测方案",
     """基于计算机视觉的工业质检解决方案，替代传统人工目检，实现产线 7x24 小时全自动缺陷检测。

## 检测能力

| 缺陷类型 | 检测精度 | 处理速度 | 适用行业 |
|----------|----------|----------|----------|
| 表面划痕 | 0.01mm | 50件/秒 | 3C电子 |
| 焊点虚焊 | 99.5% | 30件/秒 | 汽车电子 |
| 尺寸偏差 | ±0.005mm | 100件/秒 | 精密加工 |
| 色差检测 | ΔE<0.5 | 60件/秒 | 纺织印染 |

## 边缘部署

```python
import cv2
import tensorrt as trt

# 加载TensorRT引擎
logger = trt.Logger(trt.Logger.WARNING)
with open("defect_detector.trt", "rb") as f:
    runtime = trt.Runtime(logger)
    engine = runtime.deserialize_cuda_engine(f.read())

context = engine.create_execution_context()

def infer(frame):
    input_buffer = preprocess(frame)
    output_buffer = allocate_output()
    context.execute_v2([input_buffer, output_buffer])
    return postprocess(output_buffer)
```

## ROI分析

- 单条产线年节省质检人力成本：**80万元**
- 缺陷漏检率从 **3%** 降至 **0.1%**
- 客户投诉率下降 **60%**
"""),
    ("智慧教育个性化学习平台",
     """基于大模型和知识图谱的个性化学习平台，为 K12 和职业教育提供自适应学习路径规划。

## 系统功能

```
学情诊断 → 知识图谱建模 → 个性化推荐 → 学习效果评估
```

## 核心算法

| 算法 | 用途 | 效果 |
|------|------|------|
| 认知诊断(IRT) | 能力评估 | 精准定位薄弱点 |
| 知识追踪(DKT) | 学习状态预测 | 预测准确率85% |
| 协同过滤 | 内容推荐 | 点击率提升30% |
| 生成式AI | 题目生成 | 支持多学科 |

## 智能出题示例

```python
from edu_ai import QuestionGenerator

gen = QuestionGenerator(model="glm-4-edu-v2")

question = gen.generate(
    topic="一元二次方程",
    difficulty="中等",
    question_type="解答题",
    student_level="初二"
)
print(question.stem)
print(question.answer)
print(question.explanation)
```

## 应用成果

在某省重点中学的试点中，使用该平台的学生平均成绩提升了 **15%**，学习效率提高了 **25%**。
"""),
    ("智能客服机器人解决方案",
     """基于大模型和 RAG 技术的智能客服解决方案，支持多轮对话、情感分析、意图识别和知识库问答。

## 技术架构

| 组件 | 技术 | 功能 |
|------|------|------|
| 对话引擎 | GPT-4/Claude/GLM | 自然语言理解与生成 |
| 知识库 | 向量数据库 + RAG | 精准知识检索 |
| 意图识别 | BERT微调 | 用户需求分类 |
| 情感分析 | RoBERTa | 情绪识别与安抚 |
| 多轮管理 | 状态机 + LLM | 上下文跟踪 |

## 快速接入

```python
from smart_service import CustomerServiceBot

bot = CustomerServiceBot(
    llm="glm-4-plus",
    knowledge_base="./kb/ecommerce_v3",
    fallback_strategy="human_transfer"
)

response = bot.chat(
    user_id="user_12345",
    message="我的订单什么时候发货？",
    session_history=[]
)
print(response.answer)
print(response.suggested_actions)
```

## 效果指标

- 问题解决率：**92%**
- 平均响应时间：**1.2秒**
- 人工转接率：**8%**
- 客户满意度：**4.6/5.0**
"""),
    ("智慧城市交通大脑",
     """基于多源数据融合和强化学习的城市交通管理系统，实现信号灯智能控制、拥堵预测和事故预警。

## 数据融合

| 数据源 | 频率 | 用途 |
|--------|------|------|
| 卡口视频 | 实时 | 车流量统计 |
| GPS浮动车 | 30秒 | 轨迹分析 |
| 地磁线圈 | 实时 | 路口 occupancy |
| 气象数据 | 小时 | 特殊天气预警 |
| 事件上报 | 实时 | 交通事故检测 |

## 信号控制算法

```python
import gym
from stable_baselines3 import PPO

class TrafficEnv(gym.Env):
    def __init__(self, intersection_id):
        self.intersection = load_intersection(intersection_id)
        self.state_dim = 16  # 各方向车流
        self.action_dim = 4  # 相位选择

    def step(self, action):
        set_traffic_light_phase(self.intersection, action)
        wait_time = simulate_one_step()
        reward = -wait_time
        return self.observe(), reward, done, {}

model = PPO("MlpPolicy", env)
model.learn(total_timesteps=1_000_000)
```

## 实施效果

在某新一线城市的应用中：
- 高峰期平均车速提升 **18%**
- 停车次数减少 **25%**
- 碳排放降低 **12%**
"""),
    ("零售电商智能选品系统",
     """基于多模态大模型和时序预测的智能选品系统，帮助电商平台和连锁零售商优化商品结构。

## 核心能力

| 模块 | 输入 | 输出 | 算法 |
|------|------|------|------|
| 趋势预测 | 历史销量+外部数据 | 未来30天销量 | Transformer |
| 竞品分析 | 商品图片+描述 | 竞品对标报告 | CLIP + LLM |
| 定价优化 | 成本+竞品价格 | 建议售价区间 | 强化学习 |
| 陈列优化 | 货架照片 | 陈列建议 | 目标检测 |

## 代码示例

```python
from retail_ai import AssortmentOptimizer

optimizer = AssortmentOptimizer(
    store_id="store_beijing_001",
    category="休闲零食"
)

recommendations = optimizer.optimize(
    constraints={
        "sku_count": 120,
        "min_margin": 0.25,
        "max_inventory_cost": 50000
    }
)

for sku in recommendations:
    print(f"{sku.name}: 预测销量={sku.forecast_sales}, 建议定价=¥{sku.suggested_price}")
```

## 商业价值

- 库存周转天数缩短 **20%**
- 缺货率降低至 **3%**
- 毛利率提升 **2.5个百分点**
"""),
    ("法律AI智能合同审查",
     """面向律所和企业法务部门的智能合同审查系统，基于法律大模型自动识别风险条款、比对版本差异。

## 审查维度

| 维度 | 检查项 | 示例 |
|------|--------|------|
| 主体风险 | 签约方资质 | 空壳公司识别 |
| 条款风险 | 违约责任 | 单方解除权 |
| 合规风险 | 数据保护 | GDPR/个人信息保护法 |
| 商业风险 | 付款条件 | 账期过长 |

## 审查报告生成

```python
from legal_ai import ContractReviewer

reviewer = ContractReviewer(
    model="legal-glm-4-v2",
    knowledge_base="./legal_kb/commercial_contracts"
)

report = reviewer.review(
    contract_path="./nda_draft_v3.docx",
    contract_type="保密协议",
    party_role="甲方",
    risk_level="strict"
)

for risk in report.risks:
    print(f"[{risk.severity}] {risk.clause}: {risk.description}")
    print(f"  建议修改: {risk.suggestion}")
```

## 效率提升

- 单份合同审查时间从 **4小时** 缩短至 **15分钟**
- 风险识别覆盖率：**95%**
- 律师工作效率提升 **5倍**
"""),
    ("能源电力智能巡检方案",
     """面向电网、风电、光伏电站的智能巡检解决方案，融合无人机、机器人和边缘 AI 技术。

## 巡检场景

| 场景 | 设备 | AI能力 | 检出率 |
|------|------|--------|--------|
| 输电线路 | 无人机+可见光/红外 | 绝缘子缺陷、导线断股 | 96% |
| 变电站 | 轨道机器人 | 仪表读数、设备发热 | 98% |
| 风电叶片 | 无人机+激光雷达 | 裂纹、雷击损伤 | 94% |
| 光伏面板 | 无人机+红外 | 热斑、隐裂 | 97% |

## 边缘推理

```python
import onnxruntime as ort

session = ort.InferenceSession("inspection_model.onnx",
    providers=["CUDAExecutionProvider", "CPUExecutionProvider"])

def detect_defect(image):
    inputs = {session.get_inputs()[0].name: preprocess(image)}
    outputs = session.run(None, inputs)
    boxes, scores, labels = postprocess(outputs)
    return format_results(boxes, scores, labels)
```

## 实施效益

- 巡检效率提升 **8倍**
- 人工巡检成本降低 **70%**
- 设备故障预测准确率达 **85%**
"""),
    ("农业AI精准种植平台",
     """基于物联网、卫星遥感和大模型的智慧农业解决方案，实现作物生长监测、病虫害预警和精准灌溉。

## 技术体系

```
卫星遥感 → 无人机巡田 → 地面传感器 → 边缘计算 → 云端大模型
```

## 核心功能

| 功能 | 技术 | 效果 |
|------|------|------|
| 长势监测 | NDVI指数+时序分析 | 精准到株 |
| 病害识别 | 叶片图像分类 | 准确率95% |
| 产量预测 | 多源数据融合 | 误差<5% |
| 灌溉推荐 | 土壤墒情+气象预报 | 节水30% |

## 示例代码

```python
from agri_ai import FarmManager

farm = FarmManager(farm_id="farm_hebei_001")

# 获取地块健康度评分
health = farm.get_field_health(field_id="A3")
print(f"地块A3健康度: {health.score}/100")
print(f"主要问题: {health.main_issue}")
print(f"建议措施: {health.recommendations}")

# 生成本周灌溉计划
schedule = farm.generate_irrigation_plan(days=7)
for day in schedule:
    print(f"{day.date}: 灌溉量 {day.water_mm}mm, 预计耗时 {day.duration_min}分钟")
```

## 经济效益

在某大型农场的应用中：
- 化肥使用量降低 **20%**
- 灌溉用水节约 **30%**
- 作物产量提升 **12%**
"""),
]


def seed_solutions(db, users, now):
    cats = ["医疗健康", "教育培训", "金融保险", "智能制造", "智慧城市", "零售电商", "法律服务", "能源电力", "智慧农业"]
    items = []
    for i, (title, content) in enumerate(SOLUTION_CONTENTS):
        cat = random.choice(cats)
        summary = content.split("\n")[0][:200]
        cover = random.choice(COVER_IMAGES) if random.random() > 0.3 else None
        author = random.choice(users)
        created = rt(now, 55)
        items.append(Solution(
            title=title,
            content=content,
            content_type="markdown",
            summary=summary,
            category=cat,
            cover_image=cover,
            tags=f"AI解决方案,{cat}",
            is_published=True,
            author_id=author.id,
            created_at=created,
            updated_at=created,
            published_at=created,
            view_count=random.randint(150, 9000),
        ))
    for item in items:
        db.add(item)
    db.commit()
    for item in items:
        db.refresh(item)
    print(f"  Solutions: {len(items)} items")
    return items


PROJECTS_DATA = [
    {
        "title": "AI智能写作助手",
        "description": "基于大模型的智能写作平台，支持文章生成、润色、续写等功能。",
        "content": """# AI智能写作助手

## 项目简介

AI智能写作助手是一款面向内容创作者的 SaaS 产品，基于 GPT-4 和自研大模型提供全流程写作辅助。

## 技术架构

| 层级 | 技术栈 | 说明 |
|------|--------|------|
| 前端 | Vue3 + TypeScript + Element Plus | 响应式写作界面 |
| 后端 | FastAPI + SQLAlchemy | RESTful API服务 |
| 模型层 | GPT-4 / Claude / GLM-4 | 多模型路由 |
| 存储 | PostgreSQL + Redis | 持久化与缓存 |
| 部署 | Docker + K8s | 容器化编排 |

## 核心功能

```python
@app.post("/api/write/continue")
async def continue_writing(req: ContinueRequest):
    context = await get_document_context(req.doc_id)
    prompt = build_continuation_prompt(context, req.style)
    response = await llm_router.generate(
        model=req.model or "gpt-4",
        prompt=prompt,
        max_tokens=512,
        temperature=0.7
    )
    return {
        "text": response.text,
        "alternatives": response.alternatives,
        "confidence": response.confidence
    }
```

## 项目成果

- 注册用户超过 **50万**
- 日活跃用户数 **8万+**
- 用户满意度 **4.8/5.0**
""",
        "tech_stack": ["Vue3", "FastAPI", "Python", "PostgreSQL", "Redis", "Docker"],
        "category": "AI应用",
        "demo_url": "https://demo.aiwriter.example.com",
        "repo_url": "https://github.com/example/ai-writer",
    },
    {
        "title": "企业知识库问答系统",
        "description": "基于RAG技术的企业内部知识库问答平台，支持文档自动解析和精准检索。",
        "content": """# 企业知识库问答系统

## 系统概述

帮助企业构建私有知识库，员工可以通过自然语言快速获取内部文档、制度和流程信息。

## 数据处理流程

```
文档上传 → 格式解析 → 文本分块 → 向量化 → 索引存储 → 语义检索 → LLM生成答案
```

## 技术实现

```python
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

class KnowledgeBase:
    def __init__(self, collection_name):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-large-zh-v1.5"
        )
        self.store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings
        )
    def add_documents(self, docs):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=50
        )
        chunks = splitter.split_documents(docs)
        self.store.add_documents(chunks)
    def query(self, question, k=5):
        return self.store.similarity_search(question, k=k)
```

## 部署规模

| 指标 | 数值 |
|------|------|
| 支持文档格式 | PDF, Word, PPT, Excel, Markdown |
| 单文档最大页数 | 1000页 |
| 并发查询 | 500 QPS |
| 平均响应时间 | <2秒 |
""",
        "tech_stack": ["React", "FastAPI", "Python", "ChromaDB", "LangChain", "PostgreSQL"],
        "category": "企业应用",
        "demo_url": "https://demo.kbqa.example.com",
        "repo_url": "https://github.com/example/kbqa-system",
    },
    {
        "title": "AI图像生成平台",
        "description": "基于Stable Diffusion的在线图像生成平台，支持文生图、图生图和风格迁移。",
        "content": """# AI图像生成平台

## 产品特色

- 支持 **100+** 艺术风格
- 内置提示词优化器
- 支持 ControlNet 精准控制
- 4K 超分辨率放大

## 模型服务架构

```python
from diffusers import StableDiffusionPipeline, ControlNetModel
import torch

class ImageGenerationService:
    def __init__(self):
        self.base_model = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16
        ).to("cuda")
        self.controlnet = ControlNetModel.from_pretrained(
            "lllyasviel/sd-controlnet-canny",
            torch_dtype=torch.float16
        ).to("cuda")
    def generate(self, prompt, negative_prompt, width, height, steps):
        image = self.base_model(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width, height=height,
            num_inference_steps=steps,
            guidance_scale=7.5
        ).images[0]
        return image
```

## 性能优化

| 优化手段 | 效果 |
|----------|------|
| TensorRT | 推理速度提升3倍 |
| 模型量化 | 显存占用降低50% |
| 批量推理 | 吞吐量提升4倍 |
| 缓存机制 | 重复请求零延迟 |
""",
        "tech_stack": ["Vue3", "FastAPI", "Python", "PyTorch", "StableDiffusion", "CUDA"],
        "category": "AIGC",
        "demo_url": "https://demo.aigc.example.com",
        "repo_url": "https://github.com/example/aigc-platform",
    },
    {
        "title": "智能客服机器人",
        "description": "基于大模型的多渠道智能客服系统，支持网页、微信、APP等多端接入。",
        "content": """# 智能客服机器人

## 系统架构

```
用户端 → 消息网关 → 意图识别 → 对话管理 → 知识检索 → 答案生成 → 多轮交互
```

## 核心模块

```python
class CustomerServiceBot:
    def __init__(self):
        self.intent_classifier = IntentBERT()
        self.dialog_manager = DialogManager()
        self.kb_retriever = KGRetriever()
        self.response_generator = ResponseGenerator()
    async def handle_message(self, user_id, message, channel):
        intent = self.intent_classifier.predict(message)
        state = self.dialog_manager.update_state(user_id, intent, message)
        if intent == "knowledge_query":
            docs = self.kb_retriever.search(message, top_k=3)
            context = format_docs(docs)
        else:
            context = ""
        response = await self.response_generator.generate(
            message=message, intent=intent,
            state=state, context=context
        )
        return response
```

## 运营数据

| 指标 | 数值 |
|------|------|
| 接入渠道 | 网页、微信、APP、小程序 |
| 日均对话量 | 50万+ |
| 问题解决率 | 91% |
| 平均响应时间 | 1.5秒 |
| 客户满意度 | 4.5/5.0 |
""",
        "tech_stack": ["React", "Node.js", "Python", "Redis", "Elasticsearch", "WebSocket"],
        "category": "AI应用",
        "demo_url": "https://demo.chatbot.example.com",
        "repo_url": "https://github.com/example/smart-chatbot",
    },
    {
        "title": "医疗影像辅助诊断",
        "description": "基于深度学习的肺部CT影像分析系统，辅助医生进行结节检测和良恶性判断。",
        "content": """# 医疗影像辅助诊断系统

## 临床价值

帮助放射科医生提高肺结节检出率，减少漏诊和误诊。

## 算法架构

```python
import torch
import torch.nn as nn
from monai.networks.nets import UNet

class LungNoduleDetector(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = UNet(
            spatial_dims=3,
            in_channels=1,
            out_channels=2,
            channels=(16, 32, 64, 128, 256),
            strides=(2, 2, 2, 2)
        )
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool3d(1),
            nn.Flatten(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 2)
        )
    def forward(self, x):
        features = self.backbone(x)
        return self.classifier(features)
```

## 数据集与训练

| 数据集 | 样本量 | 用途 |
|--------|--------|------|
| LUNA16 | 888例 | 预训练 |
| 院内数据 | 12,000例 | 微调 |
| 多中心数据 | 8,000例 | 泛化验证 |

## 临床验证结果

- 敏感性：**96.8%**
- 特异性：**92.3%**
- AUC：**0.984**
""",
        "tech_stack": ["Vue3", "FastAPI", "Python", "PyTorch", "MONAI", "PostgreSQL"],
        "category": "智慧医疗",
        "demo_url": "https://demo.medical.example.com",
        "repo_url": "https://github.com/example/medical-ai",
    },
    {
        "title": "自动驾驶数据标注平台",
        "description": "面向自动驾驶场景的多模态数据标注平台，支持2D/3D标注、语义分割和轨迹预测。",
        "content": """# 自动驾驶数据标注平台

## 标注能力

| 类型 | 说明 | 工具 |
|------|------|------|
| 2D框标注 | 车辆、行人、交通标志 | 矩形/多边形 |
| 3D框标注 | 激光雷达点云目标 | 立方体 |
| 语义分割 | 像素级场景理解 | 画笔/多边形 |
| 关键点 | 人体姿态、车辆部件 | 关键点链 |
| 轨迹 | 时序运动预测 | 插值工具 |

## 平台架构

```python
from flask import Flask, request
from annotation_engine import AnnotationEngine

app = Flask(__name__)
engine = AnnotationEngine()

@app.route("/api/tasks/<task_id>/annotations", methods=["POST"])
def save_annotations(task_id):
    data = request.json
    result = engine.save_annotations(
        task_id=task_id,
        frame_id=data["frame_id"],
        annotations=data["annotations"],
        annotator_id=data["user_id"]
    )
    if result.annotations_count > 10:
        qc_result = engine.quality_check(task_id)
        if qc_result.score < 0.85:
            engine.flag_for_review(task_id)
    return {"success": True, "qc_score": result.qc_score}
```

## 处理规模

- 日均处理帧数：**50万帧**
- 标注员并发数：**2000人**
- 支持数据格式：KITTI, COCO, Waymo, nuScenes
""",
        "tech_stack": ["React", "Flask", "Python", "OpenCV", "Three.js", "MongoDB"],
        "category": "自动驾驶",
        "demo_url": "https://demo.adas.example.com",
        "repo_url": "https://github.com/example/adas-annotation",
    },
    {
        "title": "实时语音转写系统",
        "description": "支持多语种、多方言的实时语音转文字系统，适用于会议记录、直播字幕等场景。",
        "content": """# 实时语音转写系统

## 技术特点

- 支持 **中文、英文、日文、韩文** 等 20+ 语种
- 支持普通话、粤语、四川话等方言
- 端到端延迟 **< 300ms**
- 支持说话人分离和智能标点

## 模型架构

```python
import torch
import torch.nn as nn

class ConformerASR(nn.Module):
    def __init__(self, input_dim, vocab_size):
        super().__init__()
        self.encoder = ConformerEncoder(
            input_dim=input_dim,
            num_blocks=12,
            conv_kernel_size=31
        )
        self.decoder = TransformerDecoder(
            vocab_size=vocab_size,
            num_blocks=6
        )
    def forward(self, audio, audio_lengths, targets=None):
        encoder_out, encoder_lengths = self.encoder(audio, audio_lengths)
        if targets is not None:
            return self.decoder(encoder_out, encoder_lengths, targets)
        else:
            return self.decoder.beam_search(encoder_out, encoder_lengths)
```

## 性能指标

| 场景 | 字错率(CER) | 实时率(RTF) |
|------|-------------|-------------|
| 新闻播报 | 2.1% | 0.05 |
| 会议访谈 | 5.8% | 0.08 |
| 直播带货 | 8.3% | 0.10 |
| 电话客服 | 6.5% | 0.07 |
""",
        "tech_stack": ["Vue3", "FastAPI", "Python", "PyTorch", "WebRTC", "Redis"],
        "category": "AI应用",
        "demo_url": "https://demo.asr.example.com",
        "repo_url": "https://github.com/example/realtime-asr",
    },
    {
        "title": "金融量化交易策略平台",
        "description": "基于机器学习的量化交易策略研究与回测平台，支持多因子模型和强化学习策略。",
        "content": """# 金融量化交易策略平台

## 系统架构

```
行情数据 → 特征工程 → 模型训练 → 策略回测 → 模拟交易 → 实盘执行
```

## 策略示例：多因子选股

```python
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

class MultiFactorStrategy:
    def __init__(self):
        self.model = GradientBoostingRegressor(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05
        )
        self.factors = [
            'pe_ratio', 'pb_ratio', 'roe', 'momentum_20d',
            'volatility_60d', 'turnover_20d', 'market_cap'
        ]
    def train(self, features, returns):
        self.model.fit(features[self.factors], returns)
    def predict(self, features):
        scores = self.model.predict(features[self.factors])
        return pd.Series(scores, index=features.index)
    def generate_signals(self, features, top_n=50):
        scores = self.predict(features)
        return scores.nlargest(top_n).index.tolist()
```

## 回测结果

| 策略 | 年化收益 | 最大回撤 | 夏普比率 |
|------|----------|----------|----------|
| 多因子选股 | 28.5% | 15.2% | 1.85 |
| 动量策略 | 22.3% | 18.5% | 1.42 |
| 强化学习 | 35.1% | 20.8% | 1.92 |
""",
        "tech_stack": ["Vue3", "FastAPI", "Python", "PyTorch", "Pandas", "Redis"],
        "category": "金融科技",
        "demo_url": "https://demo.quant.example.com",
        "repo_url": "https://github.com/example/quant-platform",
    },
]


def seed_projects(db, users, now):
    items = []
    for i, p in enumerate(PROJECTS_DATA):
        cover = random.choice(COVER_IMAGES) if random.random() > 0.3 else None
        author = random.choice(users)
        created = rt(now, 70)
        items.append(Project(
            title=p["title"],
            description=p["description"],
            content=p["content"],
            cover_image=cover,
            tech_stack=p["tech_stack"],
            category=p["category"],
            demo_url=p["demo_url"],
            repo_url=p["repo_url"],
            sort_order=i,
            is_published=True,
            author_id=author.id,
            created_at=created,
            updated_at=created,
            likes_count=random.randint(10, 500),
        ))
    for item in items:
        db.add(item)
    db.commit()
    for item in items:
        db.refresh(item)
    print(f"  Projects: {len(items)} items")
    return items


MOMENTS_DATA = [
    {
        "content": "刚刚体验了一下最新的GPT-4o语音对话功能，真的太惊艳了！延迟极低，而且能理解语气和情绪。AI的进步速度真的超出想象。",
        "images": ["https://picsum.photos/seed/moment1/600/400", "https://picsum.photos/seed/moment2/600/400"],
    },
    {
        "content": "参加完智源大会的AI安全论坛，感受颇深。大模型的安全性不仅是技术问题，更是社会问题。我们需要在技术发展的同时，建立完善的治理框架。",
        "images": ["https://picsum.photos/seed/moment3/600/400"],
    },
    {
        "content": "周末用LoRA微调了一个属于自己的风格模型，效果还不错！只需要20张图片和一块RTX 4090，就能生成特定风格的插画。开源生态让AI创作变得越来越平民化。",
        "images": ["https://picsum.photos/seed/moment4/600/400", "https://picsum.photos/seed/moment5/600/400", "https://picsum.photos/seed/moment6/600/400"],
    },
    {
        "content": "公司内部的RAG知识库项目终于上线了！从文档解析到向量检索，再到大模型生成答案，整个链路跑通的那一刻真的很有成就感。现在同事们查资料方便多了。",
        "images": [],
    },
    {
        "content": "读了DeepSeek-V3的技术报告，训练成本只有557万美元，这个性价比太惊人了。MoE架构的高效性再次被证明，期待更多国产大模型的突破！",
        "images": ["https://picsum.photos/seed/moment7/600/400"],
    },
    {
        "content": "在杭州西湖边写代码，风景太美了。用FastAPI重构了一个微服务，性能提升了3倍。好的环境确实能激发创造力，推荐大家偶尔换个地方工作。",
        "images": ["https://picsum.photos/seed/moment8/600/400", "https://picsum.photos/seed/moment9/600/400"],
    },
    {
        "content": "今天面试了一个应届生，他对Transformer的理解非常深入，甚至自己实现了一个简化版。看到年轻一代的AI人才成长这么快，真的很欣慰。",
        "images": [],
    },
    {
        "content": "PyTorch 2.0的torch.compile真的是神器，模型推理速度提升了40%，而且只需要加一行代码。编译器优化在深度学习领域终于要开花结果了。",
        "images": ["https://picsum.photos/seed/moment10/600/400"],
    },
    {
        "content": "和团队一起完成了智慧交通项目的POC验证，AI信号控制让路口通行效率提升了18%。看到技术真正解决实际问题，这就是做AI最大的满足感。",
        "images": ["https://picsum.photos/seed/moment11/600/400", "https://picsum.photos/seed/moment12/600/400"],
    },
    {
        "content": "入手了一套新的机械键盘，写代码手感提升明显。工欲善其事必先利其器，程序员的快乐就是这么简单。顺便推荐一下Keychron Q1，铝坨坨质感无敌。",
        "images": ["https://picsum.photos/seed/moment13/600/400"],
    },
]


def seed_moments(db, users, now):
    items = []
    for m in MOMENTS_DATA:
        author = random.choice(users)
        created = rt(now, 30)
        items.append(Moment(
            user_id=author.id,
            content=m["content"],
            images=m["images"],
            created_at=created,
            updated_at=created,
            likes_count=random.randint(0, 100),
        ))
    for item in items:
        db.add(item)
    db.commit()
    for item in items:
        db.refresh(item)
    print(f"  Moments: {len(items)} items")
    return items


COMMENTS_DATA = [
    {"target_type": "blog", "content": "写得非常详细，特别是代码示例部分，对我帮助很大！期待后续更新。", "author_name": "Alice"},
    {"target_type": "blog", "content": "FastAPI的依赖注入确实比Flask优雅很多，已经在项目中迁移了。", "author_name": "Bob"},
    {"target_type": "blog", "content": "请问这个模型在消费级显卡上能跑吗？显存要求是多少？", "author_name": "游客38291"},
    {"target_type": "blog", "content": "RAG的检索精度确实是个难题，我们团队也在尝试混合检索方案。", "author_name": "Charlie"},
    {"target_type": "blog", "content": "Transformer的可视化部分讲得很清楚，终于理解注意力机制了。", "author_name": "Diana"},
    {"target_type": "blog", "content": "LoRA微调的经验总结非常实用，节省了我很多踩坑时间。", "author_name": "Evan"},
    {"target_type": "news", "content": "GPT-4o的语音能力确实突破很大，但隐私问题也值得关注。", "author_name": "Alice"},
    {"target_type": "news", "content": "Claude 3.5的Artifacts功能体验了一下，交互设计很巧妙。", "author_name": "游客10294"},
    {"target_type": "news", "content": "Llama 3的开源生态越来越完善了，国内很多公司都在基于此做二次开发。", "author_name": "Bob"},
    {"target_type": "news", "content": "Apple Intelligence的端侧推理方案很有前瞻性，隐私保护做得不错。", "author_name": "Charlie"},
    {"target_type": "news", "content": "欧盟AI法案的处罚力度很大，出海企业一定要提前做合规准备。", "author_name": "游客55673"},
    {"target_type": "project", "content": "这个写作助手的产品设计很用心，多模型路由的想法很好。", "author_name": "Diana"},
    {"target_type": "project", "content": "知识库系统的RAG实现很完整，请问用的什么向量数据库？", "author_name": "Evan"},
    {"target_type": "project", "content": "医疗影像项目很有社会价值，期待看到更多临床验证数据。", "author_name": "游客89321"},
    {"target_type": "project", "content": "量化交易平台的回测框架设计得很专业，夏普比率1.92很亮眼。", "author_name": "Alice"},
]


def seed_comments(db, blogs, news, projects, now):
    # Collect target IDs
    blog_ids = [b.id for b in blogs]
    news_ids = [n.id for n in news]
    project_ids = [p.id for p in projects]

    comments = []
    for c in COMMENTS_DATA:
        target_type = c["target_type"]
        if target_type == "blog":
            target_id = random.choice(blog_ids)
        elif target_type == "news":
            target_id = random.choice(news_ids)
        else:
            target_id = random.choice(project_ids)
        created = rt(now, 20)
        comment = Comment(
            target_type=target_type,
            target_id=target_id,
            author_name=c["author_name"],
            content=c["content"],
            created_at=created,
            likes_count=random.randint(0, 50),
            liked_ips="[]",
        )
        db.add(comment)
    db.commit()
    print(f"  Comments: {len(COMMENTS_DATA)} items")
    return []


def run():
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        print("\n开始创建种子数据...")

        # Users
        users = seed_users(db, now)

        # Follows
        seed_follows(db, users)

        # Blogs
        blogs = seed_blogs(db, users, now)

        # News
        news_items = seed_news(db, users, now)

        # Products
        products = seed_products(db, users, now)

        # Solutions
        solutions = seed_solutions(db, users, now)

        # Projects
        projects = seed_projects(db, users, now)

        # Moments
        moments = seed_moments(db, users, now)

        # Comments
        seed_comments(db, blogs, news_items, projects, now)

        print("\n=================================")
        print("种子数据创建完成！")
        print(f"  Users: {len(users)}")
        print(f"  Blogs: {len(blogs)}")
        print(f"  News: {len(news_items)}")
        print(f"  Products: {len(products)}")
        print(f"  Solutions: {len(solutions)}")
        print(f"  Projects: {len(projects)}")
        print(f"  Moments: {len(moments)}")
        print(f"  Comments: 15")
        print("=================================\n")
    except Exception as e:
        db.rollback()
        print(f"  Failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
