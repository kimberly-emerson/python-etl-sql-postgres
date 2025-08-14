"""
tba
"""

import os
import logging
from dotenv import load_dotenv
from pyodbc import connect, DatabaseError, Error

load_dotenv()

SQL_PATH = os.getenv("SQL_PATH")


def execute_sql_query(conn, query: str = None):
    """
    tba
    """

    rows = list()
    data = list()

    try:
        if conn is None:
            conn = connect(os.getenv("ADVENTUREWORKS_DB"))

        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            data.append(list(row))

        conn.commit()
        cursor.close()

    except DatabaseError as error:
        if conn:
            conn.rollback()
            logging.error(f"QUERY: {query}, {error}")

    except Error as error:
        if conn:
            conn.rollback()
            logging.error(error)

    finally:
        if conn:
            conn.close()

    return data
