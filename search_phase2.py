"""Phase 2: Hybrid Search - BM25 + Semantic Embeddings"""

import os
import json
from typing import List, Dict
from elasticsearch import Elasticsearch

try:
    import requests
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class HybridSearch:
    """Hybrid search: Elasticsearch BM25 + Ollama embeddings"""

    def __init__(self, es_host: str = None, ollama_host: str = None):
        self.es_host = es_host or os.environ.get("ES_HOST", "http://localhost:9200")
        self.ollama_host = ollama_host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.embedding_model = "bge-m3"
        self.es = None
        self.index_name = "knowledge"

        self._init_elasticsearch()

    def _init_elasticsearch(self):
        """Initialize Elasticsearch connection"""
        try:
            self.es = Elasticsearch([self.es_host])
            self.es.info()
            print(f"✅ Elasticsearch connected: {self.es_host}")
        except Exception as e:
            print(f"⚠️ Elasticsearch not available: {e}")
            self.es = None

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding from Ollama bge-m3"""
        if not OLLAMA_AVAILABLE:
            return None

        try:
            response = requests.post(
                f"{self.ollama_host}/api/embeddings",
                json={
                    "model": self.embedding_model,
                    "prompt": text
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get("embedding")
        except Exception as e:
            print(f"⚠️ Embedding error: {e}")

        return None

    def bm25_search(self, query: str, top_k: int = 20) -> List[Dict]:
        """Search using Elasticsearch BM25"""
        if not self.es:
            return []

        try:
            results = self.es.search(
                index=self.index_name,
                query={"match": {"content": query.lower()}},
                size=top_k
            )

            docs = []
            for hit in results["hits"]["hits"]:
                doc = hit["_source"]
                doc["bm25_score"] = hit["_score"]
                docs.append(doc)

            return docs

        except Exception as e:
            print(f"⚠️ BM25 search error: {e}")
            return []

    def semantic_rerank(self, query: str, docs: List[Dict]) -> List[Dict]:
        """Re-rank results using semantic similarity"""
        if not docs or not OLLAMA_AVAILABLE:
            return docs

        try:
            # Get query embedding
            query_embedding = self._get_embedding(query)
            if not query_embedding:
                return docs

            # Calculate semantic scores
            for doc in docs:
                doc_embedding = self._get_embedding(doc["content"][:300])
                if doc_embedding:
                    # Cosine similarity
                    similarity = self._cosine_similarity(query_embedding, doc_embedding)
                    doc["semantic_score"] = float(similarity)
                else:
                    doc["semantic_score"] = 0.0

            return docs

        except Exception as e:
            print(f"⚠️ Semantic rerank error: {e}")
            return docs

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity"""
        import math
        if not a or not b or len(a) != len(b):
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b))
        magnitude_a = math.sqrt(sum(x ** 2 for x in a))
        magnitude_b = math.sqrt(sum(x ** 2 for x in b))

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (magnitude_a * magnitude_b)

    def hybrid_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Hybrid search:
        1. BM25 ranking from Elasticsearch
        2. Semantic re-ranking with embeddings
        3. Combined score: 0.3*BM25 + 0.7*Semantic
        """

        # Step 1: BM25 search
        docs = self.bm25_search(query, top_k=20)

        if not docs:
            return []

        # Step 2: Semantic re-ranking
        docs = self.semantic_rerank(query, docs)

        # Step 3: Normalize and combine scores
        # Normalize BM25 scores
        if docs:
            max_bm25 = max(d.get("bm25_score", 0) for d in docs)
            max_semantic = max(d.get("semantic_score", 0) for d in docs)

            for doc in docs:
                bm25_norm = min(1.0, doc.get("bm25_score", 0) / max_bm25) if max_bm25 > 0 else 0
                semantic_norm = min(1.0, doc.get("semantic_score", 0) / max_semantic) if max_semantic > 0 else 0

                combined = min(1.0, 0.3 * bm25_norm + 0.7 * semantic_norm)
                doc["score"] = round(combined, 3)

            # Sort by combined score
            docs = sorted(docs, key=lambda d: d["score"], reverse=True)

        return docs[:top_k]


def search(query: str, top_k: int = 10) -> List[Dict]:
    """
    Global search function for compatibility with Phase 1
    """
    searcher = HybridSearch()
    return searcher.hybrid_search(query, top_k=top_k)


if __name__ == "__main__":
    print("🔄 Testing hybrid search...")

    searcher = HybridSearch()

    # Test queries
    test_queries = [
        "microservices architecture",
        "coding standards",
        "testing strategy",
    ]

    for query in test_queries:
        print(f"\n📍 Query: '{query}'")
        results = searcher.hybrid_search(query, top_k=3)

        if results:
            for i, doc in enumerate(results[:2], 1):
                print(f"  [{i}] {doc['title']} (score: {doc['score']:.3f})")
        else:
            print("  No results")
