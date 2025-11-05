"""
Module: postgres_schema_manager

Purpose:
--------
Provides utilities for managing PostgreSQL database objects including
databases, roles, schemas, tables, and permissions.

Key Features:
-------------
- Executes SQL scripts for creating and dropping databases and roles
- Grants permissions on databases and tables
- Reads and executes table creation queries from JSON mappings
- Logs execution outcomes for traceability and debugging

Environment Variables Required:
-------------------------------
- SQL_PATH: Base path for SQL script storage
- DB_ROLE: Role name used in role-related operations

Dependencies:
-------------
- decouple: For environment variable management
- db.postgresql: PostgreSQL connection utilities
- db.postgresql_queries: Query execution helpers
- utils.file_handler: JSON and SQL file readers
- utils.logging_handler: Custom logger for error tracking

Example Usage:
--------------
    success = create_pg_database("analytics_db")
    if success:
        grant_pg_database_permissions("analytics_db")
"""


from decouple import config

import db.postgresql as db
import db.postgresql_queries as q
import utils.file_handler as fh
from utils.logging_handler import logger as log

DESTINATION_PATH = f"{config("SQL_PATH")}\\destination"


def drop_pg_database(database: str) -> bool:
    """
    Drops a PostgreSQL database using a predefined SQL script.

    Parameters:
    ----------
    database : str
        Name of the database to drop.

    Returns:
    -------
    bool
        True if the script executed successfully, False otherwise.

    Notes:
    ------
    - Uses db_database__DROP.sql from the destination path.
    - Logs success or failure with script name.
    """

    success = False

    try:
        path = f"{DESTINATION_PATH}\\db_database__DROP.sql"
        index = path.rfind('\\')+1
        sql_script = path[index:].strip()

        # create database
        success = q.pg_query_from_file(
            path=path,
            database=database,
            use_default=True
        )

        if success:
            log.info(f"🟢 SUCCESS: {sql_script} executed.")
        else:
            log.error(f"🔴 FAILED: {sql_script} not executed.")

        return success

    except Exception as e:  # pylint: disable-broad-except
        log.error(f"🔴 ERROR: {e}", exc_info=True)


def drop_pg_role(database: str, use_default: bool) -> bool:
    """
    Drops a PostgreSQL role using a predefined SQL script.

    Parameters:
    ----------
    database : str
        Target database for role execution.
    use_default : bool
        Whether to use the default database from environment config.

    Returns:
    -------
    bool
        True if the role was dropped successfully, False otherwise.

    Notes:
    ------
    - Uses db_role__DROP.sql from the destination path.
    - Logs failure with role name from environment if unsuccessful.
    """

    success = False

    try:
        path = f"{DESTINATION_PATH}\\db_role__DROP.sql"
        index = path.rfind('\\')+1
        sql_script = path[index:].strip()

        # drop role
        success = q.pg_query_from_file(
            path=path,
            database=database,
            use_default=use_default
        )

        if success:
            log.info(f"🟢 SUCCESS: {sql_script} executed.")
        else:
            log.error(f"🔴 FAILED: {sql_script} not executed.")

        return success

    except Exception as e:
        log.error(f"🔴 FAILED: {config("DB_ROLE")} was not dropped.")
        log.error(e, exc_info=True)


def create_pg_database(database: str) -> bool:
    """
    Creates a PostgreSQL database using a predefined SQL script.

    Parameters:
    ----------
    database : str
        Name of the database to create.

    Returns:
    -------
    bool
        True if the database was created successfully, False otherwise.

    Notes:
    ------
    - Uses db_database__CREATE.sql from the destination path.
    - Logs execution status with script name.
    """

    success = False

    try:
        path = f"{DESTINATION_PATH}\\db_database__CREATE.sql"
        index = path.rfind('\\')+1
        sql_script = path[index:].strip()

        # create database
        success = q.pg_query_from_file(
            path=path,
            database=database,
            use_default=True
        )

        if success:
            log.info(f"🟢 SUCCESS: {sql_script} executed.")
        else:
            log.error(f"🔴 FAILED: {sql_script} not executed.")

        return success

    except Exception as e:  # pylint: disable-broad-except
        log.error(f"🔴 ERROR: {e}", exc_info=True)


def create_pg_role(database: str) -> bool:
    """
    Creates a PostgreSQL role using a predefined SQL script.

    Parameters:
    ----------
    database : str
        Target database for role creation.

    Returns:
    -------
    bool
        True if the role was created successfully, False otherwise.

    Notes:
    ------
    - Skips execution if database name contains "_test".
    - Uses db_role__CREATE.sql from the destination path.
    """

    success = False

    try:
        path = f"{DESTINATION_PATH}\\db_role__CREATE.sql"
        index = path.rfind('\\')+1
        sql_script = path[index:].strip()

        # create role
        if "_test" not in database:
            success = q.pg_query_from_file(
                path=path,
                database=database,
                use_default=True
            )

        if success:
            log.info(f"🟢 SUCCESS: {sql_script} executed.")
        else:
            log.error(f"🔴 FAILED: {sql_script} not executed.")

        return success

    except Exception as e:  # pylint: disable-broad-except
        log.error(f"🔴 FAILED: {database} was not dropped.")
        log.error(e, exc_info=True)


def grant_pg_database_permissions(database: str) -> bool:
    """
    Grants permissions on a PostgreSQL database using a predefined SQL script.

    Parameters:
    ----------
    database : str
        Target database for permission grants.

    Returns:
    -------
    bool
        True if permissions were granted successfully, False otherwise.

    Notes:
    ------
    - Uses db_database__GRANT.sql from the destination path.
    """

    success = False

    try:
        path = f"{DESTINATION_PATH}\\db_database__GRANT.sql"
        index = path.rfind('\\')+1
        sql_script = path[index:].strip()

        # grant database permissions
        success = q.pg_query_from_file(
            path=path,
            database=database,
            use_default=True
        )

        if success:
            log.info(f"🟢 SUCCESS: {sql_script} executed.")
        else:
            log.error(f"🔴 FAILED: {sql_script} not executed.")

        return success

    except Exception as e:  # pylint: disable-broad-except
        log.error(e, exc_info=True)

    return success


def create_pg_database_schemas(database: str):
    """
    Creates schemas within a PostgreSQL database using a predefined SQL script.

    Parameters:
    ----------
    database : str
        Target database for schema creation.

    Returns:
    -------
    bool
        True if schemas were created successfully, False otherwise.

    Notes:
    ------
    - Uses db_schemas__CREATE.sql from the destination path.
    """

    success = False
    try:
        path = f"{DESTINATION_PATH}\\db_schemas__CREATE.sql"
        index = path.rfind('\\')+1
        sql_script = path[index:].strip()

        # create database schemas
        success = q.pg_query_from_file(
            path=path,
            database=database,
            use_default=False
        )

        if success:
            log.info(f"🟢 SUCCESS: {sql_script} executed.")
        else:
            log.error(f"🔴 FAILED: {sql_script} not executed.")

        return success

    except Exception as e:  # pylint: disable-broad-except
        log.error(e, exc_info=True)


def grant_pg_table_permissions(database: str) -> bool:
    """
    Grants permissions on tables and schemas in a PostgreSQL database.

    Parameters:
    ----------
    database : str
        Target database for permission grants.

    Returns:
    -------
    bool
        True if permissions were granted successfully, False otherwise.

    Notes:
    ------
    - Uses db_role__GRANT.sql from the destination path.
    """

    success = False
    try:
        path = f"{DESTINATION_PATH}\\db_role__GRANT.sql"
        index = path.rfind('\\')+1
        sql_script = path[index:].strip()

        # grant permissions on database tables and schemas
        success = q.pg_query_from_file(
            path=path,
            database=database,
            use_default=False
        )

        if success:
            log.info(f"🟢 SUCCESS: {sql_script} executed.")
        else:
            log.error(f"🔴 FAILED: {sql_script} not executed.")

        return success

    except Exception as e:  # pylint: disable-broad-except
        log.error(e, exc_info=True)


def create_pg_tables(database: str, file: str) -> bool:
    """
    Creates tables in a PostgreSQL database using queries defined in a JSON
    mapping file.

    Parameters:
    ----------
    database : str
        Target database for table creation.
    file : str
        JSON file containing table creation mappings.

    Returns:
    -------
    bool
        True if all tables were created successfully, False otherwise.

    Exceptions:
    ----------
    FileNotFoundError:
        Raised if any referenced SQL file is missing or empty.

    Notes:
    ------
    - Reads table creation scripts from DESTINATION_PATH.
    - Uses db.set_pg_connection and q.pg_query for execution.
    - Logs success or failure for each table script.
    """

    success = False

    try:
        success, queries = fh.read_json_file("Destination Mapping", file)

        if queries[1]:

            for table in queries:
                item = table['destination_query_create']
                path = f"{DESTINATION_PATH}\\{item}"
                index = path.rfind('\\')+1
                sql_script = path[index:].strip()

                success, query = fh.read_query_from_file(path)

                if not success:
                    log.error(f"🔴 ERROR: {sql_script} is empty.")
                    raise FileNotFoundError

                conn = db.set_pg_connection(database, use_default=False)

                success = q.pg_query(conn, database, query)

                if success:
                    log.info(f"🟢 SUCCESS: {sql_script} executed.")
                else:
                    log.error(f"🔴 FAILED: {sql_script} not executed.")

        return success

    except FileNotFoundError as error:
        log.error(error, exc_info=True)

    except Exception as e:  # pylint: disable=broad-except
        log.error(e, exc_info=True)
