"""Phase 1: BM25 Search - Fixed Version"""

import json
import re
from typing import List, Dict
from rank_bm25 import BM25Okapi

# Load hardcoded docs
with open("docs_v01.json") as f:
    DOCUMENTS = json.load(f)

# Common stopwords (English + Vietnamese)
STOPWORDS = {
    # English
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'for', 'from',
    'has', 'have', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'or', 'that',
    'the', 'to', 'was', 'will', 'with', 'you', 'your',
    # Vietnamese
    'là', 'cái', 'cái', 'có', 'được', 'để', 'với', 'về', 'từ', 'bạn',
    'gì', 'nào', 'và', 'hay', 'hoặc', 'không', 'chưa', 'đã', 'sẽ', 'tôi',
    'mình', 'tôi', 'chúng', 'tôi', 'anh', 'chị', 'em', 'bạn', 'ông', 'bà'
}


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
    BM25 keyword ranking search with stopword filtering
    Returns: list of docs with scores (only if meaningful query tokens found)
    """
    if not query or not query.strip():
        return []

    # Tokenize query
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    # Filter out stopwords - keep only meaningful terms
    meaningful_tokens = [t for t in query_tokens if t not in STOPWORDS]

    # If no meaningful tokens (only stopwords), return empty
    if not meaningful_tokens:
        return []

    # Build fresh index
    bm25 = _build_bm25_index()

    # Get BM25 scores
    scores = bm25.get_scores(query_tokens)

    # Filter: only include docs where MEANINGFUL query terms actually appear
    ranked = []
    for i in sorted(range(len(scores)), key=lambda i: scores[i], reverse=True):
        score = float(scores[i])

        # Check if ANY MEANINGFUL token appears in doc
        doc_text = DOCUMENTS[i]["content"].lower().replace("-", "")
        has_match = any(token in doc_text for token in meaningful_tokens)

        if has_match and score > 0.0:  # Only accept if score > 0
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
