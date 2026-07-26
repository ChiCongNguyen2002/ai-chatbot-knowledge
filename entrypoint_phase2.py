#!/usr/bin/env python3
"""Phase 3 Entrypoint - Setup and run full RAG chatbot"""

import os, time

ES_HOST = os.environ.get("ES_HOST", "http://localhost:9200")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

print("🚀 Phase 3: Full RAG with Qwen 7B + Elasticsearch")
print(f"📊 Elasticsearch: {ES_HOST}")
print(f"🧠 Ollama: {OLLAMA_HOST}")

print("\n1️⃣ Starting Ollama...")
os.system("ollama serve &")
time.sleep(3)

print("⏳ Waiting for Ollama...")
for i in range(30):
    try:
        import requests
        requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
        print("✅ Ollama ready")
        break
    except:
        if i < 29: time.sleep(2)

print("\n2️⃣ Pulling models...")
print("   - bge-m3 (embeddings)")
os.system("ollama pull bge-m3")
print("   - Qwen 7B (synthesis)")
os.system("ollama pull qwen:7b-int4")

print("\n3️⃣ Ingesting 40+ REAL Confluence pages...")
try:
    from atlassian_ingester_full import create_full_confluence_data, save_docs_to_file, verify_ingestion
    docs = create_full_confluence_data()
    save_docs_to_file(docs)
    verify_ingestion(docs)
    print("✅ Full Confluence data loaded")
except Exception as e:
    print(f"⚠️ {e}")

print("\n4️⃣ Setting up Elasticsearch...")
time.sleep(5)
try:
    from elasticsearch_init import create_elasticsearch_index, index_documents, verify_elasticsearch
    import json
    es = create_elasticsearch_index(ES_HOST)
    if es:
        with open("jira_docs.json") as f: docs = json.load(f)
        index_documents(es, docs)
        verify_elasticsearch(es)
        print("✅ Elasticsearch ready")
except Exception as e:
    print(f"⚠️ {e}")

print("\n5️⃣ Starting FastAPI with LLM synthesis...")
os.system("python app_phase2.py")
