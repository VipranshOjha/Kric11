"""Test the live scoring pipeline against NZ vs SA 4th T20I"""
import asyncio
from app.cron import _ensure_perf_table, _fetch_scorecard, _parse_and_store, _update_leaderboard
from app import db

MATCH_ID = "74885a69-38e1-414c-b036-5035ae02fa91"

async def test():
    print("1. Creating performance tables...")
    await _ensure_perf_table()
    
    print("2. Fetching scorecard from CricketData.org...")
    sc = await _fetch_scorecard(MATCH_ID)
    print(f"   Match: {sc['name']}")
    print(f"   Status: {sc['status']}")
    
    print("3. Parsing stats and calculating fantasy points...")
    count = await _parse_and_store(sc)
    print(f"   Players stored: {count}")
    
    print("4. Updating leaderboard...")
    teams = await _update_leaderboard(MATCH_ID)
    print(f"   Fantasy teams updated: {teams}")
    
    print("\n5. Top performers:")
    rows = await db.fetch("""
        SELECT player_name, runs, fours, sixes, wickets, catches, total_points
        FROM player_match_performances
        WHERE match_api_id = $1
        ORDER BY total_points DESC LIMIT 10
    """, MATCH_ID)
    
    print(f"   {'Player':<25s} {'R':>4s} {'4s':>3s} {'6s':>3s} {'W':>2s} {'C':>2s} {'PTS':>6s}")
    print(f"   {'-'*50}")
    for r in rows:
        print(f"   {r['player_name']:<25s} {r['runs']:>4d} {r['fours']:>3d} {r['sixes']:>3d} {r['wickets']:>2d} {r['catches']:>2d} {r['total_points']:>6.1f}")

if __name__ == "__main__":
    asyncio.run(test())
