"""Multilingual cross-encoder reranking."""
from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class RerankResult:
    text: str
    score: float
    metadata: dict


class CrossEncoderReranker:
    def __init__(self, model_name: str | None = None) -> None:
        from sentence_transformers import CrossEncoder

        self.model_name = model_name or os.getenv(
            "RERANKER_MODEL", "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
        )
        self.model = CrossEncoder(self.model_name, trust_remote_code=True)

    def rerank(self, question: str, docs: list[dict], top_k: int = 3) -> list[RerankResult]:
        if not docs or top_k <= 0:
            return []
        pairs = [(question, str(doc["text"])) for doc in docs]
        scores = self.model.predict(pairs, show_progress_bar=False)
        ranked = sorted(
            zip(docs, scores), key=lambda item: float(item[1]), reverse=True
        )[: min(top_k, len(docs))]
        return [
            RerankResult(
                text=str(doc["text"]),
                score=float(score),
                metadata=dict(doc.get("metadata", {})),
            )
            for doc, score in ranked
        ]
