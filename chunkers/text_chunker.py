from __future__ import annotations

import re
from dataclasses import dataclass, field

import tiktoken

from config import Config
from parsers.base import ParsedDocument
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Chunk:
    """A single chunk of content with metadata for vector storage."""

    text: str
    chunk_index: int
    metadata: dict = field(default_factory=dict)
    # Populated later by labeler
    category: str = ""
    keywords: list[str] = field(default_factory=list)
    summary: str = ""


def chunk_document(
    doc: ParsedDocument,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[Chunk]:
    """Split a parsed document into chunks with metadata.

    Strategy:
    - For each page/slide/sheet, combine text + table text + image OCR text
    - Split into token-based chunks with overlap
    - Attach source metadata to each chunk
    """
    chunk_size = chunk_size or Config.CHUNK_SIZE
    chunk_overlap = chunk_overlap or Config.CHUNK_OVERLAP
    chunks: list[Chunk] = []
    global_idx = 0

    for page in doc.pages:
        # Combine all content from this page
        content_parts: list[str] = []

        if page.text:
            content_parts.append(page.text)

        # Convert tables to readable text
        for table in page.tables:
            table_text = _table_to_text(table)
            if table_text:
                content_parts.append(table_text)

        # Add OCR text from images
        for img_text in page.images_text:
            if img_text.strip():
                content_parts.append(f"[图片内容] {img_text.strip()}")

        page_text = "\n\n".join(content_parts).strip()
        if not page_text:
            continue

        # Split this page's content into chunks
        page_chunks = _split_text(page_text, chunk_size, chunk_overlap)

        for chunk_text in page_chunks:
            chunks.append(
                Chunk(
                    text=chunk_text,
                    chunk_index=global_idx,
                    metadata={
                        "source_file": doc.file_name,
                        "source_path": doc.file_path,
                        "file_type": doc.file_type,
                        "page_number": page.page_number,
                    },
                )
            )
            global_idx += 1

    logger.info(
        f"Chunked '{doc.file_name}': {len(doc.pages)} pages -> {len(chunks)} chunks"
    )
    return chunks


def _split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Split text into chunks using token count, respecting sentence boundaries."""
    enc = tiktoken.get_encoding("cl100k_base")

    # First, split into paragraphs/sentences as natural boundaries
    segments = _split_into_segments(text)

    chunks: list[str] = []
    current_tokens: list[str] = []
    current_count = 0

    for segment in segments:
        seg_tokens = enc.encode(segment)
        seg_count = len(seg_tokens)

        # If a single segment exceeds chunk_size, force-split it
        if seg_count > chunk_size:
            # Flush current buffer first
            if current_tokens:
                chunks.append(enc.decode(current_tokens))
                # Keep overlap
                overlap_tokens = current_tokens[-chunk_overlap:] if chunk_overlap > 0 else []
                current_tokens = overlap_tokens
                current_count = len(overlap_tokens)

            # Force-split the large segment
            for i in range(0, seg_count, chunk_size - chunk_overlap):
                part = seg_tokens[i : i + chunk_size]
                chunks.append(enc.decode(part))
            continue

        # Check if adding this segment exceeds the limit
        if current_count + seg_count > chunk_size:
            # Flush current chunk
            if current_tokens:
                chunks.append(enc.decode(current_tokens))
                # Keep overlap
                overlap_tokens = current_tokens[-chunk_overlap:] if chunk_overlap > 0 else []
                current_tokens = list(overlap_tokens)
                current_count = len(overlap_tokens)

        current_tokens.extend(seg_tokens)
        current_count += seg_count

    # Flush remaining
    if current_tokens:
        chunks.append(enc.decode(current_tokens))

    return [c.strip() for c in chunks if c.strip()]


def _split_into_segments(text: str) -> list[str]:
    """Split text into meaningful segments (paragraphs, then sentences)."""
    # Split by double newlines (paragraphs)
    paragraphs = re.split(r"\n\s*\n", text)
    segments: list[str] = []

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        # If paragraph is short enough, keep as-is
        if len(para) < 500:
            segments.append(para)
        else:
            # Split long paragraphs by sentence boundaries
            sentences = re.split(r"(?<=[。！？.!?\n])\s*", para)
            for sent in sentences:
                sent = sent.strip()
                if sent:
                    segments.append(sent)

    return segments


def _table_to_text(table: list[list[str]]) -> str:
    """Convert a 2D table into readable text with headers as keys."""
    if not table or len(table) < 2:
        if table and len(table) == 1:
            return " | ".join(table[0])
        return ""

    header = table[0]
    lines = [f"[表格] {' | '.join(header)}"]
    for row in table[1:]:
        kv_pairs = []
        for h, v in zip(header, row):
            h_str = str(h).strip()
            v_str = str(v).strip()
            if h_str and v_str:
                kv_pairs.append(f"{h_str}: {v_str}")
        if kv_pairs:
            lines.append("; ".join(kv_pairs))

    return "\n".join(lines)
