"""Hybrid BM25 and BGE-M3 retrieval backed by Qdrant."""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from config import (BM25_TOP_K, COLLECTION_NAME, DENSE_TOP_K, EMBEDDING_DIM,
                    EMBEDDING_MODEL, HYBRID_TOP_K, QDRANT_HOST, QDRANT_PORT)


@dataclass(frozen=True)
class SearchResult:
    text: str
    score: float
    metadata: dict


def _tokens(text: str) -> list[str]:
    return re.findall(r"\w+", text.casefold(), flags=re.UNICODE)


class HybridSearch:
    """Index locally for BM25 and in Qdrant for dense retrieval."""

    def __init__(self) -> None:
        from qdrant_client import QdrantClient
        from sentence_transformers import SentenceTransformer

        self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, timeout=60)
        self.encoder = SentenceTransformer(EMBEDDING_MODEL)
        self.chunks: list[dict[str, Any]] = []
        self.bm25 = None

    def index(self, chunks: list[dict]) -> None:
        if not chunks:
            raise ValueError("Cannot index an empty chunk list")
        normalized: list[dict] = []
        for chunk in chunks:
            text = chunk.get("text")
            metadata = chunk.get("metadata", {})
            if not isinstance(text, str) or not text.strip() or not isinstance(metadata, dict):
                raise TypeError("Each chunk must contain non-empty text and dict metadata")
            normalized.append({"text": text.strip(), "metadata": dict(metadata)})

        from rank_bm25 import BM25Okapi
        from qdrant_client.http.models import Distance, PointStruct, VectorParams

        self.chunks = normalized
        self.bm25 = BM25Okapi([_tokens(chunk["text"]) for chunk in normalized])
        vectors = self.encoder.encode(
            [chunk["text"] for chunk in normalized],
            batch_size=8,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
        vector_size = int(vectors.shape[1])
        if vector_size != EMBEDDING_DIM:
            raise ValueError(
                f"{EMBEDDING_MODEL} returned dimension {vector_size}; expected {EMBEDDING_DIM}"
            )
        if self.client.collection_exists(COLLECTION_NAME):
            self.client.delete_collection(COLLECTION_NAME)
        self.client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        points = [
            PointStruct(
                id=index,
                vector=vector.tolist(),
                payload={"text": chunk["text"], "metadata": chunk["metadata"]},
            )
            for index, (chunk, vector) in enumerate(zip(normalized, vectors))
        ]
        self.client.upsert(collection_name=COLLECTION_NAME, points=points, wait=True)

    def search(self, question: str) -> list[SearchResult]:
        if not self.chunks or self.bm25 is None:
            raise RuntimeError("Call index() before search()")
        if not isinstance(question, str) or not question.strip():
            return []

        bm25_scores = self.bm25.get_scores(_tokens(question))
        lexical_ids = sorted(
            range(len(self.chunks)), key=lambda index: float(bm25_scores[index]), reverse=True
        )[:BM25_TOP_K]

        query_vector = self.encoder.encode(question, normalize_embeddings=True)
        dense_hits = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector.tolist(),
            limit=min(DENSE_TOP_K, len(self.chunks)),
            with_payload=True,
        )

        # Reciprocal-rank fusion keeps BM25 and dense scores on comparable scales.
        fused: dict[int, float] = {}
        for rank, chunk_id in enumerate(lexical_ids, start=1):
            fused[chunk_id] = fused.get(chunk_id, 0.0) + 1.0 / (60 + rank)
        for rank, hit in enumerate(dense_hits, start=1):
            chunk_id = int(hit.id)
            fused[chunk_id] = fused.get(chunk_id, 0.0) + 1.0 / (60 + rank)

        ranked_ids = sorted(fused, key=fused.get, reverse=True)[:HYBRID_TOP_K]
        return [
            SearchResult(
                text=self.chunks[chunk_id]["text"],
                score=float(fused[chunk_id]),
                metadata=dict(self.chunks[chunk_id]["metadata"]),
            )
            for chunk_id in ranked_ids
        ]
