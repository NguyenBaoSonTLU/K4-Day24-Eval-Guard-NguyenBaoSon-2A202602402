"""Load the policy corpus and create hierarchical chunks for the RAG pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

from config import DATA_DIR, HIERARCHICAL_CHILD_SIZE, HIERARCHICAL_PARENT_SIZE


@dataclass(frozen=True)
class ParentChunk:
    text: str
    metadata: dict
    parent_id: str


@dataclass(frozen=True)
class ChildChunk:
    text: str
    metadata: dict
    parent_id: str


def _pdf_text(path: Path) -> str:
    from pypdf import PdfReader

    return "\n\n".join((page.extract_text() or "").strip() for page in PdfReader(path).pages).strip()


def load_documents() -> list[dict]:
    """Read every supported corpus file while retaining source metadata."""
    root = Path(DATA_DIR)
    documents: list[dict] = []
    for path in sorted(root.iterdir(), key=lambda item: item.name.casefold()):
        if path.suffix.lower() == ".md":
            text = path.read_text(encoding="utf-8")
        elif path.suffix.lower() == ".pdf":
            text = _pdf_text(path)
        else:
            continue
        if text.strip():
            documents.append({
                "text": text.strip(),
                "metadata": {
                    "source": path.name,
                    "source_path": str(path.resolve()),
                    "file_type": path.suffix.lower().lstrip("."),
                },
            })
    if not documents:
        raise ValueError(f"No supported documents found in {root}")
    return documents


def _windows(words: list[str], size: int, overlap: int) -> Iterable[tuple[int, list[str]]]:
    step = max(1, size - overlap)
    for start in range(0, len(words), step):
        window = words[start:start + size]
        if window:
            yield start, window
        if start + size >= len(words):
            break


def _document_slug(metadata: dict, text: str) -> str:
    source = str(metadata.get("source", "document"))
    slug = re.sub(r"[^0-9A-Za-zÀ-ỹ]+", "-", Path(source).stem, flags=re.UNICODE).strip("-").lower()
    return slug or f"document-{abs(hash(text))}"


def chunk_hierarchical(text: str, metadata: dict | None = None) -> tuple[list[ParentChunk], list[ChildChunk]]:
    """Split a document by word windows and attach each child to its parent."""
    if not isinstance(text, str) or not text.strip():
        return [], []
    base_metadata = dict(metadata or {})
    words = text.split()
    parent_size = max(1, int(HIERARCHICAL_PARENT_SIZE))
    child_size = max(1, int(HIERARCHICAL_CHILD_SIZE))
    parent_overlap = min(parent_size // 8, 128)
    child_overlap = min(child_size // 6, 48)
    slug = _document_slug(base_metadata, text)
    parents: list[ParentChunk] = []
    children: list[ChildChunk] = []

    for parent_number, (parent_start, parent_words) in enumerate(
        _windows(words, parent_size, parent_overlap)
    ):
        parent_id = f"{slug}:p{parent_number}"
        parent_metadata = {
            **base_metadata,
            "parent_index": parent_number,
            "word_start": parent_start,
        }
        parents.append(ParentChunk(" ".join(parent_words), parent_metadata, parent_id))
        for child_number, (child_start, child_words) in enumerate(
            _windows(parent_words, child_size, child_overlap)
        ):
            child_metadata = {
                **parent_metadata,
                "chunk_index": child_number,
                "word_start": parent_start + child_start,
            }
            children.append(ChildChunk(" ".join(child_words), child_metadata, parent_id))
    return parents, children
