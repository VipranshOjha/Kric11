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


# ─────────────────────────────────────────────────────────
#  Task 1 — Advanced Stat Simulation
# ─────────────────────────────────────────────────────────

def _simulate_batting_event(perf):
    """Simulate a single delivery faced by a batter / AR / WK."""
    perf.balls_faced += 1
    outcome = random.choices(
        [0, 1, 2, 3, 4, 6],
        weights=[30, 30, 15, 5, 12, 8],  # realistic T20 distribution
        k=1
    )[0]
    perf.runs_scored += outcome
    if outcome == 4:
        perf.fours += 1
    elif outcome == 6:
        perf.sixes += 1


def _simulate_bowling_event(perf):
    """Simulate a single delivery bowled."""
    # Wicket probability ~5%
    if random.random() < 0.05:
        perf.wickets += 1
    # Runs conceded per ball (weighted toward economy)
    conceded = random.choices(
        [0, 1, 2, 4, 6],
        weights=[25, 30, 20, 15, 10],
        k=1
    )[0]
    perf.runs_conceded += conceded
    # Increment overs simply (each call = 1 ball ≈ 1/6 of an over)
    perf.overs_bowled = round(perf.overs_bowled + 0.17, 2)
    # Maiden check: ~5% chance per call
    if conceded == 0 and random.random() < 0.05:
        perf.maidens += 1


def _simulate_fielding_event(perf):
    """10% chance to record a fielding contribution on any delivery."""
    if random.random() < 0.10:
        event = random.choices(
            ["catch", "stumping", "run_out"],
            weights=[60, 20, 20],
            k=1
        )[0]
        if event == "catch":
            perf.catches += 1
        elif event == "stumping":
            perf.stumpings += 1
        else:
            perf.run_outs += 1


# ─────────────────────────────────────────────────────────
#  Task 2 — Professional IPL Point Calculation
# ─────────────────────────────────────────────────────────

def calculate_player_points(perf, role: PlayerRole) -> float:
    """
    IPL 2026 Fantasy Point Rules:
    
    Batting:  +1/run, +1/four, +2/six
              +8 bonus at 50+ runs, +16 bonus at 100+ runs
              -2 penalty for duck (0 runs, non-bowler only)
    Bowling:  +25/wicket, +12/maiden
              +4 bonus (3W), +8 bonus (4W), +16 bonus (5W+)
    Fielding: +8/catch, +12/stumping, +12/run-out
    """
    pts = 0.0

    # ── Batting ──
    pts += perf.runs_scored * 1.0      # 1 pt per run
    pts += perf.fours * 1.0            # +1 per four
    pts += perf.sixes * 2.0            # +2 per six

    # Milestones
    if perf.runs_scored >= 100:
        pts += 16.0                    # Century bonus
    elif perf.runs_scored >= 50:
        pts += 8.0                     # Half-century bonus

    # Duck penalty (not applied to pure bowlers)
    if perf.runs_scored == 0 and perf.balls_faced > 0 and role != PlayerRole.BOWL:
        pts -= 2.0

    # ── Bowling ──
    pts += perf.wickets * 25.0         # 25 pts per wicket
    pts += perf.maidens * 12.0         # 12 pts per maiden

    # Wicket haul bonuses
    if perf.wickets >= 5:
        pts += 16.0                    # 5-wicket haul
    elif perf.wickets >= 4:
        pts += 8.0                     # 4-wicket haul
    elif perf.wickets >= 3:
        pts += 4.0                     # 3-wicket haul

    # ── Fielding ──
    pts += perf.catches * 8.0          # 8 pts per catch
    pts += perf.stumpings * 12.0       # 12 pts per stumping
    pts += perf.run_outs * 12.0        # 12 pts per run-out

    return pts


# ─────────────────────────────────────────────────────────
#  Cron Endpoint
# ─────────────────────────────────────────────────────────

@router.get("/sync")
async def sync_live_scores(authorization: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)):
    """
    Called by Vercel Cron every 1 minute during a live match.
    1. Simulates ball-by-ball stat progression for each player.
    2. Calculates individual fantasy points using IPL 2026 rules.
    3. Aggregates team totals with Captain (2x) and Vice-Captain (1.5x) multipliers.
    """

    # Auth guard for production
    if os.getenv("VERCEL_URL") and authorization != f"Bearer {CRON_SECRET}":
        return {"status": "unauthorized"}

    match_id = 1

    # Fetch all active players
    players_res = await db.execute(select(Player).where(Player.is_active == True))
    players = players_res.scalars().all()

    # Fetch existing performance records
    perfs_res = await db.execute(
        select(PlayerMatchPerformance).where(PlayerMatchPerformance.match_id == match_id)
    )
    perfs = {p.player_id: p for p in perfs_res.scalars().all()}

    # ── Phase 1: Simulate a "delivery" for each player ──
    for player in players:
        perf = perfs.get(player.id)
        if not perf:
            perf = PlayerMatchPerformance(
                match_id=match_id,
                player_id=player.id,
                runs_scored=0, balls_faced=0, fours=0, sixes=0,
                wickets=0, runs_conceded=0, overs_bowled=0.0, maidens=0,
                catches=0, stumpings=0, run_outs=0, total_points=0.0
            )
            db.add(perf)
            perfs[player.id] = perf

        # ~60% chance an event occurs this tick (simulates match pace)
        if random.random() > 0.4:
            # Batting simulation: BAT, AR, WK face deliveries
            if player.role in (PlayerRole.BAT, PlayerRole.AR, PlayerRole.WK):
                _simulate_batting_event(perf)

            # Bowling simulation: BOWL, AR bowl deliveries
            if player.role in (PlayerRole.BOWL, PlayerRole.AR):
                _simulate_bowling_event(perf)

            # Fielding simulation: any player can contribute
            _simulate_fielding_event(perf)

        # ── Phase 2: Recalculate individual fantasy points ──
        perf.total_points = calculate_player_points(perf, player.role)

    await db.commit()

    # Build points lookup
    pts_map = {pid: perf.total_points for pid, perf in perfs.items()}

    # ── Phase 3: Aggregate team totals with C / VC multipliers ──
    teams_res = await db.execute(
        select(FantasyTeam)
        .options(selectinload(FantasyTeam.players))
        .where(FantasyTeam.match_id == match_id)
    )
    teams = teams_res.scalars().all()

    for team in teams:
        team_pts = 0.0
        for tp in team.players:
            base = pts_map.get(tp.player_id, 0.0)
            if tp.is_captain:
                base *= 2.0           # Captain gets 2x
            elif tp.is_vice_captain:
                base *= 1.5           # Vice-Captain gets 1.5x
            team_pts += base
        team.total_points = round(team_pts, 1)

    await db.commit()

    return {
        "status": "success",
        "players_scored": len(perfs),
        "teams_updated": len(teams),
        "message": f"IPL 2026 scores synced for {len(teams)} rosters."
    }
