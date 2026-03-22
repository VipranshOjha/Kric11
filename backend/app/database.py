from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./kric11.db")

# Detect if we're using Postgres (Supabase) or SQLite (local dev)
_is_postgres = DATABASE_URL.startswith("postgresql")

engine_kwargs = {
    "echo": not _is_postgres,  # Quiet logs in production
}

if _is_postgres:
    # Supabase Transaction Pooler (port 6543) requires these settings:
    # - NullPool: prevents connection leaks in serverless (Vercel)
    # - prepared_statement_cache_size=0: asyncpg conflicts with pgbouncer's
    #   transaction-mode pooling when prepared statements are cached
    # - statement_cache_size=0: same reason — disable all client-side caching
    engine_kwargs["poolclass"] = NullPool
    engine_kwargs["connect_args"] = {
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0,
    }

engine = create_async_engine(DATABASE_URL, **engine_kwargs)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
