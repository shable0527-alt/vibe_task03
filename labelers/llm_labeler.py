from __future__ import annotations

import json

from openai import OpenAI

from config import Config
from chunkers.text_chunker import Chunk
from utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """你是一个证券行业的知识库标注专家。你的任务是对给定的文档片段进行分类标注。

对于每个文档片段，请返回以下 JSON 格式：
{
    "category": "分类标签",
    "keywords": ["关键词1", "关键词2", ...],
    "summary": "一句话摘要"
}

可用的分类标签（category）包括：
- 市场分析：行情走势、市场趋势、板块分析等
- 投资策略：选股策略、仓位管理、交易方法等
- 风险提示：风险揭示、警告信息、免责声明等
- 产品说明：基金/理财产品介绍、费率说明等
- 法规政策：监管政策、法律法规、合规要求等
- 公司研究：个股分析、公司基本面、财务分析等
- 行业研究：行业分析、产业链研究等
- 宏观经济：经济数据、货币政策、财政政策等
- 技术分析：K线形态、技术指标、量价分析等
- 客户服务：开户流程、操作指南、常见问题等
- 财务数据：财报数据、收益表、资产负债表等
- 其他：不属于以上分类的内容

关键词要求：提取 3-5 个最重要的关键词，用于检索匹配。
摘要要求：用一句话（不超过50字）概括该片段的核心内容。

只返回 JSON，不要有其他文字。如果输入包含多个片段（用 === 分隔），返回 JSON 数组。"""


def label_chunks(
    chunks: list[Chunk],
    batch_size: int | None = None,
) -> list[Chunk]:
    """Use LLM to label each chunk with category, keywords, and summary."""
    if not chunks:
        return chunks

    batch_size = batch_size or Config.LABELING_BATCH_SIZE
    client = OpenAI(api_key=Config.OPENAI_API_KEY, base_url=Config.OPENAI_BASE_URL)

    total = len(chunks)
    labeled = 0

    for i in range(0, total, batch_size):
        batch = chunks[i : i + batch_size]
        try:
            _label_batch(client, batch)
            labeled += len(batch)
            logger.info(f"Labeled {labeled}/{total} chunks")
        except Exception as e:
            logger.error(f"Labeling batch failed: {e}")
            # Apply fallback labels
            for chunk in batch:
                if not chunk.category:
                    chunk.category = "其他"
                    chunk.summary = chunk.text[:50]
                    chunk.keywords = []
            labeled += len(batch)

    return chunks


def _label_batch(client: OpenAI, batch: list[Chunk]) -> None:
    """Label a batch of chunks via a single LLM call."""
    if len(batch) == 1:
        user_content = batch[0].text
    else:
        user_content = "\n\n===\n\n".join(
            f"[片段 {idx + 1}]\n{chunk.text}" for idx, chunk in enumerate(batch)
        )

    resp = client.chat.completions.create(
        model=Config.LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.1,
        max_tokens=2000,
        response_format={"type": "json_object"},
    )

    content = resp.choices[0].message.content or "{}"
    result = json.loads(content)

    # Handle both single object and array responses
    if isinstance(result, dict):
        # Could be a single result or {"results": [...]}
        if "results" in result and isinstance(result["results"], list):
            labels = result["results"]
        elif "category" in result:
            labels = [result]
        else:
            # Try to find array in any key
            for v in result.values():
                if isinstance(v, list):
                    labels = v
                    break
            else:
                labels = [result]
    elif isinstance(result, list):
        labels = result
    else:
        labels = []

    # Apply labels to chunks
    for idx, chunk in enumerate(batch):
        if idx < len(labels):
            label = labels[idx]
            chunk.category = label.get("category", "其他")
            chunk.keywords = label.get("keywords", [])
            chunk.summary = label.get("summary", chunk.text[:50])
        else:
            chunk.category = "其他"
            chunk.summary = chunk.text[:50]
            chunk.keywords = []
