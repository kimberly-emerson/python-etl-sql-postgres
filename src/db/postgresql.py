"""
PostgreSQL Administration and Query Execution Module
====================================================

This module provides utilities for executing PostgreSQL queries, managing
database connections, provisioning schema assets, and handling role and
database lifecycle operations. It integrates templated SQL execution, batch
inserts, and structured logging.

Overview
--------

The module supports:

- Executing parameterized and raw SQL queries.
- Establishing PostgreSQL connections with optional administrative privileges.
- Creating databases, roles, and schemas from SQL templates.
- Dropping roles and databases.
- Substituting template variables in SQL files.

Environment Configuration
-------------------------

The following environment variables must be defined:

- ``SQL_PATH``: Base path for SQL asset files.
- ``POSTGRESQL_HOSTNAME``: Hostname of the PostgreSQL server.
- ``POSTGRESQL_PORT``: Port number for PostgreSQL.
- ``POSTGRES_DB_NAME``: Default administrative database name.
- ``POSTGRES_DB_USERNAME``: Username for PostgreSQL authentication.
- ``POSTGRES_DB_PASSWORD``: Password for PostgreSQL authentication.
- ``DB_ROLE_PASSWORD``: Password used for role creation templates.

Functions
---------

.. function:: execute_pg_query(conn, database, query: str, values: list = [])

   Executes a SQL query against a PostgreSQL database. Supports both batch
   inserts and raw queries.

   :param conn: Optional active PostgreSQL connection. If ``None``, a new
   connection is created.
   :type conn: psycopg2.Connection or None
   :param database: Target database name.
   :type database: str
   :param query: SQL query string to execute.
   :type query: str
   :param values: Optional list of parameterized values for batch execution.
   :type values: list
   :return: ``True`` if the query executed successfully, otherwise ``False``.
   :rtype: bool

   Handles rollback and logs errors for `IntegrityError`, `OperationalError`,
   and general exceptions.

.. function:: set_pg_connection(database, use_admin=False)

   Establishes a PostgreSQL connection using environment credentials.

   :param database: Target database name.
   :type database: str
   :param use_admin: If ``True``, connects to the default admin database.
   :type use_admin: bool
   :return: PostgreSQL connection object or ``None`` on failure.
   :rtype: psycopg2.Connection or None

   Logs authentication and connectivity errors with guidance messages.

.. function:: build_pg_database(database)

   Orchestrates the creation of a PostgreSQL database, roles, schemas, and
   grants using SQL templates.

   :param database: Name of the database to create.
   :type database: str
   :return: ``True`` if all steps executed successfully, otherwise ``False``.
   :rtype: bool

   Skips role creation for databases containing ``_test``.

.. function:: drop_pg_role(database, use_admin)

   Drops a PostgreSQL role using a predefined SQL template.

   :param database: Target database name.
   :type database: str
   :param use_admin: If ``True``, uses administrative connection.
   :type use_admin: bool
   :return: ``True`` if role was dropped successfully, otherwise ``False``.
   :rtype: bool

.. function:: drop_pg_database(database)

   Drops a PostgreSQL database using a force option.

   :param database: Name of the database to drop.
   :type database: str
   :return: ``True`` if the database was dropped successfully, otherwise
   ``False``.
   :rtype: bool

.. function:: pg_build(path: str, database: str, use_admin: bool)

   Reads a SQL file, substitutes template variables, and executes the query.

   :param path: Path to the SQL file.
   :type path: str
   :param database: Target database name.
   :type database: str
   :param use_admin: If ``True``, uses administrative connection.
   :type use_admin: bool
   :return: ``True`` if the query executed successfully, otherwise ``False``.
   :rtype: bool

   Supports substitution of ``$database`` and ``$password`` placeholders using
   Python's `Template`.
"""

from string import Template
from psycopg2 import connect, IntegrityError, OperationalError, Error
from psycopg2.extras import execute_batch
from decouple import config

from utils.logger import logging
from utils.file_handler import read_query_from_file

DESTINATION_PATH = f"{config("SQL_PATH")}\\destination"


def execute_pg_query(conn, database, query: str, values: list = []):
    """
    Executes a SQL query against a PostgreSQL database. Supports both batch
    inserts and raw queries.

    :param conn: Optional active PostgreSQL connection. If ``None``, a new
    connection is created.
    :type conn: psycopg2.Connection or None
    :param database: Target database name.
    :type database: str
    :param query: SQL query string to execute.
    :type query: str
    :param values: Optional list of parameterized values for batch execution.
    :type values: list
    :return: ``True`` if the query executed successfully, otherwise ``False``.
    :rtype: bool

    Handles rollback and logs errors for `IntegrityError`, `OperationalError`,
    and general exceptions.
    """
    success: bool = False

    if conn is None:
        # set connection to postgres
        # default administrative connection database
        conn = set_pg_connection(database)

    # create cursor
    cursor = conn.cursor()

    try:

        if values:
            # execute insert query if values list injected
            execute_batch(cursor, query, values, page_size=100)

        else:
            # execute other queries if no values list injected
            cursor.execute(query)

        if query.endswith("  PASSWORD 'demopass';"):
            query = query.replace("  PASSWORD 'demopass';", ";")

        logging.info(f"SUCCESS: query executed successfully.")
        success = True

        conn.commit()

    except IntegrityError as error:
        if conn:
            conn.rollback()
        logging.error(error)

    except OperationalError as error:
        if conn:
            conn.rollback()
        logging.error(error)

    except Error as error:
        if conn:
            conn.rollback()
        logging.error(error)

    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(e)

    finally:
        if conn:
            cursor.close()
            conn.close()

    return success


def set_pg_connection(database, use_admin=False):
    """
    Establishes a PostgreSQL connection using environment credentials.

    :param database: Target database name.
    :type database: str
    :param use_admin: If ``True``, connects to the default admin database.
    :type use_admin: bool
    :return: PostgreSQL connection object or ``None`` on failure.
    :rtype: psycopg2.Connection or None

    Logs authentication and connectivity errors with guidance messages.
    """

    try:
        conn = connect(
            host=config("POSTGRESQL_HOSTNAME"),
            port=config("POSTGRESQL_PORT"),
            database=config("POSTGRES_DB_NAME") if use_admin else database,
            user=config("POSTGRES_DB_USERNAME"),
            password=config("POSTGRES_DB_PASSWORD"),
        )
        conn.autocommit = True

    except OperationalError as error:
        logging.error(f"FAILURE: {error}")
        if "password authentication failed" in str(error):
            print("Check your username and password.")
        elif "connection refused" in str(error):
            print("Ensure the PostgreSQL server is running and accessible.")
        return None

    return conn


def build_pg_database(database):
    """
     Orchestrates the creation of a PostgreSQL database, roles, schemas, and
    grants using SQL templates.

    :param database: Name of the database to create.
    :type database: str
    :return: ``True`` if all steps executed successfully, otherwise ``False``.
    :rtype: bool

    Skips role creation for databases containing ``_test``.
    """

    db_create_path = f"{DESTINATION_PATH}\\db_database__CREATE.sql"
    db_grant_path = f"{DESTINATION_PATH}\\db_database__GRANT.sql"
    role_create_path = f"{DESTINATION_PATH}\\db_role__CREATE.sql"
    schemas_create_path = f"{DESTINATION_PATH}\\db_schemas__CREATE.sql"
    role_grant_path = f"{DESTINATION_PATH}\\db_role__GRANT.sql"

    # create database
    success = pg_build(path=db_create_path, database=database, use_admin=True)
    # create role
    if "_test" not in database:
        pg_build(path=role_create_path, database=database, use_admin=True)
    # grant database permissions
    success = pg_build(path=db_grant_path, database=database, use_admin=True)
    # create database schemas
    success = pg_build(path=schemas_create_path, database=database,
                       use_admin=False)
    # grant permissions on database tables and schemas
    success = pg_build(path=role_grant_path, database=database,
                       use_admin=False)
    logging.info(f"SUCCESS: {database} Database build completed.")

    return success


def drop_pg_role(database, use_admin):
    """
     Drops a PostgreSQL role using a predefined SQL template.

    :param database: Target database name.
    :type database: str
    :param use_admin: If ``True``, uses administrative connection.
    :type use_admin: bool
    :return: ``True`` if role was dropped successfully, otherwise ``False``.
    :rtype: bool
    """
    success = False

    try:
        role_drop_path = f"{DESTINATION_PATH}\\db_role__DROP.sql"
        # drop role
        pg_build(path=role_drop_path, database=database, use_admin=use_admin)
        success = True

    except Exception as e:
        logging.error(e)

    return success


def drop_pg_database(database):
    """
     Drops a PostgreSQL database using a force option.

    :param database: Name of the database to drop.
    :type database: str
    :return: ``True`` if the database was dropped successfully, otherwise
    ``False``.
    :rtype: bool
    """
    success = False
    try:
        # drop database
        query = f"DROP DATABASE IF EXISTS {database} WITH (FORCE);"
        execute_pg_query(conn=None, database="postgres", query=query,
                         values=[])
        success = True
    except Exception as e:
        logging.error(e)

    return success


def pg_build(path: str, database: str, use_admin: bool):
    """
     Reads a SQL file, substitutes template variables, and executes the query.

    :param path: Path to the SQL file.
    :type path: str
    :param database: Target database name.
    :type database: str
    :param use_admin: If ``True``, uses administrative connection.
    :type use_admin: bool
    :return: ``True`` if the query executed successfully, otherwise ``False``.
    :rtype: bool

    Supports substitution of ``$database`` and ``$password`` placeholders using
    Python's `Template`.
    """

    success: bool = False

    try:

        query: str = read_query_from_file(path)

        if "$database" in query:
            query = Template(query).substitute(
                database=database,
            )

        if "$password" in query:
            query = Template(query).substitute(
                password=config("DB_ROLE_PASSWORD"),
            )

        conn = set_pg_connection(database, use_admin)

        success = execute_pg_query(conn, database, query)

    except Exception as e:  # pylint: disable=broad-except
        logging.error(e)

    return success
