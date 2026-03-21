from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional
import random
import os

from app.database import get_db
from app.models import Match, Player, PlayerMatchPerformance, FantasyTeam, FantasyTeamPlayer, PlayerRole

CRON_SECRET = os.getenv("CRON_SECRET", "local_cron_secret")

router = APIRouter(prefix="/api/scoring", tags=["Live Scoring Engine"])

@router.get("/sync")
async def sync_live_scores(authorization: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)):
    """
    Called by Vercel Cron every 1 minute.
    Calculates live points for all players dynamically and ranks Fantasy Teams.
    """
    
    # Secure endpoint to Vercel Cron Secret in production
    if os.getenv("VERCEL_URL") and authorization != f"Bearer {CRON_SECRET}":
        return {"status": "unauthorized"}

    match_id = 1
    
    players_res = await db.execute(select(Player).where(Player.is_active == True))
    players = players_res.scalars().all()
    
    perfs_res = await db.execute(select(PlayerMatchPerformance).where(PlayerMatchPerformance.match_id == match_id))
    perfs = {p.player_id: p for p in perfs_res.scalars().all()}
    
    # 1. Simulate Live Ball-By-Ball Scoring progression
    for player in players:
        perf = perfs.get(player.id)
        if not perf:
            perf = PlayerMatchPerformance(match_id=match_id, player_id=player.id)
            db.add(perf)
            perfs[player.id] = perf
            
        if random.random() > 0.4:  # Random event occurs
            if player.role in [PlayerRole.BAT, PlayerRole.AR, PlayerRole.WK]:
                perf.runs_scored += random.choice([0, 1, 2, 4, 6])
            if player.role in [PlayerRole.BOWL, PlayerRole.AR]:
                if random.random() > 0.85:
                    perf.wickets += 1
                    
        # Apply standard Fantasy rules (1pt per run, 25pt per wicket)
        pts = (perf.runs_scored * 1.0) + (perf.wickets * 25.0)
        perf.total_points = pts
        
    await db.commit() # Save progression
    
    pts_map = {p_id: perf.total_points for p_id, perf in perfs.items()}
    
    # 2. Assign scores to user rosters (with C / VC Multipliers)
    teams_res = await db.execute(select(FantasyTeam).options(selectinload(FantasyTeam.players)).where(FantasyTeam.match_id == match_id))
    teams = teams_res.scalars().all()
    
    for team in teams:
        team_pts = 0.0
        for tp in team.players:
            base = pts_map.get(tp.player_id, 0.0)
            if tp.is_captain: base *= 2.0
            elif tp.is_vice_captain: base *= 1.5
            team_pts += base
            
        team.total_points = team_pts
        
    await db.commit()
    return {"status": "success", "message": f"Scores calculated! Updated positions for {len(teams)} rosters."}
