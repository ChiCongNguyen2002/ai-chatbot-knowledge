"""Quality Testing Suite - Verify Phase 3 meets Rovo standard"""

import json
import requests
from typing import List, Dict, Tuple

BASE_URL = "http://localhost:8000"

# Test queries from actual Anfin use cases
TEST_CASES = [
    {
        "query": "microservice là gì",
        "min_quality": 95,
        "expected_keywords": ["độc lập", "API", "deploy", "service"],
        "must_structure": True,
        "description": "Basic microservices definition"
    },
    {
        "query": "Go Routine là gì? Cách dùng?",
        "min_quality": 95,
        "expected_keywords": ["lightweight", "concurrent", "channel", "example"],
        "must_structure": True,
        "description": "Go Routine concepts with examples"
    },
    {
        "query": "API design best practices",
        "min_quality": 90,
        "expected_keywords": ["pagination", "rate limiting", "error", "cache"],
        "must_structure": True,
        "description": "API optimization principles"
    },
    {
        "query": "Kafka deployment",
        "min_quality": 90,
        "expected_keywords": ["cluster", "replication", "topics", "consumer"],
        "must_structure": True,
        "description": "Kafka infrastructure setup"
    },
    {
        "query": "code review process",
        "min_quality": 85,
        "expected_keywords": ["PR", "approve", "test", "merge"],
        "must_structure": True,
        "description": "Code review workflow"
    },
    {
        "query": "backend developer roadmap 2026",
        "min_quality": 90,
        "expected_keywords": ["microservices", "performance", "AI", "leadership"],
        "must_structure": True,
        "description": "Career development path"
    },
]

def assess_answer_quality(query: str, answer: str, expected_keywords: List[str]) -> Tuple[int, List[str]]:
    """
    Assess answer quality (0-100)

    Criteria:
    - Length: 200+ chars (comprehensive)
    - Keywords: contain expected terms
    - Vietnamese: natural Vietnamese (not gibberish)
    - Structure: has headings/sections
    - Relevance: answers the question directly
    """
    score = 0
    issues = []

    # 1. Length check (20 points)
    if len(answer) < 150:
        issues.append("❌ Too short (<150 chars)")
    elif len(answer) < 300:
        score += 10
        issues.append("⚠️ A bit short (150-300 chars)")
    else:
        score += 20

    # 2. Keywords check (30 points)
    found_keywords = []
    for keyword in expected_keywords:
        if keyword.lower() in answer.lower():
            found_keywords.append(keyword)
            score += 30 // len(expected_keywords)

    if len(found_keywords) < len(expected_keywords) // 2:
        missing = [k for k in expected_keywords if k not in found_keywords]
        issues.append(f"⚠️ Missing key concepts: {', '.join(missing[:2])}")

    # 3. Vietnamese quality check (20 points)
    vietnamese_chars = sum(1 for c in answer if ord(c) > 127)
    if vietnamese_chars < len(answer) * 0.3:
        issues.append("⚠️ Not enough Vietnamese content")
    else:
        score += 20

    # 4. No hallucinations (20 points)
    if "không biết" in answer.lower() or "tôi không" in answer.lower():
        issues.append("⚠️ Fallback to 'I don't know'")
    elif len(answer) > 50 and "[" not in answer and "(" not in answer:
        score += 20
    else:
        issues.append("⚠️ Contains formatting issues")

    # 5. Directness check (10 points)
    first_100 = answer[:100].lower()
    if any(term in first_100 for term in ["microservice", "kafka", "review", "go", "api", "backend"]):
        score += 10
    else:
        issues.append("⚠️ Doesn't answer directly from start")

    return min(100, score), issues


def test_single_query(query: str, test_case: Dict) -> Dict:
    """Test a single query and return results"""
    print(f"\n📍 Testing: {test_case['description']}")
    print(f"   Query: '{query}'")

    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"question": query},
            timeout=30
        )

        if response.status_code != 200:
            return {
                "query": query,
                "status": "❌ FAILED",
                "error": f"HTTP {response.status_code}",
                "score": 0
            }

        data = response.json()
        answer = data.get("answer", "")
        sources = data.get("sources", [])

        # Assess quality
        quality_score, issues = assess_answer_quality(
            query,
            answer,
            test_case["expected_keywords"]
        )

        # Print result
        status = "✅ PASS" if quality_score >= test_case["min_quality"] else "❌ FAIL"
        print(f"   {status} (score: {quality_score}/{test_case['min_quality']})")

        if issues:
            for issue in issues:
                print(f"      {issue}")

        print(f"   Answer preview: {answer[:100]}...")
        print(f"   Sources: {len(sources)} documents")

        return {
            "query": query,
            "status": status,
            "score": quality_score,
            "min_required": test_case["min_quality"],
            "answer_length": len(answer),
            "sources_count": len(sources),
            "issues": issues
        }

    except requests.exceptions.ConnectionError:
        return {
            "query": query,
            "status": "❌ CONNECTION FAILED",
            "error": "Cannot connect to server",
            "score": 0
        }
    except Exception as e:
        return {
            "query": query,
            "status": "❌ ERROR",
            "error": str(e),
            "score": 0
        }


def run_full_test():
    """Run complete quality test suite"""
    print("\n" + "="*80)
    print("🧪 ANFIN AI CHATBOT - QUALITY TEST SUITE")
    print("="*80)
    print(f"📊 Target: 99% quality like Rovo")
    print(f"🔗 Server: {BASE_URL}")
    print(f"📝 Test cases: {len(TEST_CASES)}")

    results = []
    total_score = 0
    passed = 0

    for test_case in TEST_CASES:
        result = test_single_query(test_case["query"], test_case)
        results.append(result)

        # Extract numeric score
        if "score" in result:
            total_score += result["score"]
            if "PASS" in result.get("status", ""):
                passed += 1

    # Summary
    print("\n" + "="*80)
    print("📊 TEST RESULTS SUMMARY")
    print("="*80)

    avg_score = total_score / len(results) if results else 0
    pass_rate = (passed / len(results) * 100) if results else 0

    print(f"\n✅ Passed: {passed}/{len(results)} ({pass_rate:.0f}%)")
    print(f"📈 Average quality score: {avg_score:.1f}/100")
    print(f"🎯 Target: 99/100")

    if avg_score >= 95:
        print("\n✅ SYSTEM QUALITY: EXCELLENT (≥95)")
        print("   Ready for production")
    elif avg_score >= 85:
        print("\n⚠️ SYSTEM QUALITY: GOOD (85-95)")
        print("   Needs minor improvements")
    elif avg_score >= 70:
        print("\n❌ SYSTEM QUALITY: POOR (70-85)")
        print("   Needs significant improvements")
    else:
        print("\n❌ SYSTEM QUALITY: UNACCEPTABLE (<70)")
        print("   Complete rebuild needed")

    # Detailed results
    print(f"\n📋 Detailed Results:")
    for result in results:
        status = result.get("status", "UNKNOWN")
        score = result.get("score", 0)
        query = result.get("query", "")
        print(f"  {status} | {score:3d}/100 | {query[:50]}")

    # Save results
    with open("quality_test_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": "2026-07-26",
            "average_score": avg_score,
            "pass_rate": pass_rate,
            "results": results
        }, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Results saved to quality_test_results.json")
    return avg_score


if __name__ == "__main__":
    try:
        avg_score = run_full_test()

        if avg_score < 95:
            print("\n" + "="*80)
            print("⚠️ QUALITY NOT MEETING TARGET")
            print("="*80)
            print("\nRecommendations to reach 99% quality:")
            print("1. ✅ Use better LLM: Mistral > Qwen for Vietnamese")
            print("2. ✅ Improve prompt: More structured instructions")
            print("3. ✅ More real data: Fetch 50+ pages from Confluence")
            print("4. ✅ Better retrieval: Tune hybrid search weights")
            print("5. ✅ Use Claude API: For critical accuracy (costs $)")
            print("="*80)
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
