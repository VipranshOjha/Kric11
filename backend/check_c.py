import asyncio
from app import db

async def verify():
    # just print all contests
    print("Contests:")
    c = await db.fetch("SELECT id, name FROM contests")
    for r in c:
        print(dict(r))

if __name__ == "__main__":
    asyncio.run(verify())
