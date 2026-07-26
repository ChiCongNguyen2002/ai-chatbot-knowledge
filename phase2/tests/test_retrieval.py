"""
Phase 2 - Retrieval Tests
Test hybrid search engine with real Anfin documents
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval.hybrid_search import HybridSearchEngine
from models.embedder import EmbedderManager


def create_test_documents():
    """Create test documents matching Phase 1 schema"""
    return [
        {
            "id": "microservices-101",
            "title": "Microservices Architecture",
            "content": "Microservices is an architectural style that structures an application as a collection of "
                      "loosely coupled, independently deployable services. Each service runs in its own process "
                      "and communicates with others via APIs. Key benefits: scalability, independent deployment, "
                      "fault isolation, technology diversity.",
            "category": "architecture",
            "tags": ["microservices", "architecture", "design-pattern"]
        },
        {
            "id": "docker-deploy",
            "title": "Docker & Container Deployment",
            "content": "Docker is a containerization platform that packages applications and dependencies into "
                      "containers. Containers are lightweight, portable, and consistent across environments. "
                      "Benefits: environment consistency, easy scaling, faster deployment, reduced operational overhead.",
            "category": "devops",
            "tags": ["docker", "containers", "deployment", "devops"]
        },
        {
            "id": "api-design",
            "title": "API Design Best Practices",
            "content": "Well-designed APIs are crucial for service communication. Best practices include: versioning, "
                      "pagination, filtering, caching, error handling, documentation. Use RESTful principles: "
                      "proper HTTP methods, status codes, URI structure. Consider GraphQL for complex querying.",
            "category": "architecture",
            "tags": ["api", "rest", "design", "integration"]
        },
        {
            "id": "kafka-messaging",
            "title": "Kafka Event Streaming",
            "content": "Apache Kafka is a distributed event streaming platform for building real-time data pipelines. "
                      "Topics organize messages by category. Partitions enable parallel processing. Consumer groups "
                      "allow multiple subscribers. Features: durability, high-throughput, fault-tolerance.",
            "category": "data-pipeline",
            "tags": ["kafka", "streaming", "messaging", "event-driven"]
        }
    ]


def test_bm25_search():
    """Test BM25 keyword search"""
    print("\n=== TEST 1: BM25 Search ===")

    docs = create_test_documents()
    search_engine = HybridSearchEngine(docs, alpha=0.4)

    queries = [
        "microservices",
        "docker container",
        "API design REST",
        "kafka streaming"
    ]

    for query in queries:
        results = search_engine.bm25_search(query, top_k=2)
        print(f"\nQuery: '{query}'")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['title']} (score: {result['score']:.3f})")


def test_vector_search():
    """Test semantic vector search"""
    print("\n=== TEST 2: Vector Search (Semantic) ===")

    docs = create_test_documents()
    search_engine = HybridSearchEngine(docs, alpha=0.4)

    # Test semantic understanding: different wording, same meaning
    queries = [
        "splitting applications into independent services",  # semantic: microservices
        "containerized application deployment",               # semantic: docker
        "how to design good interfaces between services",     # semantic: api design
        "real-time event processing system"                   # semantic: kafka
    ]

    for query in queries:
        results = search_engine.vector_search(query, top_k=2)
        print(f"\nQuery: '{query}'")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['title']} (similarity: {result['score']:.3f})")


def test_hybrid_search():
    """Test hybrid search combining both methods"""
    print("\n=== TEST 3: Hybrid Search (BM25 + Vector) ===")

    docs = create_test_documents()
    search_engine = HybridSearchEngine(docs, alpha=0.4)

    # Mix of exact keywords and semantic queries
    test_cases = [
        ("microservices architecture", "doc_id: microservices-101"),
        ("containerization platform", "doc_id: docker-deploy"),
        ("how to design APIs", "doc_id: api-design"),
        ("event-driven architecture", "doc_id: kafka-messaging"),
        # Cross-lingual test would go here if using multilingual embeddings
    ]

    for query, expected in test_cases:
        results = search_engine.hybrid_search(query, top_k=2)
        print(f"\nQuery: '{query}' (expect: {expected})")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['title']} (hybrid_score: {result['score']:.3f})")


def test_ranking_quality():
    """Test if hybrid ranking produces good results"""
    print("\n=== TEST 4: Ranking Quality ===")

    docs = create_test_documents()
    search_engine = HybridSearchEngine(docs, alpha=0.4)

    test_cases = [
        {
            "query": "How to deploy with Docker",
            "expected_top": "Docker & Container Deployment",
            "should_not_be_top": "Microservices Architecture"
        },
        {
            "query": "What is microservices",
            "expected_top": "Microservices Architecture",
            "should_not_be_top": "Docker & Container Deployment"
        },
    ]

    passed = 0
    for test in test_cases:
        results = search_engine.hybrid_search(test["query"], top_k=3)
        top_result = results[0]["title"] if results else None

        is_correct = top_result == test["expected_top"]
        status = "✅ PASS" if is_correct else "❌ FAIL"

        print(f"\n{status}: '{test['query']}'")
        print(f"  Expected: {test['expected_top']}")
        print(f"  Got: {top_result}")

        if is_correct:
            passed += 1

    print(f"\n✅ Quality Score: {passed}/{len(test_cases)} correct rankings")


def test_alpha_tuning():
    """Test different alpha (weight) values"""
    print("\n=== TEST 5: Alpha Tuning (BM25 vs Vector Weight) ===")

    docs = create_test_documents()
    query = "microservices independent deployment"

    alphas = [0.0, 0.3, 0.5, 0.7, 1.0]

    print(f"\nQuery: '{query}'")
    print("Tuning BM25 weight (alpha):\n")

    for alpha in alphas:
        search_engine = HybridSearchEngine(docs, alpha=alpha)
        results = search_engine.hybrid_search(query, top_k=2)

        print(f"  alpha={alpha:.1f} (BM25={alpha:.1f}, Vector={1-alpha:.1f}):")
        for i, result in enumerate(results[:2], 1):
            print(f"    {i}. {result['title']} (score: {result['score']:.3f})")


if __name__ == "__main__":
    print("🧪 Phase 2 Retrieval Tests - Hybrid Search Engine")
    print("=" * 60)

    try:
        test_bm25_search()
        test_vector_search()
        test_hybrid_search()
        test_ranking_quality()
        test_alpha_tuning()

        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("\n📊 Summary:")
        print("  - BM25 search: keyword-based ranking")
        print("  - Vector search: semantic similarity")
        print("  - Hybrid: weighted combination (alpha tuning)")
        print("  - Ranking quality: validation of top results")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
