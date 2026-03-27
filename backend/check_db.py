import asyncio, asyncpg

async def check():
    conn = await asyncpg.connect(
        "postgresql://postgres.hguowryelazzofkgpidt:OjhaVipransh@aws-1-ap-south-1.pooler.supabase.com:6543/postgres",
        statement_cache_size=0
    )
    u = await conn.fetchval("SELECT COUNT(*) FROM users")
    d = await conn.fetchval("SELECT COUNT(*) FROM user_drafts")
    f = await conn.fetchval("SELECT COUNT(*) FROM fantasy_teams")
    p = await conn.fetchval("SELECT COUNT(*) FROM players")
    print(f"Users: {u}, Drafts: {d}, Fantasy Teams: {f}, Players: {p}")
    await conn.close()

loop = asyncio.new_event_loop()
loop.run_until_complete(check())
loop.close()
