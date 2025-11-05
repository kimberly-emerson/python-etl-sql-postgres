"""
Module: sql_server
==================

Purpose:
--------
Provides a utility function to execute SQL Server queries using pyodbc and
environment-based connection strings.

Key Features:
-------------
- Dynamically establishes a SQL Server connection if none is provided
- Executes arbitrary SQL queries and returns results as a list of lists
- Handles database errors with rollback and structured logging
- Ensures connection closure and transactional integrity

Environment Variables Required:
-------------------------------
- SQLSERVER_CONN : ODBC connection string for SQL Server

Dependencies:
-------------
- pyodbc : Python ODBC interface for SQL Server
- python-decouple : For secure environment variable management
- utils.logging_handler : Custom logger for error tracking

Example Usage:
--------------
    success, results = execute_sql_query(None, "SELECT * FROM employees")
    if success:
        # Process results
"""

from typing import Tuple
from decouple import config
from pyodbc import connect, DatabaseError, Error

from utils.logging_handler import logger as log


def execute_sql_query(conn, query: str = None) -> Tuple[bool, list]:
    """
    Executes a SQL query against a SQL Server database using pyodbc.

    Parameters:
    ----------
    conn : pyodbc.Connection or None
        An existing database connection. If None, a new connection is created
        using the environment variable `SQLSERVER_CONN`.
    query : str, optional
        The SQL query string to execute. Defaults to None.

    Returns:
    -------
    Tuple[bool, list]
        A tuple containing:
        - success (bool): True if query execution returned rows, False
        otherwise
        - data (list): List of rows returned from the query, each row as a
        list of column values

    Exceptions:
    ----------
    DatabaseError:
        Raised for SQL Server-specific errors. Rolls back transaction and logs
        the error.
    Error:
        Raised for general pyodbc errors. Rolls back transaction and logs the
        error.

    Logging:
    -------
    - Logs query-level errors with traceback using the custom logger
    - Includes query string in error logs for debugging

    Notes:
    ------
    - Commits transaction after successful query execution
    - Closes cursor and connection in all cases (success, error, or exception)

    Example:
    -------
    >>> success, rows = execute_sql_query(None, "SELECT TOP 10 * FROM orders")
    >>> if success:
    >>>     for row in rows:
    >>>         print(row)
    """

    success: bool = False
    rows: list = list()
    data: list = list()

    try:
        if conn is None:
            conn = connect(config("SQLSERVER_CONN"))

        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            data.append(list(row))

        conn.commit()
        cursor.close()

        if data:
            success = True

        return success, data

    except DatabaseError as error:
        if conn:
            conn.rollback()
            log.error(f"🔴 ERROR: Query {query}, {error}",
                      exc_info=True)

    except Error as error:
        if conn:
            conn.rollback()
            log.error(f"🔴 ERROR: {error}",
                      exc_info=True)

    finally:
        if conn:
            conn.close()
