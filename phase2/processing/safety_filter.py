"""Safety Filter - Ngăn chặn hallucination & bậy bạ"""

from typing import List, Dict, Tuple, Optional


class SafetyFilter:
    """
    Chỉ trả lời khi CHẮC CHẮN có kiến thức
    - Confidence threshold: 0.7 (70%)
    - Relevance score threshold: 0.5
    - Không "bịa" câu trả lời từ tài liệu không liên quan
    """

    def __init__(
        self,
        min_confidence: float = 0.7,
        min_top_score: float = 0.6,
        max_results_needed: int = 2
    ):
        """
        Initialize safety filter

        Args:
            min_confidence: Tối thiểu 70% confidence để trả lời
            min_top_score: Top result phải có score ≥ 0.6
            max_results_needed: Phải có ≥ 2 relevant docs
        """
        self.min_confidence = min_confidence
        self.min_top_score = min_top_score
        self.max_results_needed = max_results_needed

    def should_answer(
        self,
        sources: List[Dict],
        confidence: float,
        query: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if answer is safe to return

        Returns:
            (should_answer: bool, reason_if_no: str)
        """
        # Check 1: Có ít nhất N tài liệu liên quan?
        if len(sources) < self.max_results_needed:
            return False, f"❌ Tôi chỉ tìm thấy {len(sources)} tài liệu, cần ít nhất {self.max_results_needed} để chắc chắn."

        # Check 2: Top result có score cao đủ không?
        top_score = sources[0].get('score', 0)
        if top_score < self.min_top_score:
            return False, f"⚠️  Độ liên quan chỉ {top_score:.0%}, tôi không đủ tự tin để trả lời."

        # Check 3: Confidence (average score) đủ cao không?
        if confidence < self.min_confidence:
            return False, f"⚠️  Độ chắc chắn chỉ {confidence:.0%}, tôi không đủ tự tin."

        # Check 4: Tất cả results có score hợp lý không? (không có doc "lạc đề")
        scores = [src.get('score', 0) for src in sources[:3]]
        if any(s < 0.4 for s in scores):
            return False, "⚠️  Một số tài liệu không liên quan, tôi không chắc chắn."

        # All checks passed
        return True, None

    def get_safe_response(
        self,
        sources: List[Dict],
        confidence: float,
        query: str,
        original_answer: str
    ) -> Dict:
        """
        Return safe response or "I don't know"

        Returns:
            {
                "answer": str,
                "is_safe": bool,
                "confidence": float,
                "sources": List[Dict]
            }
        """
        should_answer, reason = self.should_answer(sources, confidence, query)

        if should_answer:
            return {
                "answer": original_answer,
                "is_safe": True,
                "confidence": confidence,
                "sources": sources,
                "status": "✅ Confident answer"
            }
        else:
            # Return "don't know" response
            fallback = f"""
{reason}

Tôi biết về:
• Microservices Architecture
• Docker & Kubernetes
• API Design (REST, gRPC)
• Go Concurrency & Goroutines
• Testing Strategies
• DevOps & CI/CD
• Database Optimization
• Security Best Practices

Hãy hỏi về chủ đề này hoặc một chủ đề khác!
"""
            return {
                "answer": fallback.strip(),
                "is_safe": False,
                "confidence": confidence,
                "sources": [],
                "status": "⚠️  Not confident - returned I don't know"
            }


class RelevanceScorer:
    """
    Score relevance of document to query
    - Check keyword overlap
    - Check semantic distance
    - Detect "lạc đề" documents
    """

    @staticmethod
    def calculate_relevance_score(
        doc_title: str,
        doc_content: str,
        query: str,
        hybrid_score: float
    ) -> float:
        """
        Calculate if document is truly relevant

        Score = hybrid_score * keyword_match_factor * semantic_factor
        """
        query_words = set(query.lower().split())
        doc_text = f"{doc_title} {doc_content}".lower()

        # Keyword overlap (0.0 - 1.0)
        keyword_matches = sum(
            1 for word in query_words
            if len(word) > 3 and word in doc_text
        )
        keyword_factor = min(1.0, keyword_matches / len(query_words)) if query_words else 0.5

        # Semantic factor: use title match as proxy
        title_match = 1.0 if any(
            word in doc_title.lower() for word in query_words if len(word) > 3
        ) else 0.7

        # Final score
        final_score = hybrid_score * (0.6 * keyword_factor + 0.4 * title_match)

        return min(1.0, final_score)

    @staticmethod
    def filter_relevant_sources(
        sources: List[Dict],
        query: str,
        min_relevance: float = 0.4
    ) -> List[Dict]:
        """
        Keep only truly relevant sources, remove "lạc đề" docs
        """
        filtered = []

        for src in sources:
            relevance = RelevanceScorer.calculate_relevance_score(
                doc_title=src.get('title', ''),
                doc_content=src.get('content', ''),
                query=query,
                hybrid_score=src.get('score', 0)
            )

            if relevance >= min_relevance:
                src['relevance_score'] = relevance
                filtered.append(src)

        # Re-sort by relevance
        filtered.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        return filtered
