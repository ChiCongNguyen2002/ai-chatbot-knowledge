"""Hybrid search: BM25 keyword ranking + semantic embedding rerank via Ollama"""

import os
import re
import requests
import numpy as np
from rank_bm25 import BM25Okapi
from typing import List, Dict, Tuple

DOCUMENTS = [
    {
        "id": "doc-333447169:chunk-0",
        "title": "Microservices",
        "url": "https://anfin.atlassian.net/wiki/spaces/TECH/pages/333447169",
        "text": "Micro-services is an architecture style that allows applications to be built as a set of loosely coupled, fine-grained services. The micro-service architecture encourages the idea of building small, focused applications that are independently deployable. Benefits include agility, maintainability, scalability, faster time to market, technology diversity, and increased reliability. Design principles: independently deployable, culture of automation, designing for failures, observability."
    },
    {
        "id": "doc-333414404:chunk-0",
        "title": "Evaluating Microservices Architecture",
        "url": "https://anfin.atlassian.net/wiki/spaces/TECH/pages/333414404",
        "text": "Understanding which part of the business will change most rapidly. A micro-services architecture embraces change. Identify which business areas need the most flexibility. Core priorities to identify: reliability, innovation, efficiency. Assign correlation tokens to each service request. Support multiple API versioning approaches: URI path, query parameter, content-type, custom header."
    },
    {
        "id": "doc-168132609:chunk-0",
        "title": "Notifications",
        "url": "https://anfin.atlassian.net/wiki/spaces/TECH/pages/168132609",
        "text": "Notification aggregation combines multiple similar notifications into single messages. Triggered when 3+ unique incidents occur within 60-second window. Implemented using Cloud Run background tasks at 2-minute intervals. Prevents notification fatigue by grouping duplicate alerts together, improving user experience and reducing alert noise."
    }
]

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://ollama:11434")
EMBEDDING_MODEL = "bge-m3"

# Cache for embeddings (precomputed at startup)
_embeddings_cache: Dict[str, np.ndarray] = {}
_bm25_index = None
_tokenized_docs = None


def _tokenize(text: str) -> List[str]:
    """Tokenize text: lowercase, split by word boundary."""
    return re.findall(r"\w+", text.lower())


def _embed(text: str) -> np.ndarray:
    """Call Ollama embedding API, return numpy array."""
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/embeddings",
            json={"model": EMBEDDING_MODEL, "prompt": text},
            timeout=30
        )
        if response.status_code == 200:
            embedding = response.json().get("embedding", [])
            return np.array(embedding, dtype=np.float32)
        else:
            print(f"⚠️  Embedding API error: {response.status_code}")
            return np.zeros(1024, dtype=np.float32)  # Fallback zero vector
    except Exception as e:
        print(f"⚠️  Embedding failed: {e}")
        return np.zeros(1024, dtype=np.float32)


def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Cosine similarity between two vectors."""
    if len(vec1) == 0 or len(vec2) == 0:
        return 0.0
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(vec1, vec2) / (norm1 * norm2))


def init_embeddings() -> None:
    """Precompute embeddings for all documents at startup."""
    global _embeddings_cache, _bm25_index, _tokenized_docs

    print("🔄 Initializing search index...")

    # Build BM25 index
    _tokenized_docs = [_tokenize(doc["text"]) for doc in DOCUMENTS]
    _bm25_index = BM25Okapi(_tokenized_docs)

    # Precompute embeddings
    for doc in DOCUMENTS:
        print(f"  Embedding: {doc['title']}...")
        _embeddings_cache[doc["id"]] = _embed(doc["text"])

    print(f"✅ Search index ready ({len(DOCUMENTS)} docs, BM25 + {EMBEDDING_MODEL})")


def hybrid_search(query: str, top_k: int = 3) -> List[Dict]:
    """
    Hybrid search: BM25 keyword ranking + semantic embedding rerank.

    Returns: list of dicts with id, title, url, text, score
    """
    if not _bm25_index or not _tokenized_docs:
        print("⚠️  Search index not initialized, returning all docs")
        return DOCUMENTS[:top_k]

    # Stage 1: BM25 keyword ranking
    query_tokens = _tokenize(query)
    bm25_scores = _bm25_index.get_scores(query_tokens)

    # Stage 2: Semantic embedding rerank
    query_embedding = _embed(query)
    semantic_scores = [
        _cosine_similarity(query_embedding, _embeddings_cache[doc["id"]])
        for doc in DOCUMENTS
    ]

    # Stage 3: Normalize and combine scores
    bm25_norm = np.array(bm25_scores)
    if bm25_norm.max() > 0:
        bm25_norm = bm25_norm / bm25_norm.max()

    semantic_norm = np.array(semantic_scores)
    if semantic_norm.max() > 0:
        semantic_norm = semantic_norm / semantic_norm.max()

    # Weighted combination: 40% BM25 (keyword), 60% semantic (contextual)
    combined_scores = 0.4 * bm25_norm + 0.6 * semantic_norm

    # Sort and return top-k with scores
    ranked = [
        {**DOCUMENTS[i], "score": float(combined_scores[i])}
        for i in np.argsort(-combined_scores)[:top_k]
    ]

    return ranked


if __name__ == "__main__":
    # Quick test
    init_embeddings()
    results = hybrid_search("What are microservices?", top_k=3)
    for r in results:
        print(f"[{r['score']:.3f}] {r['title']}")
