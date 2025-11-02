"""
PostgreSQL Table Truncation Module
==================================

This module provides a utility function to truncate PostgreSQL tables using
SQL scripts stored in external files. It integrates query loading, database
connection setup, and execution with structured logging.

Overview
--------

The module performs the following operations:

- Reads SQL `TRUNCATE TABLE` statements from a file.
- Establishes a PostgreSQL connection.
- Executes the query against the target database.
- Logs progress and errors.

Dependencies
------------

- ``logging``: Standard Python logging module.
- ``db.postgresql``:
  - ``set_pg_connection``: Establishes a PostgreSQL connection.
  - ``execute_pg_query``: Executes SQL queries.
- ``utils.file_handler.read_query_from_file``: Reads SQL query text from file.

Functions
---------

.. function:: truncate_pg_tables(database, file: str)

   Executes a SQL `TRUNCATE TABLE` query against a PostgreSQL database using a
   query file.

   :param database: Name of the PostgreSQL database to connect to.
   :type database: str
   :param file: Path to the SQL file containing the truncate query.
   :type file: str
   :return: None

   **Execution Flow:**

   - Reads the SQL query using ``read_query_from_file``.
   - Validates that the query is not empty.
   - Establishes a PostgreSQL connection using ``set_pg_connection``.
   - Executes the query using ``execute_pg_query``.

   **Logging Behavior:**

   - Logs a warning if the query file is missing or empty.
   - Logs an error if the file is not found or if any exception occurs during
   execution.
   - Logs a success message when the query is executed.

   **Example Usage:**

   .. code-block:: python

      truncate_pg_tables(
          database="analytics_db",
          file="scripts/truncate_tables.sql"
      )
"""

import logging
from db.postgresql import execute_pg_query, set_pg_connection
from utils.file_handler import read_query_from_file


def truncate_pg_tables(database, file: str):
    """
    Executes a SQL `TRUNCATE TABLE` query against a PostgreSQL database using a
    query file.

    :param database: Name of the PostgreSQL database to connect to.
    :type database: str
    :param file: Path to the SQL file containing the truncate query.
    :type file: str
    :return: None

    **Execution Flow:**

    - Reads the SQL query using ``read_query_from_file``.
    - Validates that the query is not empty.
    - Establishes a PostgreSQL connection using ``set_pg_connection``.
    - Executes the query using ``execute_pg_query``.

    **Logging Behavior:**

    - Logs a warning if the query file is missing or empty.
    - Logs an error if the file is not found or if any exception occurs during
    execution.
    - Logs a success message when the query is executed.

    **Example Usage:**

    .. code-block:: python

       truncate_pg_tables(
           database="analytics_db",
           file="scripts/truncate_tables.sql"
       )
    """

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
