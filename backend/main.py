import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from chat_service import get_chat_reply

app = FastAPI(title="AI Support Chatbot")

# CORS is only needed if you run the frontend on a different origin during
# local dev (e.g. Vite dev server on :5173 hitting the API on :8000).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    reply = get_chat_reply(payload.message)
    return ChatResponse(reply=reply)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


# --- Serve the built React frontend (frontend/dist) as static files ---
# This lets one Docker container serve both the API and the UI, so you
# only need to deploy one service.
FRONTEND_DIST = Path(__file__).parent / "static"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        return FileResponse(FRONTEND_DIST / "index.html")
