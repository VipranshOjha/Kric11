import asyncio
from datetime import datetime, timezone, timedelta
from app import db
from app.data import TEAMS, PLAYERS

matches_csv = """Royal Challengers Bengaluru vs Sunrisers Hyderabad|28 Mar, 2026|7:30 PM|M. Chinnaswamy Stadium, Bengaluru
Mumbai Indians vs Kolkata Knight Riders|29 Mar, 2026|7:30 PM|Wankhede Stadium, Mumbai
Rajasthan Royals vs Chennai Super Kings|30 Mar, 2026|7:30 PM|ACA Stadium, Guwahati
Punjab Kings vs Gujarat Titans|31 Mar, 2026|7:30 PM|Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur
Lucknow Super Giants vs Delhi Capitals|1 Apr, 2026|7:30 PM|Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow
Kolkata Knight Riders vs Sunrisers Hyderabad|2 Apr, 2026|7:30 PM|Eden Gardens, Kolkata
Chennai Super Kings vs Punjab Kings|3 Apr, 2026|7:30 PM|M.A. Chidambaram Stadium, Chennai
Delhi Capitals vs Mumbai Indians|4 Apr, 2026|3:30 PM|Arun Jaitley Stadium, Delhi
Gujarat Titans vs Rajasthan Royals|4 Apr, 2026|7:30 PM|Narendra Modi Stadium, Ahmedabad
Sunrisers Hyderabad vs Lucknow Super Giants|5 Apr, 2026|3:30 PM|Rajiv Gandhi International Stadium, Hyderabad
Royal Challengers Bengaluru vs Chennai Super Kings|5 Apr, 2026|7:30 PM|M. Chinnaswamy Stadium, Bengaluru
Kolkata Knight Riders vs Punjab Kings|6 Apr, 2026|7:30 PM|Eden Gardens, Kolkata
Rajasthan Royals vs Mumbai Indians|7 Apr, 2026|7:30 PM|ACA Stadium, Guwahati
Delhi Capitals vs Gujarat Titans|8 Apr, 2026|7:30 PM|Arun Jaitley Stadium, Delhi
Kolkata Knight Riders vs Lucknow Super Giants|9 Apr, 2026|7:30 PM|Eden Gardens, Kolkata
Rajasthan Royals vs Royal Challengers Bengaluru|10 Apr, 2026|7:30 PM|ACA Stadium, Guwahati
Punjab Kings vs Sunrisers Hyderabad|11 Apr, 2026|3:30 PM|Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur
Chennai Super Kings vs Delhi Capitals|11 Apr, 2026|7:30 PM|M.A. Chidambaram Stadium, Chennai
Lucknow Super Giants vs Gujarat Titans|12 Apr, 2026|3:30 PM|Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow
Mumbai Indians vs Royal Challengers Bengaluru|12 Apr, 2026|7:30 PM|Wankhede Stadium, Mumbai"""

async def seed_supabase():
    print("Connecting to Supabase and clearing old data...")
    # Clean old rows (cascade carefully, or just delete all)
    await db.execute("DELETE FROM user_drafts")
    await db.execute("DELETE FROM fantasy_teams")
    await db.execute("DELETE FROM player_match_performances")
    await db.execute("DELETE FROM contests")
    await db.execute("DELETE FROM players")
    await db.execute("DELETE FROM teams")

    print(f"Adding 10 Teams...")
    team_map = {}
    for abbr, full_name in TEAMS.items():
        t_id = await db.fetchval("INSERT INTO teams (name, abbreviation) VALUES ($1, $2) RETURNING id", full_name, abbr)
        team_map[abbr] = t_id

    print(f"Adding 110 Players...")
    for p in PLAYERS:
        tid = team_map[p["team"]]
        # Insert raw via execute to prevent multiple pool connections at once, or sequential
        await db.execute(
            "INSERT INTO players (name, role, credit_value, team_id, is_active) VALUES ($1, $2, $3, $4, $5)",
            p["name"], p["role"], p["credits"], tid, True
        )
    
    # We do need to fetch the team abbreviations back to dictionary for the match parsing since they rely on full names
    # Well, we already have TEAMS imported.
    print(f"Adding 20 confirmed IPL matches to Contests...")
    ist_offset = timezone(timedelta(hours=5, minutes=30))
    match_api_counter = 1000 # dummy api ids so they aren't null, or keep them null? User wants manual updates, maybe make them None until it's linked, but then we can't test it. Let's make them NULL for now. 
    # Actually wait. If match_api_id is NULL, force_sync fails. That's correct behavior until linked!
    
    for line in matches_csv.split("\n"):
        teams_str, date_str, time_str, venue = line.split("|")
        home_str, away_str = teams_str.split(" vs ")
        
        home_abbr = next(abbr for abbr, name in TEAMS.items() if name == home_str.strip())
        away_abbr = next(abbr for abbr, name in TEAMS.items() if name == away_str.strip())
        
        home_t_id = team_map[home_abbr]
        away_t_id = team_map[away_abbr]
        
        dt_str = f"{date_str.strip()} {time_str.strip()}"
        start_date = datetime.strptime(dt_str, "%d %b, %Y %I:%M %p")
        start_date_utc = start_date.replace(tzinfo=ist_offset).astimezone(timezone.utc)
        
        match_name = f"{home_abbr} vs {away_abbr} - IPL 2026"
        await db.execute("""
            INSERT INTO contests (name, team1_id, team2_id, match_date, venue, status, start_time)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, match_name, home_t_id, away_t_id, date_str.strip(), venue.strip(), "Upcoming", start_date_utc)

    print("Supabase database successfully seeded with native asyncpg!")

if __name__ == "__main__":
    asyncio.run(seed_supabase())
