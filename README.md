# Artha Support Bot

A minimal AI support chatbot: FastAPI backend + React (Vite) frontend, single
Docker image, LLM answers grounded in a small in-prompt knowledge base.

## Stack
- **Backend:** FastAPI, served with Uvicorn
- **LLM:** Groq (Llama 3.3 70B) via the OpenAI-compatible SDK
- **Frontend:** React + Vite, built and served as static files from FastAPI
- **Deploy:** single Dockerfile (multi-stage: Node builds the frontend, Python runs the app)

## Run locally

### 1. Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env   # then paste your Groq key into .env
uvicorn main:app --reload --port 8000
```

### 2. Frontend (separate terminal, dev mode)
```bash
cd frontend
npm install
npm run dev
```
Visit the Vite dev URL (usually http://localhost:5173) — it proxies `/api` calls to the backend on :8000.

## Run with Docker (single container, prod-style)
```bash
docker build -t artha-support-bot .
docker run -p 8000:8000 --env-file backend/.env artha-support-bot
```
Visit http://localhost:8000 — one container serves both the API and the built React UI.

## Deploy free on Render
1. Push this repo to GitHub.
2. Render dashboard → New → Web Service → connect the repo.
3. Render auto-detects the Dockerfile at the repo root — leave build/start commands blank.
4. Add environment variable `GROQ_API_KEY` in the Render dashboard (never commit it).
5. Choose the free instance type and deploy. You'll get a public URL.

Note: Render's free tier spins down after inactivity, so the first request after
idle time can take 30-50 seconds (cold start) — expected behavior, not a bug.

## What I'd do differently for production
- Swap the plain-text knowledge base for real RAG over a vector database
  (pgvector or Chroma) so it scales past what fits in a prompt.
- Stream responses token-by-token instead of waiting for the full reply.
- Add rate limiting and basic auth on the `/api/chat` endpoint.
- Add automated tests for the chat service and a CI pipeline for the Docker build.
