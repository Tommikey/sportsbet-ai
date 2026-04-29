# 🚀 SportsBet AI — GitHub + Railway Deployment Guide

## STEP 1 — Push to GitHub

Open Terminal on your Mac and run these commands ONE BY ONE:

```bash
# 1. Navigate to the project
cd ~/Downloads/sportsbetting
# (or wherever you saved it — adjust path)

# 2. Initialize git
git init

# 3. Add all files
git add .

# 4. First commit
git commit -m "🚀 SportsBet AI — Initial commit"

# 5. Create main branch
git branch -M main
```

Now go to https://github.com/new and:
- Name your repo: `sportsbet-ai`
- Set it to **Public** (Railway free tier needs this)
- Do NOT tick "Add README" (we already have one)
- Click **Create repository**

GitHub will show you commands — copy your repo URL (looks like `https://github.com/YOUR_USERNAME/sportsbet-ai.git`)

Then back in Terminal:
```bash
# 6. Connect to GitHub (paste YOUR repo URL)
git remote add origin https://github.com/YOUR_USERNAME/sportsbet-ai.git

# 7. Push!
git push -u origin main
```

Your code is now on GitHub ✅

---

## STEP 2 — Deploy Backend on Railway

1. Go to https://railway.app
2. Click **Start a New Project**
3. Click **Deploy from GitHub repo**
4. Sign in with GitHub → Select `sportsbet-ai`
5. Railway will detect your repo. When prompted:
   - **Root Directory**: type `backend`
   - Leave everything else as default
6. Click **Deploy**
7. Wait ~2 minutes for it to build
8. Click your service → **Settings** → **Networking** → **Generate Domain**
9. Copy the domain (looks like `sportsbet-ai-backend.up.railway.app`)

---

## STEP 3 — Deploy Frontend on Railway

1. In your Railway project, click **+ New Service**
2. Choose **GitHub Repo** again → select `sportsbet-ai`
3. This time set:
   - **Root Directory**: `frontend`
4. Click **Deploy**
5. Go to **Settings** → **Networking** → **Generate Domain**
6. Copy the frontend URL

---

## STEP 4 — Connect Frontend to Backend

Open the file: `frontend/index.html`

Find this line (near the top of the `<script>` section):
```javascript
const API_BASE = window.BACKEND_URL || "https://YOUR-BACKEND-URL.up.railway.app/api";
```

Replace `YOUR-BACKEND-URL.up.railway.app` with your actual Railway backend domain from Step 2.

Then push the change:
```bash
git add frontend/index.html
git commit -m "🔗 Connect frontend to live Railway backend"
git push
```

Railway will auto-redeploy in ~1 minute. Your app is now LIVE! 🎉

---

## STEP 5 — Test Your Live App

Visit your frontend Railway URL — you should see the full dashboard with live predictions!

Test the API directly:
```
https://YOUR-BACKEND.up.railway.app/docs
```
This opens the interactive API documentation.

---

## Auto-Deploy (Already Set Up!)

Every time you push to GitHub, Railway automatically redeploys. So to update predictions or fixtures:

```bash
# Edit backend/data/mock_data.py with new fixtures
git add .
git commit -m "📊 Update fixtures"
git push
# Railway redeploys in ~60 seconds
```

---

## Troubleshooting

**Build fails?**
- Check Railway logs (click your service → Deployments → View Logs)
- Most common issue: wrong Root Directory — make sure backend = `backend`, frontend = `frontend`

**CORS errors in browser?**
- The backend already has CORS set to `allow_origins=["*"]` so this shouldn't happen
- If it does, check that your API_BASE URL in index.html is correct and has `/api` at the end

**Free tier limits?**
- Railway free tier gives $5/month credit — enough for this app
- If you exceed it, upgrade to $20/month Hobby plan

---

## Your App URLs (fill in after deploying)

| Service  | URL |
|----------|-----|
| Frontend | `https://____________.up.railway.app` |
| Backend  | `https://____________.up.railway.app` |
| API Docs | `https://____________.up.railway.app/docs` |
