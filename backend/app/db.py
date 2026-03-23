"""
Kric11 — Async database pool for Supabase via raw asyncpg.
No SQLAlchemy. No psycopg2. Just asyncpg + connection pooling.
"""
import os
import asyncpg

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.hguowryelazzofkgpidt:OjhaVipransh@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
)

_pool = None

async def get_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=1,
            max_size=5,
            statement_cache_size=0,  # Required for Supabase Transaction Pooler
        )
    return _pool

async def fetch(query, *args):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(query, *args)

async def fetchrow(query, *args):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, *args)

async def fetchval(query, *args):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval(query, *args)

async def execute(query, *args):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.execute(query, *args)
