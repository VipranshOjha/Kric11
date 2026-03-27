"""
Kric11 — Re-seed ONLY the players table with updated rosters.
Clears all user data that references players, then re-inserts new roster.
Keeps: teams, contests (match schedule)
"""
import asyncio
import asyncpg
import os
import sys

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.hguowryelazzofkgpidt:OjhaVipransh@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
)

sys.path.insert(0, os.path.dirname(__file__))
from app.data import PLAYERS

async def reseed_players():
    conn = await asyncpg.connect(DATABASE_URL, statement_cache_size=0)
    try:
        # 1. Clear all tables that reference players (FK order)
        await conn.execute("DELETE FROM user_drafts")
        print("  Cleared user_drafts")
        await conn.execute("DELETE FROM fantasy_teams")
        print("  Cleared fantasy_teams")
        await conn.execute("DELETE FROM player_match_performances")
        print("  Cleared player_match_performances")
        await conn.execute("DELETE FROM users")
        print("  Cleared users")

        # 2. Get team mapping
        team_rows = await conn.fetch("SELECT id, abbreviation FROM teams")
        team_map = {r["abbreviation"]: r["id"] for r in team_rows}
        print(f"\nFound {len(team_map)} teams: {list(team_map.keys())}")

        # 3. Clear old players
        await conn.execute("DELETE FROM players")
        print("Cleared old players")

        # 4. Insert new 244 players
        count = 0
        for p in PLAYERS:
            tid = team_map.get(p["team"])
            if not tid:
                print(f"  SKIP: no team for '{p['team']}' ({p['name']})")
                continue
            await conn.execute(
                "INSERT INTO players (name, role, credit_value, team_id, is_active) VALUES ($1, $2, $3, $4, $5)",
                p["name"], p["role"], p["credits"], tid, True
            )
            count += 1

        # 5. Reset contest statuses
        await conn.execute("UPDATE contests SET status = 'Upcoming', actual_winner_id = NULL")
        print("Reset contest statuses")

        # 6. Verify
        total = await conn.fetchval("SELECT COUNT(*) FROM players")
        print(f"\nInserted {count} players. DB total: {total}")
        
        for abbr in sorted(team_map.keys()):
            cnt = await conn.fetchval("SELECT COUNT(*) FROM players WHERE team_id = $1", team_map[abbr])
            print(f"  {abbr}: {cnt} players")
        
        print("\nAll done! Fresh start ready.")
    finally:
        await conn.close()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(reseed_players())
    loop.close()
