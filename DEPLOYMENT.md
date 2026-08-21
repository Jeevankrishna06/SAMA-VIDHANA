# 🚀 SAMA-VIDHANA Deployment Guide

This guide provides step-by-step instructions to deploy **SAMA-VIDHANA** on **Vercel** and **Netlify**, along with backend deployment options.

---

## 🏗️ Architecture Overview

- **Frontend**: Vite + React Single Page Application (SPA) with Tailwind CSS and Framer Motion.
- **Backend**: FastAPI (Python) serving RAG engine, FAISS vector search, and LLM endpoints.

---

## ⚡ Option 1: Deploy Frontend on Vercel

### Step 1: Push Code to GitHub / GitLab / Bitbucket
Ensure your latest changes are pushed to your remote Git repository.

### Step 2: Import Project on Vercel
1. Go to [vercel.com](https://vercel.com) and click **"Add New..." > "Project"**.
2. Select your repository.
3. Configure the project settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `SAMA-VIDHANA/frontend` (or `frontend` depending on repository structure)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### Step 3: Add Environment Variables in Vercel
Under **Settings > Environment Variables**, add:
- `VITE_API_URL`: `https://your-deployed-backend.onrender.com` (leave empty if testing locally or reverse-proxying)

### Step 4: Deploy
Click **Deploy**. Vercel will build the frontend and serve it globally on edge networks.

---

## 🌐 Option 2: Deploy Frontend on Netlify

### Step 1: Import Project on Netlify
1. Go to [app.netlify.com](https://app.netlify.com) and click **"Add new site" > "Import an existing project"**.
2. Select your Git provider and choose the repository.

### Step 2: Configure Build Settings
Netlify will automatically detect `netlify.toml`, or you can specify:
- **Base directory**: `SAMA-VIDHANA/frontend` (or `frontend`)
- **Build command**: `npm run build`
- **Publish directory**: `dist` (or `SAMA-VIDHANA/frontend/dist`)

### Step 3: Add Environment Variables
Go to **Site configuration > Environment variables**, and add:
- `VITE_API_URL`: `https://your-deployed-backend.onrender.com`

### Step 4: Deploy
Click **Deploy site**. SPA routing is automatically handled via `_redirects` and `netlify.toml`.

---

## 🐍 Backend Deployment Options (FastAPI)

The frontend needs a live FastAPI backend for RAG queries, document analysis, and document triage. You can deploy the backend to free or low-cost cloud services:

### 1. Render (Recommended)
1. Go to [render.com](https://render.com) and create a **Web Service**.
2. Connect your Git repository.
3. Settings:
   - **Root Directory**: `SAMA-VIDHANA`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install --no-cache-dir -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables:
   - `MISTRAL_API_KEY`: Your Mistral AI API key (from console.mistral.ai)
   - `PYTHONUNBUFFERED`: `1`

### 2. Railway / Fly.io / Hugging Face Spaces
- Docker or `uvicorn main:app --host 0.0.0.0 --port 8000`

Once the backend is live, copy the backend URL (e.g. `https://sama-vidhana-backend.onrender.com`) and paste it as `VITE_API_URL` in your Vercel/Netlify dashboard!

---

## 🛠️ Local Development & Testing

```bash
# 1. Start backend (Port 8000)
cd SAMA-VIDHANA
uvicorn main:app --reload --port 8000

# 2. Start frontend (Port 5173 with proxy to backend)
cd SAMA-VIDHANA/frontend
npm install
npm run dev
```
