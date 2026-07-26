"""Simple entrypoint - Ollama + FastAPI with proper process management"""

import os
import time
import sys

print("🚀 Starting Anfin AI Chatbot (Phase 4 - Production)\n")

# Step 1: Setup directories
print("1️⃣ Setup...")
os.makedirs("/root/.ollama", exist_ok=True)
os.makedirs("/root/.ollama/models", exist_ok=True)

# Step 2: Ingest documents
print("2️⃣ Loading 43 Confluence documents...")
try:
    from atlassian_ingester_full import create_full_confluence_data, save_docs_to_file
    docs = create_full_confluence_data()
    save_docs_to_file(docs)
    print(f"   ✅ Loaded {len(docs)} documents\n")
except Exception as e:
    print(f"   ❌ {e}\n")
    sys.exit(1)

# Step 3: Start Ollama in background
print("3️⃣ Starting Ollama server...")
print("   (Note: This will run in background, FastAPI foreground)\n")
os.system("nohup ollama serve > /tmp/ollama.log 2>&1 &")
time.sleep(4)

# Step 4: Wait for Ollama with better error handling
print("4️⃣ Waiting for Ollama to be ready...")
import requests
max_retries = 120  # 2 minutes
for i in range(max_retries):
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        if resp.status_code == 200:
            print("   ✅ Ollama online\n")
            break
    except Exception as e:
        if i == max_retries - 1:
            print(f"   ❌ Ollama timeout after {max_retries}s")
            print("   Checking log...")
            os.system("tail -20 /tmp/ollama.log")
            sys.exit(1)
        elif i % 10 == 0:
            print(f"   ⏳ Still waiting... ({i}s)")
        time.sleep(1)

# Step 5: Pull models
print("5️⃣ Pulling AI models (2-5 min)...")
print("   📥 Pulling bge-m3 embedding model...")
ret1 = os.system("timeout 300 ollama pull bge-m3 > /tmp/bge.log 2>&1")
if ret1 == 0:
    print("      ✅ bge-m3 ready")
else:
    print("      ⚠️ bge-m3 timeout (continuing...)")

print("   📥 Pulling mistral:latest synthesis model...")
ret2 = os.system("timeout 600 ollama pull mistral:latest > /tmp/mistral.log 2>&1")
if ret2 == 0:
    print("      ✅ mistral ready\n")
else:
    print("      ⚠️ mistral timeout (continuing...)\n")

# Step 6: Verify models loaded
print("6️⃣ Verifying models...")
os.system("ollama list")

# Step 7: Start FastAPI (replaces this process)
print("\n7️⃣ Starting FastAPI server on port 8000...\n")
os.execvp("python", ["python", "app_simple.py"])
