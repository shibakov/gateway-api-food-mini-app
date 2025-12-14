from collections.abc import AsyncIterator

import asyncpg
from fastapi import Depends

from .config import get_settings
from .db import get_connection


async def get_user_id() -> str:
    settings = get_settings()
    return settings.fixed_user_id


async def get_db_connection(conn: asyncpg.Connection = Depends(get_connection)) -> asyncpg.Connection:
    return conn
