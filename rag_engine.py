"""RAG 问答引擎：从知识库检索相关内容，结合 soul 人设和大模型生成回答。"""

from __future__ import annotations

import os

from openai import OpenAI

from config import Config
from vectorstore import ChromaStore
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Load soul.md at module level ─────────────────────────────────

_SOUL_PATH = os.path.join(os.path.dirname(__file__), "soul.md")


def _load_soul() -> str:
    try:
        with open(_SOUL_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"soul.md not found at {_SOUL_PATH}, using fallback prompt")
        return ""


_SOUL_CONTENT = _load_soul()

# ── System prompt construction ───────────────────────────────────

_SYSTEM_TEMPLATE = """{soul}

---

## 当前对话指令

你现在正在与一位用户对话。请严格遵循以下流程回答：

1. **理解意图**：先判断用户的真实需求（了解公司、咨询产品、询问业绩、购买流程、资金安全等）
2. **检索回答**：优先使用下方「参考资料」中的内容进行回答，确保信息准确
3. **补充润色**：用专业但易懂的语言组织回答，自然流畅，避免生硬地罗列信息
4. **合规检查**：涉及业绩数据时附加风险提示，不做收益承诺
5. **引导下一步**：在合适时自然引导用户深入了解或联系我们

### 回答格式要求
- 使用清晰的分段和适当的标点
- 重要数据用准确数字，不要模糊化
- 回答长度适中：简单问题2-3句，复杂问题分点回答但不超过300字
- 不要使用 markdown 格式符号（如 **、#），直接用自然语言
- 在对话中自称"我"或"我们"，称用户为"您"
"""

_CONTEXT_TEMPLATE = """以下是从知识库中检索到的参考资料，请基于这些内容回答用户问题：

{context}

---
用户问题：{query}"""

_NO_CONTEXT_TEMPLATE = """知识库中未检索到直接相关的内容。

请根据你的基础认知（soul 中的公司信息）尽量回答，如果确实无法回答，请诚实告知用户并引导其联系人工客服（investor@liboinv.com）。

---
用户问题：{query}"""


class RAGEngine:
    """Retrieval-Augmented Generation engine for securities Q&A."""

    def __init__(self, store: ChromaStore | None = None):
        self._store = store or ChromaStore()
        self._client = OpenAI(
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.OPENAI_BASE_URL,
        )
        self._system_prompt = _SYSTEM_TEMPLATE.format(soul=_SOUL_CONTENT)

    def chat(
        self,
        query: str,
        history: list[dict] | None = None,
        top_k: int = 6,
    ) -> str:
        """Answer a user query using RAG.

        Flow: query rewrite -> retrieve -> generate
        """
        # Step 1: Rewrite query for better retrieval (use conversation context)
        search_query = self._rewrite_query(query, history)

        # Step 2: Retrieve relevant context
        hits = self._store.search(search_query, top_k=top_k)

        # Step 3: Build user message with context
        if hits:
            context_parts = []
            for i, hit in enumerate(hits, 1):
                meta = hit["metadata"]
                source = meta.get("source_file", "")
                page = meta.get("page_number", "")
                score = hit.get("score", 0)
                # Only include reasonably relevant results
                if score > 0.3:
                    context_parts.append(
                        f"[资料{i} | 来源: {source} | 相关度: {score:.0%}]\n{hit['text']}"
                    )
            if context_parts:
                context_block = "\n\n".join(context_parts)
                user_message = _CONTEXT_TEMPLATE.format(
                    context=context_block, query=query
                )
            else:
                user_message = _NO_CONTEXT_TEMPLATE.format(query=query)
        else:
            user_message = _NO_CONTEXT_TEMPLATE.format(query=query)

        # Step 4: Build messages
        messages = [{"role": "system", "content": self._system_prompt}]

        # Add conversation history (keep recent turns)
        if history:
            messages.extend(history[-16:])

        messages.append({"role": "user", "content": user_message})

        # Step 5: Generate
        try:
            resp = self._client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=messages,
                temperature=0.35,
                max_tokens=1500,
            )
            answer = resp.choices[0].message.content or "抱歉，我暂时无法回答这个问题。"
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            answer = "抱歉，服务暂时出现问题，请稍后再试。如需帮助，请联系 investor@liboinv.com"

        return answer

    def _rewrite_query(self, query: str, history: list[dict] | None) -> str:
        """Rewrite query using conversation context for better retrieval.

        If the query references prior context (e.g., "那个产品怎么买"),
        expand it using recent conversation history.
        """
        if not history or len(history) < 2:
            return query

        # Check if query is too short or uses pronouns that need context
        ambiguous_markers = ["它", "这个", "那个", "该", "上面", "刚才", "前面提到"]
        needs_rewrite = len(query) < 8 or any(m in query for m in ambiguous_markers)

        if not needs_rewrite:
            return query

        # Use LLM to rewrite the query with context
        try:
            recent = history[-6:]
            context_summary = "\n".join(
                f"{'用户' if m['role']=='user' else '助手'}: {m['content'][:100]}"
                for m in recent
            )
            resp = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个查询改写助手。根据对话上下文，将用户的模糊查询改写为一个完整、明确的检索查询语句。只返回改写后的查询，不要有其他内容。",
                    },
                    {
                        "role": "user",
                        "content": f"对话上下文：\n{context_summary}\n\n用户最新问题：{query}\n\n请改写为完整的检索查询：",
                    },
                ],
                temperature=0.0,
                max_tokens=100,
            )
            rewritten = resp.choices[0].message.content.strip()
            if rewritten:
                logger.info(f"Query rewrite: '{query}' -> '{rewritten}'")
                return rewritten
        except Exception as e:
            logger.warning(f"Query rewrite failed: {e}")

        return query
