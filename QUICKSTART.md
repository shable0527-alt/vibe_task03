# 快速入门指南 - 5分钟启动 AI 客服

这是最简洁的入门指南，从零到启动只需 5 分钟。

## 第 1 步：准备环境（1 分钟）

```bash
# 进入项目目录
cd /home/uber/Desktop/project/vibe_task03

# 激活虚拟环境
source .venv/bin/activate  # 如果还未创建，先运行 python3 -m venv .venv
```

## 第 2 步：配置 API Key（1 分钟）

```bash
# 编辑环境配置
nano .env
```

填入以下内容：
```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://svip.xty.app/v1
LLM_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
```

## 第 3 步：加载或构建知识库（2 分钟）

### 选项 A：使用现有知识库（推荐快速测试）
```bash
# 直接启动，使用已有的 85 条知识
python3 main.py serve
```

### 选项 B：从文档重新构建知识库
```bash
# 将你的文档放入 docs/ 文件夹
python3 main.py build ./docs/

# 然后启动服务
python3 main.py serve
```

**支持的文件格式**：PDF, PPT, Word, Excel, 图片

## 第 4 步：打开聊天界面（1 分钟）

在浏览器打开：
```
http://localhost:8000
```

看到如下界面表示成功：
- 顶部：「理博基金 LESS IS MORE」
- 中间：聊天区域和快捷问题
- 底部：输入框

## 🎉 就这样！现在可以开始对话了

### 试试这些问题：
- "理博基金是一家什么样的公司？"
- "你们有哪些投资策略？"
- "2025年度各策略收益如何？"
- "如何购买你们的基金产品？"

---

## 常见问题速览

| 问题 | 解决方案 |
|------|----------|
| 端口 8000 被占用 | `python3 main.py serve --port 9000` |
| API Key 无效 | 检查 `.env` 文件中的 `OPENAI_API_KEY` |
| 知识库为空 | 运行 `python3 main.py build ./docs/` |
| 导入失败 | 确保已安装依赖：`pip install -r requirements.txt` |

## 下一步

想深入了解？查看完整文档：
- **使用指南**：看 `README.md`
- **人设定制**：编辑 `soul.md` 文件
- **API 集成**：访问 `http://localhost:8000/docs`

## 快速命令速查表

```bash
# 启动服务（默认 8000 端口）
python3 main.py serve

# 构建知识库
python3 main.py build ./docs/

# 查看统计
python3 main.py stats

# 搜索知识库
python3 main.py search "你的问题"

# 预览文档解析
python3 main.py preview ./docs/
```

---

**提示**：第一次启动时，LLM 会对所有文档进行分类标注，这可能需要几分钟。之后的查询速度会很快！
