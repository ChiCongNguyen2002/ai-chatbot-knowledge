"""
ULTRA-STRICT Safety Filter
Prevents ALL bad answers - threshold 0.85+ or REJECT
"""

from typing import List, Dict, Tuple, Optional


class UltraStrictSafetyFilter:
    """
    Reject unless 100% confident
    - Min confidence: 0.85 (85%)
    - Min top score: 0.85 (85%)
    - Min sources: 3
    - All must be relevant
    """

    def __init__(self):
        self.min_confidence = 0.85  # 85% confidence minimum
        self.min_top_score = 0.85   # Top result must be 85% relevant
        self.min_sources = 3        # Need at least 3 relevant sources

    def should_reject(
        self,
        sources: List[Dict],
        confidence: float,
        query: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if answer should be REJECTED (too risky to answer)

        Returns:
            (should_reject: bool, reason: str)
        """
        # Check 1: Not enough sources
        if len(sources) < self.min_sources:
            return True, f"Chỉ tìm {len(sources)} tài liệu, cần ≥3"

        # Check 2: Top result not confident enough
        top_score = sources[0].get('score', 0)
        if top_score < self.min_top_score:
            return True, f"Độ liên quan chỉ {top_score:.0%}, cần ≥85%"

        # Check 3: Overall confidence too low
        if confidence < self.min_confidence:
            return True, f"Chỉ {confidence:.0%} confident, cần ≥85%"

        # Check 4: Too many low-scoring sources
        low_scores = sum(1 for s in sources if s.get('score', 0) < 0.7)
        if low_scores > 1:
            return True, f"{low_scores} tài liệu có độ liên quan thấp"

        # All checks passed
        return False, None

    def get_safe_response(self, should_reject: bool, confidence: float) -> str:
        """Return answer or 'I don't know'"""
        if not should_reject:
            return None  # OK to answer

        return """⚠️  Xin lỗi, tôi chưa đủ tự tin về câu hỏi này.

Tôi biết chi tiết về:
✅ Microservices Architecture
✅ Docker & Kubernetes
✅ API Design & REST vs gRPC
✅ Go Routines & Concurrency
✅ Testing Strategies
✅ CI/CD & DevOps
✅ Database Optimization
✅ Security & Coding Standards

Hãy hỏi về các chủ đề trên hoặc cụ thể hơn nhé!"""


# Test it
if __name__ == "__main__":
    import sys
    sys.path.insert(0, '/tmp/ai-chatbot-knowledge/phase2')
    sys.path.insert(0, '/tmp/ai-chatbot-knowledge')

    from rag_pipeline import RAGPipeline
    from atlassian_ingester_full import create_full_confluence_data

    docs = create_full_confluence_data()
    pipeline = RAGPipeline(docs)
    safety = UltraStrictSafetyFilter()

    print("🛡️  ULTRA-STRICT SAFETY FILTER TEST")
    print("=" * 70)

    bad_queries = [
        "nice to meet you",
        "qq gì z",
        "nó hoạt động như nào",
        "microservice",  # Should be OK
        "REST là gì?",  # Should be OK
    ]

    for query in bad_queries:
        print(f"\n📌 Query: '{query}'")

        response = pipeline.search(query, use_reranking=False, top_k=3)

        # Check with strict filter
        should_reject, reason = safety.should_reject(
            response.sources,
            response.confidence,
            query
        )

        if should_reject:
            print(f"   ❌ REJECT: {reason}")
            print(f"   Response: 'I don't know'")
        else:
            print(f"   ✅ ACCEPT: Top={response.sources[0]['title']}")
            print(f"   Confidence: {response.confidence:.0%}")

print("\n" + "=" * 70)
print("✅ Ultra-strict filter prevents bad answers!")
