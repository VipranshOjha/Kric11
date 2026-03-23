import os
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

from app import db

router = APIRouter(prefix="/web", tags=["Frontend"])

_here = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(_here, "templates"))

SECRET_KEY = os.getenv("SECRET_KEY", "kric11_super_secret_key_change_in_production")
ALGORITHM = "HS256"
BUDGET_LIMIT = 100.0
MAX_PLAYERS = 12

# ── Auth Helpers ──

def _hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def _verify_pw(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def _create_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def _get_username(request: Request):
    token = request.cookies.get("access_token", "")
    if token.startswith("Bearer "):
        token = token[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
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

# ── Auth Routes ──

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, register: bool = False):
    return templates.TemplateResponse("login.html", {"request": request, "error": None, "is_register": register})

@router.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    row = await db.fetchrow("SELECT hashed_password FROM users WHERE username = $1", username)
    if not row or not _verify_pw(password, row["hashed_password"]):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password.", "is_register": False})
    token = _create_token(username)
    resp = RedirectResponse(url="/web", status_code=status.HTTP_303_SEE_OTHER)
    resp.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True, samesite="lax")
    return resp

@router.post("/register", response_class=HTMLResponse)
async def register_post(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    existing = await db.fetchrow("SELECT id FROM users WHERE username = $1 OR email = $2", username, email)
    if existing:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Username or email already taken.", "is_register": True})
    hashed = _hash_pw(password)
    await db.execute("INSERT INTO users (username, email, hashed_password) VALUES ($1, $2, $3)", username, email, hashed)
    token = _create_token(username)
    resp = RedirectResponse(url="/web", status_code=status.HTTP_303_SEE_OTHER)
    resp.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True, samesite="lax")
    return resp

@router.get("/logout")
async def logout():
    resp = RedirectResponse(url="/web/login", status_code=status.HTTP_303_SEE_OTHER)
    resp.delete_cookie("access_token")
    return resp

# ── App Shell ──

@router.get("/", response_class=HTMLResponse)
async def shell(request: Request):
    username = _get_username(request)
    if not username:
        return RedirectResponse(url="/web/login", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request, "username": username})

# ── Views ──

@router.get("/home_view", response_class=HTMLResponse)
async def home_view(request: Request):
    username = _get_username(request)
    if not username: return _auth_redirect(request)
    return templates.TemplateResponse("components/home.html", {"request": request, "username": username})

@router.get("/builder", response_class=HTMLResponse)
async def builder_page(request: Request):
    username = _get_username(request)
    if not username: return _auth_redirect(request)

    user = await db.fetchrow("SELECT id FROM users WHERE username = $1", username)
    if not user: return _auth_redirect(request)
    user_id = user["id"]

    # Get all players with team abbreviation
    players = await db.fetch("""
        SELECT p.id, p.name, p.role, p.credit_value as credits, t.abbreviation as team
        FROM players p JOIN teams t ON p.team_id = t.id
        WHERE p.is_active = TRUE
        ORDER BY p.credit_value DESC
    """)

    # Get current draft
    draft_rows = await db.fetch("SELECT player_id FROM user_drafts WHERE user_id = $1", user_id)
    draft = [r["player_id"] for r in draft_rows]

    credits_used = sum(p["credits"] for p in players if p["id"] in draft)

    return templates.TemplateResponse("components/builder.html", {
        "request": request,
        "players": players,
        "draft": draft,
        "credits_left": round(BUDGET_LIMIT - credits_used, 1),
        "count": len(draft),
        "toast": ""
    })

@router.post("/toggle/{player_id}", response_class=HTMLResponse)
async def toggle_player(request: Request, player_id: int):
    username = _get_username(request)
    if not username: return _auth_redirect(request)

    user = await db.fetchrow("SELECT id FROM users WHERE username = $1", username)
    if not user: return _auth_redirect(request)
    user_id = user["id"]

    player = await db.fetchrow("""
        SELECT p.id, p.name, p.role, p.credit_value as credits, t.abbreviation as team
        FROM players p JOIN teams t ON p.team_id = t.id WHERE p.id = $1
    """, player_id)
    if not player:
        return HTMLResponse(status_code=404)

    # Check if already selected
    existing = await db.fetchrow("SELECT id FROM user_drafts WHERE user_id = $1 AND player_id = $2", user_id, player_id)
    toast_html = ""

    if existing:
        # Deselect
        await db.execute("DELETE FROM user_drafts WHERE user_id = $1 AND player_id = $2", user_id, player_id)
    else:
        # Check limits before adding
        draft_rows = await db.fetch("SELECT player_id FROM user_drafts WHERE user_id = $1", user_id)
        draft_ids = [r["player_id"] for r in draft_rows]

        if len(draft_ids) >= MAX_PLAYERS:
            toast_html = _toast("Squad full — 12/12 selected")
        else:
            all_players = await db.fetch("SELECT id, credit_value FROM players")
            credits_map = {r["id"]: r["credit_value"] for r in all_players}
            current_credits = sum(credits_map.get(pid, 0) for pid in draft_ids)

            if current_credits + player["credits"] > BUDGET_LIMIT:
                remaining = round(BUDGET_LIMIT - current_credits, 1)
                toast_html = _toast(f"Budget exceeded — {remaining} cr left")
            else:
                await db.execute("INSERT INTO user_drafts (user_id, player_id) VALUES ($1, $2)", user_id, player_id)

    # Recalculate state
    draft_rows = await db.fetch("SELECT player_id FROM user_drafts WHERE user_id = $1", user_id)
    draft = [r["player_id"] for r in draft_rows]
    all_players = await db.fetch("SELECT id, credit_value FROM players")
    credits_map = {r["id"]: r["credit_value"] for r in all_players}
    credits_used = sum(credits_map.get(pid, 0) for pid in draft)

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
    username = _get_username(request)
    if not username: return _auth_redirect(request)

    user = await db.fetchrow("SELECT id FROM users WHERE username = $1", username)
    if not user: return _auth_redirect(request)
    user_id = user["id"]

    draft_rows = await db.fetch("SELECT player_id FROM user_drafts WHERE user_id = $1", user_id)
    if len(draft_rows) != 12:
        return HTMLResponse(f"<div id='save-status' class='bg-red-50 text-red-500 border border-red-100 p-3 mt-4 rounded-2xl text-center text-xs font-medium tracking-wider slide-in'>Select exactly 12 players ({len(draft_rows)}/12)</div>")

    existing = await db.fetchrow("SELECT id FROM fantasy_teams WHERE user_id = $1", user_id)
    if existing:
        return HTMLResponse("<div id='save-status' class='bg-amber-50 text-amber-600 border border-amber-100 p-3 mt-4 rounded-2xl text-center text-xs font-medium tracking-wider slide-in'>Roster already locked</div>")

    await db.execute("INSERT INTO fantasy_teams (user_id) VALUES ($1)", user_id)
    return HTMLResponse("<div id='save-status' class='bg-emerald-50 text-emerald-600 border border-emerald-100 p-3 mt-4 rounded-2xl text-center text-xs font-medium tracking-wider slide-in'>✓ Roster locked successfully</div>")

@router.get("/leaderboard_view", response_class=HTMLResponse)
async def leaderboard_view(request: Request):
    username = _get_username(request)
    if not username: return _auth_redirect(request)

    teams = await db.fetch("""
        SELECT u.username, ft.total_points,
            (SELECT COUNT(*) FROM user_drafts ud WHERE ud.user_id = u.id) as player_count
        FROM fantasy_teams ft
        JOIN users u ON ft.user_id = u.id
        ORDER BY ft.total_points DESC
    """)

    return templates.TemplateResponse("components/leaderboard.html", {
        "request": request,
        "teams": teams,
        "username": username
    })
