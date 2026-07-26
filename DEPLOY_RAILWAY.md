# Deploy to Railway.app (Free Tier - $5/month credit)

## Why Railway?

✅ **Free tier:** $5/month credit (enough for this chatbot)  
✅ **No credit card needed initially**  
✅ **Fast deploys:** 2-3 minutes  
✅ **Good performance:** Better than HF Spaces  
✅ **Easy rollback:** One-click rollback if needed  

---

## Step 1: Setup Railway Account

1. Go to https://railway.app
2. Sign up (GitHub recommended for faster setup)
3. Create new project

---

## Step 2: Connect Git Repo

```bash
# Install Railway CLI
npm install -g @railway/cli

# Or use Homebrew
brew install railway

# Login
railway login

# In project directory
cd /tmp/ai-chatbot-knowledge

# Link to Railway
railway link

# When prompted:
# - Create new project
# - Name: "anfin-knowledge"
# - Environment: production
```

---

## Step 3: Deploy Phase 1 MVP

```bash
# Deploy current code (Phase 1)
railway up

# This will:
# 1. Build Docker image
# 2. Push to Railway registry
# 3. Deploy container
# 4. Assign public URL

# Takes ~2-3 minutes
```

---

## Step 4: Get Your URL

```bash
# After deploy completes
railway open

# Or manually in Railway dashboard:
# Settings → Domains → Railway will assign public URL
# Example: https://anfin-knowledge-production.up.railway.app
```

---

## Step 5: Test

```bash
# Test health
curl https://your-railway-url/health

# Test chat
curl -X POST https://your-railway-url/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"microservices?"}'

# Open in browser
open https://your-railway-url
```

---

## Cost Check

```
Railway free tier: $5/month credit

Phase 1 costs:
- Small container: ~$3/month
- Data: negligible
- Total: Free (within credit)

Phase 2-4 costs:
- Elasticsearch: ~$5-10/month
- Qwen LLM: $0 (local)
- Total: ~$5-10/month (within credit)
```

---

## Deployment Chain (Phase 1 → 4)

### Phase 1 (Now - Already deployed)
```bash
# Just push current code
git push
railway up
```

### Phase 2 (After Phase 1 testing)
```bash
# I'll add:
# - elasticsearch_init.py
# - confluence_ingester.py  
# - Elasticsearch config

git add .
git commit -m "Phase 2: Add Elasticsearch + real Jira data"
railway up

# Railway auto-detects changes, rebuilds, redeploys
```

### Phase 3 (Qwen LLM)
```bash
# I'll add:
# - synthesis.py
# - Qwen model config

git add .
git commit -m "Phase 3: Add Qwen synthesis"
railway up
```

### Phase 4 (Verification)
```bash
# Final optimization
git add .
git commit -m "Phase 4: Production ready"
railway up
```

---

## Useful Railway Commands

```bash
# View logs (live)
railway logs -f

# Check status
railway status

# Rollback to previous version
railway rollback

# View environment variables
railway variables

# Set variable
railway variables set VAR_NAME=value

# Open dashboard
railway open

# Build locally before deploying
railway build

# Check resource usage
railway status
```

---

## What Happens When Phase 2 Deploys

```
Current (Phase 1):
- 10 hardcoded docs
- BM25 search only
- Response time: 1s

Phase 2 Update:
- 300+ Jira docs
- Elasticsearch index
- Hybrid search
- Response time: 3s

Railway will:
1. Stop old container
2. Build new image
3. Start new container
4. Keep same URL ✅
5. Zero downtime ✅
```

---

## Next Steps

1. ✅ Commit Phase 1 code ← Done
2. Push to Railway (you do now)
3. Test public URL
4. Send feedback
5. I'll prepare Phase 2 (Elasticsearch + Jira ingestion)

---

## Quick Deploy Summary

```bash
# One-time setup
npm install -g @railway/cli
railway login
cd /tmp/ai-chatbot-knowledge
railway link

# Every deploy (Phase 1, 2, 3, 4)
git add .
git commit -m "Phase X: description"
railway up

# Done! Railway auto-handles everything
```

**Cost:** $0-5/month (free credit covers all)  
**URL:** Stays same across all phases  
**Rollback:** One command if needed  

---

Ready to deploy Phase 1? 🚀
