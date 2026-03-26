import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.models import *
from datetime import datetime, timezone

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./kric11.db")

_is_postgres = DATABASE_URL.startswith("postgresql")

engine_kwargs = {"echo": True}
if _is_postgres:
    engine_kwargs["poolclass"] = NullPool
    engine_kwargs["connect_args"] = {
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0,
    }

engine = create_async_engine(DATABASE_URL, **engine_kwargs)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def seed_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        from app.data import TEAMS, PLAYERS
        
        # ── Insert 10 Franchises ──
        team_objects = {}
        for abbr, name in TEAMS.items():
            t = Team(name=name, abbreviation=abbr)
            session.add(t)
            team_objects[abbr] = t
            
        await session.flush()

        # ── Insert 110 Players ──
        db_players = []
        for p in PLAYERS:
            t = team_objects[p["team"]]
            role_enum = getattr(PlayerRole, p["role"])
            db_players.append(
                Player(name=p["name"], role=role_enum, credit_value=p["credits"], team_id=t.id)
            )
            
        session.add_all(db_players)

        # ── Match: IPL 2026 Opener ──
        match_date = datetime(2026, 3, 28, 14, 0, tzinfo=timezone.utc)
        rcb_id = team_objects["RCB"].id
        srh_id = team_objects["SRH"].id
        opener_match = Match(
            home_team_id=rcb_id,
            away_team_id=srh_id,
            start_time=match_date,
            status=MatchStatus.UPCOMING
        )
        session.add(opener_match)
        await session.commit()
        print("✅ Database seeded with 10 IPL franchises and 110 players for the 2026 Season!")

if __name__ == "__main__":
    asyncio.run(seed_database())
