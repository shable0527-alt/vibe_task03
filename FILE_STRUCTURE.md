# 项目文件结构详解

完整的文件树和每个文件的说明。

```
vibe_task03/
│
├─ 📄 主要文件
├─ main.py                          # CLI 命令入口
│  ├─ serve                        # 启动 Web 服务
│  ├─ build                        # 构建知识库
│  ├─ search                       # 搜索知识库
│  ├─ stats                        # 统计信息
│  └─ preview                      # 预览解析结果
│
├─ server.py                        # FastAPI 后端 + Web UI
│  ├─ /api/chat                    # 对话 API
│  ├─ /api/session/reset           # 会话重置 API
│  ├─ /api/stats                   # 统计 API
│  └─ /                            # Web 聊天界面（HTML/CSS/JS）
│
├─ rag_engine.py                    # RAG 问答引擎（核心智能）
│  ├─ RAGEngine 类
│  ├─ chat()                       # 完整对话流程
│  ├─ _rewrite_query()            # 查询改写
│  └─ SYSTEM_PROMPT                # 系统提示词模板
│
├─ pipeline.py                      # 知识库构建流水线
│  ├─ process_files()              # 主处理函数
│  ├─ _process_single_file()       # 单文件处理
│  └─ PipelineReport               # 处理报告类
│
├─ config.py                        # 配置管理
│  └─ Config 类
│     ├─ OPENAI_API_KEY
│     ├─ CHUNK_SIZE
│     ├─ SUPPORTED_EXTENSIONS
│     └─ 其他参数
│
├─ soul.md                          # AI 助手人设定义（关键！）
│  ├─ 你是谁
│  ├─ 公司核心信息
│  ├─ 对话风格与原则
│  ├─ 常见场景应对策略
│  └─ 禁止事项
│
├─ 📚 文档文件
├─ README.md                        # 完整项目文档
├─ QUICKSTART.md                    # 5分钟快速开始
├─ API_EXAMPLES.md                  # 多语言 API 调用示例
├─ FILE_STRUCTURE.md                # 本文件（项目结构）
└─ requirements.txt                 # Python 依赖列表

├─ 🔧 配置文件
├─ .env                             # 环境变量（API Key 等）
├─ .env.example                     # 环境变量示例
└─ .gitignore                       # Git 忽略规则

├─ 📁 parsers/                      # 文件解析模块
│  ├─ __init__.py
│  ├─ base.py                      # 数据结构定义
│  │  ├─ ParsedPage
│  │  └─ ParsedDocument
│  ├─ router.py                    # 文件类型自动识别
│  │  ├─ parse_file()              # 主路由函数
│  │  └─ get_all_files()           # 收集文件列表
│  ├─ pdf_parser.py                # PDF 解析
│  │  ├─ parse_pdf()
│  │  ├─ 表格提取
│  │  └─ 图片 OCR
│  ├─ pptx_parser.py               # PPT 解析
│  │  ├─ parse_pptx()
│  │  ├─ 备注提取
│  │  └─ 表格识别
│  ├─ docx_parser.py               # Word 解析
│  │  ├─ parse_docx()
│  │  ├─ 段落结构保留
│  │  └─ 表格处理
│  ├─ excel_parser.py              # Excel/CSV 解析
│  │  ├─ parse_excel()
│  │  ├─ _parse_xlsx()
│  │  └─ _parse_csv()
│  └─ image_parser.py              # 图片解析
│     ├─ parse_image()
│     ├─ Tesseract OCR
│     └─ GPT-4o Vision 兜底

├─ 📁 chunkers/                     # 内容切分模块
│  ├─ __init__.py
│  ├─ text_chunker.py              # Token 感知的智能切分
│  │  ├─ Chunk 数据类
│  │  ├─ chunk_document()           # 主切分函数
│  │  ├─ _split_text()             # Token 级切分
│  │  ├─ _split_into_segments()    # 段落/句子分割
│  │  └─ _table_to_text()          # 表格转文本
│  └─ metadata                     # 切片元数据

├─ 📁 labelers/                     # LLM 标注模块
│  ├─ __init__.py
│  └─ llm_labeler.py               # GPT 自动标注
│     ├─ label_chunks()             # 主标注函数
│     ├─ _label_batch()            # 批量标注
│     ├─ SYSTEM_PROMPT              # 标注提示词
│     └─ 12 种分类标签

├─ 📁 vectorstore/                  # 向量存储模块
│  ├─ __init__.py
│  └─ chroma_store.py              # ChromaDB 封装
│     ├─ ChromaStore 类
│     ├─ add_chunks()               # 添加文档
│     ├─ search()                  # 语义搜索
│     ├─ get_stats()               # 统计信息
│     ├─ delete_by_source()        # 删除文档
│     └─ _embed()                  # 生成向量

├─ 📁 utils/                        # 工具函数
│  ├─ __init__.py
│  └─ logger.py                    # 日志配置

├─ 📁 chroma_db/                    # 向量数据库存储
│  ├─ securities_kb/               # 知识库集合
│  │  ├─ data.parquet
│  │  └─ metadata.parquet
│  └─ (自动生成)

├─ 📁 .venv/                        # Python 虚拟环境
│  └─ (自动生成)

└─ 📁 docs/                         # 输入文档目录（自建）
   ├─ 公司介绍.docx
   ├─ 产品手册.pdf
   ├─ 策略说明.pptx
   ├─ 常见问题.xlsx
   └─ ...
```

## 🔑 关键文件说明

### 1. main.py - CLI 命令行入口
```bash
python3 main.py build ./docs/        # 构建知识库
python3 main.py serve               # 启动服务
python3 main.py search "查询"        # 搜索知识库
python3 main.py stats               # 统计信息
python3 main.py preview ./docs/     # 预览解析
```

### 2. soul.md - AI 助手人设（最重要！）
修改这个文件来自定义 AI 助手的性格、对话风格、职责等。
无需改代码，重启服务即可生效。

### 3. server.py - Web 服务
```
HTTP 服务器，提供：
- /api/chat          POST   对话接口
- /api/session/reset POST   会话重置
- /api/stats         GET    统计信息
- /                  GET    Web 聊天界面
- /docs              GET    Swagger API 文档
```

### 4. rag_engine.py - 核心智能引擎
```
RAG 问答流程：
查询改写 → 向量检索 → 相关度过滤 → 提示词拼装 → LLM 生成 → 回答
```

### 5. pipeline.py - 知识库构建
```
完整处理流程：
文件解析 → 内容切分 → LLM 标注 → 向量入库 → 生成报告
```

### 6. parsers/ - 多格式解析器
支持解析：PDF、PPT、Word、Excel、CSV、图片

### 7. vectorstore/ - 向量存储
```
ChromaDB 封装：
- 自动生成 embeddings
- 语义相似度搜索
- 持久化存储
```

## 📊 数据流向

```
输入文档
    ↓
parsers/         ← 解析为文本 + 表格 + 元数据
    ↓
chunkers/        ← 切分成 Token 级块
    ↓
labelers/        ← LLM 分类、标注、摘要
    ↓
vectorstore/     ← 生成 embeddings，存入 ChromaDB
    ↓
chroma_db/       ← 持久化向量数据库

用户查询
    ↓
server.py        ← 接收请求
    ↓
rag_engine.py    ← 查询改写、向量检索
    ↓
vectorstore/     ← 语义搜索相关文档
    ↓
rag_engine.py    ← 拼装提示词、调用 LLM
    ↓
server.py        ← 返回回答给客户端
```

## 🎯 开发工作流

### 如果想修改...

| 需求 | 编辑文件 |
|------|----------|
| AI 助手人设 | `soul.md` |
| 对话参数 | `rag_engine.py` |
| Web UI 样式 | `server.py` 中的 `_CHAT_HTML` |
| 支持新格式 | `parsers/` 添加新文件 + `config.py` |
| 标注分类 | `labelers/llm_labeler.py` |
| API 端点 | `server.py` |
| 数据库路径 | `config.py` |

### 调试技巧

```bash
# 查看日志
tail -f /tmp/server.log

# 测试单个文件解析
python3 -c "from parsers import parse_file; doc = parse_file('test.pdf'); print(doc.full_text[:500])"

# 测试 RAG 引擎
python3 -c "from rag_engine import RAGEngine; engine = RAGEngine(); print(engine.chat('测试'))"

# 删除知识库重建
rm -rf chroma_db/
python3 main.py build ./docs/
```

## 📦 依赖关系图

```
main.py
├─ config.py
├─ pipeline.py
│  ├─ parsers/
│  ├─ chunkers/
│  ├─ labelers/
│  └─ vectorstore/
│
└─ server.py
   ├─ config.py
   ├─ rag_engine.py
   │  ├─ vectorstore/
   │  └─ 外部: OpenAI API
   └─ 外部: FastAPI

rag_engine.py
├─ soul.md (读取)
├─ vectorstore/
└─ 外部: OpenAI API
```

---

**相关文档**：
- [README.md](README.md) - 完整说明
- [QUICKSTART.md](QUICKSTART.md) - 快速开始
- [API_EXAMPLES.md](API_EXAMPLES.md) - API 调用示例
