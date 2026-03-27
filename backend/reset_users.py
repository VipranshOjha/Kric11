"""
Kric11 — Reset all user data for a fresh start.
Keeps: teams, players, contests (match schedule)
Deletes: user_drafts, fantasy_teams, player_match_performances, users
"""
import asyncio
from app import db

async def reset():
    print("🔄 Resetting user data...")
    
    # Order matters due to foreign keys
    await db.execute("DELETE FROM user_drafts")
    print("  ✓ Cleared user_drafts")
    
    await db.execute("DELETE FROM fantasy_teams")
    print("  ✓ Cleared fantasy_teams")
    
    await db.execute("DELETE FROM player_match_performances")
    print("  ✓ Cleared player_match_performances")
    
    await db.execute("DELETE FROM users")
    print("  ✓ Cleared users")
    
    # Reset contest statuses back to Upcoming
    await db.execute("UPDATE contests SET status = 'Upcoming', actual_winner_id = NULL")
    print("  ✓ Reset all contest statuses to Upcoming")
    
    print("\n✅ Done! All user accounts, squads, and scores wiped.")
    print("   Teams, players, and match schedule are untouched.")
    print("   Everyone can register fresh and build their Playing XI!")

if __name__ == "__main__":
    asyncio.run(reset())
