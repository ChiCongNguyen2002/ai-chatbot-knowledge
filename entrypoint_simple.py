"""Simple entrypoint - Ollama + FastAPI, no Elasticsearch"""

import os
import time
import json

print("🚀 Starting Anfin AI Chatbot (Phase 4 Lite)")

# Step 1: Ingest documents
print("\n1️⃣ Loading real Confluence data...")
try:
    from atlassian_ingester_full import create_full_confluence_data, save_docs_to_file
    docs = create_full_confluence_data()
    save_docs_to_file(docs)
    print(f"✅ Loaded {len(docs)} documents")
except Exception as e:
    print(f"⚠️ Ingestion error: {e}")

# Step 2: Start Ollama
print("\n2️⃣ Starting Ollama...")
os.system("ollama serve &")
time.sleep(3)

# Step 3: Wait for Ollama
print("⏳ Waiting for Ollama...")
import requests
for i in range(30):
    try:
        requests.get("http://localhost:11434/api/tags", timeout=2)
        print("✅ Ollama ready")
        break
    except:
        if i < 29:
            time.sleep(2)

# Step 4: Pull models
print("\n3️⃣ Pulling models...")
print("   - bge-m3 (embeddings)")
os.system("ollama pull bge-m3 >/dev/null 2>&1")
print("   - mistral:latest (synthesis)")
os.system("ollama pull mistral:latest >/dev/null 2>&1")
print("✅ Models ready")

# Step 5: Start FastAPI
print("\n4️⃣ Starting FastAPI...")
os.system("python app_simple.py")
