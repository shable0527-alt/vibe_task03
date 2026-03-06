# 📚 文档导航指南

完整的文档体系和阅读建议。

## 🎯 快速导航

### 我想...

| 目标 | 推荐阅读 |
|------|---------|
| **快速上手** | [QUICKSTART.md](QUICKSTART.md) ⭐ |
| **了解全貌** | [README.md](README.md) |
| **查看项目结构** | [FILE_STRUCTURE.md](FILE_STRUCTURE.md) |
| **调用 API** | [API_EXAMPLES.md](API_EXAMPLES.md) |
| **自定义 AI 助手** | [soul.md](soul.md) |
| **故障排查** | [README.md](README.md#-故障排查) |
| **部署到生产** | [README.md](README.md#-部署到生产环境) |

---

## 📖 文档详细说明

### 1️⃣ QUICKSTART.md（5分钟快速开始）
**适合人群**：想立即尝试的用户
**内容**：
- 最小化安装步骤
- 4 个关键命令
- 常见问题速查表

**关键命令**：
```bash
python3 main.py serve      # 启动服务
python3 main.py build      # 构建知识库
```

**预计时间**：5分钟

---

### 2️⃣ README.md（完整项目文档）
**适合人群**：想深入了解项目的用户
**内容**：
- 功能特性
- 详细安装步骤
- 完整使用指南
- 人设定制说明
- 工作流程
- 故障排查
- 高级用法

**阅读时间**：30-45分钟

**重点部分**：
- 人设定制（soul.md 如何修改）
- 配置说明（环境变量）
- 故障排查

---

### 3️⃣ API_EXAMPLES.md（API 调用示例）
**适合人群**：想集成 API 的开发者
**内容**：
- 7 种编程语言的示例代码
- cURL 命令行示例
- 完整 API 端点说明
- 常见集成问题

**支持的语言**：
- cURL
- Python
- JavaScript / Node.js
- PHP
- Java
- Go

**使用场景**：
- 在自己的应用中调用 API
- 构建客户端应用
- 第三方集成

---

### 4️⃣ FILE_STRUCTURE.md（项目文件结构）
**适合人群**：想修改代码的开发者
**内容**：
- 完整文件树
- 每个文件的说明
- 数据流向图
- 开发工作流指南
- 调试技巧

**核心信息**：
- 文件夹和文件的用途
- 代码依赖关系
- 如果要修改某个功能，编辑哪个文件

---

### 5️⃣ soul.md（AI 助手人设）
**适合人群**：所有使用者
**内容**：
- AI 助手的身份
- 公司核心信息
- 对话风格和原则
- 常见场景应对
- 禁止事项

**特点**：
- 修改后无需改代码
- 重启服务即可生效
- 是 AI 智能程度的核心决定因素

---

## 📚 阅读路径

### 路径 A：我是第一次使用（推荐）
```
1. QUICKSTART.md（5分钟）
   ↓ 成功启动后
2. README.md 快速开始章节（5分钟）
   ↓ 需要自定义时
3. soul.md（10分钟）
   ↓ 需要集成 API 时
4. API_EXAMPLES.md（15分钟）
```

### 路径 B：我想深入开发
```
1. README.md 完整阅读（45分钟）
   ↓
2. FILE_STRUCTURE.md（20分钟）
   ↓
3. 查看源代码和注释
   ↓
4. API_EXAMPLES.md（如需集成）
```

### 路径 C：我只想用 API
```
1. QUICKSTART.md 启动部分（3分钟）
   ↓
2. API_EXAMPLES.md 你需要的语言（10分钟）
   ↓
3. 参考 /docs 页面查看完整 API 文档
```

---

## 🎯 针对不同角色

### 👤 产品经理
- 读：README.md（了解功能）
- 读：soul.md（了解 AI 能力）
- 操作：修改 soul.md 调整助手行为

### 👨‍💻 后端开发者
- 读：README.md（完整了解）
- 读：FILE_STRUCTURE.md（代码结构）
- 读：API_EXAMPLES.md（Python 示例）
- 操作：修改代码，扩展功能

### 👨‍💼 前端开发者
- 读：QUICKSTART.md（快速启动）
- 读：API_EXAMPLES.md（JavaScript 部分）
- 操作：调用 /api/chat 接口

### 🏢 系统运维
- 读：README.md（部署章节）
- 读：FILE_STRUCTURE.md（系统架构）
- 操作：部署、监控、故障排查

### 📊 数据分析师
- 读：README.md（知识库构建）
- 读：FILE_STRUCTURE.md（数据流向）
- 操作：监控知识库质量，优化标注

---

## 🔗 文档间的关联

```
QUICKSTART.md ──→ README.md ──→ FILE_STRUCTURE.md
                     ↓
                  soul.md
                     ↓
               API_EXAMPLES.md
```

## 📱 离线访问

所有文档都是 Markdown 格式，可以：
- 用任何编辑器离线查看
- 下载到本地
- 导入到 Obsidian、Notion 等笔记应用
- 转换为 PDF、HTML 等格式

## 🔍 如何搜索文档

### 在 README.md 中搜索
- Ctrl+F / Cmd+F 快速搜索
- 目录在文档开头（# 标题）

### 常见问题关键词
- 搜索 "问题" → 故障排查章节
- 搜索 "部署" → 高级用法章节
- 搜索 "API" → API_EXAMPLES.md
- 搜索 "soul" → soul.md 和 README.md

## ⚠️ 重要提示

1. **soul.md 很重要**
   - 这个文件决定了 AI 助手的"性格"
   - 修改它不需要改代码
   - 重启服务后立即生效

2. **环境变量配置**
   - 复制 .env.example → .env
   - 填入 OPENAI_API_KEY（必需！）
   - 其他参数有默认值

3. **知识库构建**
   - 第一次运行 python3 main.py build ./docs/ 会比较慢（LLM 标注）
   - 之后查询速度很快
   - 可增量添加文档

4. **多语言 API 示例**
   - 选择你用的编程语言的示例
   - 修改 URL 和参数
   - 直接复制粘贴可用

---

## 📞 文档反馈

如果文档有：
- ❌ 错误或过时信息
- ❌ 不清楚的步骤
- ✅ 需要补充的内容

请更新对应的 .md 文件。

---

## 🗺️ 文档版本

- **最后更新**：2026-03-05
- **版本**：1.0.0
- **作者**：Claude Code AI

---

**现在选择一份文档开始阅读吧！** 👇
