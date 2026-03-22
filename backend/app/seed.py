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
        # ── Teams ──
        rcb = Team(name="Royal Challengers Bengaluru", abbreviation="RCB")
        srh = Team(name="Sunrisers Hyderabad", abbreviation="SRH")
        session.add_all([rcb, srh])
        await session.flush()

        # ── RCB Squad (15 players) ── Defending Champions ──
        rcb_players = [
            Player(name="Dinesh Karthik",    role=PlayerRole.WK,   credit_value=8.5,  team_id=rcb.id),
            Player(name="Anuj Rawat",        role=PlayerRole.WK,   credit_value=7.5,  team_id=rcb.id),
            Player(name="Virat Kohli",       role=PlayerRole.BAT,  credit_value=12.0, team_id=rcb.id),
            Player(name="Rajat Patidar",     role=PlayerRole.BAT,  credit_value=11.5, team_id=rcb.id),
            Player(name="Faf du Plessis",    role=PlayerRole.BAT,  credit_value=10.0, team_id=rcb.id),
            Player(name="Mahipal Lomror",    role=PlayerRole.BAT,  credit_value=8.0,  team_id=rcb.id),
            Player(name="Glenn Maxwell",     role=PlayerRole.AR,   credit_value=10.5, team_id=rcb.id),
            Player(name="Will Jacks",        role=PlayerRole.AR,   credit_value=10.0, team_id=rcb.id),
            Player(name="Cameron Green",     role=PlayerRole.AR,   credit_value=9.5,  team_id=rcb.id),
            Player(name="Mohammed Siraj",    role=PlayerRole.BOWL, credit_value=9.5,  team_id=rcb.id),
            Player(name="Yash Dayal",        role=PlayerRole.BOWL, credit_value=8.5,  team_id=rcb.id),
            Player(name="Karn Sharma",       role=PlayerRole.BOWL, credit_value=7.5,  team_id=rcb.id),
            Player(name="Josh Hazlewood",    role=PlayerRole.BOWL, credit_value=9.0,  team_id=rcb.id),
            Player(name="Wanindu Hasaranga", role=PlayerRole.BOWL, credit_value=9.0,  team_id=rcb.id),
            Player(name="Lockie Ferguson",   role=PlayerRole.BOWL, credit_value=8.5,  team_id=rcb.id),
        ]

        # ── SRH Squad (15 players) ──
        srh_players = [
            Player(name="Heinrich Klaasen",  role=PlayerRole.WK,   credit_value=10.5, team_id=srh.id),
            Player(name="Rahul Tripathi",    role=PlayerRole.WK,   credit_value=8.0,  team_id=srh.id),
            Player(name="Travis Head",       role=PlayerRole.BAT,  credit_value=11.0, team_id=srh.id),
            Player(name="Aiden Markram",     role=PlayerRole.BAT,  credit_value=9.5,  team_id=srh.id),
            Player(name="Abdul Samad",       role=PlayerRole.BAT,  credit_value=8.0,  team_id=srh.id),
            Player(name="Rahul Tripathi",    role=PlayerRole.BAT,  credit_value=8.0,  team_id=srh.id),
            Player(name="Pat Cummins",       role=PlayerRole.AR,   credit_value=10.5, team_id=srh.id),
            Player(name="Abhishek Sharma",   role=PlayerRole.AR,   credit_value=9.5,  team_id=srh.id),
            Player(name="Nitish Reddy",      role=PlayerRole.AR,   credit_value=8.5,  team_id=srh.id),
            Player(name="Bhuvneshwar Kumar", role=PlayerRole.BOWL, credit_value=9.0,  team_id=srh.id),
            Player(name="T Natarajan",       role=PlayerRole.BOWL, credit_value=8.5,  team_id=srh.id),
            Player(name="Umran Malik",       role=PlayerRole.BOWL, credit_value=8.0,  team_id=srh.id),
            Player(name="Mayank Markande",   role=PlayerRole.BOWL, credit_value=7.5,  team_id=srh.id),
            Player(name="Marco Jansen",      role=PlayerRole.BOWL, credit_value=9.0,  team_id=srh.id),
            Player(name="Jaydev Unadkat",    role=PlayerRole.BOWL, credit_value=7.5,  team_id=srh.id),
        ]

        session.add_all(rcb_players + srh_players)

        # ── Match: IPL 2026 Opener ──
        match_date = datetime(2026, 3, 28, 14, 0, tzinfo=timezone.utc)
        opener_match = Match(
            home_team_id=rcb.id,
            away_team_id=srh.id,
            start_time=match_date,
            status=MatchStatus.UPCOMING
        )
        session.add(opener_match)
        await session.commit()
        print("✅ Database seeded with 30 players (15 RCB + 15 SRH) and IPL 2026 Opener!")

if __name__ == "__main__":
    asyncio.run(seed_database())
