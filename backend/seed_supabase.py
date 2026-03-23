"""
Kric11 — Seed Supabase Database
Run: python seed_supabase.py
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
    credit_value FLOAT DEFAULT 8.5,
    team_id INTEGER REFERENCES teams(id),
    is_active BOOLEAN DEFAULT TRUE
);

-- User Drafts (saves selected players per user)
CREATE TABLE IF NOT EXISTS user_drafts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    player_id INTEGER REFERENCES players(id),
    is_captain BOOLEAN DEFAULT FALSE,
    is_vice_captain BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id, player_id)
);

-- Locked Fantasy Teams
CREATE TABLE IF NOT EXISTS fantasy_teams (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) UNIQUE,
    total_points FLOAT DEFAULT 0.0,
    locked_at TIMESTAMP DEFAULT NOW()
);
"""

RCB_PLAYERS = [
    ("Virat Kohli",       "BAT",  12.0),
    ("Rajat Patidar",     "BAT",  11.5),
    ("Faf du Plessis",    "BAT",  10.0),
    ("Mahipal Lomror",    "BAT",  8.0),
    ("Glenn Maxwell",     "AR",   10.5),
    ("Will Jacks",        "AR",   10.0),
    ("Cameron Green",     "AR",   9.5),
    ("Dinesh Karthik",    "WK",   8.5),
    ("Anuj Rawat",        "WK",   7.5),
    ("Mohammed Siraj",    "BOWL", 9.5),
    ("Yash Dayal",        "BOWL", 8.5),
    ("Josh Hazlewood",    "BOWL", 9.0),
    ("Wanindu Hasaranga", "BOWL", 9.0),
    ("Lockie Ferguson",   "BOWL", 8.5),
    ("Karn Sharma",       "BOWL", 7.5),
]

SRH_PLAYERS = [
    ("Travis Head",       "BAT",  11.0),
    ("Aiden Markram",     "BAT",  9.5),
    ("Abdul Samad",       "BAT",  8.0),
    ("Rahul Tripathi",    "BAT",  8.0),
    ("Pat Cummins",       "AR",   10.5),
    ("Abhishek Sharma",   "AR",   9.5),
    ("Nitish Reddy",      "AR",   8.5),
    ("Heinrich Klaasen",  "WK",   10.5),
    ("Glenn Phillips",    "WK",   8.0),
    ("Bhuvneshwar Kumar", "BOWL", 9.0),
    ("T Natarajan",       "BOWL", 8.5),
    ("Umran Malik",       "BOWL", 8.0),
    ("Marco Jansen",      "BOWL", 9.0),
    ("Mayank Markande",   "BOWL", 7.5),
    ("Jaydev Unadkat",    "BOWL", 7.5),
]


async def seed():
    print("Connecting to Supabase...")
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        # Drop existing tables (clean slate)
        print("Dropping old tables...")
        await conn.execute("DROP TABLE IF EXISTS user_drafts CASCADE")
        await conn.execute("DROP TABLE IF EXISTS fantasy_teams CASCADE")
        await conn.execute("DROP TABLE IF EXISTS players CASCADE")
        await conn.execute("DROP TABLE IF EXISTS teams CASCADE")
        await conn.execute("DROP TABLE IF EXISTS users CASCADE")

        # Create tables
        print("Creating tables...")
        await conn.execute(CREATE_TABLES)

        # Insert teams
        print("Inserting teams...")
        rcb_id = await conn.fetchval(
            "INSERT INTO teams (name, abbreviation) VALUES ($1, $2) RETURNING id",
            "Royal Challengers Bengaluru", "RCB"
        )
        srh_id = await conn.fetchval(
            "INSERT INTO teams (name, abbreviation) VALUES ($1, $2) RETURNING id",
            "Sunrisers Hyderabad", "SRH"
        )

        # Insert RCB players
        print(f"Inserting 15 RCB players (team_id={rcb_id})...")
        for name, role, credits in RCB_PLAYERS:
            await conn.execute(
                "INSERT INTO players (name, role, credit_value, team_id) VALUES ($1, $2, $3, $4)",
                name, role, credits, rcb_id
            )

        # Insert SRH players
        print(f"Inserting 15 SRH players (team_id={srh_id})...")
        for name, role, credits in SRH_PLAYERS:
            await conn.execute(
                "INSERT INTO players (name, role, credit_value, team_id) VALUES ($1, $2, $3, $4)",
                name, role, credits, srh_id
            )

        # Verify
        count = await conn.fetchval("SELECT COUNT(*) FROM players")
        print(f"\n✅ Done! {count} players seeded in Supabase.")
        
        # Show a sample
        rows = await conn.fetch("SELECT p.name, p.role, p.credit_value, t.abbreviation FROM players p JOIN teams t ON p.team_id = t.id ORDER BY p.credit_value DESC LIMIT 5")
        print("\nTop 5 by credits:")
        for r in rows:
            print(f"  {r['abbreviation']} | {r['name']:20s} | {r['role']:4s} | {r['credit_value']} CR")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(seed())
