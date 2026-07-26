"""Simple in-memory search - NO Elasticsearch needed"""

import json
import os
from typing import List, Dict
from rank_bm25 import BM25Okapi

class SimpleSearch:
    """BM25 + Ollama embeddings, in-memory"""

    def __init__(self, docs_file: str = "jira_docs.json"):
        self.docs = []
        self.bm25 = None
        self.tokenized_docs = []
        self._load_documents(docs_file)

    def _load_documents(self, docs_file: str):
        """Load documents from file"""
        try:
            with open(docs_file, 'r', encoding='utf-8') as f:
                self.docs = json.load(f)
            print(f"✅ Loaded {len(self.docs)} documents")

            # Tokenize for BM25
            self.tokenized_docs = [
                doc['content'].lower().split() for doc in self.docs
            ]
            self.bm25 = BM25Okapi(self.tokenized_docs)
            print(f"✅ BM25 index ready")
        except Exception as e:
            print(f"⚠️ {e}")
            self.docs = []

    def bm25_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """BM25 search"""
        if not self.bm25:
            return []

        tokens = query.lower().split()
        scores = self.bm25.get_scores(tokens)

        # Rank by score
        ranked = [
            (i, scores[i]) for i in range(len(scores))
            if scores[i] > 0
        ]
        ranked.sort(key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in ranked[:top_k]:
            doc = self.docs[idx].copy()
            doc['score'] = float(score)
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
