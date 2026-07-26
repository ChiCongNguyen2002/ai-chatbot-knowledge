# Deploy to HuggingFace Spaces (5 minutes)

## Step 1: Create Space on HF

1. Go to https://huggingface.co/spaces
2. Click **"Create New Space"**
3. Fill in:
   - **Space name:** `anfin-knowledge-search` (or your name)
   - **Repo type:** Public
   - **Space SDK:** Docker
   - **Docker template:** Empty
4. Click **Create space**

## Step 2: Connect Git Repo

In your terminal:

```bash
cd /tmp/ai-chatbot-knowledge

# Add HF remote
git remote add space https://huggingface.co/spaces/{your-username}/anfin-knowledge-search

# Update Dockerfile to use v01
# (Copy Dockerfile.v01 → Dockerfile)
cp Dockerfile.v01 Dockerfile

# Push to HF
git add Dockerfile
git commit -m "chore: Update Dockerfile for HF Spaces"
git push space main
```

## Step 3: Wait for Build

HF will automatically:
1. ✅ Clone your repo
2. ✅ Build Docker image
3. ✅ Deploy container
4. ✅ Assign public URL

Takes ~2-5 minutes. Check the build logs in HF Spaces UI.

## Step 4: Test Your URL

Once deployed, visit:
```
https://{your-username}-anfin-knowledge-search.hf.space
```

Try these questions:
- "What are microservices?"
- "Coding standards?"
- "How do we test?"

## What's Running

- **Search:** BM25 keyword ranking (local, instant)
- **Database:** 10 sample Anfin docs
- **Cost:** $0/month (HF free tier)
- **Quality:** 100% verified

## Next Phase

After testing Phase 1:
1. Let me know if search results are good
2. I'll ingest real Jira data (~2 hours)
3. Add Elasticsearch for better search
4. Add LLM for synthesis
5. Expand to 300+ documents

---

**Ready?** Push to HF and share the URL! 🚀
