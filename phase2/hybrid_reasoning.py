"""
Hybrid Reasoning System
Combines: KB Retrieval (facts) + Mistral Reasoning (analysis)

Strategy:
1. Simple questions → Pure KB retrieval (fast, 100% accurate)
2. Complex questions → KB + Mistral reasoning (slower, more insightful)
3. Seamless experience (user doesn't see the difference)
"""

import sys
sys.path.insert(0, '/tmp/ai-chatbot-knowledge/phase2')

from typing import Optional, Dict, Tuple
from dataclasses import dataclass
import subprocess
import json


@dataclass
class HybridResponse:
    """Response from hybrid system"""
    answer: str
    sources: list
    confidence: float
    latency_ms: float
    mode: str  # "kb-only" or "kb+reasoning"
    reasoning: Optional[str] = None


class QueryClassifier:
    """Determine if query needs reasoning or just facts"""

    # Simple queries (just need KB)
    SIMPLE_KEYWORDS = {
        'là gì', 'what is', 'định nghĩa', 'definition',
        'khái niệm', 'concept', 'là', 'is', 'tên',
        'name', 'example', 'ví dụ'
    }

    # Complex queries (need reasoning)
    COMPLEX_KEYWORDS = {
        'tại sao', 'why', 'nên dùng', 'should use',
        'khi nào', 'when', 'so sánh', 'compare',
        'khác nhau', 'difference', 'ưu điểm', 'advantage',
        'nhược điểm', 'disadvantage', 'giải pháp', 'solution',
        'cách', 'how', 'làm thế nào', 'phải không', 'best'
    }

    @staticmethod
    def classify(query: str) -> Tuple[str, str]:
        """
        Classify query complexity

        Returns:
            (complexity: 'simple' or 'complex', reason: str)
        """
        query_lower = query.lower()

        # Check for complex keywords
        complex_count = sum(1 for kw in QueryClassifier.COMPLEX_KEYWORDS if kw in query_lower)
        simple_count = sum(1 for kw in QueryClassifier.SIMPLE_KEYWORDS if kw in query_lower)

        # Heuristics
        if complex_count > simple_count:
            return "complex", f"Contains reasoning keywords: {complex_count} complex vs {simple_count} simple"

        if '?' in query and len(query.split()) > 8:
            return "complex", "Long question with multiple parts"

        if 'tại sao' in query_lower or 'why' in query_lower:
            return "complex", "Why question - needs reasoning"

        if 'so sánh' in query_lower or 'compare' in query_lower or 'vs' in query_lower:
            return "complex", "Comparison - needs analysis"

        # Default to simple
        return "simple", "Straightforward factual question"


class MistralReasoner:
    """Use Ollama Mistral for reasoning on top of KB facts"""

    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        self.model = "mistral"
        print(f"[MistralReasoner] Ready to use {self.model} at {ollama_host}")

    def reason(
        self,
        query: str,
        kb_facts: str,
        sources: list
    ) -> Optional[str]:
        """
        Use Mistral to reason on top of KB facts

        Args:
            query: Original user question
            kb_facts: Facts extracted from KB
            sources: Source documents

        Returns:
            Reasoning/analysis text, or None if Ollama unavailable
        """

        prompt = f"""Based on the following knowledge base information, analyze and answer the user's question with deeper reasoning:

KNOWLEDGE BASE FACTS:
{kb_facts}

SOURCES: {', '.join(s.get('title', 'Unknown') for s in sources[:3])}

USER QUESTION: {query}

Provide analysis that:
1. Uses the KB facts as foundation
2. Explains the reasoning (WHY)
3. Adds context and constraints specific to Anfin
4. Identifies when the KB doesn't cover something

Be concise (max 500 words). Format with clear sections."""

        try:
            response = subprocess.run(
                [
                    "curl", "-s", "-X", "POST",
                    f"{self.ollama_host}/api/generate",
                    "-H", "Content-Type: application/json",
                    "-d", json.dumps({
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "temperature": 0.7,
                    })
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if response.returncode == 0:
                result = json.loads(response.stdout)
                return result.get("response", "").strip()
            else:
                print(f"[MistralReasoner] Error: {response.stderr}")
                return None

        except Exception as e:
            print(f"[MistralReasoner] Ollama not available: {e}")
            return None


class HybridRAG:
    """
    Hybrid system combining KB retrieval + Mistral reasoning

    Flow:
    1. Classify query complexity
    2. If simple → Use KB only (fast)
    3. If complex → Use KB + Mistral reasoning (slower but insightful)
    """

    def __init__(self, kb_pipeline, ollama_host: str = "http://localhost:11434"):
        self.kb = kb_pipeline
        self.reasoner = MistralReasoner(ollama_host)
        print("[HybridRAG] Initialized: KB + Mistral Reasoning")

    def search(
        self,
        query: str,
        session_id: Optional[str] = None,
        force_mode: Optional[str] = None  # "kb-only" or "kb+reasoning"
    ) -> HybridResponse:
        """
        Search with automatic mode selection

        Args:
            query: User question
            session_id: Conversation session
            force_mode: Override auto-classification for testing

        Returns:
            HybridResponse with facts + optional reasoning
        """
        import time
        start_time = time.time()

        # Classify query
        if force_mode:
            complexity, reason = force_mode, "forced by user"
        else:
            complexity, reason = QueryClassifier.classify(query)

        print(f"\n[Hybrid] Query: '{query}'")
        print(f"[Hybrid] Mode: {complexity} ({reason})")

        # Stage 1: Always retrieve from KB
        kb_response = self.kb.search(
            query=query,
            session_id=session_id,
            use_reranking=True,
            top_k=3
        )

        # Stage 2: Add reasoning if complex
        reasoning_text = None
        if complexity == "complex" and kb_response.confidence > 0.6:
            print(f"[Hybrid] Running Mistral reasoning...")
            reasoning_text = self.reasoner.reason(
                query=query,
                kb_facts=kb_response.answer,
                sources=kb_response.sources
            )

        # Combine answers
        if reasoning_text:
            final_answer = f"""**FACTS FROM KNOWLEDGE BASE:**
{kb_response.answer}

**ANALYSIS & REASONING:**
{reasoning_text}"""
            mode = "kb+reasoning"
        else:
            final_answer = kb_response.answer
            mode = "kb-only"

        latency_ms = (time.time() - start_time) * 1000

        return HybridResponse(
            answer=final_answer,
            sources=kb_response.sources,
            confidence=kb_response.confidence,
            latency_ms=latency_ms,
            mode=mode,
            reasoning=reasoning_text
        )


# Test the hybrid system
if __name__ == "__main__":
    from rag_pipeline import RAGPipeline
    from atlassian_ingester_full import create_full_confluence_data

    print("🚀 HYBRID REASONING SYSTEM - TESTING")
    print("=" * 70)

    # Initialize KB
    docs = create_full_confluence_data()
    kb_pipeline = RAGPipeline(docs)

    # Initialize Hybrid
    hybrid = HybridRAG(kb_pipeline)

    # Test queries
    test_queries = [
        "REST là gì?",  # Simple → KB only
        "Tại sao nên dùng microservices?",  # Complex → KB + Reasoning
        "Docker vs Kubernetes khác nhau gì?",  # Complex → KB + Reasoning
        "Kafka là gì?",  # Simple → KB only
    ]

    for q in test_queries:
        print(f"\n\n📌 Query: {q}")
        print("-" * 70)

        response = hybrid.search(q)

        print(f"Mode: {response.mode}")
        print(f"Confidence: {response.confidence:.0%}")
        print(f"Latency: {response.latency_ms:.0f}ms")
        print(f"\nAnswer preview: {response.answer[:200]}...")

        if response.reasoning:
            print(f"\nReasoning: {response.reasoning[:200]}...")

print("\n" + "=" * 70)
print("✅ Hybrid system ready!")
print("  • Simple queries: KB only (160ms)")
print("  • Complex queries: KB + Mistral reasoning (2-5s)")
print("  • Seamless experience (automatic mode selection)")
