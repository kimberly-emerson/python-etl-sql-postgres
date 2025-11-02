"""
tba
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
    tba
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
            query = query.replace("  PASSWORD 'demopass';",";")

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
    tba
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
    tba
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
    success = pg_build(path=schemas_create_path, database=database, use_admin=False)
    # grant permissions on database tables and schemas
    success = pg_build(path=role_grant_path, database=database, use_admin=False)
    logging.info(f"SUCCESS: {database} Database build completed.")

    return success


def drop_pg_role(database, use_admin):
    """
    tba
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
    tba
    """
    success = False
    try:
        # drop database
        query = f"DROP DATABASE IF EXISTS {database} WITH (FORCE);"
        execute_pg_query(conn=None, database="postgres", query=query, values=[])
        success = True
    except Exception as e:
        logging.error(e)

    return success


def pg_build(path: str, database: str, use_admin: bool):
    """
    tba
    """

    success: bool = False

    try:

        query: str = read_query_from_file(path)

        if '$database' in query:
            query = Template(query).substitute(
                database=database,
            )

        if '$password' in query:
            query = Template(query).substitute(
                password=config("DB_ROLE_PASSWORD"),
            )

        conn = set_pg_connection(database, use_admin)

        success = execute_pg_query(conn, database, query)

    except Exception as e:  # pylint: disable=broad-except
        logging.error(e)

    return success
