import psycopg2
from logging import Logger
from typing import List, Tuple, Any
from utils import MyDBConnectionFetch, MyDBConnectionTransaction


def insert_many_db(db_configuration: dict, query: str, logger: Logger, values: List[Tuple[Any, ...]]) -> str:
    try:
        with MyDBConnectionTransaction(configuration_parameters=db_configuration, logger=logger) as (conn, cur):
            cur.executemany(query, values)
    except psycopg2.Error as err:
        logger.exception("Postgres database connector related error occurred", exc_info=err)
    except Exception as err:
        logger.exception("Unhanded non database connector related error occurred", exc_info=err)
    else:
        return query


def update_db(db_configuration: dict, query: str, logger: Logger) -> str:
    try:
        with MyDBConnectionTransaction(configuration_parameters=db_configuration, logger=logger) as (conn, cur):
            cur.execute(query)
    except psycopg2.Error as err:
        logger.exception("Postgres database connector related error occurred", exc_info=err)
    except Exception as err:
        logger.exception("Unhanded non database connector related error occurred", exc_info=err)
    else:
        return query


def fetch_from_db(db_configuration: dict, query: str, logger: Logger) -> List[Tuple[Any, ...]]:
    try:
        with MyDBConnectionFetch(configuration_parameters=db_configuration, logger=logger) as (conn, cur):
            cur.execute(query)
    except psycopg2.Error as err:
        logger.exception("Postgres database connector related error occurred", exc_info=err)
    except Exception as err:
        logger.exception("Unhanded non database connector related error occurred", exc_info=err)
    else:
        return cur.fetchall()

