import asyncio
from app import db

async def main():
    rows = await db.fetch("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'fantasy_teams'")
    print("FANTASY_TEAMS:")
    for r in rows:
        print(dict(r))

    rows2 = await db.fetch("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'contests'")
    print("CONTESTS:")
    for r in rows2:
        print(dict(r))

if __name__ == "__main__":
    asyncio.run(main()) 
