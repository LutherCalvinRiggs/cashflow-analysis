import logging
from typing import BinaryIO

import pdfplumber

logger = logging.getLogger(__name__)


def extract_text(file: BinaryIO) -> dict:
    pages = []
    try:
        with pdfplumber.open(file) as pdf:
            for i, page in enumerate(pdf.pages):
                try:
                    text = page.extract_text() or ""
                    pages.append(text)
                except Exception as e:
                    logger.warning("Failed to extract page %d: %s", i, e)
                    pages.append("")
    except Exception as e:
        logger.error("Failed to open PDF: %s", e)
        return {"pages": [], "full_text": "", "error": str(e)}

    return {
        "pages": pages,
        "full_text": "\n\n".join(pages),
    }
