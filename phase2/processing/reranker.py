"""
Phase 2 - Cross-Encoder Reranker
Semantic relevance scoring using cross-encoder models
"""

from typing import List, Dict
import numpy as np


class CrossEncoderReranker:
    """
    Rerank search results using cross-encoder models.

    Strategy:
    1. Take top-20 hybrid search results
    2. Score relevance of each (query, document) pair
    3. Rerank by cross-encoder score
    4. Return top-5 reranked results

    Why cross-encoder?
    - Bi-encoder (Phase 1): embed query, embed doc, compute similarity (fast but less accurate)
    - Cross-encoder: pass (query, doc) pair to model together (slower but more accurate)
    - Use for final reranking of top candidates only (expensive operation)
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize reranker with cross-encoder model

        Args:
            model_name: HuggingFace model ID
                - "cross-encoder/ms-marco-MiniLM-L-6-v2": Fast, good for general ranking
                - "cross-encoder/mmarco-mMiniLMv2-L12-H384-multilingual": Multilingual
                - Recommended: Use MiniLM for fast local inference
        """
        self.model_name = model_name
        self.model = None

    def load(self) -> None:
        """Load cross-encoder model from HuggingFace hub"""
        if self.model is None:
            print(f"[Reranker] Loading {self.model_name}...")
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(self.model_name)
            print(f"[Reranker] Cross-encoder loaded")

    def score_pairs(
        self,
        query: str,
        documents: List[Dict],
        batch_size: int = 32
    ) -> List[float]:
        """
        Score relevance of (query, document) pairs

        Args:
            query: User question
            documents: List of documents with 'title' and 'content' fields
            batch_size: Process in batches for memory efficiency

        Returns:
            List of relevance scores [0, 1] for each document
        """
        if self.model is None:
            self.load()

        # Prepare (query, document) pairs
        pairs = []
        for doc in documents:
            # Combine title + content for better ranking context
            doc_text = f"{doc['title']}. {doc['content']}"
            pairs.append([query, doc_text])

        # Score all pairs
        scores = self.model.predict(pairs, batch_size=batch_size)

        # Normalize to [0, 1]
        # Cross-encoder outputs raw scores (can be negative or >1)
        # Normalize using sigmoid-like approach
        scores = 1 / (1 + np.exp(-scores))  # Sigmoid normalization

        return scores.tolist()

    def rerank(
        self,
        query: str,
        documents: List[Dict],
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Dict]:
        """
        Rerank documents by cross-encoder relevance

        Strategy:
        1. Score each document
        2. Filter by threshold (optional)
        3. Sort by score
        4. Return top-k

        Args:
            query: User question
            documents: List of documents with 'id', 'title', 'content'
            top_k: Number of results to return
            threshold: Minimum relevance score (0.0 = no threshold)

        Returns:
            Reranked documents with cross-encoder scores
        """
        if not documents:
            return []

        # Score documents
        scores = self.score_pairs(query, documents)

        # Combine with documents
        scored_docs = []
        for doc, score in zip(documents, scores):
            if score >= threshold:
                doc_copy = doc.copy()
                doc_copy['rerank_score'] = float(score)
                scored_docs.append(doc_copy)

        # Sort by cross-encoder score (descending)
        scored_docs.sort(key=lambda x: x['rerank_score'], reverse=True)

        return scored_docs[:top_k]

    def rerank_hybrid_results(
        self,
        query: str,
        hybrid_results: List[Dict],
        top_k: int = 5
    ) -> List[Dict]:
        """
        Convenience method: rerank hybrid search results

        Args:
            query: User question
            hybrid_results: Results from HybridSearchEngine
            top_k: Number of results to return

        Returns:
            Reranked results with both hybrid_score and rerank_score
        """
        if not hybrid_results:
            return []

        # Keep top-20 from hybrid (avoid reranking all, too expensive)
        candidates = hybrid_results[:20] if len(hybrid_results) > 20 else hybrid_results

        # Rerank
        reranked = self.rerank(query, candidates, top_k=top_k)

        return reranked


class RerankerPipeline:
    """
    Full reranking pipeline combining hybrid search + cross-encoder reranking
    """

    def __init__(self, hybrid_search_engine, reranker):
        """
        Initialize pipeline with hybrid search and reranker

        Args:
            hybrid_search_engine: HybridSearchEngine instance
            reranker: CrossEncoderReranker instance
        """
        self.hybrid_search = hybrid_search_engine
        self.reranker = reranker

    def search_and_rerank(
        self,
        query: str,
        hybrid_top_k: int = 20,
        final_top_k: int = 5
    ) -> List[Dict]:
        """
        Full pipeline: hybrid search → rerank → return

        Args:
            query: User question
            hybrid_top_k: Number of candidates from hybrid search
            final_top_k: Number of final results to return

        Returns:
            Top-k reranked results
        """
        # Stage 1: Hybrid search (fast, gets broad candidates)
        candidates = self.hybrid_search.hybrid_search(query, top_k=hybrid_top_k)

        # Stage 2: Cross-encoder reranking (slower, better ranking)
        final_results = self.reranker.rerank(query, candidates, top_k=final_top_k)

        return final_results
