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

def auth_redirect(request: Request):
    if "hx-request" in request.headers:
        response = HTMLResponse()
        response.headers["HX-Redirect"] = "/web/login"
        return response
    return RedirectResponse(url="/web/login", status_code=303)

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
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/home_view", response_class=HTMLResponse)
async def home_view(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user: return auth_redirect(request)
    
    html = f"""
    <div class='fade-in mt-6 p-6 flex flex-col items-center justify-center space-y-4'>
        <div class="h-20 w-20 rounded-full bg-slate-800 border-4 border-slate-700 flex items-center justify-center shadow-lg mb-2">
            <svg class="h-8 w-8 text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
        </div>
        <h2 class='text-2xl font-black text-white tracking-wide uppercase'>WELCOME {user.username}</h2>
        <div class="w-full max-w-sm mt-8 p-5 bg-gradient-to-br from-indigo-900 to-slate-800 rounded-2xl shadow-xl border border-indigo-500/30">
            <div class="flex justify-between items-center bg-slate-900/50 p-3 rounded-xl shadow-inner">
                <span class="text-rose-500 font-bold tracking-wider">RCB</span>
                <span class="text-[10px] text-slate-500 font-black tracking-widest uppercase bg-slate-800 px-2 py-1 rounded">MATCH 1</span>
                <span class="text-orange-500 font-bold tracking-wider">SRH</span>
            </div>
            <p class="text-center text-xs text-indigo-300 mt-4 font-bold tracking-widest uppercase">March 28, 7:30 PM IST</p>
        </div>
        <div class="pt-8">
            <button hx-get="/web/logout" class="text-slate-500 text-xs font-bold tracking-widest uppercase hover:text-slate-400">Logout Session</button>
        </div>
    </div>
    """
    return HTMLResponse(html)

@router.get("/builder", response_class=HTMLResponse)
async def builder_page(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user: return auth_redirect(request)
        
    players_res = await db.execute(select(Player).options(selectinload(Player.team)).where(Player.is_active == True))
    players = players_res.scalars().all()
    ui_players = [{"id": p.id, "name": p.name, "role": p.role, "team": p.team.abbreviation, "credits": p.credit_value} for p in players]
    
    draft = user_drafts.setdefault(user.id, [])
    credits_used = sum(p.credit_value for p in players if p.id in draft)
    
    return templates.TemplateResponse("components/builder.html", {
        "request": request,
        "players": ui_players,
        "draft": draft,
        "credits_left": 100.0 - credits_used,
        "count": len(draft)
    })

@router.post("/toggle/{player_id}", response_class=HTMLResponse)
async def toggle_player(request: Request, player_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user: return auth_redirect(request)
        
    draft = user_drafts.setdefault(user.id, [])
    if player_id in draft:
        draft.remove(player_id)
    else:
        if len(draft) < 12: draft.append(player_id)
            
    players_res = await db.execute(select(Player).options(selectinload(Player.team)))
    all_players = players_res.scalars().all()
    
    credits_used = sum(p.credit_value for p in all_players if p.id in draft)
    
    db_player = next((p for p in all_players if p.id == player_id), None)
    ui_player = {"id": db_player.id, "name": db_player.name, "role": db_player.role, "team": db_player.team.abbreviation, "credits": db_player.credit_value}
    
    return templates.TemplateResponse("components/player_card.html", {
        "request": request,
        "p": ui_player,
        "is_selected": player_id in draft,
        "credits_left": 100.0 - credits_used,
        "count": len(draft)
    })

@router.post("/save_team", response_class=HTMLResponse)
async def save_team(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user: return auth_redirect(request)
        
    draft = user_drafts.get(user.id, [])
    if len(draft) != 12:
        return HTMLResponse("<div class='p-3 mt-4 bg-rose-500/20 text-rose-400 border border-rose-500/50 rounded-xl text-center text-xs tracking-widest uppercase font-bold fade-in'>Select exactly 12 players!</div>")
        
    existing = await db.execute(select(FantasyTeam).where((FantasyTeam.user_id == user.id) & (FantasyTeam.match_id == 1)))
    if existing.scalars().first():
        return HTMLResponse("<div class='p-3 mt-4 bg-orange-500/20 text-orange-400 border border-orange-500/50 rounded-xl text-center text-xs tracking-widest uppercase font-bold fade-in'>Roster Already Locked for Match 1!</div>")
        
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
    
    return HTMLResponse("<div class='p-3 mt-4 bg-emerald-500/20 text-emerald-400 border border-emerald-500/50 rounded-xl text-center text-xs tracking-widest uppercase font-bold shadow-[0_0_15px_rgba(16,185,129,0.2)] fade-in'>✅ Roster Secured Successfully!</div>")

@router.get("/leaderboard_view", response_class=HTMLResponse)
async def leaderboard_view(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user_from_cookie(request, db)
    if not user: return auth_redirect(request)
        
    teams_res = await db.execute(select(FantasyTeam).options(selectinload(FantasyTeam.user)).where(FantasyTeam.match_id == 1).order_by(FantasyTeam.total_points.desc()))
    teams = teams_res.scalars().all()
    
    html = "<div class='fade-in mt-6 space-y-4 px-2'>"
    html += "<h2 class='text-2xl font-black text-white tracking-wide uppercase text-center mb-6'>LEADERBOARD</h2>"
    
    if not teams:
        html += "<p class='text-center text-slate-400 text-sm font-bold tracking-widest uppercase'>No rosters locked in yet.</p>"
    
    for i, t in enumerate(teams):
        rank = i + 1
        color = "text-amber-400" if rank == 1 else "text-slate-300" if rank == 2 else "text-amber-600" if rank == 3 else "text-slate-500"
        bg = "bg-gradient-to-r from-amber-500/20 to-slate-800 border-l-4 border-amber-500" if rank == 1 else "bg-slate-800 border-l-4 border-transparent"
        
        html += f"""
        <div class="flex items-center justify-between p-4 rounded-2xl {bg} shadow-lg shadow-slate-900/50">
            <div class="flex items-center space-x-4">
                <div class="{color} font-black text-xl w-6 text-center">{rank}</div>
                <div class="h-10 w-10 bg-slate-700 rounded-full flex items-center justify-center font-bold text-white shadow-inner">{t.user.username[0].upper()}</div>
                <div>
                    <h3 class="font-bold text-white tracking-wide">{t.user.username}</h3>
                    <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Team {t.id}</p>
                </div>
            </div>
            <div class="text-right">
                <h3 class="font-black text-sky-400 text-xl">{t.total_points}</h3>
                <p class="text-[9px] text-slate-500 font-bold uppercase tracking-widest mt-0.5">PTS</p>
            </div>
        </div>
        """
    html += "</div>"
    return HTMLResponse(html)
