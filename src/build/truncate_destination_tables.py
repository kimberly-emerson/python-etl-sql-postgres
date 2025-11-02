"""
tba
"""

import logging
from db.postgresql import execute_pg_query, set_pg_connection
from utils.file_handler import read_query_from_file


def truncate_pg_tables(database, file: str):

    try:
        # read queries from truncate file
        query = read_query_from_file(file)

        # test if query is not empty
        if not query:
            logging.warning(f"{file} does not return a query.")
            raise FileNotFoundError

        # set database connection
        conn = set_pg_connection(database)

        # execute queries in file
        execute_pg_query(conn, query=query)

        logging.info(f"{file[49:len(file)]} executed.")

    except FileNotFoundError as error:
        logging.error(error)

    except Exception as e:  # pylint: disable=broad-except
        logging.error(e)
