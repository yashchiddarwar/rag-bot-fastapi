# Deployment Guide - Free Hosting for RAG Bot

This guide covers deploying your RAG bot to free hosting platforms without exposing your API keys.

## ⚠️ Security First

**NEVER commit your `.env` file or API keys to Git!**

Already added to `.gitignore`:
- `.env`
- `__pycache__/`
- Other sensitive files

## Option 1: Render (Recommended - Easiest)

### Steps:

1. **Prepare your repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Push to GitHub:**
   - Create a new repository on GitHub (keep it private if you want)
   - Push your code:
   ```bash
   git remote add origin https://github.com/yourusername/rag-bot.git
   git branch -M main
   git push -u origin main
   ```

3. **Deploy on Render:**
   - Go to https://render.com and sign up
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the `render.yaml` file
   - **Add your secret environment variables:**
     - `OPENROUTER_API_KEY`: Your OpenRouter API key
     - `PINECONE_API_KEY`: Your Pinecone API key
   - Click "Create Web Service"

4. **First deployment:**
   - After deployment, run the ingestion script once:
   - Use Render's shell or run locally: `python ingest.py`

### Render Free Tier:
- ✅ 750 hours/month free
- ✅ Automatic HTTPS
- ✅ Auto-deploy on git push
- ⚠️ Sleeps after 15 min of inactivity (wakes on request)

---

## Option 2: Railway

### Steps:

1. **Push to GitHub** (same as Option 1)

2. **Deploy on Railway:**
   - Go to https://railway.app and sign up
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Python
   - Add environment variables in Settings → Variables:
     ```
     OPENROUTER_API_KEY=your_key_here
     PINECONE_API_KEY=your_key_here
     PINECONE_ENVIRONMENT=us-east-1
     PINECONE_INDEX_NAME=rag-bot
     OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free
     EMBEDDING_MODEL=openai/text-embedding-3-small
     ```
   - Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Railway Free Tier:
- ✅ $5 free credit/month
- ✅ No sleeping
- ✅ Good performance

---

## Option 3: Fly.io

### Steps:

1. **Install flyctl:**
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   
   # Mac/Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login and launch:**
   ```bash
   fly auth login
   fly launch
   ```

3. **Set secrets:**
   ```bash
   fly secrets set OPENROUTER_API_KEY=your_key_here
   fly secrets set PINECONE_API_KEY=your_key_here
   fly secrets set PINECONE_ENVIRONMENT=us-east-1
   fly secrets set PINECONE_INDEX_NAME=rag-bot
   ```

4. **Deploy:**
   ```bash
   fly deploy
   ```

### Fly.io Free Tier:
- ✅ 3 VMs with 256MB RAM
- ✅ No sleeping
- ✅ Good global performance

---

## Option 4: Hugging Face Spaces

Great for ML projects!

1. Go to https://huggingface.co/spaces
2. Create new Space → Select "Docker"
3. Upload your files
4. Add secrets in Settings → Repository secrets
5. Your app will be at: `https://huggingface.co/spaces/username/rag-bot`

---

## Environment Variables Setup

For any platform, you need to set these environment variables:

### Required:
```
OPENROUTER_API_KEY=your_openrouter_key
PINECONE_API_KEY=your_pinecone_key
```

### Optional (with defaults):
```
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free
EMBEDDING_MODEL=openai/text-embedding-3-small
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=rag-bot
CHUNK_SIZE=600
CHUNK_OVERLAP=120
TOP_K_RESULTS=5
```

---

## Post-Deployment

### Run Ingestion Once:

After deploying, you need to ingest your documents:

**Option A: Run locally**
```bash
python ingest.py
```

**Option B: Run on platform**
- Render: Use Shell feature
- Railway: Use terminal
- Fly.io: `fly ssh console -C "python ingest.py"`

### Test Your Deployment:

```bash
curl -X POST "https://your-app-url.com/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the best practices for caching?"}'
```

---

## Cost Optimization

Since you're on free tiers:

1. ✅ **Using free model:** `meta-llama/llama-3.1-8b-instruct:free`
2. ✅ **Pinecone free tier:** 1 index, 100k vectors
3. ✅ **OpenRouter free tier:** Limited requests
4. ✅ **Reduced token limits:** `max_tokens=1000`

### If you run out of credits:

**Switch embedding to free:**
Update your `.env`:
```
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

Then update the code to use HuggingFace embeddings instead of OpenAI.

---

## Monitoring

After deployment:
- Check logs on your platform dashboard
- Monitor API usage on OpenRouter
- Check Pinecone usage

---

## Quick Deploy Checklist:

- [ ] `.env` file is in `.gitignore`
- [ ] Code pushed to GitHub
- [ ] Environment variables set on hosting platform
- [ ] App deployed successfully
- [ ] Run `ingest.py` once
- [ ] Test with a query
- [ ] API keys secured ✅

---

## Need Help?

- Render Docs: https://render.com/docs
- Railway Docs: https://docs.railway.app
- Fly.io Docs: https://fly.io/docs
