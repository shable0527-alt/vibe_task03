from __future__ import annotations

import os

from PIL import Image

from .base import ParsedDocument, ParsedPage
from utils.logger import get_logger

logger = get_logger(__name__)


def parse_image(file_path: str) -> ParsedDocument:
    """Extract text from an image using OCR, with GPT-4o Vision fallback."""
    img = Image.open(file_path)
    w, h = img.size

    ocr_text = _ocr_image(img)

    # If OCR yields very little text, try GPT-4o Vision
    if len(ocr_text.strip()) < 20:
        vision_text = _vision_describe(file_path)
        if vision_text:
            ocr_text = vision_text

    page = ParsedPage(
        page_number=1,
        text=ocr_text.strip(),
    )

    logger.info(f"Image parsed: {file_path} ({w}x{h})")
    return ParsedDocument(
        file_name=os.path.basename(file_path),
        file_path=file_path,
        file_type="image",
        pages=[page],
        metadata={"width": w, "height": h},
    )


def _ocr_image(img: Image.Image) -> str:
    try:
        import pytesseract

        return pytesseract.image_to_string(img, lang="chi_sim+eng")
    except Exception as e:
        logger.warning(f"OCR failed: {e}")
        return ""


def _vision_describe(file_path: str) -> str:
    """Use GPT-4o Vision to describe an image when OCR fails."""
    try:
        import base64

        from openai import OpenAI
        from config import Config

        if not Config.OPENAI_API_KEY:
            return ""

        with open(file_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()

        ext = os.path.splitext(file_path)[1].lower().lstrip(".")
        mime_map = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                    "bmp": "image/bmp", "webp": "image/webp", "tiff": "image/tiff"}
        mime = mime_map.get(ext, "image/png")

        client = OpenAI(api_key=Config.OPENAI_API_KEY, base_url=Config.OPENAI_BASE_URL)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "请详细描述这张图片中的所有文字内容和关键信息。如果包含图表，请描述图表的数据和含义。请用中文回答。",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime};base64,{b64}"},
                        },
                    ],
                }
            ],
            max_tokens=1000,
        )
        return resp.choices[0].message.content or ""
    except Exception as e:
        logger.warning(f"Vision API failed: {e}")
        return ""
