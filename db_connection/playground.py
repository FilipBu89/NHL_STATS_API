from pathlib import Path
from typing import List, Any, Tuple
import asyncio
import asyncpg
from utils import get_db_config, get_logger, FILES_DIR, silence_event_loop_closed
from queries import *
from parse_json_for_db import *
from db_commands import update_db, insert_many_db
from db_commans_async import update_db_async
from db_param import *

DB_CONNECTION_CONFIG: Path = Path("database.ini")
PLAYERS_DIR: Path = FILES_DIR / "players"
PLAYER_STATS_DIR: Path = FILES_DIR / "player_stats"
CREATE_TABLES_QUERY: str = f"{CREATE_TEAMS_TABLE_QUERY}\n{CREATE_PLAYERS_TABLE_QUERY}"


async def main():
    # get logger for DB connection
    logger = get_logger()

    # get and parse DB connection configuration
    config = get_db_config(filename=DB_CONNECTION_CONFIG)

    create_tbl_result = update_db(
        db_configuration=config,
        logger=logger,
        query=CREATE_PLAYERS_STATS_TABLE_QUERY
    )
    print(create_tbl_result)

    insert_statements: List[str] = []
    insert_records: List[Tuple[Any, ...]] = []
    for file in PLAYER_STATS_DIR.glob("*"):
        result = parse_player_stats_insert(file=file)
        insert_statements += result[0]
        insert_records += result[1]

    async with asyncpg.create_pool(
        host=HOST,
        port=PORT,
        user=USER,
        database=DATABASE,
        password=PASSWORD
    ) as pool:
        coro_to_do = [
            update_db_async(pool=pool, query=insert_statements[i],
                            values=[insert_records[i]], logger=logger) for i in range(len(insert_statements))]

        result = await asyncio.gather(*coro_to_do, return_exceptions=True)
        # await update_db_async(pool=pool, query=insert_statements[0], values=[insert_records[0]], logger=logger)
        # await update_db_async(pool=pool, query=insert_statements[1], values=[insert_records[1]], logger=logger)
        # await update_db_async(pool=pool, query=insert_records[0], logger=logger)

if __name__ == "__main__":
    asyncio.run(main())












