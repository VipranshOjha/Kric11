import asyncio
from app.cron import _ensure_perf_table, _update_leaderboard

async def main():
    await _ensure_perf_table()
    # 74885a69-38e1-414c-b036-5035ae02fa91 is NZ vs SA match API ID
    teams = await _update_leaderboard("74885a69-38e1-414c-b036-5035ae02fa91")
    print(f"Updated {teams} leaderboards")

if __name__ == "__main__":
    asyncio.run(main())
