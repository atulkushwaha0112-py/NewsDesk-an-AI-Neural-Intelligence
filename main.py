import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from login.router.auth_router       import router as auth_router
from login.router.preference_router import router as preference_router
from dashboard.router               import router as dashboard_router
from dashboard.article_router       import router as article_router
from tracking.router                import router as tracking_router
from profile.router                 import router as profile_router
from admin.router                   import router as admin_router

app = FastAPI(title="NewsDesk")

base_dir   = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, "login", "templates", "static")
os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(auth_router,       prefix="/auth",        tags=["Auth"])
app.include_router(preference_router, prefix="/preferences", tags=["Preferences"])
app.include_router(dashboard_router,  prefix="/dashboard",   tags=["Dashboard"])
app.include_router(article_router,    prefix="/article",     tags=["Article"])
app.include_router(tracking_router,   prefix="/tracking",    tags=["Tracking"])
app.include_router(profile_router,    prefix="/profile",     tags=["Profile"])
app.include_router(admin_router,      prefix="/admin",       tags=["Admin"])

# Bootstrap default admin if none exist
from config import ADMIN_DATA_DIR
from admin.utils.storage import create_admin
if not any(f.endswith(".json") for f in os.listdir(ADMIN_DATA_DIR)):
    create_admin("admin", "admin123")
    print("Default admin created: 'admin' / 'admin123'")

# ── Routes ──────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Step 1 — Video splash screen"""
    return FileResponse(
        os.path.join(static_dir, "video_intro.html"),
        media_type="text/html"
    )

# video_intro.html redirects to /static/intro.html  (Step 2 — animated scenes)
# intro.html redirects to /auth/login               (Step 3 — login page)
