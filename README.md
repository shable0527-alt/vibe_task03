# 理博基金 AI 智能客服系统

一个基于大语言模型和向量知识库的智能客服解决方案，可快速构建行业专业的 AI 助手。本项目采用 RAG（检索增强生成）架构，支持多种文档格式（PDF、PPT、Word、Excel、图片）的自动解析和智能标注。

## 📋 功能特性

### 核心功能
- **多格式文档解析**：支持 PDF、PPT、DOCX、Excel、CSV、图片（含 OCR）
- **智能内容切分**：基于 Token 的语义感知切分，保留语句边界
- **LLM 智能标注**：自动对文档片段进行分类、提取关键词、生成摘要
- **向量知识库**：基于 ChromaDB + OpenAI Embeddings 的高效语义搜索
- **RAG 问答引擎**：检索 + 生成 + 人设完整闭环
- **Web 聊天界面**：响应式设计、多轮对话、会话管理
- **REST API**：完整的 API 接口支持集成

### 高级特性
- **Soul 人设系统**：通过 `soul.md` 快速定义 AI 助手人设和应对规则
- **查询改写**：基于对话历史自动展开模糊指代
- **温度控制**：专业回答、流畅对话的参数优化
- **会话记忆**：多轮对话历史保留，支持上下文理解

## 🚀 快速开始

### 前置要求
- Python 3.10+
- OpenAI API Key（需要 gpt-4o 和 embedding 模型权限）

### 安装步骤

#### 1. 克隆/进入项目目录
```bash
cd /home/uber/Desktop/project/vibe_task03
```

#### 2. 创建虚拟环境
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量
```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
nano .env
```

配置示例：
```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://svip.xty.app/v1  # 或 https://api.openai.com/v1

EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o

CHROMA_PERSIST_DIR=./chroma_db
CHROMA_COLLECTION_NAME=securities_kb

CHUNK_SIZE=512
CHUNK_OVERLAP=64
```

## 📖 使用指南

### 1. 构建知识库

#### 从文件夹构建（推荐）
```bash
python3 main.py build ./docs/
```

#### 从单个文件构建
```bash
python3 main.py build ./docs/product_guide.pdf
```

**支持的文件格式：**
- PDF（含表格、图片 OCR）
- PPT/PPTX（含备注、表格）
- Word（DOCX）
- Excel（XLSX、XLS、CSV）
- 图片（PNG、JPG、BMP、TIFF，含 Tesseract OCR）

**构建流程：**
1. 文件解析（获取原始文本）
2. 智能切分（基于 Token 的语义分割）
3. LLM 标注（分类、关键词、摘要）
4. 向量入库（生成 embeddings 并存储）

**输出示例：**
```
============================================================
  知识库构建报告
============================================================
  文件总数:     6
  成功处理:     6
  处理失败:     0
  切片总数:     85
============================================================
  [OK] 公司介绍.docx (docx) - 1 pages, 6 chunks
        分类: 公司研究(1), 产品说明(1), 其他(4)
  [OK] 产品手册.pdf (pdf) - 36 pages, 43 chunks
        分类: 投资策略(6), 产品说明(2), 其他(35)
============================================================
```

### 2. 启动 AI 客服服务

```bash
# 默认监听 http://0.0.0.0:8000
python3 main.py serve

# 或指定端口和主机
python3 main.py serve --port 9000 --host 127.0.0.1
```

**访问方式：**
- **Web 聊天界面**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs（Swagger）
- **健康检查**：http://localhost:8000/api/stats

### 3. 查询和搜索

#### 命令行搜索
```bash
# 基础搜索
python3 main.py search "基金净值如何计算"

# 按分类过滤
python3 main.py search "投资策略" --category "产品说明"

# 获取更多结果
python3 main.py search "风险提示" -k 10
```

#### 查看知识库统计
```bash
python3 main.py stats
```

#### 预览文档解析效果
```bash
# 预览不会进行标注和入库
python3 main.py preview ./docs/
```

### 4. API 接口调用

#### 发送消息并获取回答
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你们有哪些投资策略？",
    "session_id": "optional-session-id"
  }'
```

**响应格式：**
```json
{
  "reply": "我们的主要策略包括...",
  "session_id": "uuid-string"
}
```

#### 重置会话
```bash
curl -X POST http://localhost:8000/api/session/reset \
  -H "Content-Type: application/json" \
  -d '{"session_id": "uuid-string"}'
```

#### 获取统计信息
```bash
curl http://localhost:8000/api/stats
```

**响应格式：**
```json
{
  "total_documents": 85,
  "collection_name": "securities_kb",
  "active_sessions": 3
}
```

## 🎯 人设定制

### 快速修改 AI 助手人设

编辑 `soul.md` 文件即可快速自定义助手的：
- 身份和职责
- 公司信息和产品介绍
- 对话风格和原则
- 常见场景的应对策略
- 禁止事项和合规规则

**修改后无需重启代码，只需重启服务即可生效：**
```bash
# 终止现有服务（Ctrl+C）
# 重启服务
python3 main.py serve
```

### Soul.md 结构说明

```markdown
# 一、你是谁
定义 AI 助手的身份、公司、职责

# 二、公司核心信息
关键事实：注册信息、管理者、产品、数据等

# 三、对话风格与原则
语气、核心原则（严格基于知识库、合规底线、客户导向等）

# 四、常见场景应对策略
针对性的回答模板和引导方式

# 五、禁止事项
明确的边界和红线
```

## 📁 项目结构

```
vibe_task03/
├── main.py                    # CLI 入口（build, serve, search, stats, preview）
├── config.py                  # 配置管理
├── rag_engine.py             # RAG 问答引擎（核心智能）
├── pipeline.py               # 知识库构建流水线
├── server.py                 # FastAPI 后端 + Web UI
├── soul.md                   # AI 助手人设定义（关键！）
├── requirements.txt          # Python 依赖
├── .env.example              # 环境变量示例
├── .venv/                    # 虚拟环境
├── chroma_db/                # 向量数据库存储
├── docs/                     # 待处理的文档
├── parsers/                  # 文件解析器
│   ├── base.py              # 数据结构定义
│   ├── pdf_parser.py        # PDF 解析
│   ├── pptx_parser.py       # PPT 解析
│   ├── docx_parser.py       # Word 解析
│   ├── excel_parser.py      # Excel 解析
│   ├── image_parser.py      # 图片解析 + OCR
│   └── router.py            # 文件类型自动识别
├── chunkers/                 # 内容切分
│   └── text_chunker.py      # Token 感知的智能切分
├── labelers/                 # LLM 标注
│   └── llm_labeler.py       # GPT 自动标注分类
├── vectorstore/              # 向量存储
│   └── chroma_store.py      # ChromaDB 封装
└── utils/
    └── logger.py            # 日志工具
```

## 🔧 配置说明

### 核心参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `CHUNK_SIZE` | 512 | 切片大小（Token） |
| `CHUNK_OVERLAP` | 64 | 切片重叠（Token） |
| `LABELING_BATCH_SIZE` | 5 | LLM 标注批次大小 |
| `EMBEDDING_MODEL` | text-embedding-3-small | Embedding 模型 |
| `LLM_MODEL` | gpt-4o | 大语言模型 |

### 向量数据库

- **存储位置**：`./chroma_db/`（可配置）
- **集合名称**：`securities_kb`（可配置）
- **相似度算法**：cosine
- **检索 Top-K**：默认 6，可调整

## 📊 工作流程

```
用户输入
   ↓
查询改写（基于对话历史）
   ↓
向量检索（ChromaDB）
   ↓
相关度过滤（>30%）
   ↓
提示词拼装
├─ Soul 人设
├─ 系统指令
├─ 检索结果
└─ 用户问题
   ↓
LLM 生成（GPT-4o）
   ↓
流畅自然的回答
   ↓
会话历史更新
```

## 🎨 Web 界面特性

- **响应式设计**：适配桌面、平板、手机
- **实时打字指示**：显示 AI 正在思考
- **会话管理**：「新对话」按钮快速重置
- **快捷问题**：6 个预设问题，支持自定义
- **品牌化定制**：Logo、配色、页脚信息可修改

## 🔐 数据安全和隐私

- **本地向量存储**：所有 embeddings 存储在本地 ChromaDB
- **会话隔离**：每个用户有独立的 session ID
- **API 认证**：支持添加身份验证（可扩展）
- **数据清理**：会话可随时重置

## 🚨 故障排查

### 问题：找不到 soul.md
```
错误信息：soul.md not found at ...
```
**解决方案**：确保 `soul.md` 与 `rag_engine.py` 同级目录

### 问题：API 超时
```
错误信息：LLM call failed: timeout
```
**解决方案**：
- 检查网络连接
- 增加 `timeout` 参数
- 检查 API Key 是否有效

### 问题：OCR 不工作
```
错误信息：pytesseract module not found
```
**解决方案**：
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows
# 下载官方安装程序：https://github.com/UB-Mannheim/tesseract/wiki
```

### 问题：向量数据库报错
```
错误信息：ChromaDB error: ...
```
**解决方案**：
```bash
# 删除旧数据库并重建
rm -rf chroma_db/
python3 main.py build ./docs/
```

## 📚 高级用法

### 自定义标注分类

编辑 `labelers/llm_labeler.py` 中的 `SYSTEM_PROMPT`：

```python
可用的分类标签（category）包括：
- 市场分析：行情走势、市场趋势、板块分析等
- 投资策略：选股策略、仓位管理、交易方法等
- ... (可自由添加)
```

### 调整切分策略

编辑 `config.py`：
```python
CHUNK_SIZE = 256      # 减小以获得更细粒度的切片
CHUNK_OVERLAP = 32    # 减小重叠以降低成本
```

### 修改 LLM 温度

编辑 `rag_engine.py`：
```python
temperature=0.35,  # 0-1，越低越确定，越高越创意
```

## 🤝 扩展和集成

### 添加新的文件格式支持

1. 在 `parsers/` 下创建新的解析器，如 `markdown_parser.py`
2. 在 `config.py` 添加文件扩展名
3. 在 `parsers/router.py` 添加路由逻辑

### 集成到现有系统

```python
from rag_engine import RAGEngine
from vectorstore import ChromaStore

# 初始化
store = ChromaStore()
engine = RAGEngine(store=store)

# 使用
reply = engine.chat(query="用户问题", history=[])
print(reply)
```

### 部署到生产环境

```bash
# 使用 gunicorn（推荐）
gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app

# 或 Docker
docker build -t libo-ai-service .
docker run -p 8000:8000 libo-ai-service
```

## 📈 性能优化建议

| 优化项 | 建议 |
|--------|------|
| 知识库规模 | >10000 条文档时考虑分片存储 |
| 检索速度 | 增加 ChromaDB 索引 |
| API 成本 | 使用批量处理、缓存 embeddings |
| 响应速度 | 部署多个 uvicorn worker |

## 📄 许可证

本项目为示例项目，基于当前的理博基金知识库。

## 💡 关键概念解释

### RAG（检索增强生成）
将检索和生成相结合，保证 LLM 的回答准确、有根据。

### Embeddings
将文本转换为高维向量，用于语义相似度计算。

### Chunking
将长文本分割成小块，便于检索和处理。

### Token
语言模型处理的基本单位，约 4 个字符 = 1 token。

## 📞 支持和反馈

如有问题或建议，请：
1. 检查故障排查章节
2. 查看服务日志：`tail -f /tmp/server.log`
3. 联系技术支持

---

**最后更新**：2026-03-05
**版本**：1.0.0
**作者**：Claude Code AI
