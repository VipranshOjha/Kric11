"""
Kric11 — Hardcoded player data and in-memory state.
No database required. Everything lives in memory per serverless invocation.
Updated for 2026 IPL Season (10 Franchises, Top 11 players each).
"""

# ── Teams ──
TEAMS = {
    "CSK": "Chennai Super Kings",
    "DC":  "Delhi Capitals",
    "GT":  "Gujarat Titans",
    "KKR": "Kolkata Knight Riders",
    "LSG": "Lucknow Super Giants",
    "MI":  "Mumbai Indians",
    "PBKS": "Punjab Kings",
    "RCB": "Royal Challengers Bengaluru",
    "RR":  "Rajasthan Royals",
    "SRH": "Sunrisers Hyderabad",
}

# ── Players (110 total: 11 per team) ──
PLAYERS = [
    # CSK
    {"id": 1, "name": "Ruturaj Gaikwad", "role": "BAT", "team": "CSK", "credits": 10.5},
    {"id": 2, "name": "MS Dhoni", "role": "WK", "team": "CSK", "credits": 8.5},
    {"id": 3, "name": "Ravindra Jadeja", "role": "AR", "team": "CSK", "credits": 11.0},
    {"id": 4, "name": "Matheesha Pathirana", "role": "BOWL", "team": "CSK", "credits": 9.5},
    {"id": 5, "name": "Shivam Dube", "role": "AR", "team": "CSK", "credits": 9.5},
    {"id": 6, "name": "Rachin Ravindra", "role": "AR", "team": "CSK", "credits": 9.0},
    {"id": 7, "name": "Deepak Chahar", "role": "BOWL", "team": "CSK", "credits": 8.5},
    {"id": 8, "name": "Ajinkya Rahane", "role": "BAT", "team": "CSK", "credits": 8.0},
    {"id": 9, "name": "Shardul Thakur", "role": "BOWL", "team": "CSK", "credits": 8.5},
    {"id": 10, "name": "Maheesh Theekshana", "role": "BOWL", "team": "CSK", "credits": 8.5},
    {"id": 11, "name": "Mustafizur Rahman", "role": "BOWL", "team": "CSK", "credits": 9.0},

    # DC
    {"id": 12, "name": "Rishabh Pant", "role": "WK", "team": "DC", "credits": 11.0},
    {"id": 13, "name": "David Warner", "role": "BAT", "team": "DC", "credits": 10.5},
    {"id": 14, "name": "Axar Patel", "role": "AR", "team": "DC", "credits": 10.0},
    {"id": 15, "name": "Kuldeep Yadav", "role": "BOWL", "team": "DC", "credits": 9.5},
    {"id": 16, "name": "Tristan Stubbs", "role": "BAT", "team": "DC", "credits": 9.0},
    {"id": 17, "name": "Jake Fraser-McGurk", "role": "BAT", "team": "DC", "credits": 9.5},
    {"id": 18, "name": "Khaleel Ahmed", "role": "BOWL", "team": "DC", "credits": 8.5},
    {"id": 19, "name": "Mukesh Kumar", "role": "BOWL", "team": "DC", "credits": 8.0},
    {"id": 20, "name": "Ishant Sharma", "role": "BOWL", "team": "DC", "credits": 8.0},
    {"id": 21, "name": "Prithvi Shaw", "role": "BAT", "team": "DC", "credits": 8.5},
    {"id": 22, "name": "Mitchell Marsh", "role": "AR", "team": "DC", "credits": 9.5},

    # GT
    {"id": 23, "name": "Shubman Gill", "role": "BAT", "team": "GT", "credits": 11.0},
    {"id": 24, "name": "Rashid Khan", "role": "AR", "team": "GT", "credits": 10.5},
    {"id": 25, "name": "Sai Sudharsan", "role": "BAT", "team": "GT", "credits": 9.5},
    {"id": 26, "name": "David Miller", "role": "BAT", "team": "GT", "credits": 9.5},
    {"id": 27, "name": "Mohammed Shami", "role": "BOWL", "team": "GT", "credits": 9.5},
    {"id": 28, "name": "Rahul Tewatia", "role": "AR", "team": "GT", "credits": 8.5},
    {"id": 29, "name": "Noor Ahmad", "role": "BOWL", "team": "GT", "credits": 8.5},
    {"id": 30, "name": "Mohit Sharma", "role": "BOWL", "team": "GT", "credits": 9.0},
    {"id": 31, "name": "Wriddhiman Saha", "role": "WK", "team": "GT", "credits": 8.0},
    {"id": 32, "name": "Spencer Johnson", "role": "BOWL", "team": "GT", "credits": 8.0},
    {"id": 33, "name": "Shahrukh Khan", "role": "BAT", "team": "GT", "credits": 8.0},

    # KKR
    {"id": 34, "name": "Shreyas Iyer", "role": "BAT", "team": "KKR", "credits": 9.5},
    {"id": 35, "name": "Andre Russell", "role": "AR", "team": "KKR", "credits": 10.5},
    {"id": 36, "name": "Sunil Narine", "role": "AR", "team": "KKR", "credits": 10.5},
    {"id": 37, "name": "Mitchell Starc", "role": "BOWL", "team": "KKR", "credits": 10.0},
    {"id": 38, "name": "Rinku Singh", "role": "BAT", "team": "KKR", "credits": 9.0},
    {"id": 39, "name": "Phil Salt", "role": "WK", "team": "KKR", "credits": 9.5},
    {"id": 40, "name": "Varun Chakaravarthy", "role": "BOWL", "team": "KKR", "credits": 9.0},
    {"id": 41, "name": "Venkatesh Iyer", "role": "AR", "team": "KKR", "credits": 8.5},
    {"id": 42, "name": "Harshit Rana", "role": "BOWL", "team": "KKR", "credits": 8.5},
    {"id": 43, "name": "Ramandeep Singh", "role": "BAT", "team": "KKR", "credits": 8.0},
    {"id": 44, "name": "Vaibhav Arora", "role": "BOWL", "team": "KKR", "credits": 8.0},

    # LSG
    {"id": 45, "name": "KL Rahul", "role": "WK", "team": "LSG", "credits": 10.5},
    {"id": 46, "name": "Marcus Stoinis", "role": "AR", "team": "LSG", "credits": 10.0},
    {"id": 47, "name": "Nicholas Pooran", "role": "WK", "team": "LSG", "credits": 10.5},
    {"id": 48, "name": "Quinton de Kock", "role": "WK", "team": "LSG", "credits": 9.5},
    {"id": 49, "name": "Ravi Bishnoi", "role": "BOWL", "team": "LSG", "credits": 9.0},
    {"id": 50, "name": "Mayank Yadav", "role": "BOWL", "team": "LSG", "credits": 8.5},
    {"id": 51, "name": "Krunal Pandya", "role": "AR", "team": "LSG", "credits": 8.5},
    {"id": 52, "name": "Ayush Badoni", "role": "BAT", "team": "LSG", "credits": 8.0},
    {"id": 53, "name": "Naveen-ul-Haq", "role": "BOWL", "team": "LSG", "credits": 8.5},
    {"id": 54, "name": "Mohsin Khan", "role": "BOWL", "team": "LSG", "credits": 8.0},
    {"id": 55, "name": "Yash Thakur", "role": "BOWL", "team": "LSG", "credits": 8.0},

    # MI
    {"id": 56, "name": "Hardik Pandya", "role": "AR", "team": "MI", "credits": 10.5},
    {"id": 57, "name": "Rohit Sharma", "role": "BAT", "team": "MI", "credits": 10.5},
    {"id": 58, "name": "Suryakumar Yadav", "role": "BAT", "team": "MI", "credits": 11.0},
    {"id": 59, "name": "Jasprit Bumrah", "role": "BOWL", "team": "MI", "credits": 11.0},
    {"id": 60, "name": "Ishan Kishan", "role": "WK", "team": "MI", "credits": 9.5},
    {"id": 61, "name": "Tim David", "role": "BAT", "team": "MI", "credits": 9.0},
    {"id": 62, "name": "Tilak Varma", "role": "BAT", "team": "MI", "credits": 9.0},
    {"id": 63, "name": "Gerald Coetzee", "role": "BOWL", "team": "MI", "credits": 8.5},
    {"id": 64, "name": "Piyush Chawla", "role": "BOWL", "team": "MI", "credits": 8.5},
    {"id": 65, "name": "Nehal Wadhera", "role": "BAT", "team": "MI", "credits": 8.0},
    {"id": 66, "name": "Akash Madhwal", "role": "BOWL", "team": "MI", "credits": 8.0},

    # PBKS
    {"id": 67, "name": "Shikhar Dhawan", "role": "BAT", "team": "PBKS", "credits": 9.5},
    {"id": 68, "name": "Sam Curran", "role": "AR", "team": "PBKS", "credits": 10.0},
    {"id": 69, "name": "Kagiso Rabada", "role": "BOWL", "team": "PBKS", "credits": 9.5},
    {"id": 70, "name": "Arshdeep Singh", "role": "BOWL", "team": "PBKS", "credits": 9.0},
    {"id": 71, "name": "Liam Livingstone", "role": "AR", "team": "PBKS", "credits": 9.5},
    {"id": 72, "name": "Jonny Bairstow", "role": "WK", "team": "PBKS", "credits": 9.0},
    {"id": 73, "name": "Harshal Patel", "role": "BOWL", "team": "PBKS", "credits": 9.0},
    {"id": 74, "name": "Shashank Singh", "role": "BAT", "team": "PBKS", "credits": 8.5},
    {"id": 75, "name": "Ashutosh Sharma", "role": "BAT", "team": "PBKS", "credits": 8.5},
    {"id": 76, "name": "Jitesh Sharma", "role": "WK", "team": "PBKS", "credits": 8.0},
    {"id": 77, "name": "Rahul Chahar", "role": "BOWL", "team": "PBKS", "credits": 8.0},

    # RCB
    {"id": 78, "name": "Virat Kohli", "role": "BAT", "team": "RCB", "credits": 11.5},
    {"id": 79, "name": "Faf du Plessis", "role": "BAT", "team": "RCB", "credits": 10.0},
    {"id": 80, "name": "Glenn Maxwell", "role": "AR", "team": "RCB", "credits": 10.5},
    {"id": 81, "name": "Mohammed Siraj", "role": "BOWL", "team": "RCB", "credits": 9.5},
    {"id": 82, "name": "Rajat Patidar", "role": "BAT", "team": "RCB", "credits": 9.0},
    {"id": 83, "name": "Cameron Green", "role": "AR", "team": "RCB", "credits": 9.5},
    {"id": 84, "name": "Will Jacks", "role": "AR", "team": "RCB", "credits": 9.5},
    {"id": 85, "name": "Dinesh Karthik", "role": "WK", "team": "RCB", "credits": 8.5},
    {"id": 86, "name": "Yash Dayal", "role": "BOWL", "team": "RCB", "credits": 8.5},
    {"id": 87, "name": "Lockie Ferguson", "role": "BOWL", "team": "RCB", "credits": 8.5},
    {"id": 88, "name": "Swapnil Singh", "role": "AR", "team": "RCB", "credits": 7.5},

    # RR
    {"id": 89, "name": "Sanju Samson", "role": "WK", "team": "RR", "credits": 10.5},
    {"id": 90, "name": "Jos Buttler", "role": "BAT", "team": "RR", "credits": 10.5},
    {"id": 91, "name": "Yashasvi Jaiswal", "role": "BAT", "team": "RR", "credits": 10.0},
    {"id": 92, "name": "Yuzvendra Chahal", "role": "BOWL", "team": "RR", "credits": 9.5},
    {"id": 93, "name": "Trent Boult", "role": "BOWL", "team": "RR", "credits": 9.5},
    {"id": 94, "name": "Riyan Parag", "role": "BAT", "team": "RR", "credits": 9.0},
    {"id": 95, "name": "Ravichandran Ashwin", "role": "AR", "team": "RR", "credits": 9.0},
    {"id": 96, "name": "Avesh Khan", "role": "BOWL", "team": "RR", "credits": 8.5},
    {"id": 97, "name": "Sandeep Sharma", "role": "BOWL", "team": "RR", "credits": 8.5},
    {"id": 98, "name": "Shimron Hetmyer", "role": "BAT", "team": "RR", "credits": 8.5},
    {"id": 99, "name": "Dhruv Jurel", "role": "WK", "team": "RR", "credits": 8.0},

    # SRH
    {"id": 100, "name": "Pat Cummins", "role": "AR", "team": "SRH", "credits": 10.0},
    {"id": 101, "name": "Travis Head", "role": "BAT", "team": "SRH", "credits": 10.5},
    {"id": 102, "name": "Heinrich Klaasen", "role": "WK", "team": "SRH", "credits": 10.5},
    {"id": 103, "name": "Abhishek Sharma", "role": "AR", "team": "SRH", "credits": 9.5},
    {"id": 104, "name": "Bhuvneshwar Kumar", "role": "BOWL", "team": "SRH", "credits": 9.0},
    {"id": 105, "name": "T Natarajan", "role": "BOWL", "team": "SRH", "credits": 8.5},
    {"id": 106, "name": "Aiden Markram", "role": "BAT", "team": "SRH", "credits": 9.0},
    {"id": 107, "name": "Nitish Reddy", "role": "AR", "team": "SRH", "credits": 8.5},
    {"id": 108, "name": "Mayank Markande", "role": "BOWL", "team": "SRH", "credits": 8.0},
    {"id": 109, "name": "Shahbaz Ahmed", "role": "AR", "team": "SRH", "credits": 8.0},
    {"id": 110, "name": "Jaydev Unadkat", "role": "BOWL", "team": "SRH", "credits": 8.0},
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
