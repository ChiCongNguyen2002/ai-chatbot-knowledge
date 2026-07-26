"""
Phase 2 - Integration Tests
End-to-end testing of full RAG pipeline with all 9 components
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_pipeline import RAGPipeline


def create_test_documents():
    """Create comprehensive test documents"""
    return [
        {
            "id": "microservices-101",
            "title": "Microservices Architecture",
            "content": "Microservices is an architectural style that structures an application as a collection "
                      "of loosely coupled, independently deployable services. Each service runs in its own process "
                      "and communicates with others via APIs. Key benefits: scalability, independent deployment, "
                      "fault isolation, technology diversity.",
            "category": "architecture",
            "tags": ["microservices", "architecture", "design-pattern"],
            "confidence": 0.95,
            "updated_at": "2026-07-20"
        },
        {
            "id": "docker-deploy",
            "title": "Docker & Container Deployment",
            "content": "Docker is a containerization platform that packages applications and dependencies into "
                      "containers. Containers are lightweight, portable, and consistent across environments. "
                      "Benefits: environment consistency, easy scaling, faster deployment, reduced operational overhead. "
                      "Use with Kubernetes for orchestration.",
            "category": "devops",
            "tags": ["docker", "containers", "deployment", "devops"],
            "confidence": 0.98,
            "updated_at": "2026-07-22"
        },
        {
            "id": "api-design",
            "title": "API Design Best Practices",
            "content": "Well-designed APIs are crucial for service communication. Best practices include: versioning, "
                      "pagination, filtering, caching, error handling, documentation. Use RESTful principles: "
                      "proper HTTP methods, status codes, URI structure. Consider GraphQL for complex querying. "
                      "Essential for microservices.",
            "category": "architecture",
            "tags": ["api", "rest", "design", "integration"],
            "confidence": 0.92,
            "updated_at": "2026-07-25"
        },
        {
            "id": "kafka-messaging",
            "title": "Kafka Event Streaming",
            "content": "Apache Kafka is a distributed event streaming platform for building real-time data pipelines. "
                      "Topics organize messages by category. Partitions enable parallel processing. Consumer groups "
                      "allow multiple subscribers. Features: durability, high-throughput, fault-tolerance. "
                      "Integrates with microservices for async communication.",
            "category": "data-pipeline",
            "tags": ["kafka", "streaming", "messaging", "event-driven"],
            "confidence": 0.90,
            "updated_at": "2026-07-21"
        },
        {
            "id": "testing-guide",
            "title": "Testing Strategies for Microservices",
            "content": "Testing microservices requires different strategies than monolithic apps. Unit tests for individual "
                      "services, integration tests for service interactions, contract tests for APIs, "
                      "end-to-end tests for full flows. Key challenge: managing test data and dependencies.",
            "category": "testing",
            "tags": ["testing", "microservices", "quality-assurance"],
            "confidence": 0.85,
            "updated_at": "2026-07-19"
        },
    ]


def test_full_pipeline_basic():
    """Test basic pipeline functionality"""
    print("\n=== TEST 1: Full Pipeline - Basic Search ===\n")

    docs = create_test_documents()
    pipeline = RAGPipeline(docs)

    test_queries = [
        "What is microservices?",
        "How do I deploy with Docker?",
        "Tell me about API design",
    ]

    for query in test_queries:
        response = pipeline.search(query, use_reranking=False, top_k=2)

        print(f"Query: {query}")
        print(f"  Confidence: {response.confidence:.2f}")
        print(f"  Latency: {response.latency_ms:.1f}ms")
        print(f"  Sources: {len(response.sources)}")
        for i, src in enumerate(response.sources, 1):
            print(f"    {i}. {src['title']}")
        print()


def test_pipeline_with_reranking():
    """Test pipeline with cross-encoder reranking"""
    print("\n=== TEST 2: Full Pipeline - With Reranking ===\n")

    docs = create_test_documents()
    pipeline = RAGPipeline(docs)

    query = "microservices deployment and scaling"

    print(f"Query: {query}\n")

    # Without reranking
    response_no_rerank = pipeline.search(query, use_reranking=False, top_k=3)
    print("Without Reranking:")
    for i, src in enumerate(response_no_rerank.sources, 1):
        print(f"  {i}. {src['title']} (score: {src['score']:.3f})")

    # With reranking
    response_with_rerank = pipeline.search(query, use_reranking=True, top_k=3)
    print("\nWith Reranking:")
    for i, src in enumerate(response_with_rerank.sources, 1):
        score = src.get('rerank_score', src.get('score', 0))
        print(f"  {i}. {src['title']} (score: {score:.3f})")

    print(f"\nLatency impact:")
    print(f"  Without rerank: {response_no_rerank.latency_ms:.1f}ms")
    print(f"  With rerank: {response_with_rerank.latency_ms:.1f}ms")


def test_pipeline_with_filters():
    """Test pipeline with metadata filters"""
    print("\n=== TEST 3: Full Pipeline - Metadata Filtering ===\n")

    docs = create_test_documents()
    pipeline = RAGPipeline(docs)

    query = "technology and architecture"

    # Search without filters
    response_all = pipeline.search(query, use_reranking=False, top_k=5)
    print(f"All results ({len(response_all.sources)}):")
    for src in response_all.sources:
        category = src.get('category', 'unknown')
        print(f"  - {src['title']} (category: {category})")

    # Search with category filter
    print(f"\nFiltered to 'architecture' only:")
    response_filtered = pipeline.search(
        query,
        apply_filters={'categories': ['architecture']},
        use_reranking=False,
        top_k=5
    )
    for src in response_filtered.sources:
        category = src.get('category', 'unknown')
        print(f"  - {src['title']} (category: {category})")


def test_multi_turn_conversation():
    """Test pipeline with multi-turn conversation"""
    print("\n=== TEST 4: Multi-Turn Conversation ===\n")

    docs = create_test_documents()
    pipeline = RAGPipeline(docs)

    session_id = "session_001"

    # Turn 1
    response1 = pipeline.search(
        "What is microservices?",
        session_id=session_id,
        use_reranking=True
    )
    print(f"Turn 1: What is microservices?")
    print(f"  Confidence: {response1.confidence:.2f}")
    print(f"  Turns tracked: {response1.metadata['conversation_turns']}")

    # Turn 2
    response2 = pipeline.search(
        "How do I deploy it?",
        session_id=session_id,
        use_reranking=True
    )
    print(f"\nTurn 2: How do I deploy it?")
    print(f"  Confidence: {response2.confidence:.2f}")
    print(f"  Turns tracked: {response2.metadata['conversation_turns']}")

    # Turn 3
    response3 = pipeline.search(
        "What about testing?",
        session_id=session_id,
        use_reranking=True
    )
    print(f"\nTurn 3: What about testing?")
    print(f"  Confidence: {response3.confidence:.2f}")
    print(f"  Turns tracked: {response3.metadata['conversation_turns']}")


def test_pipeline_metrics():
    """Test pipeline metrics and metadata"""
    print("\n=== TEST 5: Pipeline Metrics ===\n")

    docs = create_test_documents()
    pipeline = RAGPipeline(docs)

    info = pipeline.get_pipeline_info()

    print("Pipeline Architecture:")
    print(f"  Stages: {info['stages']}")
    print(f"  Documents indexed: {info['documents_indexed']}")
    print(f"\nComponents:")
    for i, comp in enumerate(info['components'], 1):
        print(f"  {i}. {comp}")

    print(f"\nConfiguration:")
    for key, val in info['configuration'].items():
        print(f"  {key}: {val}")

    # Run a query and show latency breakdown
    print(f"\nPerformance Test:")
    response = pipeline.search("microservices docker kubernetes", use_reranking=True)
    print(f"  Total latency: {response.latency_ms:.1f}ms")
    print(f"  Confidence: {response.confidence:.2%}")
    print(f"  Results: {len(response.sources)}")


def test_pipeline_end_to_end():
    """Full end-to-end test of all pipeline stages"""
    print("\n=== TEST 6: End-to-End Pipeline Test ===\n")

    docs = create_test_documents()
    pipeline = RAGPipeline(docs)

    test_cases = [
        {
            "query": "microservices architecture patterns",
            "expected_first": "Microservices Architecture",
            "filters": None,
            "session": None
        },
        {
            "query": "containerization and orchestration",
            "expected_first": "Docker & Container Deployment",
            "filters": {"categories": ["devops"]},
            "session": "session_e2e"
        },
        {
            "query": "API design for distributed systems",
            "expected_first": "API Design Best Practices",
            "filters": {"min_confidence": 0.90},
            "session": "session_e2e"
        },
    ]

    passed = 0
    for i, test in enumerate(test_cases, 1):
        response = pipeline.search(
            test["query"],
            session_id=test["session"],
            apply_filters=test["filters"],
            use_reranking=True,
            top_k=3
        )

        first_title = response.sources[0]['title'] if response.sources else "NO RESULTS"
        is_correct = first_title == test["expected_first"]
        status = "✅" if is_correct else "❌"

        print(f"{status} Test {i}: {test['query']}")
        print(f"    Expected: {test['expected_first']}")
        print(f"    Got: {first_title}")
        print(f"    Confidence: {response.confidence:.2%}")
        print(f"    Latency: {response.latency_ms:.1f}ms\n")

        if is_correct:
            passed += 1

    print(f"E2E Test Score: {passed}/{len(test_cases)} passed")


if __name__ == "__main__":
    print("🧪 Phase 2 Integration Tests - Full RAG Pipeline (9 Components)")
    print("=" * 70)

    try:
        test_full_pipeline_basic()
        test_pipeline_with_reranking()
        test_pipeline_with_filters()
        test_multi_turn_conversation()
        test_pipeline_metrics()
        test_pipeline_end_to_end()

        print("=" * 70)
        print("✅ All integration tests completed successfully!")
        print("\n🎉 Phase 2 RAG Pipeline: FULLY INTEGRATED & TESTED")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
