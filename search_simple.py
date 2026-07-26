"""Simple in-memory search - NO Elasticsearch needed"""

import json
import os
import re
from typing import List, Dict
from rank_bm25 import BM25Okapi

# Vietnamese + English stop words
STOP_WORDS = {
    # Vietnamese
    'là', 'gì', 'cái', 'cách', 'như', 'thế', 'nào', 'hay', 'hay', 'và', 'hoặc', 'trong', 'với', 'này', 'kia',
    'đó', 'cái', 'tại', 'vì', 'bao', 'nhiêu', 'nào', 'nên', 'được', 'có', 'không', 'có', 'từ', 'để', 'khi',
    'nếu', 'mà', 'nhưng', 'cũng', 'chỉ', 'cũng', 'luôn', 'nhất', 'lại', 'thì', 'sẽ', 'đã', 'đang', 'hết',
    'chưa', 'lên', 'xuống', 'ra', 'vào', 'qua', 'lại', 'về', 'đến', 'sau', 'trước', 'giữa', 'giữa',
    # English
    'the', 'is', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'of', 'for', 'with', 'by',
    'as', 'was', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'can', 'may', 'might', 'must', 'what', 'which', 'who', 'where', 'when', 'why', 'how'
}

def normalize_plural(token: str) -> str:
    """Convert plural to singular (simple rule: remove trailing 's' if word ends in 's')"""
    if token.endswith('s') and len(token) > 2:
        return token[:-1]
    return token

def tokenize(text: str, normalize_plurals: bool = True) -> List[str]:
    """Tokenize text: remove punctuation, lowercase, filter stop words, normalize plurals"""
    # Remove punctuation and lowercase
    text = re.sub(r'[^\w\s]', '', text.lower())
    # Split and filter
    tokens = [t for t in text.split() if t and t not in STOP_WORDS]
    # Normalize plurals to singular (don't add both forms - breaks BM25 scoring)
    if normalize_plurals:
        tokens = [normalize_plural(t) for t in tokens]
    return tokens

class SimpleSearch:
    """BM25 + Intelligent ranking, in-memory"""

    def __init__(self, docs_file: str = "jira_docs.json"):
        self.docs = []
        self.bm25 = None
        self.tokenized_docs = []
        # Keyword-to-document mapping for better ranking
        self.keyword_map = {
            'devops': ['Docker', 'Kubernetes', 'Monitoring', 'CI/CD', 'Kafka'],
            'deploy': ['Docker', 'Kubernetes', 'CI/CD', 'Kafka', 'deployment'],
            'microservice': ['Microservices Architecture'],
            'vs': ['Microservices Architecture'],  # Boost Microservices for comparison queries
            'comparison': ['Microservices Architecture'],
            'nodejs': ['Coding Standards'],  # Exact match
            'go': ['Go Routine', 'Concurrency Patterns'],
            'api': ['API Design', 'API Response', 'API Authentication'],
            'security': ['Security Best Practices'],
            'kafka': ['Kafka deployment', 'Kafka with Redpanda'],
            'testing': ['Testing', 'Unit Testing', 'Integration Testing'],
        }
        self._load_documents(docs_file)

    def _load_documents(self, docs_file: str):
        """Load documents from file"""
        try:
            with open(docs_file, 'r', encoding='utf-8') as f:
                self.docs = json.load(f)
            print(f"✅ Loaded {len(self.docs)} documents")

            # Tokenize for BM25: include title + content so title keywords aren't lost
            self.tokenized_docs = []
            for doc in self.docs:
                # Combine title and content for better matching
                full_text = f"{doc['title']} {doc['content']}"
                self.tokenized_docs.append(tokenize(full_text))

            self.bm25 = BM25Okapi(self.tokenized_docs)
            print(f"✅ BM25 index ready")
        except Exception as e:
            print(f"⚠️ {e}")
            self.docs = []

    def _boost_score(self, doc_idx: int, query: str, bm25_score: float) -> float:
        """Boost score based on document relevance and query keywords"""
        doc = self.docs[doc_idx]
        doc_title = doc['title'].lower()
        doc_content = doc['content'].lower()
        query_lower = query.lower()

        boosted = bm25_score

        # Boost 1: Keyword-to-document mapping (HIGHEST PRIORITY)
        for keyword, preferred_docs in self.keyword_map.items():
            if keyword in query_lower:
                # Check if current doc title matches any preferred doc
                for pref_doc in preferred_docs:
                    if pref_doc.lower() in doc_title:
                        boosted *= 2.5  # Strong boost for keyword match
                        break

        # Boost 2: Document length (longer = more authoritative)
        doc_length = len(doc_content.split())
        if doc_length > 300:
            boosted *= 1.2  # +20% for long docs

        # Boost 3: Title keyword match (medium weight)
        query_words = [w for w in query_lower.split() if len(w) > 3]  # Only significant words
        title_matches = sum(1 for word in query_words if word in doc_title)
        if title_matches > 0:
            boosted *= (1 + 0.2 * title_matches)  # +20% per match

        # Penalize generic "best practices" docs if specific keyword present
        if "best practice" in doc_title and len(query_words) > 1:
            specific_keyword = [w for w in query_words if w not in ['best', 'practice', 'practices']]
            if specific_keyword and specific_keyword[0] not in doc_title:
                boosted *= 0.5  # Penalize by 50%

        return min(10.0, boosted)  # Cap at 10.0

    def bm25_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """BM25 search with intelligent boosting"""
        if not self.bm25:
            return []

        tokens = tokenize(query)
        if not tokens:
            return []

        scores = self.bm25.get_scores(tokens)

        # Rank by score with intelligent boosting
        ranked = []
        for i in range(len(scores)):
            if scores[i] > 0:
                boosted_score = self._boost_score(i, query, scores[i])
                ranked.append((i, boosted_score))

        ranked.sort(key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in ranked[:top_k]:
            doc = self.docs[idx].copy()
            doc['score'] = float(min(1.0, score / 10.0))  # Normalize to 0-1
            results.append(doc)

        return results

    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """Simple search - just BM25, no semantic"""
        results = self.bm25_search(query, top_k=top_k)

        # Normalize scores to 0-1
        if results:
            max_score = max(r['score'] for r in results)
            for doc in results:
                doc['score'] = min(1.0, doc['score'] / max_score if max_score > 0 else 0)

        return results
