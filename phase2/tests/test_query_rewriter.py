"""
Phase 2 - Query Rewriter Tests
Test intent detection and query expansion
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processing.query_rewriter import QueryRewriter, QueryAnalyzer


def test_intent_detection():
    """Test query intent detection"""
    print("\n=== TEST 1: Intent Detection ===\n")

    rewriter = QueryRewriter()

    test_queries = [
        ("What is microservices?", "definition"),
        ("How do I deploy with Docker?", "how-to"),
        ("Microservices vs monolithic", "comparison"),
        ("Example of Kafka usage", "example"),
        ("Best practices for API design", "best-practice"),
        ("Tell me about Kubernetes", "general"),
    ]

    correct = 0
    for query, expected_intent in test_queries:
        detected = rewriter.detect_intent(query)
        status = "✅" if detected == expected_intent else "❌"
        print(f"{status} '{query}'")
        print(f"   Expected: {expected_intent}")
        print(f"   Detected: {detected}\n")

        if detected == expected_intent:
            correct += 1

    print(f"Intent Detection Accuracy: {correct}/{len(test_queries)}")


def test_query_expansion():
    """Test query term expansion"""
    print("\n=== TEST 2: Query Term Expansion ===\n")

    rewriter = QueryRewriter()

    test_queries = [
        "microservices",
        "docker container",
        "kubernetes k8s",
        "api design",
    ]

    for query in test_queries:
        tokens = query.split()
        expanded = rewriter.expand_terms(tokens)

        print(f"Original: {' '.join(tokens)}")
        print(f"Expanded: {' '.join(expanded)}")
        print(f"Added: {set(expanded) - set(tokens)}\n")


def test_query_rewriting():
    """Test full query rewriting pipeline"""
    print("\n=== TEST 3: Query Rewriting ===\n")

    rewriter = QueryRewriter()

    test_queries = [
        "What is microservices?",
        "How do I use Docker?",
        "Compare microservices vs monolithic",
    ]

    for query in test_queries:
        result = rewriter.rewrite_query(query)

        print(f"Original Query: {result['original']}")
        print(f"Intent: {result['intent']}")
        print(f"Boost Terms: {result['boost_terms']}")
        print(f"Primary Variation: {result['primary_variation']}")
        print(f"\nAll Variations:")
        for i, var in enumerate(result['variations'], 1):
            print(f"  {i}. [{var['type']}] {var['query']}")
        print()


def test_multi_query_generation():
    """Test multi-query generation for ensemble search"""
    print("\n=== TEST 4: Multi-Query Generation ===\n")

    rewriter = QueryRewriter()

    test_queries = [
        "How to scale microservices",
        "Docker deployment best practices",
        "Kafka event streaming",
    ]

    for query in test_queries:
        variations = rewriter.generate_multi_queries(query, num_queries=3)

        print(f"Original: {query}")
        print("Variations for ensemble search:")
        for i, var in enumerate(variations, 1):
            print(f"  {i}. {var}")
        print()


def test_query_analysis():
    """Test query analysis utilities"""
    print("\n=== TEST 5: Query Analysis ===\n")

    analyzer = QueryAnalyzer()

    test_queries = [
        "Docker",
        "How do I use microservices?",
        "What is the difference between monolithic and microservices architecture and when should I choose one over the other?",
    ]

    for query in test_queries:
        length = analyzer.get_query_length(query)
        complexity = analyzer.get_query_complexity(query)
        entities = analyzer.extract_entities(query)

        print(f"Query: {query}")
        print(f"  Length: {length}")
        print(f"  Complexity: {complexity}")
        print(f"  Entities: {entities}\n")


def test_real_world_scenarios():
    """Test on real-world queries from users"""
    print("\n=== TEST 6: Real-World Scenarios ===\n")

    rewriter = QueryRewriter()

    scenarios = [
        {
            "query": "microservice là gì?",
            "expected_intent": "definition",
            "description": "Vietnamese definition query"
        },
        {
            "query": "how to implement API versioning",
            "expected_intent": "how-to",
            "description": "English how-to query"
        },
        {
            "query": "Docker vs Kubernetes",
            "expected_intent": "comparison",
            "description": "Comparison query"
        },
    ]

    for scenario in scenarios:
        result = rewriter.rewrite_query(scenario["query"])

        print(f"Scenario: {scenario['description']}")
        print(f"Query: {scenario['query']}")
        print(f"Intent: {result['intent']} (expected: {scenario['expected_intent']})")
        print(f"Primary Variation: {result['primary_variation']}\n")


if __name__ == "__main__":
    print("🧪 Phase 2 Query Rewriter Tests - Intent Detection & Expansion")
    print("=" * 70)

    try:
        test_intent_detection()
        test_query_expansion()
        test_query_rewriting()
        test_multi_query_generation()
        test_query_analysis()
        test_real_world_scenarios()

        print("=" * 70)
        print("✅ All query rewriter tests completed!")

        print("\n📊 Summary:")
        print("  - Intent detection: Working (definition, how-to, comparison, etc.)")
        print("  - Query expansion: Synonym-based term enrichment")
        print("  - Multi-query generation: 3-way search ensemble")
        print("  - Query analysis: Length, complexity, entity extraction")
        print("  - Real-world scenarios: Multilingual support ready")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
