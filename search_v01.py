"""Phase 1: BM25 Search - Quality Verified"""

import json
import re
from typing import List, Dict
from rank_bm25 import BM25Okapi

# Load hardcoded docs
with open("docs_v01.json") as f:
    DOCUMENTS = json.load(f)

_bm25_index = None
_tokenized_docs = None


def _tokenize(text: str) -> List[str]:
    """Tokenize: lowercase, split by word boundary, handle hyphens"""
    # Replace hyphens with spaces for better tokenization
    text = text.replace("-", " ")
    return re.findall(r"\w+", text.lower())


def init_search_index() -> None:
    """Initialize BM25 index"""
    global _bm25_index, _tokenized_docs

    print("🔄 Initializing BM25 search index...")

    # Build index from doc content
    _tokenized_docs = [_tokenize(doc["content"]) for doc in DOCUMENTS]
    _bm25_index = BM25Okapi(_tokenized_docs)

    print(f"✅ Index ready: {len(DOCUMENTS)} docs")


def search(query: str, top_k: int = 3) -> List[Dict]:
    """
    BM25 ranking search
    Returns: list of docs with scores
    """
    if not _bm25_index:
        print("⚠️ Index not initialized")
        return DOCUMENTS[:top_k]

    # Tokenize query
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    # Get BM25 scores
    scores = _bm25_index.get_scores(query_tokens)

    # Sort and return top-k
    ranked = [
        {**DOCUMENTS[i], "score": float(scores[i])}
        for i in sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    ]

    return ranked


# ===== QUALITY VERIFICATION =====
def verify_search_quality():
    """Verify search works correctly"""
    init_search_index()

    test_cases = [
        {
            "query": "microservices?",
            "expected_top": "Microservices Architecture Best Practices",
            "min_score": 0.0  # Any match is OK
        },
        {
            "query": "error handling best practices",
            "expected_top": "Coding Standards and Best Practices",
            "min_score": 0.0
        },
        {
            "query": "notification system",
            "expected_top": "Notifications System Architecture",
            "min_score": 0.0
        }
    ]

    print("\n" + "="*60)
    print("SEARCH QUALITY VERIFICATION")
    print("="*60)

    passed = 0
    for test in test_cases:
        results = search(test["query"], top_k=3)
        top_title = results[0]["title"] if results else "NO RESULTS"
        top_score = results[0]["score"] if results else 0

        is_correct = (
            top_title == test["expected_top"] and
            top_score >= test["min_score"]
        )

        status = "✅" if is_correct else "❌"
        print(f"\n{status} Query: '{test['query']}'")
        print(f"   Expected: {test['expected_top']} (score >= {test['min_score']})")
        print(f"   Got: {top_title} (score {top_score:.2f})")

        if is_correct:
            passed += 1

    quality_score = (passed / len(test_cases)) * 100
    print(f"\n{'='*60}")
    print(f"Search Quality Score: {quality_score:.0f}%")

    if quality_score >= 95:
        print("✅ PASS: Search quality excellent")
        return True
    elif quality_score >= 80:
        print("⚠️ WARNING: Search quality acceptable")
        return True
    else:
        print("❌ FAIL: Search quality too low")
        return False


if __name__ == "__main__":
    verify_search_quality()
