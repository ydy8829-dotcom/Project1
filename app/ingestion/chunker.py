from dataclasses import dataclass


@dataclass
class Chunk:
    chunk_id: str
    text: str
    metadata: dict


def chunk_text(text: str, metadata: dict, chunk_size: int = 1200, overlap: int = 150) -> list[Chunk]:
    text = " ".join(text.split())
    if not text:
        return []
    chunks = []
    start = 0
    index = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        item = dict(metadata)
        item["chunk_index"] = index
        chunk_id = f"{metadata.get('document_id', 'doc')}-{index:04d}"
        chunks.append(Chunk(chunk_id, text[start:end], item | {"chunk_id": chunk_id}))
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
        index += 1
    return chunks
