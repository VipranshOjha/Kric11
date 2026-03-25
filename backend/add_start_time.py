import asyncio
from app import db

async def main():
    try:
        await db.execute("ALTER TABLE contests ADD COLUMN IF NOT EXISTS start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '1 day'")
        print("Column added.")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
