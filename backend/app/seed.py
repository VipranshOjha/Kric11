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

        # ── Matches: IPL 2026 Schedule ──
        matches_csv = """Royal Challengers Bengaluru vs Sunrisers Hyderabad|28 Mar, 2026|7:30 PM
Mumbai Indians vs Kolkata Knight Riders|29 Mar, 2026|7:30 PM
Rajasthan Royals vs Chennai Super Kings|30 Mar, 2026|7:30 PM
Punjab Kings vs Gujarat Titans|31 Mar, 2026|7:30 PM
Lucknow Super Giants vs Delhi Capitals|1 Apr, 2026|7:30 PM
Kolkata Knight Riders vs Sunrisers Hyderabad|2 Apr, 2026|7:30 PM
Chennai Super Kings vs Punjab Kings|3 Apr, 2026|7:30 PM
Delhi Capitals vs Mumbai Indians|4 Apr, 2026|3:30 PM
Gujarat Titans vs Rajasthan Royals|4 Apr, 2026|7:30 PM
Sunrisers Hyderabad vs Lucknow Super Giants|5 Apr, 2026|3:30 PM
Royal Challengers Bengaluru vs Chennai Super Kings|5 Apr, 2026|7:30 PM
Kolkata Knight Riders vs Punjab Kings|6 Apr, 2026|7:30 PM
Rajasthan Royals vs Mumbai Indians|7 Apr, 2026|7:30 PM
Delhi Capitals vs Gujarat Titans|8 Apr, 2026|7:30 PM
Kolkata Knight Riders vs Lucknow Super Giants|9 Apr, 2026|7:30 PM
Rajasthan Royals vs Royal Challengers Bengaluru|10 Apr, 2026|7:30 PM
Punjab Kings vs Sunrisers Hyderabad|11 Apr, 2026|3:30 PM
Chennai Super Kings vs Delhi Capitals|11 Apr, 2026|7:30 PM
Lucknow Super Giants vs Gujarat Titans|12 Apr, 2026|3:30 PM
Mumbai Indians vs Royal Challengers Bengaluru|12 Apr, 2026|7:30 PM"""

        from datetime import timedelta
        ist_offset = timezone(timedelta(hours=5, minutes=30))
        
        db_matches = []
        for line in matches_csv.split("\n"):
            teams_str, date_str, time_str = line.split("|")
            home_str, away_str = teams_str.split(" vs ")
            
            home_abbr = next(abbr for abbr, name in TEAMS.items() if name == home_str.strip())
            away_abbr = next(abbr for abbr, name in TEAMS.items() if name == away_str.strip())
            
            home_t = team_objects[home_abbr]
            away_t = team_objects[away_abbr]
            
            dt_str = f"{date_str.strip()} {time_str.strip()}"
            start_date = datetime.strptime(dt_str, "%d %b, %Y %I:%M %p")
            # Assign IST timezone then convert to UTC
            start_date_utc = start_date.replace(tzinfo=ist_offset).astimezone(timezone.utc)
            
            m = Match(
                home_team_id=home_t.id,
                away_team_id=away_t.id,
                start_time=start_date_utc,
                status=MatchStatus.UPCOMING
            )
            db_matches.append(m)

        session.add_all(db_matches)
        await session.commit()
        print(f"Database seeded with 10 IPL franchises, 110 players, and {len(db_matches)} upcoming matches for the 2026 Season!")

if __name__ == "__main__":
    asyncio.run(seed_database())
