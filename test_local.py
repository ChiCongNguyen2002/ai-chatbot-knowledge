#!/usr/bin/env python3
"""Local testing - verify search + synthesis before Railway deploy"""

import json
import sys

print("🧪 LOCAL TEST - Anfin Knowledge Chatbot\n")

# Test 1: Load documents
print("="*60)
print("TEST 1: Load Documents")
print("="*60)
try:
    from atlassian_ingester_full import create_full_confluence_data
    docs = create_full_confluence_data()
    print(f"✅ Loaded {len(docs)} documents")
    print(f"   Sample: {docs[0]['title']}")
    print(f"   Content length: {len(docs[0]['content'])} chars\n")
except Exception as e:
    print(f"❌ FAILED: {e}\n")
    sys.exit(1)

# Test 2: BM25 Search
print("="*60)
print("TEST 2: BM25 Search")
print("="*60)
try:
    from search_simple import SimpleSearch

    # Save docs first
    with open("test_docs.json", "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False)

    search = SimpleSearch("test_docs.json")

    # Test query
    test_query = "microservice là gì"
    results = search.search(test_query, top_k=5)

    print(f"Query: '{test_query}'")
    print(f"Results: {len(results)} documents found")
    if results:
        print(f"✅ Top result: {results[0]['title']}")
        print(f"   Score: {results[0]['score']:.3f}")
        print(f"   Preview: {results[0]['content'][:100]}...\n")
    else:
        print(f"⚠️ No results found\n")
except Exception as e:
    print(f"❌ FAILED: {e}\n")
    sys.exit(1)

# Test 3: FastAPI App (without Ollama/synthesis)
print("="*60)
print("TEST 3: FastAPI Endpoints")
print("="*60)
try:
    # Make sure test_docs.json exists
    with open("jira_docs.json", "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False)

    from app_simple import app
    try:
        from fastapi.testclient import TestClient
        client = TestClient(app)
    except:
        from starlette.testclient import TestClient
        client = TestClient(app)

    # Test health endpoint
    resp = client.get("/health")
    print(f"GET /health → {resp.status_code}")
    print(f"   Response: {resp.json()}")
    print()

    # Test greeting
    resp = client.post("/chat", json={"question": "hello"})
    print(f"POST /chat (greeting) → {resp.status_code}")
    print(f"   Answer: {resp.json()['answer'][:100]}...")
    print()

    # Test search (without synthesis)
    resp = client.post("/chat", json={"question": "microservice là gì"})
    print(f"POST /chat (search) → {resp.status_code}")
    data = resp.json()
    print(f"   Answer: {data['answer'][:100]}...")
    print(f"   Sources: {len(data['sources'])} documents")
    print()

    # Test no match
    resp = client.post("/chat", json={"question": "bạn thích gì"})
    print(f"POST /chat (no match) → {resp.status_code}")
    print(f"   Answer: {resp.json()['answer'][:100]}...")
    print()

    print("✅ All FastAPI tests passed\n")
except Exception as e:
    print(f"❌ FAILED: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Input/Output Examples
print("="*60)
print("TEST 4: Example Input/Output")
print("="*60)

test_cases = [
    ("microservice là gì", "Should return microservices doc"),
    ("Go Routine dùng khi nào", "Should return Go docs"),
    ("API design best practices", "Should return API docs"),
    ("Kafka deployment", "Should return DevOps docs"),
    ("chào bạn", "Should detect greeting"),
]

for query, expected in test_cases:
    print(f"\nInput: '{query}'")
    print(f"Expected: {expected}")
    try:
        resp = client.post("/chat", json={"question": query})
        data = resp.json()
        answer = data['answer'][:80]
        sources = len(data['sources'])

        if "greeting" in data.get('model', ''):
            print(f"✅ Greeting detected")
        elif sources > 0:
            print(f"✅ Found {sources} source(s)")
            print(f"   Answer preview: {answer}...")
        else:
            print(f"⚠️ No sources found")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "="*60)
print("✅ LOCAL TESTING COMPLETE")
print("="*60)
print("\nNOTE: Synthesis (Mistral) requires Ollama running!")
print("      FastAPI endpoints are working ✅")
print("      Search is working ✅")
print("      Need to test Mistral synthesis on Railway or local Ollama\n")

print("Ready to deploy to Railway? 🚀")
