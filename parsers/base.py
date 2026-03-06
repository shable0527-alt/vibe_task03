from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ParsedPage:
    """A single page / sheet / slide of extracted content."""

    page_number: int
    text: str
    tables: list[list[list[str]]] = field(default_factory=list)  # list of 2D tables
    images_text: list[str] = field(default_factory=list)  # OCR text from embedded images


@dataclass
class ParsedDocument:
    """Result of parsing one file."""

    file_name: str
    file_path: str
    file_type: str  # pdf, pptx, excel, image
    pages: list[ParsedPage] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    @property
    def full_text(self) -> str:
        parts = []
        for page in self.pages:
            if page.text:
                parts.append(page.text)
            for img_text in page.images_text:
                if img_text.strip():
                    parts.append(img_text)
        return "\n\n".join(parts)
