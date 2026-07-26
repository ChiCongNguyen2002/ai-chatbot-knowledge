#!/bin/bash
set -e

# Start Ollama server in background
ollama serve &

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama server..."
until curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; do
  sleep 1
done

echo "✅ Ollama server ready"

# Pull models if not already present (first run only)
echo "📥 Pulling models (first run only)..."
ollama pull phi3:mini

echo "✅ Models ready (using BM25 search - no embeddings)"

# Start FastAPI app as foreground process (PID 1)
exec python app_demo.py
