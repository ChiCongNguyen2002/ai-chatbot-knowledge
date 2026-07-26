# PHASE 2 PLAN - Real Data + Elasticsearch (2 hours)

**After Phase 1 is deployed & tested on Railway**

---

## 🎯 Goal

Convert MVP (10 docs) → Production (300+ Jira issues)
- Ingest real data via Atlassian MCP
- Add Elasticsearch for better search
- Improve quality from 60% → 95%

---

## 📋 What I'll Do

### Step 1: Ingestion via Atlassian MCP (40 min)

**Create: `atlassian_ingester.py`**
```python
# Uses Claude's native Atlassian MCP
# Pulls from Jira (you authorize once)
# Extracts: issue title, description, comments
# Output: 300+ documents JSON

Features:
✅ Pull all Jira projects
✅ Extract full issue context
✅ Chunk by 500 tokens
✅ Preserve metadata (project, assignee, updated date)
✅ Handle large attachments
```

**Quality checks I'll do:**
- ✅ Document count 100-500
- ✅ No empty documents
- ✅ Metadata complete
- ✅ No duplicates
- ✅ Chunking size 100-1000 chars

**I'll ask you IF:**
- Ingestion fails (permission issue)
- Document count unexpected (< 50 or > 1000)
- Content looks wrong

---

### Step 2: Elasticsearch Setup (40 min)

**Create: `elasticsearch_config.py`**
```python
# Start Elasticsearch in Docker
# Create index with BM25 + field mapping
# Index all 300 docs

Features:
✅ Fast full-text search
✅ Advanced query support
✅ Scoring optimization
✅ 5 doc buffer (storage efficient)
```

**Docker compose update:**
```yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    mem_limit: 1G
```

**Quality checks I'll do:**
- ✅ ES starts successfully
- ✅ All 300 docs indexed
- ✅ Search returns results
- ✅ Query latency < 100ms

---

### Step 3: Upgrade Search to Hybrid (40 min)

**Update: `search.py`**
```python
# Old: BM25 only
# New: BM25 + semantic embedding (bge-m3)

def hybrid_search(question, top_k=10):
    # Stage 1: BM25 via Elasticsearch
    bm25_results = es.search(...)
    
    # Stage 2: Embeddings via Ollama bge-m3
    embedding = ollama.embed(question)
    
    # Stage 3: Combine scores
    combined = 0.3*bm25_score + 0.7*semantic_score
    
    return top_k ranked docs
```

**Quality checks I'll do:**
- ✅ Semantic embeddings working
- ✅ Hybrid ranking correct
- ✅ Top-10 docs relevant
- ✅ Search quality 95%+

**Test queries:**
```
"Jira workflow setup"        → Should return workflow docs
"How to create new project?" → Should return project management docs
"API authentication"         → Should return auth docs
```

---

### Step 4: Update Docker + Deploy (20 min)

**Update files:**
- `docker-compose.yml` - Add Elasticsearch service
- `Dockerfile` - Add Ollama + bge-m3 model pulling
- `requirements.txt` - Add elasticsearch, ollama packages
- `entrypoint.sh` - Start all services

**Update Railway:**
```bash
# Commit changes
git add .
git commit -m "Phase 2: Add Elasticsearch + real Jira data"

# Railway auto-rebuilds and deploys
railway up

# Same URL, new features
https://your-railway-url/ (now with 300 docs + better search)
```

---

## 📊 Quality Gates (Phase 2)

| Check | Target | Auto-verify |
|-------|--------|-------------|
| **Docs ingested** | 100-500 | ✅ Count check |
| **No empty docs** | 100% valid | ✅ Content check |
| **Search accuracy** | 95%+ | ✅ Test queries |
| **Response time** | < 3s avg | ✅ Perf check |
| **Elasticsearch** | Healthy | ✅ Health endpoint |
| **Ollama** | Embedding working | ✅ Test embed call |

---

## ⏱️ Timeline

```
Start: After Phase 1 deployed + tested
├─ 40 min: Ingest 300 Jira docs
├─ 40 min: Setup Elasticsearch
├─ 40 min: Upgrade search
└─ 20 min: Deploy to Railway
   TOTAL: ~2 hours

Deliverable: Public URL with 300 docs, 95% search quality
```

---

## 🎯 Expected Improvement

| Metric | Phase 1 | Phase 2 | Improvement |
|--------|---------|---------|-------------|
| Documents | 10 | 300 | 30x |
| Search accuracy | 60% | 95% | +35% |
| Search time | 1s | 3s | +2s (acceptable) |
| Quality | Basic | Good | ⭐⭐⭐⭐ |
| Cost | $0 | $5-10/mo | $5-10/mo |

---

## What You Need to Provide

When Phase 2 starts, you'll need:
1. ✅ Jira access (we'll use Atlassian MCP - no token needed)
2. ✅ Approval to pull all Jira data
3. ✅ Feedback on search results

---

## After Phase 2

- ✅ 300+ docs indexed in Elasticsearch
- ✅ Hybrid search (BM25 + semantic)
- ✅ Quality 95%
- ✅ Ready for Phase 3 (LLM synthesis)

Next: Phase 3 adds AI generation ← I synthesize answers from 10+ docs

---

**Phase 2 Status:** Ready to start after Phase 1 testing ✅
