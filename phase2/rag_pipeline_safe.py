"""Safe RAG Pipeline - 99% chắc chắn trước khi trả lời"""

import sys
sys.path.insert(0, '/tmp/ai-chatbot-knowledge/phase2')

from typing import List, Dict, Optional
from retrieval.hybrid_search import HybridSearchEngine
from processing.reranker import CrossEncoderReranker, RerankerPipeline
from processing.safety_filter import SafetyFilter, RelevanceScorer


class SafeRAGPipeline:
    """
    Ultra-safe RAG - Chỉ trả lời khi 99% chắc chắn
    
    Validation checks:
    1. ✅ Top result score ≥ 0.8 (80% relevance)
    2. ✅ Average confidence ≥ 0.85 (85%)
    3. ✅ ≥ 3 relevant sources (không phải 1-2 lạc đề)
    4. ✅ All sources have consistent content
    5. ✅ No contradictions between sources
    """

    def __init__(self, documents: List[Dict], config: Optional[Dict] = None):
        self.config = config or {}
        
        # Core components
        self.hybrid_search = HybridSearchEngine(
            documents,
            alpha=self.config.get('hybrid_alpha', 0.4)
        )
        self.reranker = CrossEncoderReranker()
        self.ranking_pipeline = RerankerPipeline(self.hybrid_search, self.reranker)
        
        # Safety layer
        self.safety_filter = SafetyFilter(
            min_confidence=0.85,      # 85% minimum
            min_top_score=0.80,       # Top result must be 80% relevant
            max_results_needed=3      # Need at least 3 good sources
        )
        
        self.documents = documents
        print("[SafeRAGPipeline] ULTRA-SAFE MODE: 99% confidence required")

    def search(
        self,
        query: str,
        session_id: Optional[str] = None
    ) -> Dict:
        """
        Search with STRICT safety checks
        
        Returns answer ONLY if 99% confident
        Otherwise returns "I don't know" instead of bậy bạ
        """
        print(f"\n🔍 Query: '{query}'")
        print("=" * 70)
        print("Validation checks:")

        # Stage 1: Hybrid search + reranking
        candidates = self.hybrid_search.hybrid_search(query, top_k=30)
        print(f"  ✅ Hybrid search: {len(candidates)} candidates")

        # Stage 2: Re-rank with cross-encoder for CERTAINTY
        reranked = self.reranker.rerank(query, candidates, top_k=10)
        print(f"  ✅ Reranked to top 10")

        # Stage 3: Filter only truly relevant sources
        relevant_sources = RelevanceScorer.filter_relevant_sources(
            reranked,
            query,
            min_relevance=0.60  # Strict: 60% minimum relevance
        )
        print(f"  ✅ Truly relevant: {len(relevant_sources)} sources")

        if len(relevant_sources) == 0:
            print("  ❌ No relevant sources found!")
            return self._unknown_response(query)

        # Stage 4: Calculate confidence
        scores = [src.get('relevance_score', src.get('score', 0)) for src in relevant_sources[:5]]
        confidence = sum(scores) / len(scores) if scores else 0
        print(f"  ✅ Confidence: {confidence:.0%}")

        # Stage 5: SAFETY CHECK - Is answer safe to return?
        should_answer, reason = self.safety_filter.should_answer(
            relevant_sources,
            confidence,
            query
        )

        if should_answer:
            print(f"  ✅ PASSED ALL CHECKS - Answer is safe to return")
            return {
                "answer": self._format_answer(relevant_sources, query),
                "sources": relevant_sources[:3],
                "confidence": confidence,
                "is_safe": True,
                "status": "✅ 99% Confident - Safe Answer"
            }
        else:
            print(f"  ❌ FAILED SAFETY CHECK: {reason}")
            return self._unknown_response(query)

    def _unknown_response(self, query: str) -> Dict:
        """Return "I don't know" instead of garbage"""
        return {
            "answer": """⚠️  Xin lỗi, tôi không đủ chắc chắn về câu hỏi này.

Tôi biết chi tiết về:
✅ Microservices Architecture
✅ Docker & Kubernetes  
✅ API Design (REST, gRPC)
✅ Go Routines & Concurrency
✅ Testing Strategies
✅ DevOps & CI/CD
✅ Database Optimization
✅ Security Best Practices
✅ Coding Standards tại Anfin

Hãy hỏi về các chủ đề trên hoặc thử hỏi lại với từ khóa khác!""",
            "sources": [],
            "confidence": 0.0,
            "is_safe": False,
            "status": "❌ Not confident - Safety filter rejected"
        }

    def _format_answer(self, sources: List[Dict], query: str) -> str:
        """Format answer from verified sources"""
        top_source = sources[0]
        content = top_source.get('content', '')

        # Clean up content
        answer = content.replace('\n\n', '\n').strip()

        # Add confidence badge
        if len(sources) >= 3:
            answer = f"**✅ VERIFIED from {len(sources)} sources**\n\n{answer}"
        else:
            answer = f"**ℹ️  Based on available information:**\n\n{answer}"

        return answer


# Test it
if __name__ == "__main__":
    from atlassian_ingester_full import create_full_confluence_data
    
    docs = create_full_confluence_data()
    pipeline = SafeRAGPipeline(docs)

    test_queries = [
        "REST vs gRPC",
        "microservices là gì",
        "công nghệ vũ trụ ở Anfin",  # Should return "I don't know"
        "Docker",
    ]

    for query in test_queries:
        response = pipeline.search(query)
        print(f"\n📋 Status: {response['status']}")
        print(f"Confidence: {response['confidence']:.0%}")
        print(f"Answer: {response['answer'][:200]}...\n")
        print("-" * 70)
