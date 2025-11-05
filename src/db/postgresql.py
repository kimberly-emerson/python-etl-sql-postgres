"""
Module: postgresql

This module provides utilities for establishing a PostgreSQL database
connection using credentials and configuration values stored in environment
variables.

Key Features:
- Dynamically selects between default and custom database names
- Handles connection errors with contextual logging and user-friendly messages
- Supports autocommit mode for transactional consistency

Environment Variables Required:
- SQL_PATH: Base path for SQL-related operations
- POSTGRES_DB_NAME: Default database name
- POSTGRESQL_HOSTNAME: Hostname of the PostgreSQL server
- POSTGRESQL_PORT: Port number for the PostgreSQL server
- POSTGRES_DB_USERNAME: Username for authentication
- POSTGRES_DB_PASSWORD: Password for authentication

Dependencies:
- psycopg2: PostgreSQL adapter for Python
- python-decouple: For secure environment variable management
- utils.logging_handler: Custom logger for error tracking

Example Usage:
    conn = set_pg_connection("analytics_db")
    if conn:
        # Proceed with queries
"""

from psycopg2 import connect, OperationalError
from decouple import config

from utils.logging_handler import logger as log


DESTINATION_PATH = f"{config("SQL_PATH")}\\destination"


def set_pg_connection(database: str, use_default: bool = False):
    """
    Establishes a connection to a PostgreSQL database using psycopg2.

    Parameters:
    ----------
    database : str
        The name of the database to connect to. Ignored if `use_default` is
        True.
    use_default : bool, optional
        If True, uses the default database name from environment
        config(`POSTGRES_DB_NAME`).
        If False, uses the provided `database` argument.

    Returns:
    -------
    psycopg2.extensions.connection or None
        A PostgreSQL connection object if successful, otherwise None.

    Raises:
    ------
    OperationalError
        Catches and logs connection errors such as authentication failure or
        server unavailability.

    Logging:
    -------
    - Logs detailed error messages with traceback using the custom logger.
    - Prints user-friendly hints for common connection issues.

    Example:
    -------
    >>> conn = set_pg_connection("sales_db")
    >>> if conn:
    >>>     # Use conn to execute queries
    """

    try:
        db: str = None
        if use_default:
            db = config("POSTGRES_DB_NAME")
        else:
            db = database

        conn = connect(
            host=config("POSTGRESQL_HOSTNAME"),
            port=config("POSTGRESQL_PORT"),
            database=db,
            user=config("POSTGRES_DB_USERNAME"),
            password=config("POSTGRES_DB_PASSWORD"),
        )
        conn.autocommit = True

    except OperationalError as error:
        log.error(f"🔴 ERROR: {error}", exc_info=True)
        if "password authentication failed" in str(error):
            print("Check your username and password.")
        elif "connection refused" in str(error):
            print("Ensure the PostgreSQL server is running and \
                    accessible.")
        return None

    return conn
