"""BM25 keyword search - simplified for Railway free tier (no embeddings)"""

import os
import re
from rank_bm25 import BM25Okapi
from typing import List, Dict

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

_bm25_index = None
_tokenized_docs = None


def _tokenize(text: str) -> List[str]:
    """Tokenize text: lowercase, split by word boundary."""
    return re.findall(r"\w+", text.lower())


def init_embeddings() -> None:
    """Initialize BM25 index (no embeddings for Railway free tier)."""
    global _bm25_index, _tokenized_docs

    print("🔄 Initializing search index (BM25 only)...")

    # Build BM25 index
    _tokenized_docs = [_tokenize(doc["text"]) for doc in DOCUMENTS]
    _bm25_index = BM25Okapi(_tokenized_docs)

    print(f"✅ Search index ready ({len(DOCUMENTS)} docs, BM25 ranking)")


def hybrid_search(query: str, top_k: int = 3) -> List[Dict]:
    """
    BM25 keyword ranking (no embeddings to save memory).

    Returns: list of dicts with id, title, url, text, score
    """
    if not _bm25_index or not _tokenized_docs:
        print("⚠️  Search index not initialized, returning all docs")
        return DOCUMENTS[:top_k]

    # BM25 keyword ranking
    query_tokens = _tokenize(query)
    bm25_scores = _bm25_index.get_scores(query_tokens)

    # Sort and return top-k
    ranked = [
        {**DOCUMENTS[i], "score": float(bm25_scores[i])}
        for i in sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:top_k]
    ]

    return ranked


if __name__ == "__main__":
    # Quick test
    init_embeddings()
    results = hybrid_search("What are microservices?", top_k=3)
    for r in results:
        print(f"[{r['score']:.3f}] {r['title']}")
