"""
tracking/router.py
──────────────────
Endpoints for the news tracking system.
"""
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from templates import tracking_render
from login.utils.dependencies import get_current_user
from login.utils.storage import load_user, save_user
from login.utils.ollama_utils import summarise_timeline, chat_with_context_ai
from login.utils.schemas import ChatContextRequest
from tracking.matcher import find_related_news
from config import ALL_CATEGORIES

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────
class SummariseTimelineRequest(BaseModel):
    topic_title: str
    articles: list[dict]


# ── Tracking list page ───────────────────────────────────────────────────────
@router.get("/", response_class=HTMLResponse)
async def tracking_page(request: Request, current_user: dict = Depends(get_current_user)):
    return tracking_render("tracking.html", {"all_categories": ALL_CATEGORIES})


# ── API: list tracked topics ─────────────────────────────────────────────────
@router.get("/list")
async def list_tracked(current_user: dict = Depends(get_current_user)):
    user = load_user(current_user["username"])
    tracked = user.get("tracked_topics", [])
    return {"tracked_topics": tracked, "count": len(tracked)}


# ── Summarise timeline ──────────────────────────────────────────────────────
@router.post("/summarise")
async def summarise_timeline_endpoint(
    body: SummariseTimelineRequest,
    current_user: dict = Depends(get_current_user),
):
    if not body.articles:
        raise HTTPException(400, "No articles to summarise")
        
    return StreamingResponse(
        summarise_timeline(body.topic_title, body.articles),
        media_type="text/plain"
    )


# ── Remove tracked topic ────────────────────────────────────────────────────
@router.delete("/remove/{news_id:path}")
async def remove_tracked(news_id: str, current_user: dict = Depends(get_current_user)):
    user = load_user(current_user["username"])
    tracked = user.get("tracked_topics", [])

    original_len = len(tracked)
    tracked = [t for t in tracked if t.get("news_id") != news_id]

    if len(tracked) == original_len:
        raise HTTPException(404, "Tracked topic not found")

    user["tracked_topics"] = tracked
    save_user(user)

    return {"message": "Tracking removed", "news_id": news_id, "remaining": len(tracked)}


# ── Timeline page ───────────────────────────────────────────────────────────
@router.get("/timeline/{news_id:path}", response_class=HTMLResponse)
async def timeline_page(news_id: str, request: Request, current_user: dict = Depends(get_current_user)):
    return tracking_render("timeline.html", {"all_categories": ALL_CATEGORIES})


# ── API: get related news for a tracked topic ───────────────────────────────
@router.get("/data/{news_id:path}")
async def timeline_data(news_id: str, current_user: dict = Depends(get_current_user)):
    user = load_user(current_user["username"])
    tracked = user.get("tracked_topics", [])

    # Find the tracked topic by news_id
    topic = None
    for t in tracked:
        if t.get("news_id") == news_id:
            topic = t
            break

    if not topic:
        raise HTTPException(404, "Tracked topic not found")

    # Find related news articles using precise matching
    related = find_related_news(topic["title"], limit=50)

    # Store the updated tracked news count in user data
    for t in tracked:
        if t.get("news_id") == news_id:
            t["last_checked"] = datetime.now(timezone.utc).isoformat()
            t["related_count"] = len(related)
            break
    user["tracked_topics"] = tracked
    save_user(user)

    return {
        "topic": topic,
        "articles": related,
        "count": len(related),
    }

@router.post("/chat")
async def chat_with_timeline(
    body: ChatContextRequest,
    current_user: dict = Depends(get_current_user),
):
    if not body.messages:
        raise HTTPException(400, "Message history cannot be empty")
        
    return StreamingResponse(
        chat_with_context_ai(body.context_text, [m.model_dump() for m in body.messages]),
        media_type="text/plain"
    )
