"""Phase 1: BM25 Search - Fixed Version"""

import json
import re
from typing import List, Dict
from rank_bm25 import BM25Okapi

# Load hardcoded docs
with open("docs_v01.json") as f:
    DOCUMENTS = json.load(f)


def _tokenize(text: str) -> List[str]:
    """Tokenize: lowercase, remove hyphens, split by word boundary"""
    # Remove hyphens so "micro-services" → "microservices"
    text = text.replace("-", "")
    return re.findall(r"\w+", text.lower())


def _build_bm25_index():
    """Build BM25 index from documents"""
    tokenized_docs = [_tokenize(doc["content"]) for doc in DOCUMENTS]
    return BM25Okapi(tokenized_docs)


def search(query: str, top_k: int = 3) -> List[Dict]:
    """
    BM25 keyword ranking search with threshold filtering
    Returns: list of docs with scores (only if query tokens found)
    """
    if not query or not query.strip():
        return []

    # Build fresh index
    bm25 = _build_bm25_index()

    # Tokenize query
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    # Get BM25 scores
    scores = bm25.get_scores(query_tokens)

    # Filter: only include docs where query terms actually appear
    ranked = []
    for i in sorted(range(len(scores)), key=lambda i: scores[i], reverse=True):
        score = float(scores[i])

        # Check if ANY query token appears in doc (remove hyphens like tokenization does)
        doc_text = DOCUMENTS[i]["content"].lower().replace("-", "")
        has_match = any(token in doc_text for token in query_tokens)

        if has_match:
            doc_copy = dict(DOCUMENTS[i])
            doc_copy["score"] = score
            ranked.append(doc_copy)

            if len(ranked) >= top_k:
                break

    return ranked


# ===== QUALITY VERIFICATION =====
def verify_search_quality():
    """Verify search works correctly"""

    test_cases = [
        {
            "query": "microservices",
            "expected_top": "Microservices Architecture Best Practices",
        },
        {
            "query": "error handling",
            "expected_top": "Coding Standards and Best Practices",
        },
        {
            "query": "notification",
            "expected_top": "Notifications System Architecture",
        }
    ]

    print("\n" + "="*60)
    print("SEARCH QUALITY VERIFICATION")
    print("="*60)

    passed = 0
    for test in test_cases:
        results = search(test["query"], top_k=3)

        if not results:
            print(f"\n❌ Query: '{test['query']}'")
            print(f"   NO RESULTS FOUND!")
            continue

        top_title = results[0]["title"]
        top_score = results[0]["score"]
        is_correct = top_title == test["expected_top"]

        status = "✅" if is_correct else "❌"
        print(f"\n{status} Query: '{test['query']}'")
        print(f"   Expected: {test['expected_top']}")
        print(f"   Got: {top_title}")
        print(f"   Score: {top_score:.4f}")

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
