from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import User, Match, Player, FantasyTeam, FantasyTeamPlayer
from app.auth import get_current_user_from_cookie, verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/web", tags=["Frontend"])
templates = Jinja2Templates(directory="app/templates")

user_drafts = {}

BUDGET_LIMIT = 100.0
MAX_PLAYERS = 12

def auth_redirect(request: Request):
    if "hx-request" in request.headers:
        response = HTMLResponse()
        response.headers["HX-Redirect"] = "/web/login"
        return response
    return RedirectResponse(url="/web/login", status_code=303)

def _make_toast(msg: str, style: str = "warning"):
    """Generate an OOB toast notification that auto-dismisses — Nordic flat style."""
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
        setTimeout(function() {{ var tc = document.getElementById('toast-container'); if(tc) tc.innerHTML = ''; }}, 2500);
    </script>
    """

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, register: bool = False):
    return templates.TemplateResponse("login.html", {"request": request, "error": None, "is_register": register})

@router.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, username: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).where(User.username == username))
    user = res.scalars().first()
    
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password.", "is_register": False})
        
    access_token = create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/web", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@router.post("/register", response_class=HTMLResponse)
async def register_post(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).where((User.email == email) | (User.username == username)))
    if res.scalars().first():
        return templates.TemplateResponse("login.html", {"request": request, "error": "User already exists.", "is_register": True})

    hashed_pw = get_password_hash(password)
    new_user = User(username=username, email=email, hashed_password=hashed_pw)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.username})
    response = RedirectResponse(url="/web", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/web/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response

@router.get("/", response_class=HTMLResponse)
async def shell(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/web/login", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request, "username": user.username})

@router.get("/home_view", response_class=HTMLResponse)
async def home_view(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user: return auth_redirect(request)
    return templates.TemplateResponse("components/home.html", {"request": request, "username": user.username})

@router.get("/builder", response_class=HTMLResponse)
async def builder_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user: return auth_redirect(request)
        
    players_res = await db.execute(select(Player).options(selectinload(Player.team)).where(Player.is_active == True).order_by(Player.credit_value.desc()))
    players = players_res.scalars().all()
    ui_players = [{"id": p.id, "name": p.name, "role": p.role.value if hasattr(p.role, 'value') else p.role, "team": p.team.abbreviation, "credits": p.credit_value} for p in players]
    
    draft = user_drafts.setdefault(user.id, [])
    credits_used = sum(p.credit_value for p in players if p.id in draft)
    
    return templates.TemplateResponse("components/builder.html", {
        "request": request,
        "players": ui_players,
        "draft": draft,
        "credits_left": round(BUDGET_LIMIT - credits_used, 1),
        "count": len(draft),
        "toast": ""
    })

@router.post("/toggle/{player_id}", response_class=HTMLResponse)
async def toggle_player(request: Request, player_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user: return auth_redirect(request)
        
    draft = user_drafts.setdefault(user.id, [])
    
    players_res = await db.execute(select(Player).options(selectinload(Player.team)))
    all_players = players_res.scalars().all()
    
    db_player = next((p for p in all_players if p.id == player_id), None)
    if not db_player:
        return HTMLResponse(status_code=404)
    
    toast_html = ""
    
    if player_id in draft:
        # ── DESELECT ──
        draft.remove(player_id)
    else:
        # ── STRICT BUDGET ENFORCEMENT ──
        if len(draft) >= MAX_PLAYERS:
            toast_html = _make_toast("⛔ SQUAD FULL — 12/12 SELECTED")
        else:
            current_credits = sum(p.credit_value for p in all_players if p.id in draft)
            if current_credits + db_player.credit_value > BUDGET_LIMIT:
                remaining = round(BUDGET_LIMIT - current_credits, 1)
                toast_html = _make_toast(f"💰 BUDGET EXCEEDED — {remaining} CR LEFT")
            else:
                draft.append(player_id)

    credits_used = sum(p.credit_value for p in all_players if p.id in draft)
    ui_player = {"id": db_player.id, "name": db_player.name, "role": db_player.role.value if hasattr(db_player.role, 'value') else db_player.role, "team": db_player.team.abbreviation, "credits": db_player.credit_value}
    
    resp = templates.TemplateResponse("components/player_card.html", {
        "request": request,
        "p": ui_player,
        "is_selected": player_id in draft,
        "credits_left": round(BUDGET_LIMIT - credits_used, 1),
        "count": len(draft),
        "toast": toast_html
    })
    return resp

@router.post("/save_team", response_class=HTMLResponse)
async def save_team(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user: return auth_redirect(request)
        
    draft = user_drafts.get(user.id, [])
    if len(draft) != 12:
        return HTMLResponse(f"""<div id="save-status" class='glass-card p-3 mt-4 border-rose-500/30 text-rose-400 text-center text-xs tracking-widest uppercase font-bold fade-in'>Select exactly 12 players! ({len(draft)}/12)</div>""")
        
    existing = await db.execute(select(FantasyTeam).where((FantasyTeam.user_id == user.id) & (FantasyTeam.match_id == 1)))
    if existing.scalars().first():
        return HTMLResponse("<div id='save-status' class='glass-card p-3 mt-4 border-amber-500/30 text-amber-400 text-center text-xs tracking-widest uppercase font-bold fade-in'>Roster Already Locked for Match 1!</div>")
        
    new_team = FantasyTeam(user_id=user.id, match_id=1, total_points=0.0)
    db.add(new_team)
    await db.flush()
    
    assocs = []
    for idx, p_id in enumerate(draft):
        assocs.append(FantasyTeamPlayer(
            fantasy_team_id=new_team.id,
            player_id=p_id,
            is_captain=(idx == 0),
            is_vice_captain=(idx == 1),
            is_impact_player=(idx == 11)
        ))
    db.add_all(assocs)
    await db.commit()
    
    return HTMLResponse("""<div id='save-status' class='glass-card p-3 mt-4 border-emerald-500/30 text-emerald-400 text-center text-xs tracking-widest uppercase font-bold shadow-[0_0_20px_rgba(16,185,129,0.15)] fade-in'>✅ ROSTER SECURED!</div>""")

@router.get("/leaderboard_view", response_class=HTMLResponse)
async def leaderboard_view(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user: return auth_redirect(request)
        
    teams_res = await db.execute(select(FantasyTeam).options(selectinload(FantasyTeam.user)).where(FantasyTeam.match_id == 1).order_by(FantasyTeam.total_points.desc()))
    teams = teams_res.scalars().all()
    
    return templates.TemplateResponse("components/leaderboard.html", {
        "request": request,
        "teams": teams,
        "username": user.username
    })
