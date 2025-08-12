"""
tba
"""

import os
import logging
from dotenv import load_dotenv
from pyodbc import connect, DatabaseError, Error
# from utils.read_files import read_query_from_file

load_dotenv()

SQL_PATH = os.getenv("SQL_PATH")


def execute_sql_query(conn=None, query=None):
    """
    tba
    """

    records = None

    try:
        if conn is None:
            conn = connect(os.getenv("ADVENTUREWORKS_DB"))

        cursor = conn.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        conn.commit()
        cursor.close()
    except DatabaseError as error:
        if conn:
            conn.rollback()
            logging.error(error)
    except Error as error:
        if conn:
            conn.rollback()
            logging.error(error)
    finally:
        if conn:
            conn.close()

    return records
