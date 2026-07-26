"""
Phase 2 - Full RAG Pipeline Integration
Complete retrieval-augmented generation pipeline combining all 9 priorities
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import time

from retrieval.hybrid_search import HybridSearchEngine
from processing.reranker import CrossEncoderReranker, RerankerPipeline
from processing.query_rewriter import QueryRewriter, QueryAnalyzer
from processing.chunking import SmartChunker
from processing.metadata_filter import MetadataFilter
from processing.compression import ContextCompressor, CitationHandler
from processing.safety_filter_strict import UltraStrictSafetyFilter
from memory.conversation import ConversationManager
from knowledge.graph import KnowledgeGraph


@dataclass
class RAGResponse:
    """Response from RAG pipeline"""
    answer: str
    sources: List[Dict]
    confidence: float
    latency_ms: float
    metadata: Dict = None


class RAGPipeline:
    """
    Complete RAG pipeline: Query → Search → Rank → Compress → Answer

    9-stage pipeline:
    1. Query Rewriting (intent detection + expansion)
    2. Hybrid Search (BM25 + Vector)
    3. Cross-Encoder Reranking (semantic relevance)
    4. Smart Chunking (semantic boundaries)
    5. Metadata Filtering (category, tags, freshness)
    6. Knowledge Graph Enrichment (related entities)
    7. Context Compression (fit token limits)
    8. Citation Tracking (source attribution)
    9. Conversation Memory (multi-turn context)
    """

    def __init__(self, documents: List[Dict], config: Optional[Dict] = None):
        """
        Initialize RAG pipeline

        Args:
            documents: List of documents to index
            config: Configuration dict with optional overrides
        """
        self.config = config or {}

        # Stage 1: Query Rewriting
        self.query_rewriter = QueryRewriter()
        self.query_analyzer = QueryAnalyzer()

        # Stage 2: Hybrid Search
        alpha = self.config.get('hybrid_alpha', 0.4)
        self.hybrid_search = HybridSearchEngine(documents, alpha=alpha)

        # Stage 3: Cross-Encoder Reranking
        self.reranker = CrossEncoderReranker()
        self.ranking_pipeline = RerankerPipeline(self.hybrid_search, self.reranker)

        # Stage 4: Smart Chunking
        chunk_size = self.config.get('chunk_size', 300)
        self.chunker = SmartChunker(chunk_size=chunk_size)

        # Stage 5: Metadata Filtering
        self.metadata_filter = MetadataFilter()

        # Stage 6: Knowledge Graph
        self.knowledge_graph = KnowledgeGraph()

        # Stage 7: Context Compression
        max_tokens = self.config.get('max_tokens', 4000)
        self.compressor = ContextCompressor(max_tokens=max_tokens)

        # Stage 8: Citation Handling
        self.citation_handler = CitationHandler()

        # Stage 9: Conversation Memory
        self.conversation_manager = ConversationManager()

        # Safety layer (ULTRA-STRICT)
        self.safety_filter = UltraStrictSafetyFilter()

        # Store original documents
        self.documents = documents

        print("[RAGPipeline] Initialized with 9-stage architecture")
        print(f"  - {len(documents)} documents indexed")
        print("  - Stages: Rewrite → Search → Rerank → Chunk → Filter → Graph → Compress → Cite → Memory")
        print("  - Safety: ULTRA-STRICT (78% confidence, 85% top score minimum)")

    def search(
        self,
        query: str,
        session_id: Optional[str] = None,
        apply_filters: Optional[Dict] = None,
        use_reranking: bool = True,
        top_k: int = 5,
        max_context_words: int = 2000
    ) -> RAGResponse:
        """
        Full pipeline search

        Args:
            query: User question
            session_id: Conversation session ID (for multi-turn)
            apply_filters: Metadata filters to apply
            use_reranking: Whether to use cross-encoder reranking
            top_k: Number of results to return
            max_context_words: Maximum words in compressed context

        Returns:
            RAGResponse with answer and sources
        """
        start_time = time.time()

        # Stage 1: Query Rewriting
        rewritten = self.query_rewriter.rewrite_query(query)
        primary_query = rewritten['primary_variation']

        # Stage 2: Hybrid Search
        if use_reranking:
            # Use reranking pipeline (top-20 candidates → top-5)
            search_results = self.ranking_pipeline.search_and_rerank(
                primary_query,
                hybrid_top_k=20,
                final_top_k=top_k
            )
        else:
            # Use hybrid search only
            search_results = self.hybrid_search.hybrid_search(primary_query, top_k=top_k)

        # Stage 3: Filter by metadata
        if apply_filters:
            search_results = self.metadata_filter.apply_filters(search_results, apply_filters)

        # Stage 4: Add knowledge graph context
        graph_enriched = self._enrich_with_graph(search_results, query)

        # Stage 5: Compress context
        compressed_context = self.compressor.compress_context(
            graph_enriched,
            query,
            max_words=max_context_words
        )

        # Stage 6: Track citations
        for doc in graph_enriched[:top_k]:
            self.citation_handler.add_citation(
                doc.get('id', 'unknown'),
                doc.get('title', ''),
                doc.get('content', ''),
                doc.get('content', '')[:100]
            )

        # Stage 7: Add conversation context if session provided
        conversation_context = ""
        if session_id:
            self.conversation_manager.add_user_message(session_id, query)
            conversation_context = self.conversation_manager.get_conversation_context(session_id)

        # Combine contexts
        final_context = (
            f"Previous conversation:\n{conversation_context}\n\n"
            if conversation_context
            else ""
        ) + compressed_context

        # Calculate confidence (average score of top results)
        confidence = sum(r.get('score', 0) for r in graph_enriched[:top_k]) / max(top_k, 1)
        confidence = min(1.0, confidence)  # Clamp to [0, 1]

        # ULTRA-STRICT SAFETY CHECK - Reject if not confident enough
        should_reject, reason = self.safety_filter.should_reject(
            graph_enriched[:top_k],
            confidence,
            query
        )

        if should_reject:
            final_context = self.safety_filter.get_safe_response(True, confidence)
            graph_enriched = []  # No sources for "I don't know" response
            confidence = 0.0

        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000

        # Create response
        response = RAGResponse(
            answer=final_context,
            sources=graph_enriched[:top_k],
            confidence=confidence,
            latency_ms=latency_ms,
            metadata={
                'query_intent': rewritten['intent'],
                'rewritten_query': primary_query,
                'results_count': len(graph_enriched),
                'used_reranking': use_reranking,
                'conversation_turns': self.conversation_manager.get_session(session_id).get_conversation_length() if session_id else 0,
            }
        )

        # Store assistant response in conversation
        if session_id:
            self.conversation_manager.add_assistant_message(
                session_id,
                final_context,
                metadata={'confidence': confidence, 'latency_ms': latency_ms}
            )

        return response

    def _enrich_with_graph(self, results: List[Dict], query: str) -> List[Dict]:
        """
        Enrich search results with knowledge graph relationships

        Args:
            results: Search results
            query: User query

        Returns:
            Results with graph relationships added
        """
        enriched = []

        for result in results:
            result_copy = result.copy()

            # Extract entities from result
            entities = self.knowledge_graph.extract_entities_from_text(
                f"{result['title']} {result['content']}"
            )

            # Add related entities
            related = set()
            for entity_name, _ in entities:
                related.update(
                    self.knowledge_graph.get_related_entities(entity_name, depth=2)
                )

            result_copy['related_entities'] = list(related)
            enriched.append(result_copy)

        return enriched

    def get_pipeline_info(self) -> Dict:
        """Get information about pipeline configuration"""
        return {
            'stages': 9,
            'documents_indexed': len(self.documents),
            'components': [
                'query_rewriter',
                'hybrid_search',
                'cross_encoder_reranker',
                'smart_chunker',
                'metadata_filter',
                'knowledge_graph',
                'context_compressor',
                'citation_handler',
                'conversation_manager'
            ],
            'configuration': {
                'hybrid_alpha': self.config.get('hybrid_alpha', 0.4),
                'chunk_size': self.config.get('chunk_size', 300),
                'max_tokens': self.config.get('max_tokens', 4000),
            }
        }
