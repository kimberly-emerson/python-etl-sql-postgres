from string import Template
from decouple import config
from psycopg2 import Error, IntegrityError, OperationalError
from psycopg2.extras import execute_batch

import db.postgresql as db
import utils.file_handler as fh
from utils.logging_handler import logger as log


def pg_query(
        conn, database: str, query: str, values: list = []) -> bool:
    """
    """
    success: bool = False

    if conn is None:
        # set connection to postgres
        # default administrative connection database
        conn = db.set_pg_connection(database)

    # create cursor
    cursor = conn.cursor()

    try:

        if values:
            # execute insert query if values list injected
            execute_batch(cursor, query, values, page_size=100)

        else:
            # execute other queries if no values list injected
            cursor.execute(query)

        if "$password" in query:
            query = Template(query).substitute(
                password=config("DB_ROLE_PASSWORD"),
            )

        success = True
        conn.commit()

        return success

    except IntegrityError as error:
        if conn:
            conn.rollback()
        log.error(error, exc_info=True)

    except OperationalError as error:
        if conn:
            conn.rollback()
        log.error(error, exc_info=True)

    except Error as error:
        if conn:
            conn.rollback()
        log.error(error, exc_info=True)

    except Exception as e:
        if conn:
            conn.rollback()
        log.error(e, exc_info=True)

    finally:
        if conn:
            cursor.close()
            conn.close()


def pg_query_from_file(
        path: str, database: str, use_default: bool) -> bool:
    """
    """

    success: bool = False

    try:

        success, query = fh.read_query_from_file(path)

        if "$database" in query:
            query = Template(query).substitute(
                database=database,
            )

        if "$password" in query:
            query = Template(query).substitute(
                password=config("DB_ROLE_PASSWORD"),
            )

        conn = db.set_pg_connection(database, use_default)

        success = pg_query(conn, database, query)
        return success

    except Exception as e:  # pylint: disable=broad-except
        log.error(e, exc_info=True)
