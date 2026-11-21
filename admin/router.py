import os
import json
from fastapi import APIRouter, HTTPException, Response, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

from templates import admin_render
from login.utils.auth_utils import verify_password, create_access_token, decode_token
from admin.utils.schemas import AdminLoginRequest
from admin.utils.storage import load_admin, update_admin_last_login

from config import USER_DATA_DIR, NEWS_DATA_DIR, TRACKING_DIR, ALL_CATEGORIES

router = APIRouter()

def get_current_admin(request: Request):
    token = request.cookies.get("admin_access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    admin_user = load_admin(payload["sub"])
    if not admin_user:
        raise HTTPException(status_code=401, detail="Admin not found")
        
    return admin_user

@router.get("/", response_class=RedirectResponse)
async def admin_root():
    return RedirectResponse(url="/admin/login")

@router.get("/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return admin_render("login.html", {})

@router.post("/login")
async def admin_login(body: AdminLoginRequest, response: Response):
    admin = load_admin(body.username)
    # Verify the stored password hash (legacy records are migrated during startup).
    if not admin or not verify_password(body.password, admin["password_hash"]):
        raise HTTPException(401, "Invalid admin username or password")

    update_admin_last_login(body.username)
    token = create_access_token({"sub": admin["username"]})

    response.set_cookie(
        key="admin_access_token", value=token,
        httponly=True, max_age=86400, samesite="lax",
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": admin["username"],
    }

@router.post("/logout")
async def admin_logout(response: Response):
    response.delete_cookie("admin_access_token")
    return {"message": "Admin logged out"}

@router.get("/stats", response_class=HTMLResponse)
async def admin_stats_page(request: Request, admin=Depends(get_current_admin)):
    return admin_render("stats.html", {"admin": admin})

@router.get("/api/stats_data")
async def get_stats_data(admin=Depends(get_current_admin)):
    # 1. Total users
    total_users = 0
    if os.path.exists(USER_DATA_DIR):
        total_users = sum(1 for f in os.listdir(USER_DATA_DIR) if f.endswith(".json"))

    # 2. Total tracked topics
    total_tracked = 0
    if os.path.exists(TRACKING_DIR):
        total_tracked = sum(1 for f in os.listdir(TRACKING_DIR) if f.endswith(".json"))
        
    # 3. Posts per category & Total Posts
    posts_per_category = {}
    total_posts = 0
    
    if os.path.exists(NEWS_DATA_DIR):
        for filename in os.listdir(NEWS_DATA_DIR):
            if not filename.endswith(".json"): continue
            cat_key = filename.replace(".json", "")
            cat_name = ALL_CATEGORIES.get(cat_key, cat_key.replace("_", " ").title())
            
            try:
                with open(os.path.join(NEWS_DATA_DIR, filename), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    count = len(data) if isinstance(data, list) else 0
                    posts_per_category[cat_name] = count
                    total_posts += count
            except Exception:
                pass
                
    # Sort posts per category by count
    sorted_categories = dict(sorted(posts_per_category.items(), key=lambda item: item[1], reverse=True))

    return {
        "total_users": total_users,
        "total_tracked_topics": total_tracked,
        "total_posts": total_posts,
        "posts_per_category": sorted_categories
    }
