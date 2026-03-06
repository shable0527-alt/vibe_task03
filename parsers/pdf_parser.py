from __future__ import annotations

import io

import fitz  # PyMuPDF
from PIL import Image

from .base import ParsedDocument, ParsedPage
from utils.logger import get_logger

logger = get_logger(__name__)

# Minimum image size (pixels) to attempt OCR — skip tiny icons/logos
MIN_IMAGE_SIZE = 100


def parse_pdf(file_path: str) -> ParsedDocument:
    """Extract text, tables, and image OCR from a PDF file."""
    doc = fitz.open(file_path)
    pages: list[ParsedPage] = []

    for page_idx, page in enumerate(doc):
        # Extract text
        text = page.get_text("text")

        # Extract tables (PyMuPDF built-in table detection)
        tables: list[list[list[str]]] = []
        try:
            found_tables = page.find_tables()
            for table in found_tables:
                rows = table.extract()
                cleaned = [
                    [cell if cell is not None else "" for cell in row] for row in rows
                ]
                tables.append(cleaned)
        except Exception:
            pass  # table detection may fail on some pages

        # Extract images and attempt OCR
        images_text: list[str] = []
        try:
            for img_info in page.get_images(full=True):
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                if base_image:
                    image_bytes = base_image["image"]
                    img = Image.open(io.BytesIO(image_bytes))
                    w, h = img.size
                    if w >= MIN_IMAGE_SIZE and h >= MIN_IMAGE_SIZE:
                        ocr_text = _ocr_image(img)
                        if ocr_text.strip():
                            images_text.append(ocr_text)
        except Exception as e:
            logger.warning(f"PDF image extraction failed on page {page_idx + 1}: {e}")

        pages.append(
            ParsedPage(
                page_number=page_idx + 1,
                text=text.strip(),
                tables=tables,
                images_text=images_text,
            )
        )

    doc.close()
    logger.info(f"PDF parsed: {file_path} ({len(pages)} pages)")
    return ParsedDocument(
        file_name=_basename(file_path),
        file_path=file_path,
        file_type="pdf",
        pages=pages,
        metadata={"total_pages": len(pages)},
    )


def _ocr_image(img: Image.Image) -> str:
    """Run OCR on a PIL image. Falls back to empty string on failure."""
    try:
        import pytesseract

        return pytesseract.image_to_string(img, lang="chi_sim+eng")
    except Exception:
        return ""


def _basename(path: str) -> str:
    import os

    return os.path.basename(path)
