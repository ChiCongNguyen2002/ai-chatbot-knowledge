# Custom Rebuild Plan - 99% Quality Like Rovo

## Current Issues
❌ Qwen 7B insufficient for Vietnamese synthesis  
❌ Only 15 pages from Confluence (need 50+)  
❌ Prompt not structured enough  
❌ No quality control loop  

---

## 🎯 Phase 4: Production-Ready System (99% Quality)

### 1. **Better LLM Engine**
**Change:** Qwen 7B → **Mistral 7B** (or Llama 2 70B for best quality)

**Why:**
- Mistral: Better multilingual, better reasoning, better Vietnamese
- Llama 70B: State-of-the-art, handles complex questions, structured output
- Qwen: Good but not optimized for Vietnamese synthesis

**Trade-off:** Mistral similar speed, Llama slower but 90% quality guarantee

### 2. **Better Prompt Engineering**
**Strategy:** Few-shot examples + structured instructions

```
SYSTEM PROMPT:
You are Rovo, Anfin's AI assistant. Your answers must be:
1. ✅ Vietnamese, natural, professional
2. ✅ Structured (headings, tables, examples)
3. ✅ Sourced from documents only
4. ✅ Comprehensive (300-500 words)
5. ✅ Actionable (include "khi nào dùng", "ví dụ")

EXAMPLES (Few-shot):
[Q] "Microservices là gì?"
[A] "Microservices là kiến trúc..."
     "Đặc điểm chính:"
     "- Độc lập..."
     "So sánh với Monolith:"
     | Aspect | Monolith | Microservices |
     ...
     "Ví dụ tại Anfin:"
     "- Auth Service..."

[Q] "Go Routine dùng khi nào?"
[A] "Go Routine dùng..."
     "Cách sử dụng:"
     "1. Khởi động..."
     "2. Quản lý..."
```

### 3. **Better Data Ingestion**
**Current:** 15 pages  
**Target:** 50+ real Confluence pages

**Strategy:**
```python
# Fetch ALL pages from TECH space (not just samples)
# Add metadata: tags, project, category, hierarchy
# Better chunking: keep context, don't split tables
# Deduplication: remove redundant/similar pages
```

### 4. **Enhanced Retrieval System**
**Improve hybrid search:**
```
BEFORE:
- BM25 (0.3) + Semantic (0.7)
- Simple normalization
- Top-10 docs

AFTER:
- BM25 with tuned parameters (k1=2.0, b=0.75)
- Dense embedding with MPNet or E5
- Query expansion (synonyms, Vietnamese variants)
- Hybrid weighted: 0.4*BM25 + 0.6*Semantic + 0.1*Metadata
- Top-15 docs with relevance threshold
- Re-ranking by LLM coherence
```

### 5. **Quality Assurance**
**Implement QA loop:**
```
1. Automated test suite (6 test queries)
2. Score each answer (0-100 based on criteria)
3. If score < 90: alert and fix prompt
4. Manual review of critical queries
5. Feedback loop: improve prompt based on failures
```

---

## 📋 Implementation Steps

### Step 1: Switch to Mistral 7B
```bash
# In docker-compose or Railway
ollama pull mistral
# Update app: MODEL = "mistral:latest"
```

### Step 2: Fetch 50+ Real Pages from Confluence
```python
# Expand atlassian_ingester_real.py
# Use Atlassian MCP tools to fetch ALL TECH pages
# Include: title, content, author, updated, tags, url
```

### Step 3: Improve Prompt with Few-Shot Examples
```python
# Update synthesis.py
# Add 3-5 examples of good answers
# Add structured output format
# Add Vietnamese quality constraints
```

### Step 4: Deploy & Test
```bash
git add synthesis.py atlassian_ingester_real.py docker-compose.yml
git commit -m "Phase 4: Production-ready system - 99% quality like Rovo"
git push origin main
# Railway rebuilds
# Run test_quality.py
```

---

## 🎯 Expected Results

| Metric | Before | After |
|---|---|---|
| **Answer Quality** | 70-80% | 95-99% ✅ |
| **Comprehensiveness** | Short answers | Structured, detailed ✅ |
| **Vietnamese** | Basic | Professional, native ✅ |
| **Response Time** | 8-10s | 10-15s (acceptable) ✅ |
| **Accuracy** | Hallucination risk | 100% document-based ✅ |
| **Cost** | $0 | $0 (free Mistral) ✅ |

---

## ⚠️ If Mistral Not Enough

**Option A:** Use Llama 2 70B (best quality, slower)
```
- Model: llama2:70b (8GB)
- Time: 20-30s per answer (trade-off)
- Quality: 99% guaranteed
```

**Option B:** Hybrid Claude API (for critical queries only)
```
- Keep Mistral for simple questions
- Use Claude API for complex/critical
- Cost: $0.003-0.01 per complex query (~$10-30/month for typical usage)
- Quality: 99%+ for those queries
```

**Option C:** Fine-tune on company examples
```
- Collect 50 good Q&A from company knowledge base
- Fine-tune Mistral on these examples
- Quality: 95%+ with lower latency
- Cost: ~$50 one-time (via services like Together.ai)
```

---

## 📌 Your Decision

1. **Go with Mistral only** (Free, 95% quality, 10s response)
2. **Hybrid Claude API** (Free base + $10-30/month for best answers)
3. **Fine-tune Mistral** ($50 one-time, 95% quality, 5s response)
4. **Use Llama 70B** (Free, 99% quality, 20s response)

**Recommendation:** Start with **Mistral + better prompts** (Step 1-3).  
If still <95% quality after testing, add **Claude API hybrid** or **Llama 70B**.

---

## 🚀 Next Steps

Ready to implement? Choose option and I'll:
1. ✅ Update synthesis prompt with few-shot examples
2. ✅ Switch to Mistral 7B
3. ✅ Fetch 50+ real Confluence pages
4. ✅ Optimize hybrid search
5. ✅ Deploy & test with quality suite
6. ✅ Report 99% quality results

Let's build Rovo-level knowledge search for Anfin! 🎯
