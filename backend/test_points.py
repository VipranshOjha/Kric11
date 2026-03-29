import asyncio
from app import db

async def verify():
    print("Contest 6 Match API ID:")
    c = await db.fetchrow("SELECT id, match_api_id FROM contests WHERE id = 6")
    print(dict(c) if c else None)

    print("\nPerformances Count:")
    count = await db.fetchval("SELECT COUNT(*) FROM player_match_performances")
    print(count)
    
    if c and c['match_api_id']:
        print("\nPerformances for this match:")
        p = await db.fetch("SELECT player_name, runs, total_points FROM player_match_performances WHERE match_api_id = $1 LIMIT 5", c['match_api_id'])
        for r in p:
            print(dict(r))

    print("\nTop Fantasy Teams:")
    teams = await db.fetch("SELECT u.username, ft.total_points FROM fantasy_teams ft JOIN users u ON u.id = ft.user_id WHERE ft.contest_id = 6 ORDER BY total_points DESC")
    for t in teams:
        print(f"{t['username']}: {t['total_points']}")

if __name__ == "__main__":
    asyncio.run(verify())
