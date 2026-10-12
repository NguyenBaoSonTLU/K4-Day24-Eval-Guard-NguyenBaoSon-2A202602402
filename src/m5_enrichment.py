"""Deterministic enrichment that preserves chunk count and order."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class EnrichedChunk:
    enriched_text: str
    auto_metadata: dict


_STOPWORDS = {
    "và", "là", "của", "có", "được", "cho", "trong", "theo", "các", "một",
    "nhân", "viên", "phải", "khi", "với", "từ", "đến", "này", "không", "thì",
}


def _keywords(text: str, limit: int = 8) -> list[str]:
    words = re.findall(r"[0-9A-Za-zÀ-ỹ]+", text.casefold(), flags=re.UNICODE)
    counts = Counter(word for word in words if len(word) > 2 and word not in _STOPWORDS)
    return [word for word, _ in counts.most_common(limit)]


def enrich_chunks(chunks: list[dict]) -> list[EnrichedChunk]:
    """Add source and keyword signals without calling another model/API."""
    enriched: list[EnrichedChunk] = []
    for chunk in chunks:
        text = str(chunk.get("text", "")).strip()
        metadata = dict(chunk.get("metadata", {}))
        source = str(metadata.get("source", "unknown"))
        keywords = _keywords(text)
        prefix = f"Nguồn: {source}. Từ khóa: {', '.join(keywords)}."
        enriched.append(
            EnrichedChunk(
                enriched_text=f"{prefix}\n{text}",
                auto_metadata={"keywords": keywords, "enrichment": "deterministic-v1"},
            )
        )
    return enriched
