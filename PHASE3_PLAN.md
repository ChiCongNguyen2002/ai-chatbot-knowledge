# PHASE 3 PLAN - LLM Synthesis (1.5 hours)

**After Phase 2 is deployed & search quality verified**

---

## 🎯 Goal

Add AI answer generation
- Use Qwen 7B (local LLM, free)
- Synthesize from 10-20 relevant docs
- Quality 90%

---

## 📋 What I'll Do

### Step 1: Download & Test Qwen 7B Model (45 min)

**Create: `qwen_setup.py`**
```python
# Download Qwen 7B int4 (~4GB)
# Via Ollama (already in Docker)
# Test model responsiveness

ollama pull qwen:7b-int4
```

**Quality checks I'll do:**
- ✅ Model downloads successfully
- ✅ Model loads in < 30s
- ✅ Test generation (basic prompt)
- ✅ Response time < 15s

**Test prompt:**
```
"List 3 benefits of microservices in 50 words"
→ Expected: Coherent, under 15s
```

---

### Step 2: Build Synthesis Logic (30 min)

**Create: `synthesis.py`**
```python
def synthesize_answer(question, top_docs):
    """
    Smart synthesis:
    - If top-1 score > 0.9 → return doc as-is (no LLM cost)
    - If score < 0.9 → use LLM to synthesize from 10-20 docs
    """
    
    if top_docs[0]["score"] > 0.9:
        # Perfect match, just return doc
        return {
            "answer": top_docs[0]["content"],
            "type": "direct",
            "source_count": 1
        }
    else:
        # Need synthesis
        prompt = f"""Based on these Jira documents:

{format_docs(top_docs[:10])}

Answer this question:
{question}

Response: professional, actionable, under 300 words"""
        
        response = ollama.generate(
            model="qwen:7b-int4",
            prompt=prompt
        )
        
        return {
            "answer": response,
            "type": "synthesized",
            "source_count": 10
        }
```

**Logic:**
- Smart cost optimization (skip LLM when not needed)
- Use top 10-20 docs for context
- Limit response length
- Professional tone

**Quality checks I'll do:**
- ✅ Direct answers when score > 0.9
- ✅ Synthesis when needed
- ✅ No hallucination (references documents)
- ✅ Response time < 15s

---

### Step 3: Integrate with API (30 min)

**Update: `app.py`**
```python
@app.post("/chat")
async def chat(request: ChatRequest):
    # Step 1: Search
    docs = hybrid_search(request.question, top_k=10)
    
    # Step 2: Smart synthesis (NEW)
    answer_data = synthesize_answer(request.question, docs)
    
    # Step 3: Return
    return {
        "answer": answer_data["answer"],
        "sources": docs[:3],
        "synthesis_type": answer_data["type"],
        "source_count": answer_data["source_count"]
    }
```

**UI Update:**
```javascript
// Show if answer is direct or synthesized
if (data.synthesis_type === "direct") {
    badge.text = "📄 Direct from docs"
} else {
    badge.text = "🤖 AI synthesized from " + data.source_count + " docs"
}
```

---

### Step 4: Deploy to Railway (15 min)

```bash
# Commit changes
git add .
git commit -m "Phase 3: Add Qwen 7B LLM synthesis"

# Railway rebuilds + deploys
railway up

# Same URL, now with AI answers
https://your-railway-url/
```

**Railway will:**
1. ✅ Build new image (includes Qwen model)
2. ✅ Pull Qwen model (~4GB, cached after first run)
3. ✅ Start Qwen server in background
4. ✅ Start FastAPI
5. ✅ Keep same URL (no downtime)

---

## 📊 Quality Gates (Phase 3)

| Check | Target | Auto-verify |
|-------|--------|-------------|
| **Qwen loaded** | < 30s | ✅ Startup check |
| **Generation works** | All prompts succeed | ✅ Test calls |
| **Response time** | < 15s | ✅ Performance check |
| **No hallucination** | References sources | ✅ Content check |
| **Smart synthesis** | Direct when score > 0.9 | ✅ Logic check |
| **Answer quality** | 90%+ | ✅ Test cases |

---

## 🧪 Test Cases (Phase 3)

```
Test 1: "Jira workflow best practices?"
├─ Search: finds workflow docs (score 0.95)
├─ Synthesis: SKIP (score > 0.9)
├─ Answer: Direct from doc
└─ Speed: 2s ✅

Test 2: "How to integrate Jira with external tools?"
├─ Search: finds 5+ relevant docs (avg score 0.75)
├─ Synthesis: YES (score < 0.9)
├─ Answer: Synthesized from 10 docs
└─ Speed: 12s ✅

Test 3: "Best practices for issue tracking?"
├─ Search: multiple relevant docs
├─ Synthesis: YES (combine multiple)
├─ Answer: Professional summary
└─ Speed: 12s ✅
```

---

## ⏱️ Timeline

```
Start: After Phase 2 search quality verified (95%+)
├─ 45 min: Download & test Qwen model
├─ 30 min: Build synthesis logic
├─ 30 min: Integrate with API
└─ 15 min: Deploy to Railway
   TOTAL: ~1.5 hours

Deliverable: Public URL with AI-synthesized answers
```

---

## 💰 Cost Impact

| Component | Cost |
|-----------|------|
| Elasticsearch | $5-10/mo |
| Qwen 7B (local) | $0 |
| Railway container | $3-5/mo |
| **Total** | **$8-15/mo** |

Still within Railway free tier $5 credit + minimal overage.

---

## 📊 Expected Quality

| Metric | Phase 2 | Phase 3 | Change |
|--------|---------|---------|--------|
| Direct answers | 40% | 40% | Same |
| Synthesized | N/A | 60% | +60% |
| Quality (direct) | 95% | 95% | Same |
| Quality (synthesis) | N/A | 90% | +90% |
| Overall | 95% | 94% | -1% (acceptable) |
| User satisfaction | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | +1 star |

---

## What Happens at Deployment

**Before Phase 3:**
```
User: "Best practices for project management?"
Search: Found 8 docs
Answer: First doc excerpt (600 chars)
Time: 2s
Feel: "OK but incomplete"
```

**After Phase 3:**
```
User: "Best practices for project management?"
Search: Found 8 docs
Synthesis: AI reads all 8 docs → writes unified answer
Answer: "Best practices include:
  1. Clear project scope...
  2. Regular status updates...
  3. Stakeholder communication...
  [synthesized from 8 docs]"
Time: 12s
Feel: "Wow, exactly what I needed!"
```

---

## After Phase 3

- ✅ 300+ docs indexed
- ✅ Hybrid search 95%
- ✅ AI synthesis 90% quality
- ✅ Smart optimization (skip LLM when not needed)
- ✅ Professional answers from 10+ docs

Next: Phase 4 (Final verification + optimization)

---

**Phase 3 Status:** Ready after Phase 2 ✅
