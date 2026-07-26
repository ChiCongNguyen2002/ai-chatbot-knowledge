"""Simple entrypoint - Ollama + FastAPI"""

import os
import time
import subprocess
import sys

print("🚀 Starting Anfin AI Chatbot (Phase 4 Lite)")

# Step 1: Ingest documents
print("\n1️⃣ Loading real Confluence data...")
try:
    from atlassian_ingester_full import create_full_confluence_data, save_docs_to_file
    docs = create_full_confluence_data()
    save_docs_to_file(docs)
    print(f"✅ Loaded {len(docs)} documents")
except Exception as e:
    print(f"⚠️ {e}")
    sys.exit(1)

# Step 2: Start Ollama (foreground in subprocess)
print("\n2️⃣ Starting Ollama...")
ollama_proc = subprocess.Popen(
    ["ollama", "serve"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT
)
time.sleep(3)

# Step 3: Wait for Ollama
print("⏳ Waiting for Ollama...")
import requests
max_retries = 60
for i in range(max_retries):
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        if resp.status_code == 200:
            print("✅ Ollama ready")
            break
    except:
        if i < max_retries - 1:
            time.sleep(1)
        else:
            print("❌ Ollama failed to start!")
            sys.exit(1)

# Step 4: Pull models
print("\n3️⃣ Pulling models (this takes 2-3 min)...")
print("   - bge-m3 (embeddings)...")
os.system("ollama pull bge-m3")
print("   - mistral:latest (synthesis)...")
os.system("ollama pull mistral:latest")
print("✅ Models ready")

# Step 5: Start FastAPI
print("\n4️⃣ Starting FastAPI on port 8000...")
os.execvp("python", ["python", "app_simple.py"])
