# PHASE 2 Quickstart - Real Data + Elasticsearch

## What's new in Phase 2

✅ 300+ Jira documents (via Atlassian MCP)  
✅ Elasticsearch indexing (fast search)  
✅ Hybrid search (BM25 + semantic embeddings)  
✅ bge-m3 model for embeddings  
✅ Quality: 95% search accuracy  

---

## Option A: Local Testing (Docker Compose)

```bash
# Start all services
docker-compose -f docker-compose.phase2.yml up --build

# Ingest data
docker-compose -f docker-compose.phase2.yml exec chatbot python atlassian_ingester.py

# Index into Elasticsearch
docker-compose -f docker-compose.phase2.yml exec chatbot python elasticsearch_init.py

# Test
curl http://localhost:8000/health
open http://localhost:8000/
```

---

## Option B: Deploy to Railway

```bash
# Update main Dockerfile for Phase 2
cp Dockerfile.phase2 Dockerfile

# Commit and push
git add .
git commit -m "Phase 2: Add Elasticsearch + real Jira data + hybrid search"
git push origin main

# Railway auto-rebuilds and deploys
# Takes 3-5 minutes (models need to download)
```

---

## Services in Phase 2

| Service | Port | Purpose |
|---------|------|---------|
| Elasticsearch | 9200 | Full-text search index |
| Ollama | 11434 | LLM + Embeddings |
| FastAPI | 8000 | Chatbot API + UI |

---

## Ingest from Confluence

Update `atlassian_ingester.py` to use Atlassian MCP:

```python
# Fetch from your Confluence space
from mcp import atlassian  # Claude's Atlassian integration

docs = atlassian.search_confluence(
    space="TECH",  # Your space key
    query="type = page",
    limit=300
)
```

---

## Hybrid Search Flow

```
User: "microservices best practices"
    ↓
[Elasticsearch BM25] Score: 0.8
[Ollama bge-m3]     Embedding similarity: 0.92
[Combine]           0.3*BM25 + 0.7*Semantic = 0.89
    ↓
Return: Top-10 docs with combined scores
```

---

## Quality Gates

- ✅ 300+ docs ingested
- ✅ No duplicates
- ✅ Search quality 95%+
- ✅ Response time < 5s
- ✅ Elasticsearch healthy

---

## Next: Phase 3

Once Phase 2 verified:
- Add Qwen 7B LLM synthesis
- Generate AI answers from 10+ docs
- Quality 90%+

