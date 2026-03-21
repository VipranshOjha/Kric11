from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Match, Player, FantasyTeam, FantasyTeamPlayer, MatchStatus, Team
from app.schemas import FantasyTeamCreate
from app.auth import get_current_user, User

router = APIRouter(prefix="/fantasy", tags=["Fantasy Operations"])

@router.get("/matches")
async def get_matches(db: AsyncSession = Depends(get_db)):
    """Compact JSON for Mobile UI: Shows upcoming matches."""
    result = await db.execute(
        select(Match)
        .options(selectinload(Match.home_team), selectinload(Match.away_team))
        .where(Match.status == MatchStatus.UPCOMING)
    )
    matches = result.scalars().all()
    
    # Optimized mobile response
    return [{
        "id": m.id,
        "title": f"{m.home_team.abbreviation} vs {m.away_team.abbreviation}",
        "home": m.home_team.name,
        "away": m.away_team.name,
        "starts_at": m.start_time.isoformat()
    } for m in matches]

@router.get("/matches/{match_id}/players")
async def get_match_players(match_id: int, db: AsyncSession = Depends(get_db)):
    """Fetches all valid players for both teams participating in the match."""
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalars().first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    players_res = await db.execute(
        select(Player)
        .options(selectinload(Player.team))
        .where(Player.team_id.in_([match.home_team_id, match.away_team_id]))
        .where(Player.is_active == True)
    )
    players = players_res.scalars().all()
    
    # Compact response for mobile roster builder
    return [{
        "id": p.id,
        "name": p.name,
        "team": p.team.abbreviation,
        "role": p.role,
        "credits": p.credit_value
    } for p in players]

@router.post("/teams")
async def create_fantasy_team(
    team_data: FantasyTeamCreate, 
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    """Save user's roster to database."""
    # Check if match exists and is upcoming
    match_res = await db.execute(select(Match).where(Match.id == team_data.match_id))
    match = match_res.scalars().first()
    
    if not match or match.status != MatchStatus.UPCOMING:
        raise HTTPException(status_code=400, detail="Match not available for team creation")

    # Check if user already has a team for this match
    existing_team_res = await db.execute(
        select(FantasyTeam).where(
            (FantasyTeam.user_id == user.id) & 
            (FantasyTeam.match_id == team_data.match_id)
        )
    )
    if existing_team_res.scalars().first():
        raise HTTPException(status_code=400, detail="You have already created a team for this match.")

    # Convert Pydantic model to SQLAlchemy models
    new_team = FantasyTeam(user_id=user.id, match_id=team_data.match_id)
    db.add(new_team)
    await db.flush() # Get team ID early

    team_players = []
    for p in team_data.players:
        assoc = FantasyTeamPlayer(
            fantasy_team_id=new_team.id,
            player_id=p.player_id,
            is_captain=p.is_captain,
            is_vice_captain=p.is_vice_captain,
            is_impact_player=p.is_impact_player
        )
        team_players.append(assoc)
    
    db.add_all(team_players)
    await db.commit()
    
    return {"status": "success", "team_id": new_team.id, "message": "Fantasy team created successfully!"}
