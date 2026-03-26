import asyncio
from app import db

async def run():
    print("Modifying DB Scheme...")
    try:
        await db.execute("ALTER TABLE contests ADD COLUMN actual_winner_id INTEGER NULL REFERENCES teams(id);")
        print("[+] Added actual_winner_id to contests")
    except Exception as e:
        print("error contests:", e)
        
    try:
        await db.execute("ALTER TABLE fantasy_teams ADD COLUMN predicted_winner_id INTEGER NULL REFERENCES teams(id);")
        print("[+] Added predicted_winner_id to fantasy_teams")
    except Exception as e:
        print("error fantasy_teams:", e)

if __name__ == "__main__":
    asyncio.run(run())
