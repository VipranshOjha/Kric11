"""
Kric11 — Live Scoring via CricketData.org API
Fetches real scorecards and calculates IPL 2026 fantasy points.
"""
import os
import httpx
import logging
from fastapi import APIRouter

from app import db

router = APIRouter(prefix="/api/scoring", tags=["Live Scoring"])
log = logging.getLogger("kric11.cron")

CRICKET_API_KEY = os.getenv("CRICKET_DATA_API_KEY", "16c8f2cf-ad1a-4cd7-bb7c-2d0483fca5cd")
CRICKET_API_BASE = "https://api.cricapi.com/v1"


# ── Fantasy Point Rules (IPL 2026) ──

def calculate_fantasy_points(batting, bowling, fielding):
    """Calculate total fantasy points for a player's match performance."""
    pts = 0.0

    # Batting
    runs = batting.get("r", 0)
    fours = batting.get("4s", 0)
    sixes = batting.get("6s", 0)
    balls = batting.get("b", 0)

    pts += runs * 1           # +1 per run
    pts += fours * 1          # +1 bonus per boundary
    pts += sixes * 2          # +2 bonus per six
    if runs >= 100: pts += 16  # Century bonus
    elif runs >= 50: pts += 8  # Half-century bonus
    elif runs >= 30: pts += 4  # 30-run bonus
    if runs == 0 and balls >= 1 and batting.get("dismissed", False):
        pts -= 2               # Duck penalty

    # Strike rate bonus/penalty (min 10 balls)
    if balls >= 10:
        sr = (runs / balls) * 100
        if sr >= 170: pts += 6
        elif sr >= 150: pts += 4
        elif sr >= 130: pts += 2
        elif sr < 50: pts -= 6
        elif sr < 60: pts -= 4
        elif sr < 70: pts -= 2

    # Bowling
    wickets = bowling.get("w", 0)
    maidens = bowling.get("m", 0)
    economy = bowling.get("eco", 0)
    overs = bowling.get("o", 0)

    pts += wickets * 25       # +25 per wicket
    pts += maidens * 12       # +12 per maiden
    if wickets >= 5: pts += 16 # 5-wicket haul bonus
    elif wickets >= 4: pts += 8
    elif wickets >= 3: pts += 4

    # Economy bonus/penalty (min 2 overs)
    if overs >= 2:
        if economy <= 5: pts += 6
        elif economy <= 6: pts += 4
        elif economy <= 7: pts += 2
        elif economy >= 12: pts -= 6
        elif economy >= 11: pts -= 4
        elif economy >= 10: pts -= 2

    # Fielding
    catches = fielding.get("catch", 0)
    stumpings = fielding.get("stumped", 0)
    runouts = fielding.get("runout", 0)

    pts += catches * 8
    pts += stumpings * 12
    pts += runouts * 6
    if catches >= 3: pts += 4  # 3+ catch bonus

    return pts


async def _ensure_perf_table():
    """Create player_match_performances table if it doesn't exist."""
    await db.execute("""
        CREATE TABLE IF NOT EXISTS player_match_performances (
            id SERIAL PRIMARY KEY,
            match_api_id VARCHAR(100) NOT NULL,
            player_name VARCHAR(100) NOT NULL,
            player_api_id VARCHAR(100),
            runs INTEGER DEFAULT 0,
            balls_faced INTEGER DEFAULT 0,
            fours INTEGER DEFAULT 0,
            sixes INTEGER DEFAULT 0,
            wickets INTEGER DEFAULT 0,
            runs_conceded INTEGER DEFAULT 0,
            overs_bowled FLOAT DEFAULT 0,
            maidens INTEGER DEFAULT 0,
            economy FLOAT DEFAULT 0,
            catches INTEGER DEFAULT 0,
            stumpings INTEGER DEFAULT 0,
            run_outs INTEGER DEFAULT 0,
            dismissed BOOLEAN DEFAULT FALSE,
            total_points FLOAT DEFAULT 0,
            updated_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(match_api_id, player_name)
        )
    """)

    await db.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id SERIAL PRIMARY KEY,
            api_id VARCHAR(100) UNIQUE NOT NULL,
            name VARCHAR(255),
            status VARCHAR(255),
            teams TEXT,
            match_type VARCHAR(20),
            date VARCHAR(30),
            match_started BOOLEAN DEFAULT FALSE,
            match_ended BOOLEAN DEFAULT FALSE,
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)


async def _fetch_scorecard(match_id: str):
    """Fetch scorecard from CricketData.org."""
    url = f"{CRICKET_API_BASE}/match_scorecard"
    params = {"apikey": CRICKET_API_KEY, "id": match_id}

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    if data.get("status") != "success":
        log.warning(f"API returned status={data.get('status')} for match {match_id}")
        return None

    return data.get("data")


async def _parse_and_store(match_data: dict):
    """Parse scorecard and upsert player performances."""
    match_id = match_data["id"]
    scorecards = match_data.get("scorecard", [])

    # Aggregate all stats per player across both innings
    players = {}  # name → {batting: {}, bowling: {}, fielding: {}}

    for inning in scorecards:
        # Parse batting
        for b in inning.get("batting", []):
            name = b["batsman"]["name"]
            api_id = b["batsman"]["id"]
            if name not in players:
                players[name] = {"api_id": api_id, "batting": {}, "bowling": {}, "fielding": {}}

            prev = players[name]["batting"]
            players[name]["batting"] = {
                "r": prev.get("r", 0) + b.get("r", 0),
                "b": prev.get("b", 0) + b.get("b", 0),
                "4s": prev.get("4s", 0) + b.get("4s", 0),
                "6s": prev.get("6s", 0) + b.get("6s", 0),
                "dismissed": prev.get("dismissed", False) or (b.get("dismissal") is not None),
            }

        # Parse bowling
        for bw in inning.get("bowling", []):
            name = bw["bowler"]["name"]
            api_id = bw["bowler"]["id"]
            if name not in players:
                players[name] = {"api_id": api_id, "batting": {}, "bowling": {}, "fielding": {}}

            prev = players[name]["bowling"]
            new_overs = prev.get("o", 0) + bw.get("o", 0)
            new_runs = prev.get("r", 0) + bw.get("r", 0)
            players[name]["bowling"] = {
                "o": new_overs,
                "m": prev.get("m", 0) + bw.get("m", 0),
                "r": new_runs,
                "w": prev.get("w", 0) + bw.get("w", 0),
                "eco": round(new_runs / new_overs, 1) if new_overs > 0 else 0,
            }

        # Parse fielding
        for f in inning.get("catching", []):
            if "catcher" not in f:
                continue
            name = f["catcher"]["name"]
            api_id = f["catcher"]["id"]
            if name not in players:
                players[name] = {"api_id": api_id, "batting": {}, "bowling": {}, "fielding": {}}

            prev = players[name]["fielding"]
            players[name]["fielding"] = {
                "catch": prev.get("catch", 0) + f.get("catch", 0),
                "stumped": prev.get("stumped", 0) + f.get("stumped", 0),
                "runout": prev.get("runout", 0) + f.get("runout", 0),
            }

    # Calculate points and upsert into DB
    upserted = 0
    for name, stats in players.items():
        points = calculate_fantasy_points(stats["batting"], stats["bowling"], stats["fielding"])

        await db.execute("""
            INSERT INTO player_match_performances
                (match_api_id, player_name, player_api_id,
                 runs, balls_faced, fours, sixes,
                 wickets, runs_conceded, overs_bowled, maidens, economy,
                 catches, stumpings, run_outs, dismissed,
                 total_points, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, NOW())
            ON CONFLICT (match_api_id, player_name) DO UPDATE SET
                runs = $4, balls_faced = $5, fours = $6, sixes = $7,
                wickets = $8, runs_conceded = $9, overs_bowled = $10,
                maidens = $11, economy = $12,
                catches = $13, stumpings = $14, run_outs = $15,
                dismissed = $16, total_points = $17, updated_at = NOW()
        """,
            match_id, name, stats.get("api_id"),
            stats["batting"].get("r", 0), stats["batting"].get("b", 0),
            stats["batting"].get("4s", 0), stats["batting"].get("6s", 0),
            stats["bowling"].get("w", 0), stats["bowling"].get("r", 0),
            stats["bowling"].get("o", 0.0), stats["bowling"].get("m", 0),
            stats["bowling"].get("eco", 0.0),
            stats["fielding"].get("catch", 0), stats["fielding"].get("stumped", 0),
            stats["fielding"].get("runout", 0),
            stats["batting"].get("dismissed", False),
            points
        )
        upserted += 1

    return upserted


async def _update_leaderboard(match_api_id: str):
    """
    Recalculate each user's total fantasy points based on their drafted
    players' real performance data. Applies Captain (2x) and VC (1.5x).
    """
    # Get all locked fantasy teams
    teams = await db.fetch("""
        SELECT ft.id as ft_id, ft.user_id
        FROM fantasy_teams ft
    """)

    for team in teams:
        user_id = team["user_id"]

        # Get the user's drafted players with C/VC flags
        drafts = await db.fetch("""
            SELECT ud.player_id, ud.is_captain, ud.is_vice_captain, p.name as player_name
            FROM user_drafts ud
            JOIN players p ON ud.player_id = p.id
            WHERE ud.user_id = $1
        """, user_id)

        total = 0.0
        for d in drafts:
            # Match by player name (fuzzy — our DB name vs API name)
            perf = await db.fetchrow("""
                SELECT total_points FROM player_match_performances
                WHERE match_api_id = $1 AND player_name ILIKE $2
            """, match_api_id, f"%{d['player_name']}%")

            if perf:
                pts = perf["total_points"]
                if d["is_captain"]:
                    pts *= 2.0
                elif d["is_vice_captain"]:
                    pts *= 1.5
                total += pts

        # Update the fantasy team's total
        await db.execute("UPDATE fantasy_teams SET total_points = $1 WHERE user_id = $2", total, user_id)

    return len(teams)


# ── API Endpoints ──

@router.get("/sync")
async def sync_live_scores():
    """
    Main sync endpoint — called by Vercel Cron or GitHub Actions.
    Fetches current matches, grabs scorecards, calculates points.
    """
    await _ensure_perf_table()

    # Step 1: Get current/recent matches
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{CRICKET_API_BASE}/currentMatches", params={
            "apikey": CRICKET_API_KEY, "offset": 0
        })
        resp.raise_for_status()
        matches_data = resp.json()

    if matches_data.get("status") != "success":
        return {"status": "error", "message": "Failed to fetch matches"}

    results = []
    for match in matches_data.get("data", []):
        match_id = match["id"]
        match_name = match.get("name", "")

        # Store/update match record
        await db.execute("""
            INSERT INTO matches (api_id, name, status, teams, match_type, date, match_started, match_ended, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
            ON CONFLICT (api_id) DO UPDATE SET
                status = $3, match_started = $7, match_ended = $8, updated_at = NOW()
        """,
            match_id, match_name, match.get("status", ""),
            ", ".join(match.get("teams", [])),
            match.get("matchType", ""),
            match.get("date", ""),
            match.get("matchStarted", False),
            match.get("matchEnded", False)
        )

        # Only fetch scorecard if match has started and has fantasy data
        if not match.get("matchStarted"):
            continue

        try:
            scorecard_data = await _fetch_scorecard(match_id)
            if scorecard_data and scorecard_data.get("scorecard"):
                count = await _parse_and_store(scorecard_data)
                teams_updated = await _update_leaderboard(match_id)
                results.append({
                    "match": match_name,
                    "players_synced": count,
                    "teams_updated": teams_updated
                })
        except Exception as e:
            log.error(f"Error syncing {match_name}: {e}")
            results.append({"match": match_name, "error": str(e)})

    return {
        "status": "success",
        "matches_processed": len(results),
        "details": results,
        "api_hits": matches_data.get("info", {}).get("hitsUsed", "?")
    }


@router.get("/matches")
async def list_matches():
    """Return all tracked matches."""
    await _ensure_perf_table()
    rows = await db.fetch("SELECT * FROM matches ORDER BY date DESC LIMIT 20")
    return {"matches": [dict(r) for r in rows]}


@router.get("/scorecard/{match_api_id}")
async def get_scorecard(match_api_id: str):
    """Return stored player performances for a specific match."""
    rows = await db.fetch("""
        SELECT player_name, runs, balls_faced, fours, sixes,
               wickets, overs_bowled, maidens, economy,
               catches, stumpings, run_outs, total_points
        FROM player_match_performances
        WHERE match_api_id = $1
        ORDER BY total_points DESC
    """, match_api_id)
    return {"players": [dict(r) for r in rows]}
