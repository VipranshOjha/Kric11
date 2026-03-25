import asyncio
from app import db

async def main():
    rows = await db.fetch("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'contests'")
    for r in rows:
        print(dict(r))

    rows2 = await db.fetch("SELECT * FROM contests LIMIT 1")
    if rows2:
        print(dict(rows2[0]))

if __name__ == "__main__":
    asyncio.run(main())
