import os
import httpx
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

from app import db
from app.cron import CRICKET_API_KEY, CRICKET_API_BASE

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

def _create_token(username: str, user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    return jwt.encode({"sub": username, "uid": user_id, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

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

async def _get_user_id(request: Request):
    token = request.cookies.get("access_token", "")
    if token.startswith("Bearer "):
        token = token[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid = payload.get("uid")
        username = payload.get("sub")
        if uid:
            return username, uid
        
        # Fallback for old tokens without uid
        if username:
            user = await db.fetchrow("SELECT id FROM users WHERE username = $1", username)
            return username, user["id"] if user else None
    except JWTError:
        pass
    return None, None

def _get_active_contest(request: Request):
    c = request.cookies.get("active_contest")
    if c and c.isdigit():
        return int(c)
    return None

async def _get_draft_state(user_id, contest_id):
    if not contest_id: return [], None, None
    draft_rows = await db.fetch(
        "SELECT player_id, is_captain, is_vice_captain FROM user_drafts WHERE user_id = $1 AND contest_id = $2", 
        user_id, contest_id
    )
    draft = [r["player_id"] for r in draft_rows]
    captain_id = next((r["player_id"] for r in draft_rows if r["is_captain"]), None)
    vc_id = next((r["player_id"] for r in draft_rows if r["is_vice_captain"]), None)
    return draft, captain_id, vc_id

# ── Auth Routes ──

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, register: bool = False):
    return templates.TemplateResponse("login.html", {"request": request, "error": None, "is_register": register})

@router.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    row = await db.fetchrow("SELECT id, hashed_password FROM users WHERE username = $1", username)
    if not row or not _verify_pw(password, row["hashed_password"]):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password.", "is_register": False})
    token = _create_token(username, row["id"])
    resp = RedirectResponse(url="/web", status_code=status.HTTP_303_SEE_OTHER)
    resp.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True, samesite="lax")
    return resp

@router.post("/register", response_class=HTMLResponse)
async def register_post(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    existing = await db.fetchrow("SELECT id FROM users WHERE username = $1 OR email = $2", username, email)
    if existing:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Username or email already taken.", "is_register": True})
    hashed = _hash_pw(password)
    user_id = await db.fetchval("INSERT INTO users (username, email, hashed_password) VALUES ($1, $2, $3) RETURNING id", username, email, hashed)
    token = _create_token(username, user_id)
    resp = RedirectResponse(url="/web", status_code=status.HTTP_303_SEE_OTHER)
    resp.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True, samesite="lax")
    return resp

@router.get("/logout")
async def logout():
    resp = RedirectResponse(url="/web/login", status_code=status.HTTP_303_SEE_OTHER)
    resp.delete_cookie("access_token")
    resp.delete_cookie("active_contest")
    return resp

# ── App Shell ──

@router.get("/", response_class=HTMLResponse)
async def shell(request: Request):
    username = _get_username(request)
    if not username:
        return RedirectResponse(url="/web/login", status_code=303)
    
    t1, t2 = "", ""
    contest_id = _get_active_contest(request)
    if contest_id:
        contest = await db.fetchrow("SELECT t1.abbreviation as t1, t2.abbreviation as t2 FROM contests c JOIN teams t1 ON c.team1_id = t1.id JOIN teams t2 ON c.team2_id = t2.id WHERE c.id = $1", contest_id)
        if contest:
            t1, t2 = contest["t1"], contest["t2"]

    return templates.TemplateResponse("index.html", {"request": request, "username": username, "t1": t1, "t2": t2})

# ── Views ──

@router.get("/home_view", response_class=HTMLResponse)
async def home_view(request: Request):
    username = _get_username(request)
    if not username: return _auth_redirect(request)
    active_id = _get_active_contest(request)
    
    contests_db = await db.fetch("""
        SELECT c.id, c.name, c.status, c.match_date, c.venue, 
               t1.abbreviation as t1_abbr, t2.abbreviation as t2_abbr
        FROM contests c
        JOIN teams t1 ON c.team1_id = t1.id
        JOIN teams t2 ON c.team2_id = t2.id
        ORDER BY c.id ASC
    """)
    contests = []
    for r in contests_db:
        d = dict(r)
        d["active"] = (d["id"] == active_id)
        contests.append(d)
        
    return templates.TemplateResponse("components/home.html", {
        "request": request, "username": username, "contests": contests
    })

@router.post("/select_contest/{contest_id}", response_class=HTMLResponse)
async def select_contest(request: Request, contest_id: int):
    username = _get_username(request)
    if not username: return _auth_redirect(request)
    
    # Fetch contest info to update the header teams OOB
    contest = await db.fetchrow("""
        SELECT t1.abbreviation as t1, t2.abbreviation as t2
        FROM contests c
        JOIN teams t1 ON c.team1_id = t1.id
        JOIN teams t2 ON c.team2_id = t2.id
        WHERE c.id = $1
    """, contest_id)
    
    if contest:
        header_oob = f"""
        <div id="app-header-teams" class="flex items-center space-x-3 text-xs font-medium text-slate-400 tracking-wider" hx-swap-oob="true">
            <span class="text-slate-600">{contest["t1"]}</span>
            <span class="text-slate-300">·</span>
            <span class="text-slate-600">{contest["t2"]}</span>
        </div>
        """
    else:
        header_oob = ""
        
    resp = HTMLResponse(header_oob)
    resp.set_cookie("active_contest", str(contest_id), httponly=True, samesite="lax")
    return resp

@router.post("/create_test_contest", response_class=HTMLResponse)
async def create_test_contest(request: Request):
    username = _get_username(request)
    if not username: return _auth_redirect(request)
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.get(f"{CRICKET_API_BASE}/currentMatches", params={"apikey": CRICKET_API_KEY, "offset": 0})
            data = res.json()
            if data.get("status") == "success" and data.get("data"):
                # Just take the first valid match as a test and grab teams
                m = next((x for x in data["data"] if len(x.get("teams", [])) == 2), None)
                if not m:
                    return HTMLResponse(f"<span>No valid matches found on API</span>")
                
                # Automatically insert teams if not exist, then contest
                t1_name = m["teams"][0]
                t2_name = m["teams"][1]
                t1_abbr = t1_name[:3].upper()
                t2_abbr = t2_name[:3].upper()
                
                t1_id = await db.fetchval("INSERT INTO teams (name, abbreviation) VALUES ($1, $2) ON CONFLICT (name) DO UPDATE SET name=EXCLUDED.name RETURNING id", t1_name, t1_abbr)
                if not t1_id:
                     t1_id = await db.fetchval("SELECT id FROM teams WHERE name=$1", t1_name)
                     
                t2_id = await db.fetchval("INSERT INTO teams (name, abbreviation) VALUES ($1, $2) ON CONFLICT (name) DO UPDATE SET name=EXCLUDED.name RETURNING id", t2_name, t2_abbr)
                if not t2_id:
                     t2_id = await db.fetchval("SELECT id FROM teams WHERE name=$1", t2_name)
                     
                # Insert Contest
                c_id = await db.fetchval("""
                    INSERT INTO contests (name, match_api_id, team1_id, team2_id, match_date, venue, status)
                    VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id
                """, m["name"], m["id"], t1_id, t2_id, m["date"], m["venue"], m["status"])
                
                # Fetch dummy players? Left out for brevity.
                return HTMLResponse(f"""<div id="toast-container" hx-swap-oob="true">
                    <div class="fixed top-20 left-1/2 -translate-x-1/2 z-[999] bg-emerald-50 text-emerald-600 rounded-2xl px-5 py-3 border text-xs">
                        Contest Added: {t1_abbr} vs {t2_abbr}
                    </div>
                </div>
                <script>setTimeout(() => document.getElementById('toast-container').innerHTML='', 2500); htmx.ajax('GET', '/web/home_view', '#main-content');</script>""")
            
    except Exception as e:
        return HTMLResponse(f"<span>Error: {str(e)}</span>")
    return HTMLResponse("Failed")


@router.get("/builder", response_class=HTMLResponse)
async def builder_page(request: Request):
    username, user_id = await _get_user_id(request)
    if not user_id: return _auth_redirect(request)
    
    contest_id = _get_active_contest(request)
    if not contest_id:
        return HTMLResponse("<div class='p-8 text-center text-slate-500'>Please select a contest from Home first.</div>")

    contest = await db.fetchrow("SELECT team1_id, team2_id FROM contests WHERE id = $1", contest_id)
    if not contest:
        return HTMLResponse("<div class='p-8 text-center text-slate-500'>Contest not found.</div>")

    players = await db.fetch("""
        SELECT p.id, p.name, p.role, p.credit_value as credits, t.abbreviation as team
        FROM players p JOIN teams t ON p.team_id = t.id
        WHERE p.is_active = TRUE AND (p.team_id = $1 OR p.team_id = $2)
        ORDER BY p.credit_value DESC
    """, contest["team1_id"], contest["team2_id"])

    draft, captain_id, vc_id = await _get_draft_state(user_id, contest_id)
    credits_used = sum(p["credits"] for p in players if p["id"] in draft)

    return templates.TemplateResponse("components/builder.html", {
        "request": request,
        "players": players,
        "draft": draft,
        "captain_id": captain_id,
        "vc_id": vc_id,
        "credits_left": round(BUDGET_LIMIT - credits_used, 1),
        "count": len(draft),
        "toast": ""
    })

@router.post("/toggle/{player_id}", response_class=HTMLResponse)
async def toggle_player(request: Request, player_id: int):
    username, user_id = await _get_user_id(request)
    if not user_id: return _auth_redirect(request)
    
    contest_id = _get_active_contest(request)
    if not contest_id: return HTMLResponse(status_code=400)

    player = await db.fetchrow("""
        SELECT p.id, p.name, p.role, p.credit_value as credits, t.abbreviation as team
        FROM players p JOIN teams t ON p.team_id = t.id WHERE p.id = $1
    """, player_id)
    if not player:
        return HTMLResponse(status_code=404)

    # 2. Get current draft state directly
    draft_rows = await db.fetch("""
        SELECT ud.player_id, p.credit_value 
        FROM user_drafts ud 
        JOIN players p ON ud.player_id = p.id
        WHERE ud.user_id = $1 AND ud.contest_id = $2
    """, user_id, contest_id)
    
    draft = [r["player_id"] for r in draft_rows]
    credits_used = sum(r["credit_value"] for r in draft_rows)
    is_selected = player_id in draft
    toast_html = ""

    # 3. Toggle Logic
    if is_selected:
        await db.execute("DELETE FROM user_drafts WHERE user_id = $1 AND contest_id = $2 AND player_id = $3", user_id, contest_id, player_id)
        draft.remove(player_id)
        credits_used -= player["credits"]
        is_selected = False
    else:
        if len(draft) >= MAX_PLAYERS:
            toast_html = _toast("No space in team")
        elif credits_used + player["credits"] > BUDGET_LIMIT:
            toast_html = _toast("Not Enough Credits")
        else:
            await db.execute("INSERT INTO user_drafts (user_id, contest_id, player_id) VALUES ($1, $2, $3)", user_id, contest_id, player_id)
            draft.append(player_id)
            credits_used += player["credits"]
            is_selected = True

    # 4. Get updated draft C/VC state
    _, captain_id, vc_id = await _get_draft_state(user_id, contest_id)

    return templates.TemplateResponse("components/player_card.html", {
        "request": request,
        "p": player,
        "is_selected": is_selected,
        "captain_id": captain_id,
        "vc_id": vc_id,
        "credits_left": round(BUDGET_LIMIT - credits_used, 1),
        "count": len(draft),
        "toast": toast_html
    })

@router.post("/set_role/{player_id}/{role}", response_class=HTMLResponse)
async def set_captain_vc(request: Request, player_id: int, role: str):
    username, user_id = await _get_user_id(request)
    if not user_id: return _auth_redirect(request)
    
    contest_id = _get_active_contest(request)
    if not contest_id: return HTMLResponse(status_code=400)

    in_draft = await db.fetchrow("SELECT id FROM user_drafts WHERE user_id = $1 AND contest_id = $2 AND player_id = $3", 
                                 user_id, contest_id, player_id)
    if not in_draft:
        return HTMLResponse(status_code=400)

    if role == "C":
        await db.execute("UPDATE user_drafts SET is_captain = FALSE WHERE user_id = $1 AND contest_id = $2", user_id, contest_id)
        await db.execute("UPDATE user_drafts SET is_captain = TRUE, is_vice_captain = FALSE WHERE user_id = $1 AND contest_id = $2 AND player_id = $3", user_id, contest_id, player_id)
    elif role == "VC":
        await db.execute("UPDATE user_drafts SET is_vice_captain = FALSE WHERE user_id = $1 AND contest_id = $2", user_id, contest_id)
        await db.execute("UPDATE user_drafts SET is_vice_captain = TRUE, is_captain = FALSE WHERE user_id = $1 AND contest_id = $2 AND player_id = $3", user_id, contest_id, player_id)

    return await builder_page(request)


@router.post("/save_team", response_class=HTMLResponse)
async def save_team(request: Request):
    username, user_id = await _get_user_id(request)
    if not user_id: return _auth_redirect(request)
    
    contest_id = _get_active_contest(request)
    if not contest_id: return HTMLResponse(status_code=400)

    draft_rows = await db.fetch("SELECT player_id, is_captain, is_vice_captain FROM user_drafts WHERE user_id = $1 AND contest_id = $2", user_id, contest_id)
    if len(draft_rows) != 12:
        return HTMLResponse(f"<div id='save-status' class='bg-red-50 text-red-500 border border-red-100 p-3 mt-4 rounded-2xl text-center text-xs font-medium tracking-wider slide-in'>Select exactly 12 players ({len(draft_rows)}/12)</div>")

    has_c = any(r["is_captain"] for r in draft_rows)
    has_vc = any(r["is_vice_captain"] for r in draft_rows)
    if not has_c or not has_vc:
        return HTMLResponse("<div id='save-status' class='bg-red-50 text-red-500 border border-red-100 p-3 mt-4 rounded-2xl text-center text-xs font-medium tracking-wider slide-in'>Set a Captain and Vice-Captain first</div>")

    existing = await db.fetchrow("SELECT id FROM fantasy_teams WHERE user_id = $1 AND contest_id = $2", user_id, contest_id)
    if existing:
        return HTMLResponse("<div id='save-status' class='bg-amber-50 text-amber-600 border border-amber-100 p-3 mt-4 rounded-2xl text-center text-xs font-medium tracking-wider slide-in'>Roster already locked</div>")

    await db.execute("INSERT INTO fantasy_teams (user_id, contest_id) VALUES ($1, $2)", user_id, contest_id)
    
    # Instantly calculate points if the match is already synced
    contest = await db.fetchrow("SELECT match_api_id FROM contests WHERE id = $1", contest_id)
    if contest and contest["match_api_id"]:
        draft_rows = await db.fetch("""
            SELECT ud.is_captain, ud.is_vice_captain, p.name as player_name
            FROM user_drafts ud JOIN players p ON ud.player_id = p.id
            WHERE ud.user_id = $1 AND ud.contest_id = $2
        """, user_id, contest_id)
        
        total = 0.0
        # O(1) bulk fetch instead of N+1
        perfs = await db.fetch("SELECT player_name, total_points FROM player_match_performances WHERE match_api_id = $1", contest["match_api_id"])
        
        for d in draft_rows:
            d_name = d['player_name'].lower()
            for p in perfs:
                p_name = p['player_name'].lower()
                if d_name in p_name or p_name in d_name:
                    pts = p["total_points"]
                    if d["is_captain"]: pts *= 2.0
                    elif d["is_vice_captain"]: pts *= 1.5
                    total += pts
                    break
                
        await db.execute("UPDATE fantasy_teams SET total_points = $1 WHERE user_id = $2 AND contest_id = $3", total, user_id, contest_id)

    return HTMLResponse("<div id='save-status' class='bg-emerald-50 text-emerald-600 border border-emerald-100 p-3 mt-4 rounded-2xl text-center text-xs font-medium tracking-wider slide-in'>✓ Roster locked successfully</div>")


@router.get("/leaderboard_view", response_class=HTMLResponse)
async def leaderboard_view(request: Request):
    username = _get_username(request)
    if not username: return _auth_redirect(request)
    
    contest_id = _get_active_contest(request)
    if not contest_id:
        return HTMLResponse("<div class='p-8 text-center text-slate-500'>Please select a contest from Home first.</div>")

    teams = await db.fetch("""
        SELECT u.username, ft.total_points,
            (SELECT COUNT(*) FROM user_drafts ud WHERE ud.user_id = u.id AND ud.contest_id = $1) as player_count
        FROM fantasy_teams ft JOIN users u ON ft.user_id = u.id
        WHERE ft.contest_id = $1
        ORDER BY ft.total_points DESC
    """, contest_id)

    return templates.TemplateResponse("components/leaderboard.html", {
        "request": request, "teams": teams, "username": username
    })
