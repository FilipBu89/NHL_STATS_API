from asyncpg.pool import Pool
import asyncpg
from typing import Tuple, Any, List
from logging import Logger


async def update_db_async(pool: Pool, query: str, values: List[tuple], logger: Logger) -> str:
    try:
        async with pool.acquire() as conn:
            async with conn.transaction():
                return await conn.executemany(command=query, args=values)
    except asyncpg.PostgresError as err:
        logger.exception("Postgres database connector related error occurred", exc_info=err)
    except Exception as err:
        logger.exception("Unhanded non database connector related error occurred", exc_info=err)
