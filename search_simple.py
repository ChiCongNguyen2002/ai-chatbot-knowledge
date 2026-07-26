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

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings (for typo tolerance)"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def find_closest_token(token: str, candidates: List[str], max_distance: int = 2) -> str:
    """Find closest matching token from candidates using Levenshtein distance"""
    if not candidates:
        return token

    closest = min(candidates, key=lambda c: levenshtein_distance(token, c))
    distance = levenshtein_distance(token, closest)

    # Return closest if within max distance, otherwise return original
    return closest if distance <= max_distance else token

def tokenize(text: str, normalize_plurals: bool = True) -> List[str]:
    """Tokenize text: remove punctuation, lowercase, filter stop words, normalize plurals"""
    # Remove punctuation and lowercase
    text = re.sub(r'[^\w\s]', '', text.lower())
    # Split and filter
    tokens = [t for t in text.split() if t and t not in STOP_WORDS]
    # Normalize plurals to singular
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
            'vs': ['Microservices Architecture'],
            'comparison': ['Microservices Architecture'],
            'nodejs': ['Coding Standards'],
            'go': ['Go Routine', 'Concurrency Patterns'],
            'api': ['Nguyên tắc tối ưu thiết kế API', 'API Design', 'API Response'],
            'security': ['Security Best Practices'],
            'kafka': ['Kafka deployment', 'Kafka with Redpanda'],
            'testing': ['Testing', 'Unit Testing', 'Integration Testing'],
            'monitor': ['Monitoring', 'Observability'],
            'logging': ['Logging', 'Monitoring'],
            'ci': ['CI/CD Pipeline'],
            'cd': ['CI/CD Pipeline'],
            'docker': ['Docker', 'Container'],
            'k8s': ['Kubernetes'],
            'kubernetes': ['Kubernetes', 'K8s'],
            'db': ['Database'],
            'database': ['Database', 'Optimization'],
            'sql': ['Database', 'PostgreSQL'],
            'redis': ['Redis Cache'],
            'cache': ['Redis Cache', 'Caching'],
        }

        # Query expansion: synonyms for better matching
        self.synonym_map = {
            'devops': ['deploy', 'deployment', 'infrastructure', 'docker', 'kubernetes'],
            'microservice': ['microservices', 'architecture', 'service-oriented'],
            'goroutine': ['go routine', 'concurrent', 'concurrency'],
            'testing': ['test', 'unit test', 'integration', 'e2e'],
            'security': ['safe', 'auth', 'authentication', 'encryption'],
            'database': ['db', 'sql', 'postgres', 'data'],
            'api': ['endpoint', 'rest', 'http', 'interface'],
            'logging': ['log', 'monitoring', 'observability', 'metrics'],
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

        # Boost 1: Document length first (longer = more authoritative)
        doc_length = len(doc_content.split())

        # Boost 2: Keyword-to-document mapping (HIGHEST PRIORITY)
        for keyword, preferred_docs in self.keyword_map.items():
            if keyword in query_lower:
                # Check if current doc title matches any preferred doc
                for pref_doc in preferred_docs:
                    if pref_doc.lower() in doc_title:
                        boosted *= 2.5  # Strong boost for keyword match
                        break

        # Boost 3: Prefer comprehensive/main docs for single-word queries
        if len(query_lower.split()) == 1:  # Single word query
            # Boost docs that contain the keyword in title AND are comprehensive
            for word in query_lower.split():
                if word in doc_title and doc_length > 200:
                    boosted *= 1.5  # Boost comprehensive docs

        # Boost 4: Document length (longer = more authoritative)
        if doc_length > 300:
            boosted *= 1.2  # +20% for long docs

        # Boost 5: Title keyword match (medium weight)
        query_words = [w for w in query_lower.split() if len(w) > 3]  # Only significant words
        title_matches = sum(1 for word in query_words if word in doc_title)
        if title_matches > 0:
            boosted *= (1 + 0.2 * title_matches)  # +20% per match

        # Boost 6: Penalize generic "best practices" docs if specific keyword present
        if "best practice" in doc_title and len(query_words) > 1:
            specific_keyword = [w for w in query_words if w not in ['best', 'practice', 'practices']]
            if specific_keyword and specific_keyword[0] not in doc_title:
                boosted *= 0.5  # Penalize by 50%

        return min(10.0, boosted)  # Cap at 10.0

    def _expand_query(self, tokens: List[str]) -> List[str]:
        """Expand query with synonyms for better matching"""
        expanded = list(tokens)
        for token in tokens:
            if token in self.synonym_map:
                expanded.extend(self.synonym_map[token])
        return list(set(expanded))  # Remove duplicates

    def bm25_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """BM25 search with intelligent boosting, query expansion, and fuzzy matching"""
        if not self.bm25:
            return []

        tokens = tokenize(query)
        if not tokens:
            return []

        # Get all available tokens from documents
        all_vocab = set()
        for doc_tokens in self.tokenized_docs:
            all_vocab.update(doc_tokens)

        # Apply fuzzy matching for typos: replace misspelled tokens with closest matches
        fuzzy_tokens = []
        for token in tokens:
            if token in all_vocab:
                fuzzy_tokens.append(token)
            else:
                # Try to find close match (typo correction)
                closest = find_closest_token(token, list(all_vocab), max_distance=2)
                fuzzy_tokens.append(closest)

        # Expand query with synonyms
        expanded_tokens = self._expand_query(fuzzy_tokens)
        scores = self.bm25.get_scores(expanded_tokens)

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
