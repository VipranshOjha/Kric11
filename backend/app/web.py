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

async def _is_match_locked(contest_id: int) -> bool:
    if not contest_id: return False
    start_time = await db.fetchval("SELECT start_time FROM contests WHERE id = $1", contest_id)
    if start_time and datetime.now(timezone.utc) >= start_time:
        return True
    return False

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
                    INSERT INTO contests (name, match_api_id, team1_id, team2_id, match_date, venue, status, start_time)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING id
                """, m["name"], m["id"], t1_id, t2_id, m.get("date", ""), m.get("venue", ""), m.get("status", ""), datetime.now(timezone.utc) + timedelta(minutes=10))
                
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
    
    match_started = await _is_match_locked(contest_id)
    roster_locked = await db.fetchval("SELECT id FROM fantasy_teams WHERE user_id = $1 AND contest_id = $2", user_id, contest_id)

    return templates.TemplateResponse("components/builder.html", {
        "request": request,
        "players": players,
        "draft": draft,
        "captain_id": captain_id,
        "vc_id": vc_id,
        "credits_left": round(BUDGET_LIMIT - credits_used, 1),
        "count": len(draft),
        "toast": "",
        "match_started": match_started,
        "roster_locked": bool(roster_locked)
    })

@router.post("/toggle/{player_id}", response_class=HTMLResponse)
async def toggle_player(request: Request, player_id: int):
    username, user_id = await _get_user_id(request)
    if not user_id: return _auth_redirect(request)
    
    contest_id = _get_active_contest(request)
    if not contest_id: return HTMLResponse(status_code=400)
    
    if await _is_match_locked(contest_id):
        return HTMLResponse(_toast("Match has already started. Edits disabled.", "error"))

    roster_locked = await db.fetchval("SELECT id FROM fantasy_teams WHERE user_id = $1 AND contest_id = $2", user_id, contest_id)
    if roster_locked:
        return HTMLResponse(_toast("Roster is already locked.", "error"))

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
        "toast": toast_html,
        "match_started": False,
        "roster_locked": False
    })

@router.post("/set_role/{player_id}/{role}", response_class=HTMLResponse)
async def set_captain_vc(request: Request, player_id: int, role: str):
    username, user_id = await _get_user_id(request)
    if not user_id: return _auth_redirect(request)
    
    contest_id = _get_active_contest(request)
    if not contest_id: return HTMLResponse(status_code=400)

    if await _is_match_locked(contest_id):
        return HTMLResponse(_toast("Match has already started. Edits disabled.", "error"))
        
    roster_locked = await db.fetchval("SELECT id FROM fantasy_teams WHERE user_id = $1 AND contest_id = $2", user_id, contest_id)
    if roster_locked:
        return HTMLResponse(_toast("Roster is already locked.", "error"))

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


@router.post("/confirm_team", response_class=HTMLResponse)
async def confirm_team(request: Request):
    username, user_id = await _get_user_id(request)
    if not user_id: return _auth_redirect(request)
    
    contest_id = _get_active_contest(request)
    if not contest_id: return HTMLResponse(status_code=400)

    if await _is_match_locked(contest_id):
        return HTMLResponse(_toast("Match has already started. Edits disabled.", "error"))

    draft_rows = await db.fetch("""
        SELECT ud.is_captain, ud.is_vice_captain, p.name as player_name, p.role
        FROM user_drafts ud JOIN players p ON ud.player_id = p.id
        WHERE ud.user_id = $1 AND ud.contest_id = $2
    """, user_id, contest_id)
    
    if len(draft_rows) != 12:
        return HTMLResponse(_toast(f"Select exactly 12 players ({len(draft_rows)}/12)", "error"))

    c_player = next((p for p in draft_rows if p["is_captain"]), None)
    vc_player = next((p for p in draft_rows if p["is_vice_captain"]), None)
    
    if not c_player or not vc_player:
        return HTMLResponse(_toast("Set a Captain and Vice-Captain first", "error"))

    existing = await db.fetchrow("SELECT id FROM fantasy_teams WHERE user_id = $1 AND contest_id = $2", user_id, contest_id)
    if existing:
        return HTMLResponse(_toast("Roster already locked", "error"))

    # Fetch Contest Teams for the Prediction Radio Input
    contest = await db.fetchrow("""
        SELECT t1.id as t1_id, t1.abbreviation as t1_abbr, 
               t2.id as t2_id, t2.abbreviation as t2_abbr
        FROM contests c 
        JOIN teams t1 ON c.team1_id = t1.id 
        JOIN teams t2 ON c.team2_id = t2.id 
        WHERE c.id = $1
    """, contest_id)

    return templates.TemplateResponse("components/confirm_modal.html", {
        "request": request,
        "players": draft_rows,
        "c_player": c_player,
        "vc_player": vc_player,
        "contest": contest
    })


@router.post("/save_team", response_class=HTMLResponse)
async def save_team(request: Request, predicted_winner: int = Form(...)):
    username, user_id = await _get_user_id(request)
    if not user_id: return _auth_redirect(request)
    
    contest_id = _get_active_contest(request)
    if not contest_id: return HTMLResponse(status_code=400)

    if await _is_match_locked(contest_id):
        return HTMLResponse(_toast("Match has already started. Edits disabled.", "error"))

    draft_rows = await db.fetch("SELECT player_id, is_captain, is_vice_captain FROM user_drafts WHERE user_id = $1 AND contest_id = $2", user_id, contest_id)
    if len(draft_rows) != 12:
        return HTMLResponse(_toast(f"Select exactly 12 players ({len(draft_rows)}/12)", "error"))

    has_c = any(r["is_captain"] for r in draft_rows)
    has_vc = any(r["is_vice_captain"] for r in draft_rows)
    if not has_c or not has_vc:
        return HTMLResponse(_toast("Set a Captain and Vice-Captain first", "error"))

    existing = await db.fetchrow("SELECT id FROM fantasy_teams WHERE user_id = $1 AND contest_id = $2", user_id, contest_id)
    if existing:
        # If it already exists, gracefully ignore or output toast
        return HTMLResponse(_toast("Roster already locked", "error"))

    await db.execute("INSERT INTO fantasy_teams (user_id, contest_id, predicted_winner_id) VALUES ($1, $2, $3)", user_id, contest_id, predicted_winner)
    
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

    # Return the entire builder page to reflect the locked state
    # Wait, the frontend might just replace the modal/button, let's trigger an htmx redirect or refresh
    return HTMLResponse("""
        <div id="toast-container" hx-swap-oob="true">
            <div class="fixed top-20 left-1/2 -translate-x-1/2 z-[999] max-w-xs w-full px-5 py-3 rounded-2xl
                bg-emerald-50 text-emerald-600 border border-emerald-100 text-xs font-medium tracking-wider text-center shadow-sm slide-in">
                ✓ Roster locked successfully
            </div>
        </div>
        <script>
            setTimeout(() => document.getElementById('toast-container').innerHTML='', 2500);
            htmx.ajax('GET', '/web/builder', '#main-content');
        </script>
    """)

from app.cron import _fetch_scorecard, _parse_and_store, _update_leaderboard

@router.post("/force_sync", response_class=HTMLResponse)
async def force_sync(request: Request):
    """Manual trigger to sync latest score for UI button bypassing chronological checks"""
    username = _get_username(request)
    if not username: return HTMLResponse(_toast("Unauthorized", "error"))
    
    contest_id = _get_active_contest(request)
    if not contest_id: return HTMLResponse(_toast("No active contest selected", "error"))
    
    contest = await db.fetchrow("SELECT id, match_api_id, status FROM contests WHERE id = $1", contest_id)
    if not contest or not contest["match_api_id"]:
        return HTMLResponse(_toast("Match API ID not linked. Wait for live start.", "error"))
        
    try:
        score_data = await _fetch_scorecard(contest["match_api_id"])
        if score_data and score_data.get("scorecard"):
            await _parse_and_store(score_data)
            await _update_leaderboard(contest["match_api_id"])
            return HTMLResponse(_toast("Successfully manually updated live stats!"))
        return HTMLResponse(_toast("Failed to retrieve live stats right now.", "error"))
    except Exception as e:
        return HTMLResponse(_toast(f"Sync error: {str(e)}", "error"))


@router.get("/leaderboard_view", response_class=HTMLResponse)
async def leaderboard_view(request: Request):
    username = _get_username(request)
    if not username: return _auth_redirect(request)
    
    contest_id = _get_active_contest(request)
    if not contest_id:
        return HTMLResponse("<div class='p-8 text-center text-slate-500'>Please select a contest from Home first.</div>")

    teams = await db.fetch("""
        SELECT u.id as user_id, u.username, ft.total_points,
            (SELECT COUNT(*) FROM user_drafts ud WHERE ud.user_id = u.id AND ud.contest_id = $1) as detail_count
        FROM fantasy_teams ft JOIN users u ON ft.user_id = u.id
        WHERE ft.contest_id = $1
        ORDER BY ft.total_points DESC
    """, contest_id)

    return templates.TemplateResponse("components/leaderboard.html", {
        "request": request, "teams": teams, "username": username, "is_global": False, "contest_id": contest_id
    })


@router.get("/global_leaderboard_view", response_class=HTMLResponse)
async def global_leaderboard_view(request: Request):
    username = _get_username(request)
    if not username: return _auth_redirect(request)
    
    # Aggregate tournament points based on rank per match + prediction bonus
    teams = await db.fetch("""
        WITH MatchRanks AS (
            SELECT 
                ft.user_id, 
                ft.contest_id,
                ft.predicted_winner_id,
                c.actual_winner_id,
                RANK() OVER(PARTITION BY ft.contest_id ORDER BY ft.total_points DESC) as rnk
            FROM fantasy_teams ft
            JOIN contests c ON ft.contest_id = c.id
            WHERE ft.total_points > 0
        ),
        TournamentPoints AS (
            SELECT 
                user_id,
                GREATEST(11 - rnk, 0) + 
                (CASE WHEN predicted_winner_id = actual_winner_id AND actual_winner_id IS NOT NULL THEN 2 ELSE 0 END) as tourney_pts
            FROM MatchRanks
        )
        SELECT 
            u.username, 
            COALESCE(SUM(tp.tourney_pts), 0) as total_points, 
            COUNT(tp.user_id) as detail_count
        FROM users u
        LEFT JOIN TournamentPoints tp ON u.id = tp.user_id
        GROUP BY u.id, u.username
        ORDER BY total_points DESC, detail_count DESC
    """)

    return templates.TemplateResponse("components/leaderboard.html", {
        "request": request, "teams": teams, "username": username, "is_global": True
    })

@router.get("/players", response_class=HTMLResponse)
async def players_hub(request: Request):
    username = _get_username(request)
    if not username: return _auth_redirect(request)

    # Note: Using COALESCE on numeric aggregations for safety
    stats = await db.fetch("""
        SELECT player_name, 
               COUNT(DISTINCT match_api_id) as matches_played,
               COALESCE(SUM(runs), 0) as total_runs,
               COALESCE(SUM(wickets), 0) as total_wickets,
               COALESCE(SUM(sixes), 0) as total_sixes,
               COALESCE(SUM(total_points), 0.0) as total_points
        FROM player_match_performances
        GROUP BY player_name
        ORDER BY total_points DESC
    """)

    players = [dict(r) for r in stats]
    orange_cap = max(players, key=lambda x: x["total_runs"]) if players else None
    purple_cap = max(players, key=lambda x: x["total_wickets"]) if players else None
    max_sixes = max(players, key=lambda x: x["total_sixes"]) if players else None

    return templates.TemplateResponse("components/players.html", {
        "request": request,
        "players": players,
        "orange_cap": orange_cap,
        "purple_cap": purple_cap,
        "max_sixes": max_sixes
    })

@router.get("/team/{contest_id}/user/{target_user_id}", response_class=HTMLResponse)
async def view_opponent_team(request: Request, contest_id: int, target_user_id: int):
    username, user_id = await _get_user_id(request)
    if not user_id: return _auth_redirect(request)
    
    # Privacy Check: Current user must have locked their own team
    self_locked = await db.fetchrow("SELECT id FROM fantasy_teams WHERE user_id = $1 AND contest_id = $2", user_id, contest_id)
    if not self_locked:
        return HTMLResponse(_toast("You must lock in your own team before viewing others!", "error"), status_code=403)
        
    opponent_username = await db.fetchval("SELECT username FROM users WHERE id = $1", target_user_id)
    
    # Fetch target user's team
    players = await db.fetch("""
        SELECT p.name, p.role, ud.is_captain, ud.is_vice_captain, t.abbreviation as team
        FROM user_drafts ud 
        JOIN players p ON ud.player_id = p.id
        JOIN teams t ON p.team_id = t.id
        WHERE ud.user_id = $1 AND ud.contest_id = $2
        ORDER BY p.role, p.name
    """, target_user_id, contest_id)
    
    if not players:
        return HTMLResponse(_toast("This user hasn't locked a team yet.", "info"))
        
    return templates.TemplateResponse("components/opponent_modal.html", {
        "request": request,
        "players": players,
        "opponent_username": opponent_username
    })
