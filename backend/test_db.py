import asyncio
from app.cron import _ensure_perf_table, _fetch_scorecard, _parse_and_store, _update_leaderboard

async def populate():
    await _ensure_perf_table()
    
    match_id = "74885a69-38e1-414c-b036-5035ae02fa91"
    print(f"Fetching scorecard for {match_id}...")
    scorecard_data = await _fetch_scorecard(match_id)
    
    if scorecard_data and scorecard_data.get("scorecard"):
        count = await _parse_and_store(scorecard_data)
        print(f"Stored {count} players.")
        teams = await _update_leaderboard(match_id)
        print(f"Updated {teams} leaderboards.")
    else:
        print("Failed to fetch scorecard")

if __name__ == "__main__":
    asyncio.run(populate())
