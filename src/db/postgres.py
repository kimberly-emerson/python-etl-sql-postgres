"""
PostgreSQL Setup and Execution Module

This module provides a structured interface for initializing and configuring a PostgreSQL
database environment using SQL scripts. It includes utilities for establishing connections,
executing queries, and orchestrating multi-step database provisioning workflows.

Core Components:
----------------
- `execute_pg_query(conn=None, query=None)`:
    Executes a SQL query with automatic commit, rollback on error, and connection cleanup.
    If no connection is provided, one is created from environment variables.

- `set_pg_connection(database=None)`:
    Returns a PostgreSQL connection object based on the specified database context.
    Supports switching between default and "aw_sales" databases.

- `pg_build(path=None, database=None)`:
    Reads a SQL query from a file and executes it on the target database.
    Combines query loading, connection setup, and execution into a single step.

- `build_pg_database()`:
    Orchestrates the full database setup by executing a predefined sequence of SQL scripts
    for creating databases, roles, schemas, and permissions.

Environment Variables:
----------------------
- `SQL_PATH`: Root directory for SQL script files.
- `POSTGRESQL_HOSTNAME`: Hostname of the PostgreSQL server.
- `POSTGRESQL_PORT`: Port number for the PostgreSQL server.
- `POSTGRES_DB_NAME`: Default database name.
- `AW_SALES_DB_NAME`: Alternate database name for "aw_sales" context.
- `POSTGRES_DB_USERNAME`: Username for database authentication.
- `POSTGRES_DB_PASSWORD`: Password for database authentication.

Assumptions:
------------
- SQL scripts are stored under `SQL_PATH\\destination\\` with structured filenames.
- The utility `read_query_from_file` is available and correctly implemented.
- psycopg2 is installed and accessible for database operations.

Logging:
--------
- Errors during query execution or connection setup are logged using Python's `logging` module.
- A success message is logged upon completion of the full database build.

Usage Example:
--------------
To provision the database environment:
    >>> build_pg_database()

To execute a specific SQL script:
    >>> pg_build(path="path/to/script.sql", database="aw_sales")

Notes:
------
- This module is designed for setup and provisioning, not for querying or data retrieval.
- Transactions are committed automatically; rollback occurs only on failure.
- Connections are closed after each operation to ensure resource cleanup.
"""

import os
import logging
from psycopg2 import connect, DatabaseError, Error
from utils.read_files import read_query_from_file

SQL_PATH = os.getenv("SQL_PATH")


def execute_pg_query(conn=None, query=None):
    """
    Executes a SQL query on a PostgreSQL database with automatic commit, rollback, and cleanup.

    This function runs the provided SQL query using a PostgreSQL connection. If no connection
    is passed, it creates one using environment variables:
    - POSTGRESQL_HOSTNAME
    - POSTGRESQL_PORT
    - POSTGRES_DB_NAME
    - POSTGRES_DB_USERNAME
    - POSTGRES_DB_PASSWORD

    After executing the query, it commits the transaction. If an error occurs, it rolls back
    the transaction and logs the error. The connection and cursor are closed in all cases.

    Parameters:
        conn (psycopg2.connection, optional): An existing PostgreSQL connection object.
            If None, a new connection is created from environment variables.
        query (str, optional): The SQL query string to execute.

    Returns:
        None

    Exceptions:
        - Logs any `psycopg2.DatabaseError` or `psycopg2.Error` encountered during execution.
        - Rolls back the transaction if an error occurs and a connection is active.

    Notes:
        - This function is suitable for executing non-returning SQL statements (e.g., DDL, DML).
        - It handles both connection creation and cleanup, making it safe for standalone use.
        - If a connection is passed in, it will still be closed after execution.
        - For queries requiring result retrieval, extend this function or use a separate utility.
    """

    try:
        if conn is None:
            conn = connect(
                host=os.getenv("POSTGRESQL_HOSTNAME"),
                port=os.getenv("POSTGRESQL_PORT"),
                database=os.getenv("POSTGRES_DB_NAME"),
                user=os.getenv("POSTGRES_DB_USERNAME"),
                password=os.getenv("POSTGRES_DB_PASSWORD"),
            )

        cursor = conn.cursor()
        cursor.execute(query)
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


def set_pg_connection(database=None):
    """
    Establishes a PostgreSQL connection based on the specified database context.

    This function creates and returns a PostgreSQL connection object using environment
    variables for configuration. If the `database` argument is `"aw_sales"`, it connects
    to the AW Sales database using `AW_SALES_DB_NAME`. Otherwise, it defaults to the
    general database specified by `POSTGRES_DB_NAME`.

    All connections are configured with `autocommit = True`.

    Parameters:
        database (str, optional): The name of the target database context.
            If `"aw_sales"`, connects to the AW Sales database.
            Otherwise, connects to the default PostgreSQL database.

    Returns:
        psycopg2.connection: A live PostgreSQL connection object with autocommit enabled.

    Environment Variables:
        - POSTGRESQL_HOSTNAME
        - POSTGRESQL_PORT
        - AW_SALES_DB_NAME (used if database == "aw_sales")
        - POSTGRES_DB_NAME (used for default connection)
        - POSTGRES_DB_USERNAME
        - POSTGRES_DB_PASSWORD

    Notes:
        - Caller is responsible for closing the connection after use.
        - This function does not validate the database name beyond simple matching.
    """

    conn = None

    match database:
        case "aw_sales":
            conn = connect(
                host=os.getenv("POSTGRESQL_HOSTNAME"),
                port=os.getenv("POSTGRESQL_PORT"),
                database=os.getenv("AW_SALES_DB_NAME"),
                user=os.getenv("POSTGRES_DB_USERNAME"),
                password=os.getenv("POSTGRES_DB_PASSWORD"),
            )
            conn.autocommit = True
        case _:
            conn = connect(
                host=os.getenv("POSTGRESQL_HOSTNAME"),
                port=os.getenv("POSTGRESQL_PORT"),
                database=os.getenv("POSTGRES_DB_NAME"),
                user=os.getenv("POSTGRES_DB_USERNAME"),
                password=os.getenv("POSTGRES_DB_PASSWORD"),
            )
            conn.autocommit = True

    return conn


def build_pg_database():
    """
    Orchestrates the creation and configuration of a PostgreSQL database environment.

    This function executes a series of SQL scripts to:
    1. Create the database.
    2. Create roles.
    3. Grant permissions on the database.
    4. Create schemas within the `aw_sales` database.
    5. Grant role permissions within the `aw_sales` database.

    The SQL scripts are expected to be located in the `destination` subdirectory
    of the global `SQL_PATH` variable, with filenames following a structured naming convention.

    Execution Order:
        - db_database__CREATE.sql
        - db_role__CREATE.sql
        - db_database__GRANT.sql
        - db_schemas__CREATE.sql (targeting "aw_sales" database)
        - db_role__GRANT.sql (targeting "aw_sales" database)

    Returns:
        None

    Side Effects:
        - Executes SQL scripts against PostgreSQL databases.
        - Logs a success message upon completion.
        - Relies on the `pg_build` function to handle execution and error logging.

    Notes:
        - Assumes `SQL_PATH` is a globally defined variable.
        - Assumes supporting SQL files exist and are syntactically correct.
        - No rollback or transactional safety is implemented.
    """

    db_create_path = f"{SQL_PATH}\\destination\\db_database__CREATE.sql"
    db_grant_path = f"{SQL_PATH}\\destination\\db_database__GRANT.sql"
    role_create_path = f"{SQL_PATH}\\destination\\db_role__CREATE.sql"
    schemas_create_path = f"{SQL_PATH}\\destination\\db_schemas__CREATE.sql"
    role_grant_path = f"{SQL_PATH}\\destination\\db_role__GRANT.sql"

    pg_build(path=db_create_path, database=None)
    pg_build(path=role_create_path, database=None)
    pg_build(path=db_grant_path, database=None)
    pg_build(path=schemas_create_path, database="aw_sales")
    pg_build(path=role_grant_path, database="aw_sales")

    logging.info("SUCCESS: Database build completed.")


def pg_build(path=None, database=None):
    """
    Reads a SQL query from a file and executes it on a specified PostgreSQL database.

    This function coordinates three operations:
    1. Reads a query string from the file at the given `path`.
    2. Establishes a PostgreSQL connection based on the `database` context.
    3. Executes the query using the established connection.

    Parameters:
        path (str, optional): Path to the file containing the SQL query.
        database (str, optional): Name of the target database context.
            If `"aw_sales"`, connects to the AW Sales database.
            Otherwise, connects to the default PostgreSQL database.

    Returns:
        None

    Exceptions:
        Logs any exception that occurs during query reading, connection setup,
        or query execution. Errors are not re-raised.

    Notes:
        - Assumes supporting functions `read_query_from_file`, `set_pg_connection`,
          and `execute_pg_query` are defined and properly handle their own exceptions.
        - This function does not return results or confirm success.
    """
    try:
        query = read_query_from_file(path)
        conn = set_pg_connection(database)
        execute_pg_query(conn, query)
    except Exception as e:  # pylint: disable=broad-except
        logging.error(e)
