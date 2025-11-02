"""
SQL Server Query Execution Module
=================================

This module provides a utility function for executing SQL queries against a
SQL Server database using `pyodbc`. It supports dynamic connection handling,
result parsing, and structured error logging.

Overview
--------

The module performs the following operations:

- Establishes a connection to SQL Server using an environment-defined DSN.
- Executes a SQL query and fetches all results.
- Converts query results into a list of row-wise lists.
- Commits transactions and handles rollback on error.
- Logs query failures and connection issues.

Environment Configuration
-------------------------

- ``SQL_PATH``: Used for locating SQL assets or scripts (not directly used in
this function).
- ``ADVENTUREWORKS_DB``: ODBC connection string or DSN for the target SQL
Server database.

Dependencies
------------

- ``logging``: Standard Python logging module.
- ``decouple.config``: For environment variable access.
- ``pyodbc.connect``: For establishing SQL Server connections.

Functions
---------

.. function:: execute_sql_query(conn, query: str = None)

   Executes a SQL query against a SQL Server database and returns the results.

   :param conn: Optional active database connection. If ``None``, a new
   connection is created using the ``ADVENTUREWORKS_DB`` environment variable.
   :type conn: pyodbc.Connection or None
   :param query: SQL query string to be executed.
   :type query: str
   :return: List of rows, where each row is a list of column values.
   :rtype: list[list[Any]]

   **Execution Flow:**

   - If no connection is provided, a new one is created using the configured
   DSN.
   - Executes the query and fetches all rows.
   - Converts each row to a list and appends to the result set.
   - Commits the transaction and closes the cursor.
   - Rolls back and logs errors on failure.
   - Closes the connection in all cases.

   **Logging Behavior:**

   - Logs the query and error message on `DatabaseError`.
   - Logs generic errors on `Error`.
   - Ensures rollback and connection closure on failure.

   **Example Usage:**

   .. code-block:: python

      results = execute_sql_query(
          conn=None,
          query="SELECT TOP 10 * FROM Sales.SalesOrderHeader"
      )
"""

import logging
from decouple import config
from pyodbc import connect, DatabaseError, Error


SQL_PATH = config("SQL_PATH")


def execute_sql_query(conn, query: str = None):
    """
     Executes a SQL query against a SQL Server database and returns the results.

    :param conn: Optional active database connection. If ``None``, a new
    connection is created using the ``ADVENTUREWORKS_DB`` environment variable.
    :type conn: pyodbc.Connection or None
    :param query: SQL query string to be executed.
    :type query: str
    :return: List of rows, where each row is a list of column values.
    :rtype: list[list[Any]]

    **Execution Flow:**

    - If no connection is provided, a new one is created using the configured
    DSN.
    - Executes the query and fetches all rows.
    - Converts each row to a list and appends to the result set.
    - Commits the transaction and closes the cursor.
    - Rolls back and logs errors on failure.
    - Closes the connection in all cases.

    **Logging Behavior:**

    - Logs the query and error message on `DatabaseError`.
    - Logs generic errors on `Error`.
    - Ensures rollback and connection closure on failure.

    **Example Usage:**

    .. code-block:: python

       results = execute_sql_query(
           conn=None,
           query="SELECT TOP 10 * FROM Sales.SalesOrderHeader"
       )
    """

    rows = list()
    data = list()

    try:
        if conn is None:
            conn = connect(config("ADVENTUREWORKS_DB"))

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
