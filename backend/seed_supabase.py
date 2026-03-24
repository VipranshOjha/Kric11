"""
Kric11 — Seed Supabase with multi-contest support
Adds: contests table, NZ + SA squads, and 2 contest records
"""
import asyncio
import asyncpg

DATABASE_URL = "postgresql://postgres.hguowryelazzofkgpidt:OjhaVipransh@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

CREATE_TABLES = """
-- Users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Teams
CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    abbreviation VARCHAR(10) UNIQUE NOT NULL
);

-- Players
CREATE TABLE IF NOT EXISTS players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,
    credit_value FLOAT DEFAULT 8.0,
    team_id INTEGER REFERENCES teams(id),
    is_active BOOLEAN DEFAULT TRUE
);

-- Contests (one per match)
CREATE TABLE IF NOT EXISTS contests (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    match_api_id VARCHAR(100),
    team1_id INTEGER REFERENCES teams(id),
    team2_id INTEGER REFERENCES teams(id),
    match_date VARCHAR(30),
    venue VARCHAR(255),
    status VARCHAR(50) DEFAULT 'upcoming',
    created_at TIMESTAMP DEFAULT NOW()
);

-- User Drafts (per contest)
CREATE TABLE IF NOT EXISTS user_drafts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    contest_id INTEGER REFERENCES contests(id),
    player_id INTEGER REFERENCES players(id),
    is_captain BOOLEAN DEFAULT FALSE,
    is_vice_captain BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id, contest_id, player_id)
);

-- Locked Fantasy Teams (per contest)
CREATE TABLE IF NOT EXISTS fantasy_teams (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    contest_id INTEGER REFERENCES contests(id),
    total_points FLOAT DEFAULT 0.0,
    locked_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, contest_id)
);

-- Player Match Performances
CREATE TABLE IF NOT EXISTS player_match_performances (
    id SERIAL PRIMARY KEY,
    match_api_id VARCHAR(100) NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    player_api_id VARCHAR(100),
    runs INTEGER DEFAULT 0,
    balls_faced INTEGER DEFAULT 0,
    fours INTEGER DEFAULT 0,
    sixes INTEGER DEFAULT 0,
    wickets INTEGER DEFAULT 0,
    runs_conceded INTEGER DEFAULT 0,
    overs_bowled FLOAT DEFAULT 0,
    maidens INTEGER DEFAULT 0,
    economy FLOAT DEFAULT 0,
    catches INTEGER DEFAULT 0,
    stumpings INTEGER DEFAULT 0,
    run_outs INTEGER DEFAULT 0,
    dismissed BOOLEAN DEFAULT FALSE,
    total_points FLOAT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(match_api_id, player_name)
);

CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    api_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255),
    status VARCHAR(255),
    teams TEXT,
    match_type VARCHAR(20),
    date VARCHAR(30),
    match_started BOOLEAN DEFAULT FALSE,
    match_ended BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT NOW()
);
"""

# ── Squads ──

RCB_PLAYERS = [
    ("Virat Kohli",       "BAT",  10.5),
    ("Rajat Patidar",     "BAT",  9.0),
    ("Faf du Plessis",    "BAT",  8.5),
    ("Mahipal Lomror",    "BAT",  7.0),
    ("Glenn Maxwell",     "AR",   9.5),
    ("Will Jacks",        "AR",   8.5),
    ("Cameron Green",     "AR",   8.0),
    ("Dinesh Karthik",    "WK",   8.0),
    ("Anuj Rawat",        "WK",   6.5),
    ("Mohammed Siraj",    "BOWL", 8.5),
    ("Yash Dayal",        "BOWL", 7.0),
    ("Josh Hazlewood",    "BOWL", 8.0),
    ("Wanindu Hasaranga", "BOWL", 8.5),
    ("Lockie Ferguson",   "BOWL", 7.5),
    ("Karn Sharma",       "BOWL", 6.5),
]

SRH_PLAYERS = [
    ("Travis Head",       "BAT",  10.0),
    ("Aiden Markram",     "BAT",  8.0),
    ("Abdul Samad",       "BAT",  7.0),
    ("Rahul Tripathi",    "BAT",  7.0),
    ("Pat Cummins",       "AR",   10.0),
    ("Abhishek Sharma",   "AR",   8.5),
    ("Nitish Reddy",      "AR",   7.5),
    ("Heinrich Klaasen",  "WK",   9.5),
    ("Glenn Phillips",    "WK",   7.0),
    ("Bhuvneshwar Kumar", "BOWL", 8.0),
    ("T Natarajan",       "BOWL", 7.5),
    ("Umran Malik",       "BOWL", 7.0),
    ("Marco Jansen",      "BOWL", 8.0),
    ("Mayank Markande",   "BOWL", 6.5),
    ("Jaydev Unadkat",    "BOWL", 6.5),
]

# NZ vs SA 4th T20I squads (from the actual API scorecard)
NZ_PLAYERS = [
    ("Tim Robinson",      "BAT",  8.5),
    ("Katene D Clarke",   "BAT",  7.0),
    ("Dane Cleaver",      "WK",   8.5),
    ("Nick Kelly",        "BAT",  7.5),
    ("Bevon Jacobs",      "BAT",  6.5),
    ("James Neesham",     "AR",   8.5),
    ("Cole McConchie",    "AR",   7.5),
    ("Josh Clarkson",     "AR",   7.0),
    ("Zakary Foulkes",    "BOWL", 7.5),
    ("Kyle Jamieson",     "BOWL", 9.0),
    ("Ben Sears",         "BOWL", 8.0),
]

SA_PLAYERS = [
    ("Wiaan Mulder",      "AR",   8.0),
    ("Tony de Zorzi",     "BAT",  8.5),
    ("Connor Esterhuizen","WK",   9.0),
    ("Rubin Hermann",     "BAT",  7.5),
    ("Dian Forrester",    "BAT",  7.0),
    ("Jason Smith",       "AR",   7.5),
    ("George Linde",      "AR",   7.5),
    ("Gerald Coetzee",    "BOWL", 9.0),
    ("Ottneil Baartman",  "BOWL", 8.5),
    ("Prenelan Subrayen", "BOWL", 8.0),
    ("Keshav Maharaj",    "BOWL", 8.5),
]


async def seed():
    print("Connecting to Supabase...")
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        # Drop all tables (clean slate)
        print("Dropping old tables...")
        for t in ["user_drafts", "fantasy_teams", "player_match_performances",
                   "matches", "contests", "players", "teams", "users"]:
            await conn.execute(f"DROP TABLE IF EXISTS {t} CASCADE")

        print("Creating tables...")
        await conn.execute(CREATE_TABLES)

        # --- Insert Teams ---
        print("Inserting teams...")
        rcb_id = await conn.fetchval("INSERT INTO teams (name, abbreviation) VALUES ($1, $2) RETURNING id",
                                     "Royal Challengers Bengaluru", "RCB")
        srh_id = await conn.fetchval("INSERT INTO teams (name, abbreviation) VALUES ($1, $2) RETURNING id",
                                     "Sunrisers Hyderabad", "SRH")
        nz_id = await conn.fetchval("INSERT INTO teams (name, abbreviation) VALUES ($1, $2) RETURNING id",
                                    "New Zealand", "NZ")
        sa_id = await conn.fetchval("INSERT INTO teams (name, abbreviation) VALUES ($1, $2) RETURNING id",
                                    "South Africa", "RSA")

        # --- Insert Players ---
        for label, squad, tid in [("RCB", RCB_PLAYERS, rcb_id), ("SRH", SRH_PLAYERS, srh_id),
                                  ("NZ", NZ_PLAYERS, nz_id), ("RSA", SA_PLAYERS, sa_id)]:
            print(f"  {label}: {len(squad)} players")
            for name, role, credits in squad:
                await conn.execute("INSERT INTO players (name, role, credit_value, team_id) VALUES ($1,$2,$3,$4)",
                                   name, role, credits, tid)

        # --- Create Contests ---
        print("Creating contests...")
        c1 = await conn.fetchval("""
            INSERT INTO contests (name, match_api_id, team1_id, team2_id, match_date, venue, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id
        """, "RCB vs SRH · IPL 2026", None, rcb_id, srh_id, "2026-03-28", "M. Chinnaswamy Stadium", "upcoming")

        c2 = await conn.fetchval("""
            INSERT INTO contests (name, match_api_id, team1_id, team2_id, match_date, venue, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id
        """, "NZ vs SA · 4th T20I", "74885a69-38e1-414c-b036-5035ae02fa91",
             nz_id, sa_id, "2026-03-22", "Sky Stadium, Wellington", "completed")

        total = await conn.fetchval("SELECT COUNT(*) FROM players")
        contests = await conn.fetchval("SELECT COUNT(*) FROM contests")

        print(f"\n✅ Seeded! {total} players, {contests} contests")
        print(f"   Contest 1 (id={c1}): RCB vs SRH — upcoming")
        print(f"   Contest 2 (id={c2}): NZ vs SA — completed (has real scorecard data)")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(seed())
