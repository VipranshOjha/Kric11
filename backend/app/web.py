import os
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

from app.data import (
    PLAYERS, PLAYERS_BY_ID, USERS, DRAFTS, LOCKED_TEAMS,
    BUDGET_LIMIT, MAX_PLAYERS
)

router = APIRouter(prefix="/web", tags=["Frontend"])

_here = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(_here, "templates"))

SECRET_KEY = os.getenv("SECRET_KEY", "kric11_super_secret_key_change_in_production")
ALGORITHM = "HS256"

# ── Auth helpers ──

def _hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def _verify_pw(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def _create_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def _get_user(request: Request):
    token = request.cookies.get("access_token", "")
    if token.startswith("Bearer "):
        token = token[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username and username in USERS:
            return username
    except JWTError:
        pass
    return None

def _auth_redirect(request: Request):
    if "hx-request" in request.headers:
        resp = HTMLResponse()
        resp.headers["HX-Redirect"] = "/web/login"
        return resp
    return RedirectResponse(url="/web/login", status_code=303)

def _toast(msg: str, style: str = "warning"):
    bg = "bg-red-50 text-red-500 border-red-100" if style == "error" else "bg-amber-50 text-amber-600 border-amber-100"
    return f"""
    <div id="toast-container" hx-swap-oob="true">
        <div class="fixed top-20 left-1/2 -translate-x-1/2 z-[999] max-w-xs w-full px-5 py-3 rounded-2xl
            {bg} border text-xs font-medium tracking-wider text-center shadow-sm slide-in">
            {msg}
        </div>
    </div>
    <script>
        if(navigator.vibrate) navigator.vibrate(5);
        setTimeout(function() {{ var c=document.getElementById('toast-container'); if(c) c.innerHTML=''; }}, 2500);
    </script>
    """

# ── Routes ──

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, register: bool = False):
    return templates.TemplateResponse("login.html", {"request": request, "error": None, "is_register": register})

@router.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    user = USERS.get(username)
    if not user or not _verify_pw(password, user["password"]):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password.", "is_register": False})
    token = _create_token(username)
    resp = RedirectResponse(url="/web", status_code=status.HTTP_303_SEE_OTHER)
    resp.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return resp

@router.post("/register", response_class=HTMLResponse)
async def register_post(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    if username in USERS:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Username already taken.", "is_register": True})
    USERS[username] = {"password": _hash_pw(password), "email": email}
    token = _create_token(username)
    resp = RedirectResponse(url="/web", status_code=status.HTTP_303_SEE_OTHER)
    resp.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return resp

@router.get("/logout")
async def logout():
    resp = RedirectResponse(url="/web/login", status_code=status.HTTP_303_SEE_OTHER)
    resp.delete_cookie("access_token")
    return resp

@router.get("/", response_class=HTMLResponse)
async def shell(request: Request):
    username = _get_user(request)
    if not username:
        return RedirectResponse(url="/web/login", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request, "username": username})

@router.get("/home_view", response_class=HTMLResponse)
async def home_view(request: Request):
    username = _get_user(request)
    if not username: return _auth_redirect(request)
    return templates.TemplateResponse("components/home.html", {"request": request, "username": username})

@router.get("/builder", response_class=HTMLResponse)
async def builder_page(request: Request):
    username = _get_user(request)
    if not username: return _auth_redirect(request)

    draft = DRAFTS.setdefault(username, [])
    credits_used = sum(PLAYERS_BY_ID[pid]["credits"] for pid in draft if pid in PLAYERS_BY_ID)

    return templates.TemplateResponse("components/builder.html", {
        "request": request,
        "players": sorted(PLAYERS, key=lambda p: p["credits"], reverse=True),
        "draft": draft,
        "credits_left": round(BUDGET_LIMIT - credits_used, 1),
        "count": len(draft),
        "toast": ""
    })

@router.post("/toggle/{player_id}", response_class=HTMLResponse)
async def toggle_player(request: Request, player_id: int):
    username = _get_user(request)
    if not username: return _auth_redirect(request)

    player = PLAYERS_BY_ID.get(player_id)
    if not player:
        return HTMLResponse(status_code=404)

    draft = DRAFTS.setdefault(username, [])
    toast_html = ""

    if player_id in draft:
        draft.remove(player_id)
    else:
        if len(draft) >= MAX_PLAYERS:
            toast_html = _toast("Squad full — 12/12 selected")
        else:
            current_credits = sum(PLAYERS_BY_ID[pid]["credits"] for pid in draft)
            if current_credits + player["credits"] > BUDGET_LIMIT:
                remaining = round(BUDGET_LIMIT - current_credits, 1)
                toast_html = _toast(f"Budget exceeded — {remaining} cr left")
            else:
                draft.append(player_id)

    credits_used = sum(PLAYERS_BY_ID[pid]["credits"] for pid in draft)

    return templates.TemplateResponse("components/player_card.html", {
        "request": request,
        "p": player,
        "is_selected": player_id in draft,
        "credits_left": round(BUDGET_LIMIT - credits_used, 1),
        "count": len(draft),
        "toast": toast_html
    })

@router.post("/save_team", response_class=HTMLResponse)
async def save_team(request: Request):
    username = _get_user(request)
    if not username: return _auth_redirect(request)

    draft = DRAFTS.get(username, [])
    if len(draft) != 12:
        return HTMLResponse(f"<div id='save-status' class='bg-red-50 text-red-500 border border-red-100 p-3 mt-4 rounded-2xl text-center text-xs font-medium tracking-wider slide-in'>Select exactly 12 players ({len(draft)}/12)</div>")

    if username in LOCKED_TEAMS:
        return HTMLResponse("<div id='save-status' class='bg-amber-50 text-amber-600 border border-amber-100 p-3 mt-4 rounded-2xl text-center text-xs font-medium tracking-wider slide-in'>Roster already locked</div>")

    LOCKED_TEAMS[username] = {
        "players": list(draft),
        "captain": draft[0],
        "vice_captain": draft[1],
        "points": 0.0
    }

    return HTMLResponse("<div id='save-status' class='bg-emerald-50 text-emerald-600 border border-emerald-100 p-3 mt-4 rounded-2xl text-center text-xs font-medium tracking-wider slide-in'>✓ Roster locked successfully</div>")

@router.get("/leaderboard_view", response_class=HTMLResponse)
async def leaderboard_view(request: Request):
    username = _get_user(request)
    if not username: return _auth_redirect(request)

    teams = sorted(LOCKED_TEAMS.items(), key=lambda x: x[1]["points"], reverse=True)

    return templates.TemplateResponse("components/leaderboard.html", {
        "request": request,
        "teams": teams,
        "username": username
    })
