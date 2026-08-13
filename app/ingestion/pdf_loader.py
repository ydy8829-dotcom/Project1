from pathlib import Path

import fitz


def load_pdf(path: str | Path) -> list[dict]:
    """별도 수집한 PDF를 페이지 단위 문서로 변환한다."""
    path = Path(path)
    pages = []
    with fitz.open(path) as document:
        for number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()
            if text:
                pages.append({"text": text, "page_number": number, "local_path": str(path)})
    return pages
