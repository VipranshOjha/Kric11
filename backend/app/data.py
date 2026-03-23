"""
Kric11 — Hardcoded player data and in-memory state.
No database required. Everything lives in memory per serverless invocation.
"""

# ── Teams ──
TEAMS = {
    "RCB": "Royal Challengers Bengaluru",
    "SRH": "Sunrisers Hyderabad",
}

# ── Players (30 total: 15 RCB + 15 SRH) ──
PLAYERS = [
    # RCB — Defending Champions
    {"id": 1,  "name": "Virat Kohli",       "role": "BAT",  "team": "RCB", "credits": 12.0},
    {"id": 2,  "name": "Rajat Patidar",     "role": "BAT",  "team": "RCB", "credits": 11.5},
    {"id": 3,  "name": "Faf du Plessis",    "role": "BAT",  "team": "RCB", "credits": 10.0},
    {"id": 4,  "name": "Mahipal Lomror",    "role": "BAT",  "team": "RCB", "credits": 8.0},
    {"id": 5,  "name": "Glenn Maxwell",     "role": "AR",   "team": "RCB", "credits": 10.5},
    {"id": 6,  "name": "Will Jacks",        "role": "AR",   "team": "RCB", "credits": 10.0},
    {"id": 7,  "name": "Cameron Green",     "role": "AR",   "team": "RCB", "credits": 9.5},
    {"id": 8,  "name": "Dinesh Karthik",    "role": "WK",   "team": "RCB", "credits": 8.5},
    {"id": 9,  "name": "Anuj Rawat",        "role": "WK",   "team": "RCB", "credits": 7.5},
    {"id": 10, "name": "Mohammed Siraj",    "role": "BOWL", "team": "RCB", "credits": 9.5},
    {"id": 11, "name": "Yash Dayal",        "role": "BOWL", "team": "RCB", "credits": 8.5},
    {"id": 12, "name": "Josh Hazlewood",    "role": "BOWL", "team": "RCB", "credits": 9.0},
    {"id": 13, "name": "Wanindu Hasaranga", "role": "BOWL", "team": "RCB", "credits": 9.0},
    {"id": 14, "name": "Lockie Ferguson",   "role": "BOWL", "team": "RCB", "credits": 8.5},
    {"id": 15, "name": "Karn Sharma",       "role": "BOWL", "team": "RCB", "credits": 7.5},

    # SRH — Opener Opponents
    {"id": 16, "name": "Travis Head",       "role": "BAT",  "team": "SRH", "credits": 11.0},
    {"id": 17, "name": "Aiden Markram",     "role": "BAT",  "team": "SRH", "credits": 9.5},
    {"id": 18, "name": "Abdul Samad",       "role": "BAT",  "team": "SRH", "credits": 8.0},
    {"id": 19, "name": "Rahul Tripathi",    "role": "BAT",  "team": "SRH", "credits": 8.0},
    {"id": 20, "name": "Pat Cummins",       "role": "AR",   "team": "SRH", "credits": 10.5},
    {"id": 21, "name": "Abhishek Sharma",   "role": "AR",   "team": "SRH", "credits": 9.5},
    {"id": 22, "name": "Nitish Reddy",      "role": "AR",   "team": "SRH", "credits": 8.5},
    {"id": 23, "name": "Heinrich Klaasen",  "role": "WK",   "team": "SRH", "credits": 10.5},
    {"id": 24, "name": "Rahul Tripathi",    "role": "WK",   "team": "SRH", "credits": 8.0},
    {"id": 25, "name": "Bhuvneshwar Kumar", "role": "BOWL", "team": "SRH", "credits": 9.0},
    {"id": 26, "name": "T Natarajan",       "role": "BOWL", "team": "SRH", "credits": 8.5},
    {"id": 27, "name": "Umran Malik",       "role": "BOWL", "team": "SRH", "credits": 8.0},
    {"id": 28, "name": "Marco Jansen",      "role": "BOWL", "team": "SRH", "credits": 9.0},
    {"id": 29, "name": "Mayank Markande",   "role": "BOWL", "team": "SRH", "credits": 7.5},
    {"id": 30, "name": "Jaydev Unadkat",    "role": "BOWL", "team": "SRH", "credits": 7.5},
]

# Quick lookup
PLAYERS_BY_ID = {p["id"]: p for p in PLAYERS}

# ── In-Memory State ──
# {username: {password, email, drafts: [player_ids], team_locked: bool, points: float}}
USERS = {}
DRAFTS = {}       # {username: [player_id, ...]}
LOCKED_TEAMS = {} # {username: {"players": [...], "captain": id, "vice_captain": id, "points": float}}

BUDGET_LIMIT = 100.0
MAX_PLAYERS = 12
