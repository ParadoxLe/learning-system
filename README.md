# 📚 多智能体个性化学习资源生成系统

基于多智能体协作的个性化学习系统，采用 DeepSeek 大模型驱动 10+ 专业 AI Agent，从学习画像构建、资源生成、路径规划到智能辅导与评估，打造完整的个性化学习闭环。

---

## ✨ 项目特点

### 🧠 6 维学习画像
摒弃传统表单，通过自然语言对话自动抽取 6 维学习特征：
- **知识基础** — 已掌握主题、薄弱点、学习目标
- **认知风格** — 视觉型 / 逻辑型 / 动手型 / 文字型 等
- **学习节奏** — 快/中/慢，专注时长，每周学时
- **偏好模态** — 文字/视频/音频/交互/图示/代码实操
- **易错模式** — 常见错误类型与频率分析
- **学习动机** — 内在/外在动机，主要学习目标

### 🤖 多智能体协同
10+ 专业 Agent 各司其职，由 Orchestrator 统一编排调度：

| Agent | 职责 |
|---|---|
| 🎯 Orchestrator | 意图识别、任务分发、结果汇总 |
| 🧠 ProfileAgent | 对话式画像采集、6 维特征提取 |
| 📝 DocAgent | 课程文档生成，自适应难度 |
| 🧩 MindMapAgent | Mermaid 思维导图、知识结构可视化 |
| ✏️ ExerciseAgent | 4 种题型、针对性练习 |
| 📖 ReadingAgent | 三级拓展阅读推荐 |
| 🎬 VideoAgent | 教学视频分镜脚本 |
| 💻 CodeAgent | 编程案例与实战项目 |
| 🗺️ PathAgent | 阶段化学习路径规划 |
| 🤖 TutorAgent | 多模态智能辅导答疑 |
| 📊 AssessmentAgent | 6 维学习评估与建议 |

### 📦 6 类资源一键生成
- 课程文档 · 思维导图 · 练习题 · 拓展阅读 · 视频脚本 · 代码案例

### 🗺️ 动态学习路径
根据画像和资源库，自动规划分阶段学习路线，支持节点完成追踪与进度可视化。

### 💡 智能辅导
TutorAgent 根据学生认知风格调整讲解方式，支持文字解析 + 图解说明 + 类比讲解 + 举一反三。

### 📊 精准评估
多维度评估知识掌握度、进步趋势、薄弱环节、学习效率、资源适配度。

### 🔮 知识盲盒
结合 RAG 检索增强生成，每日推送个性化知识点，温故知新。

### 📚 资源库（RAG）
支持 PDF 上传与智能解析，基于 ChromaDB 向量检索实现语义搜索与文档问答。

### 🎬 视频生成
集成 Doubao-Seedance API，将视频脚本自动生成教学视频。

### 👩‍🏫 数字人
集成 iFlytek 数字人 SDK，提供虚拟教师形象与语音交互。

### 🎨 古典图书馆 UI
温暖沉稳的胡桃木色系 + 羊皮纸背景 + 古铜金点缀，营造沉浸式学习氛围。

---

## 🏗️ 系统架构

```
┌──────────────────────────────────────────────────────┐
│                    Frontend (Vue 3)                    │
│  Element Plus · Pinia · Vue Router · ECharts          │
│  Mermaid · Markdown-it · Axios                        │
│  port :5173                                           │
└──────────────────────┬───────────────────────────────┘
                       │  /api/* (proxy)
┌──────────────────────┴───────────────────────────────┐
│                  Backend (FastAPI)                     │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Routers  │  │ Services │  │  Agents  │           │
│  │ (12)     │→ │ (12)     │→ │  (10+)   │           │
│  └──────────┘  └──────────┘  └──────────┘           │
│                                                       │
│  ┌──────────────────────────────────────┐            │
│  │        External Integrations          │            │
│  │  DeepSeek API · Seedance Video        │            │
│  │  iFlytek Digital Human · ChromaDB    │            │
│  └──────────────────────────────────────┘            │
│                                                       │
│  SQLite · ChromaDB Vector Store                       │
│  port :8000                                           │
└──────────────────────────────────────────────────────┘
```

### 数据流

```
用户输入 → Orchestrator 意图识别 → 分发至专业 Agent
    → Agent 调用 DeepSeek API 生成内容
    → Service 层处理业务逻辑 + 持久化
    → Router 返回 JSON 响应
    → 前端 SSE 流式渲染 / 直接展示
```

---

## 📁 项目结构

```
learning-agent-system/
├── backend/                      # Python FastAPI 后端
│   ├── main.py                   # 应用入口，注册路由
│   ├── config.py                 # 环境变量配置
│   ├── database.py               # SQLAlchemy + 自动迁移
│   ├── agents/                   # AI Agent 实现
│   │   ├── base.py               # Agent 基类（DeepSeek 封装）
│   │   ├── orchestrator.py       # 主编排器
│   │   ├── profile_agent.py      # 画像分析
│   │   ├── path_agent.py         # 路径规划
│   │   ├── tutor_agent.py        # 智能辅导
│   │   ├── assessment_agent.py   # 学习评估
│   │   ├── blind_box_agent.py    # 知识盲盒
│   │   └── resource_agents/      # 资源生成子 Agent（7个）
│   ├── routers/                  # API 路由（12个模块）
│   ├── services/                 # 业务逻辑层（12个模块）
│   ├── models/                   # SQLAlchemy 数据模型（7个）
│   ├── schemas/                  # Pydantic 请求/响应模型
│   └── utils/                    # 工具函数
├── frontend-vue/                 # Vue 3 前端 SPA
│   ├── vite.config.js            # Vite 配置 + API 代理
│   ├── index.html                # HTML 入口
│   └── src/
│       ├── main.js               # Vue 应用启动
│       ├── App.vue               # 根组件
│       ├── api/index.js          # Axios API 封装
│       ├── router/index.js       # 路由配置（12 条路由）
│       ├── stores/               # Pinia 状态管理
│       │   ├── auth.js           # 认证状态
│       │   └── student.js        # 学生/画像状态
│       ├── components/           # 可复用组件
│       │   ├── AppLayout.vue     # 侧边栏布局
│       │   ├── FloatingTutor.vue # 悬浮辅导助手
│       │   ├── KnowledgeBlindBox.vue # 知识盲盒
│       │   ├── DigitalHuman.vue  # 数字人组件
│       │   └── ProfileBanner.vue # 画像概览条
│       ├── views/                # 页面组件（12 个）
│       └── styles/global.css     # 全局样式（图书馆主题）
├── data/                         # 运行时数据
│   ├── learning_system.db        # SQLite 数据库
│   ├── chroma_db/                # ChromaDB 向量库
│   └── uploads/                  # 上传文件
├── .env                          # 环境变量配置
└── requirements.txt              # Python 依赖
```

---

## 🚀 启动方式

### 环境要求

- **Python** >= 3.10
- **Node.js** >= 18
- **npm** >= 9

### 1. 克隆项目

```bash
git clone <repo-url>
cd learning-agent-system
```

### 2. 配置环境变量

编辑 `.env` 文件，填入必要的 API Key：

```env
# DeepSeek API（必填）
DEEPSEEK_API_KEY=sk-your-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 数据库
DATABASE_URL=sqlite:///./data/learning_system.db

# JWT
JWT_SECRET=your-secret-key

# 视频生成 - Doubao Seedance（可选）
SEEDANCE_API_KEY=your-seedance-key
SEEDANCE_BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# 数字人 - iFlytek（可选）
IFLYTEK_APP_ID=your-app-id
IFLYTEK_API_KEY=your-api-key
IFLYTEK_API_SECRET=your-api-secret
IFLYTEK_AVATAR_ID=your-avatar-id

# RAG Embedding（可选）
HF_ENDPOINT=https://hf-mirror.com
```

### 3. 启动后端

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 启动 FastAPI 服务（端口 8000）
cd backend
python main.py
```

或使用 uvicorn：

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

API 文档自动生成，启动后访问：
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### 4. 启动前端

```bash
# 安装 npm 依赖
cd frontend-vue
npm install

# 启动 Vite 开发服务器（端口 5173）
npm run dev
```

前端开发服务器已配置 API 代理，`/api/*` 请求自动转发至 `http://127.0.0.1:8000`。

### 5. 访问系统

浏览器打开 **http://localhost:5173**，注册账号后即可使用。

### 生产构建

```bash
cd frontend-vue
npm run build        # 输出至 dist/

# 将 dist/ 部署至任意静态服务器，或由 FastAPI 托管
```

---

## 🔧 技术栈

| 层级 | 技术 |
|---|---|
| 前端框架 | Vue 3 (Composition API) |
| UI 组件库 | Element Plus |
| 状态管理 | Pinia |
| 路由 | Vue Router |
| 图表 | ECharts |
| 图表渲染 | Mermaid |
| Markdown | Markdown-it |
| 构建工具 | Vite |
| 后端框架 | FastAPI |
| ORM | SQLAlchemy |
| 数据校验 | Pydantic |
| AI 模型 | DeepSeek (via OpenAI SDK) |
| 向量数据库 | ChromaDB |
| 数据库 | SQLite |
| 视频生成 | Doubao-Seedance |
| 数字人 | iFlytek Virtual Human |
| 嵌入模型 | Sentence-Transformers (HuggingFace) |

---

## 📋 功能模块一览

| 模块 | 路由 | 说明 |
|---|---|---|
| 登录/注册 | `/login` `/register` | 账号密码 + 图形验证码 |
| 引导页 | `/welcome` | 系统介绍与快速开始 |
| 学习仪表盘 | `/` | 日历计划、统计卡片、今日任务 |
| 画像构建 | `/onboarding` | 对话式引导，自动抽取6维特征 |
| 学习画像 | `/profile` | 思维导图可视化 + 详情面板 |
| 资源生成 | `/resources` | 多智能体协作，6类资源一键生成 |
| 路径规划 | `/learning-path` | 分阶段路径、节点追踪、进度可视化 |
| 智能辅导 | `/tutoring` | 认知风格适配、多模态答疑 |
| 学习评估 | `/assessment` | 6维评估、趋势分析、知识盲盒 |
| 资源库 | `/library` | PDF 上传解析、RAG 语义搜索 |
| 个人设置 | `/settings` | 密码修改、头像上传 |

