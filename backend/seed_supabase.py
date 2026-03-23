"""
Kric11 — Seed Supabase Database with realistic IPL 2026 credits
Credit range: 6.5 – 10.5 CR (budget = 100 CR for 12 players → avg 8.33)
"""
import asyncio
import asyncpg

DATABASE_URL = "postgresql://postgres.hguowryelazzofkgpidt:OjhaVipransh@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    abbreviation VARCHAR(10) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,
    credit_value FLOAT DEFAULT 8.0,
    team_id INTEGER REFERENCES teams(id),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS user_drafts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    player_id INTEGER REFERENCES players(id),
    is_captain BOOLEAN DEFAULT FALSE,
    is_vice_captain BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id, player_id)
);

CREATE TABLE IF NOT EXISTS fantasy_teams (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) UNIQUE,
    total_points FLOAT DEFAULT 0.0,
    locked_at TIMESTAMP DEFAULT NOW()
);
"""

# ── Realistic IPL 2026 Credits ──
# Budget = 100 CR for 12 players → average 8.33 per player
# Range: 6.5 (budget pick) to 10.5 (premium star)
# Strategy: You MUST pick some budget players to afford 2-3 stars

RCB_PLAYERS = [
    ("Virat Kohli",       "BAT",  10.5),  # Premium — top run scorer
    ("Rajat Patidar",     "BAT",  9.0),
    ("Faf du Plessis",    "BAT",  8.5),
    ("Mahipal Lomror",    "BAT",  7.0),
    ("Glenn Maxwell",     "AR",   9.5),   # Premium all-rounder
    ("Will Jacks",        "AR",   8.5),
    ("Cameron Green",     "AR",   8.0),
    ("Dinesh Karthik",    "WK",   8.0),
    ("Anuj Rawat",        "WK",   6.5),   # Budget pick
    ("Mohammed Siraj",    "BOWL", 8.5),
    ("Yash Dayal",        "BOWL", 7.0),
    ("Josh Hazlewood",    "BOWL", 8.0),
    ("Wanindu Hasaranga", "BOWL", 8.5),
    ("Lockie Ferguson",   "BOWL", 7.5),
    ("Karn Sharma",       "BOWL", 6.5),   # Budget pick
]

SRH_PLAYERS = [
    ("Travis Head",       "BAT",  10.0),  # Premium opener
    ("Aiden Markram",     "BAT",  8.0),
    ("Abdul Samad",       "BAT",  7.0),
    ("Rahul Tripathi",    "BAT",  7.0),
    ("Pat Cummins",       "AR",   10.0),  # Premium captain material
    ("Abhishek Sharma",   "AR",   8.5),
    ("Nitish Reddy",      "AR",   7.5),
    ("Heinrich Klaasen",  "WK",   9.5),   # Premium finisher
    ("Glenn Phillips",    "WK",   7.0),
    ("Bhuvneshwar Kumar", "BOWL", 8.0),
    ("T Natarajan",       "BOWL", 7.5),
    ("Umran Malik",       "BOWL", 7.0),
    ("Marco Jansen",      "BOWL", 8.0),
    ("Mayank Markande",   "BOWL", 6.5),   # Budget pick
    ("Jaydev Unadkat",    "BOWL", 6.5),   # Budget pick
]


async def seed():
    print("Connecting to Supabase...")
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        print("Dropping old tables...")
        await conn.execute("DROP TABLE IF EXISTS user_drafts CASCADE")
        await conn.execute("DROP TABLE IF EXISTS fantasy_teams CASCADE")
        await conn.execute("DROP TABLE IF EXISTS players CASCADE")
        await conn.execute("DROP TABLE IF EXISTS teams CASCADE")
        await conn.execute("DROP TABLE IF EXISTS users CASCADE")

        print("Creating tables...")
        await conn.execute(CREATE_TABLES)

        print("Inserting teams...")
        rcb_id = await conn.fetchval(
            "INSERT INTO teams (name, abbreviation) VALUES ($1, $2) RETURNING id",
            "Royal Challengers Bengaluru", "RCB"
        )
        srh_id = await conn.fetchval(
            "INSERT INTO teams (name, abbreviation) VALUES ($1, $2) RETURNING id",
            "Sunrisers Hyderabad", "SRH"
        )

        print("Inserting RCB squad (15)...")
        for name, role, credits in RCB_PLAYERS:
            await conn.execute(
                "INSERT INTO players (name, role, credit_value, team_id) VALUES ($1, $2, $3, $4)",
                name, role, credits, rcb_id
            )

        print("Inserting SRH squad (15)...")
        for name, role, credits in SRH_PLAYERS:
            await conn.execute(
                "INSERT INTO players (name, role, credit_value, team_id) VALUES ($1, $2, $3, $4)",
                name, role, credits, srh_id
            )

        count = await conn.fetchval("SELECT COUNT(*) FROM players")
        avg = await conn.fetchval("SELECT ROUND(AVG(credit_value)::numeric, 1) FROM players")
        mn = await conn.fetchval("SELECT MIN(credit_value) FROM players")
        mx = await conn.fetchval("SELECT MAX(credit_value) FROM players")

        print(f"\n✅ {count} players seeded!")
        print(f"   Credits: min={mn}, max={mx}, avg={avg}")
        print(f"   Budget: 100 CR for 12 players (avg slot = 8.33)")
        print(f"   Strategy: Pick 2-3 premium + fill with budget picks")

        rows = await conn.fetch("""
            SELECT p.name, p.role, p.credit_value, t.abbreviation
            FROM players p JOIN teams t ON p.team_id = t.id
            ORDER BY p.credit_value DESC LIMIT 6
        """)
        print("\n   Top 6:")
        for r in rows:
            print(f"   {r['abbreviation']} | {r['name']:20s} | {r['role']:4s} | {r['credit_value']} CR")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(seed())
