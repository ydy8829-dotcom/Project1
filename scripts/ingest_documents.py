from pathlib import Path
import argparse
import hashlib
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ingestion.chunker import chunk_text
from app.ingestion.pdf_loader import load_pdf


def main():
    parser = argparse.ArgumentParser(description="Ingest collected PDF, text and Markdown documents")
    parser.add_argument("--input-dir", default="data/raw")
    parser.add_argument("--output-dir", default="data/processed")
    args = parser.parse_args()
    raw, output = Path(args.input_dir), Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    files = [p for p in raw.rglob("*") if p.is_file() and p.suffix.lower() in {".pdf", ".txt", ".md"}]
    chunks = []
    for path in files:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        pages = load_pdf(path) if path.suffix.lower() == ".pdf" else [{"text": path.read_text(encoding="utf-8"), "page_number": None}]
        for page in pages:
            base = {"document_id": path.stem, "title": path.name, "source_url": "", "page_number": page.get("page_number"), "local_path": str(path), "sha256": digest}
            chunks.extend({"text": c.text, **c.metadata} for c in chunk_text(page["text"], base))
    target = output / "chunks.jsonl"
    target.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in chunks) + ("\n" if chunks else ""), encoding="utf-8")
    print(f"처리 완료: {len(chunks)} chunks -> {target}")


if __name__ == "__main__":
    main()
