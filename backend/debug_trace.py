import asyncio
import traceback
from app.database import AsyncSessionLocal
from app.cron import sync_live_scores
from unittest.mock import MagicMock

async def test_sync():
    async with AsyncSessionLocal() as db:
        try:
            req = MagicMock()
            result = await sync_live_scores(authorization=None, db=db)
            print("SUCCESS:", result)
        except Exception:
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sync())
