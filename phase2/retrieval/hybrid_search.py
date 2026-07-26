"""
Phase 2 - Hybrid Search Engine
Combines BM25 keyword search + FAISS vector search
"""

import numpy as np
from typing import List, Dict
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer


class HybridSearchEngine:
    """
    Hybrid search combining:
    - BM25: Traditional keyword ranking
    - FAISS: Vector similarity search
    - Combined: Weighted hybrid score
    """

    def __init__(
        self,
        documents: List[Dict],
        embedding_model: str = "all-MiniLM-L6-v2",
        alpha: float = 0.4  # 40% BM25, 60% vector
    ):
        """
        Initialize hybrid search engine

        Args:
            documents: List of docs with 'id', 'title', 'content'
            embedding_model: Lightweight sentence-transformer model
            alpha: Weight for BM25 (1-alpha = weight for vector)
        """
        self.docs = documents
        self.alpha = alpha
        self.embedding_model = SentenceTransformer(embedding_model)

        print(f"[HybridSearch] Initializing with {len(documents)} documents")

        # Initialize BM25
        self.tokenized_docs = [
            doc['content'].lower().split()
            for doc in documents
        ]
        self.bm25 = BM25Okapi(self.tokenized_docs)
        print("[HybridSearch] BM25 index ready")

        # Initialize FAISS
        self.embeddings = self._create_embeddings()
        self.index = self._build_faiss_index()
        print("[HybridSearch] FAISS index ready")

    def _create_embeddings(self) -> np.ndarray:
        """Create vector embeddings for all documents"""
        corpus = [
            f"{doc['title']} {doc['content']}"
            for doc in self.docs
        ]

        embeddings = self.embedding_model.encode(
            corpus,
            show_progress_bar=False,
            convert_to_numpy=True
        )

        return embeddings

    def _build_faiss_index(self):
        """Build FAISS index for fast similarity search"""
        import faiss

        dimension = self.embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(self.embeddings.astype('float32'))

        return index

    def bm25_search(self, query: str, top_k: int = 50) -> List[Dict]:
        """
        Traditional keyword search using BM25

        Args:
            query: User question
            top_k: Number of results

        Returns:
            List of documents ranked by BM25 score
        """
        tokens = query.lower().split()
        scores = self.bm25.get_scores(tokens)

        results = []
        for idx, score in enumerate(scores):
            if score > 0:
                results.append({
                    'id': self.docs[idx]['id'],
                    'title': self.docs[idx]['title'],
                    'content': self.docs[idx]['content'],
                    'score': float(score),
                    'method': 'bm25'
                })

        return sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]

    def vector_search(self, query: str, top_k: int = 50) -> List[Dict]:
        """
        Semantic search using embeddings

        Args:
            query: User question
            top_k: Number of results

        Returns:
            List of documents ranked by semantic similarity
        """
        query_embedding = self.embedding_model.encode(
            query,
            convert_to_numpy=True
        ).reshape(1, -1)

        distances, indices = self.index.search(
            query_embedding.astype('float32'),
            top_k
        )

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            # Convert L2 distance to similarity (inverse)
            similarity = 1 / (1 + float(distance))
            results.append({
                'id': self.docs[idx]['id'],
                'title': self.docs[idx]['title'],
                'content': self.docs[idx]['content'],
                'score': similarity,
                'method': 'vector'
            })

        return results

    def hybrid_search(
        self,
        query: str,
        top_k: int = 50
    ) -> List[Dict]:
        """
        Combine BM25 + Vector search

        Strategy:
        1. Run both methods
        2. Normalize scores to [0, 1]
        3. Combine with weights: alpha*BM25 + (1-alpha)*Vector
        4. Return top-k by combined score

        Args:
            query: User question
            top_k: Number of results

        Returns:
            List of documents ranked by hybrid score
        """
        # Get results from both methods
        bm25_results = self.bm25_search(query, top_k=100)
        vector_results = self.vector_search(query, top_k=100)

        # Normalize scores
        bm25_max = max([r['score'] for r in bm25_results], default=1)
        vector_max = max([r['score'] for r in vector_results], default=1)

        # Combine scores
        score_map = {}

        # Add BM25 scores
        for result in bm25_results:
            doc_id = result['id']
            normalized_score = result['score'] / bm25_max if bm25_max > 0 else 0
            score_map[doc_id] = score_map.get(doc_id, 0) + self.alpha * normalized_score

        # Add Vector scores
        for result in vector_results:
            doc_id = result['id']
            normalized_score = result['score'] / vector_max if vector_max > 0 else 0
            score_map[doc_id] = score_map.get(doc_id, 0) + (1 - self.alpha) * normalized_score

        # Sort by combined score
        final_results = [
            {
                'id': doc_id,
                'title': next(d['title'] for d in self.docs if d['id'] == doc_id),
                'content': next(d['content'] for d in self.docs if d['id'] == doc_id),
                'score': score,
                'method': 'hybrid'
            }
            for doc_id, score in score_map.items()
        ]

        return sorted(
            final_results,
            key=lambda x: x['score'],
            reverse=True
        )[:top_k]
