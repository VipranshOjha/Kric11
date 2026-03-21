import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models import Base, Team, Player, PlayerRole, Match, MatchStatus
from datetime import datetime, timedelta, timezone

DATABASE_URL = "sqlite+aiosqlite:///./kric11.db"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def seed_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Create Teams
        rcb = Team(name="Royal Challengers Bengaluru", abbreviation="RCB")
        srh = Team(name="Sunrisers Hyderabad", abbreviation="SRH")
        
        session.add_all([rcb, srh])
        await session.flush() # To get IDs

        # Create High-Value RCB Players (Defending Champions)
        rcb_players = [
            Player(name="Virat Kohli", role=PlayerRole.BAT, credit_value=12.0, team_id=rcb.id),
            Player(name="Rajat Patidar", role=PlayerRole.BAT, credit_value=11.5, team_id=rcb.id), # Captain
            Player(name="Will Jacks", role=PlayerRole.AR, credit_value=10.0, team_id=rcb.id),
            Player(name="Mohammed Siraj", role=PlayerRole.BOWL, credit_value=9.5, team_id=rcb.id),
            Player(name="Dinesh Karthik", role=PlayerRole.WK, credit_value=8.5, team_id=rcb.id),
        ]

        # Create SRH Players (Opener Opponents)
        srh_players = [
            Player(name="Pat Cummins", role=PlayerRole.AR, credit_value=10.5, team_id=srh.id),
            Player(name="Travis Head", role=PlayerRole.BAT, credit_value=11.0, team_id=srh.id),
            Player(name="Heinrich Klaasen", role=PlayerRole.WK, credit_value=10.5, team_id=srh.id),
            Player(name="Abhishek Sharma", role=PlayerRole.AR, credit_value=9.5, team_id=srh.id),
            Player(name="Bhuvneshwar Kumar", role=PlayerRole.BOWL, credit_value=9.0, team_id=srh.id),
        ]

        session.add_all(rcb_players + srh_players)

        # Match: Opener on March 28
        # Usually IPL starts in the evening IST: 19:30 IST is 14:00 UTC
        match_date = datetime(2026, 3, 28, 14, 0, tzinfo=timezone.utc)
        opener_match = Match(
            home_team_id=rcb.id,
            away_team_id=srh.id,
            start_time=match_date,
            status=MatchStatus.UPCOMING
        )
        
        session.add(opener_match)
        await session.commit()
        print("Database seeded successfully with RCB and SRH profiles!")

if __name__ == "__main__":
    asyncio.run(seed_database())
