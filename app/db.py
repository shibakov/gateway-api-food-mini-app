import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Callable

import asyncpg

from .config import get_settings


class Database:
    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None
        self._lock = asyncio.Lock()

    async def get_pool(self) -> asyncpg.Pool:
        if self._pool:
            return self._pool

        async with self._lock:
            if self._pool:
                return self._pool

            settings = get_settings()
            self._pool = await asyncpg.create_pool(
                settings.database_url,
                min_size=settings.db_pool_min_size,
                max_size=settings.db_pool_max_size,
                timeout=settings.db_pool_timeout,
                command_timeout=settings.db_command_timeout,
                statement_cache_size=0,
            )
            return self._pool

    @asynccontextmanager
    async def connection(self) -> AsyncIterator[asyncpg.Connection]:
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            yield conn


database = Database()


async def get_connection() -> AsyncIterator[asyncpg.Connection]:
    async with database.connection() as conn:
        yield conn


async def transactional(conn: asyncpg.Connection, func: Callable[..., AsyncIterator]) -> None:
    async with conn.transaction():
        await func(conn)
