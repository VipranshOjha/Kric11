import asyncio
from app import db

async def show():
    rows = await db.fetch("""
        SELECT player_name, runs, fours, sixes, wickets, maidens, catches, 
               ROUND(total_points::numeric, 1) as pts
        FROM player_match_performances
        WHERE match_api_id = '74885a69-38e1-414c-b036-5035ae02fa91'
        ORDER BY total_points DESC LIMIT 15
    """)
    print(f"\n{'Player':<25s} {'R':>4s} {'4s':>3s} {'6s':>3s} {'W':>2s} {'M':>2s} {'C':>2s} {'PTS':>6s}")
    print("-" * 55)
    for r in rows:
        print(f"{r['player_name']:<25s} {r['runs']:>4d} {r['fours']:>3d} {r['sixes']:>3d} {r['wickets']:>2d} {r['maidens']:>2d} {r['catches']:>2d} {float(r['pts']):>6.1f}")
    print(f"\nTotal players stored: {len(rows)}")

asyncio.run(show())
