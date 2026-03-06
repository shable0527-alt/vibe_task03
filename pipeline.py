from __future__ import annotations

from dataclasses import dataclass, field

from parsers import parse_file, ParsedDocument
from parsers.router import get_all_files
from chunkers import chunk_document
from chunkers.text_chunker import Chunk
from labelers import label_chunks
from vectorstore import ChromaStore
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ProcessingResult:
    """Result of processing a single file."""

    file_name: str
    file_path: str
    file_type: str
    total_pages: int
    total_chunks: int
    chunks_stored: int
    categories: dict[str, int] = field(default_factory=dict)
    error: str | None = None


@dataclass
class PipelineReport:
    """Summary report of the entire pipeline run."""

    total_files: int = 0
    processed_files: int = 0
    failed_files: int = 0
    total_chunks: int = 0
    results: list[ProcessingResult] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"{'='*60}",
            f"  知识库构建报告",
            f"{'='*60}",
            f"  文件总数:     {self.total_files}",
            f"  成功处理:     {self.processed_files}",
            f"  处理失败:     {self.failed_files}",
            f"  切片总数:     {self.total_chunks}",
            f"{'='*60}",
        ]
        for r in self.results:
            status = "OK" if r.error is None else "FAIL"
            lines.append(
                f"  [{status}] {r.file_name} ({r.file_type}) "
                f"- {r.total_pages} pages, {r.total_chunks} chunks"
            )
            if r.categories:
                cat_str = ", ".join(f"{k}({v})" for k, v in r.categories.items())
                lines.append(f"        分类: {cat_str}")
            if r.error:
                lines.append(f"        错误: {r.error}")
        lines.append(f"{'='*60}")
        return "\n".join(lines)


def process_files(
    input_path: str,
    enable_labeling: bool = True,
    store: ChromaStore | None = None,
) -> PipelineReport:
    """Main pipeline: parse -> chunk -> label -> store.

    Args:
        input_path: Path to a file or directory.
        enable_labeling: Whether to use LLM for labeling.
        store: ChromaStore instance (created if None).
    """
    # Collect files
    files = get_all_files(input_path)
    report = PipelineReport(total_files=len(files))

    if not files:
        logger.warning(f"No supported files found in: {input_path}")
        return report

    # Initialize store
    if store is None:
        store = ChromaStore()

    for file_path in files:
        result = _process_single_file(file_path, enable_labeling, store)
        report.results.append(result)
        if result.error is None:
            report.processed_files += 1
            report.total_chunks += result.chunks_stored
        else:
            report.failed_files += 1

    return report


def _process_single_file(
    file_path: str,
    enable_labeling: bool,
    store: ChromaStore,
) -> ProcessingResult:
    """Process a single file through the pipeline."""
    try:
        # Step 1: Parse
        logger.info(f"Parsing: {file_path}")
        doc: ParsedDocument = parse_file(file_path)

        # Step 2: Chunk
        chunks: list[Chunk] = chunk_document(doc)
        if not chunks:
            logger.warning(f"No content extracted from: {file_path}")
            return ProcessingResult(
                file_name=doc.file_name,
                file_path=file_path,
                file_type=doc.file_type,
                total_pages=len(doc.pages),
                total_chunks=0,
                chunks_stored=0,
            )

        # Step 3: Label
        if enable_labeling:
            logger.info(f"Labeling {len(chunks)} chunks...")
            chunks = label_chunks(chunks)

        # Step 4: Store
        logger.info(f"Storing {len(chunks)} chunks...")
        stored = store.add_chunks(chunks)

        # Gather category stats
        categories: dict[str, int] = {}
        for chunk in chunks:
            cat = chunk.category or "未分类"
            categories[cat] = categories.get(cat, 0) + 1

        return ProcessingResult(
            file_name=doc.file_name,
            file_path=file_path,
            file_type=doc.file_type,
            total_pages=len(doc.pages),
            total_chunks=len(chunks),
            chunks_stored=stored,
            categories=categories,
        )

    except Exception as e:
        logger.error(f"Failed to process {file_path}: {e}")
        return ProcessingResult(
            file_name=file_path.split("/")[-1],
            file_path=file_path,
            file_type="unknown",
            total_pages=0,
            total_chunks=0,
            chunks_stored=0,
            error=str(e),
        )
