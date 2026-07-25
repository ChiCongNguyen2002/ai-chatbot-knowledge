---
title: AI Chatbot Demo Free
emoji: 🤖
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 8000
pinned: false
---

# 🤖 AI Chatbot - FREE Local LLM

Enterprise knowledge search chatbot running completely local with **zero cost**.

**Search powered by:** Hybrid BM25 + Semantic Embeddings (multilingual via bge-m3)

## ⚡ Quick Start (30 seconds)

```bash
cd /tmp/chatbot_demo
docker-compose up
```

Then open: **http://localhost:8000**

## 📋 What's Included

- **app_demo.py** — FastAPI chatbot server + Web UI
- **docker-compose.yml** — Orchestrates Ollama + Chatbot
- **requirements.txt** — Python dependencies

## 🌐 Access Points

| Interface | URL |
|-----------|-----|
| **Web UI** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **Ollama** | http://localhost:11434 |

## 💰 Cost

```
✅ $0.00/month
✅ No API keys needed
✅ Runs completely local
```

## 🧪 Test It

### Web UI (Easy)
```
1. Open http://localhost:8000
2. Ask: "What are microservices?"
3. Get AI answer + citations
```

### API (Quick)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What are microservices?","session_id":""}'
```

## 🛑 Stop

```bash
docker-compose down
```

## 📊 Performance & Models

### Local Development (`docker-compose up`)
- **LLM:** Mistral 7B (full model)
- **Embedding:** bge-m3 (multilingual)
- **Response time:** ~10 seconds
- **Cost per response:** $0.00

### Public Demo (Hugging Face Spaces)
- **LLM:** Phi 3 Mini (smaller, faster)
- **Embedding:** bge-m3 (multilingual)
- **Response time:** Variable (shared CPU)
- **Cost per response:** $0.00
- **Status:** Deployed at [HuggingFace Spaces](#) (Link coming after first push)

## 🔄 What Changed (Hybrid Search Update)

**Before:**  Simple substring keyword matching (poor quality)
**After:**   BM25 ranking + Semantic embeddings (multilingual)

Test it:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"How are duplicate alerts grouped together?","session_id":""}'
```
Should now correctly find the Notifications doc (semantic match, not keyword match).

---

## 🚀 Next Steps

### Local: Try Different Models
Edit `docker-compose.yml`, change `model-puller` command:
```yaml
command: sh -c "ollama pull llama2 && ollama pull bge-m3"
```
Then restart: `docker-compose up -d`

### Deploy: Hugging Face Spaces
1. Fork this repo to GitHub
2. Create Hugging Face Space (Docker SDK)
3. Connect to your GitHub repo
4. Automatic deploy on push to main branch

---

**Ready to chat?** Run: `docker-compose up`
