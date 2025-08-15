"""
tba
"""
import os
import logging
from string import Template
from psycopg2 import connect, IntegrityError, OperationalError, Error
from psycopg2.extras import execute_batch
from utils.file_handler import read_query_from_file

DESTINATION_PATH = f"{os.getenv("SQL_PATH")}\\destination"


def execute_pg_query(conn, query: str, values: list = []):
    """
    tba
    """
    success: bool = False

    if conn is None:
        # set connection to postgres - default administrative connection database
        conn = set_pg_connection()
    
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

        logging.info(f"SUCCESS: {query}")
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


def set_pg_connection(database: str = None):
    """
    tba
    """
    
    conn = None

    try:

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

    except OperationalError as error:
        logging.error(f"FAILURE: {error}")
        if "password authentication failed" in str(error):
            print("Check your username and password.")
        elif "connection refused" in str(error):
            print("Ensure the PostgreSQL server is running and accessible.")
        return None

    return conn


def build_pg_database():
    """
    tba
    """

    db_create_path = f"{DESTINATION_PATH}\\db_database__CREATE.sql"
    db_grant_path = f"{DESTINATION_PATH}\\db_database__GRANT.sql"
    role_create_path = f"{DESTINATION_PATH}\\db_role__CREATE.sql"
    schemas_create_path = f"{DESTINATION_PATH}\\db_schemas__CREATE.sql"
    role_grant_path = f"{DESTINATION_PATH}\\db_role__GRANT.sql"

    # create database
    pg_build(path=db_create_path, database=None)
    # create role
    pg_build(path=role_create_path, database=None)
    # grant database permissions
    pg_build(path=db_grant_path, database=None)
    # create database schemas
    pg_build(path=schemas_create_path, database="aw_sales")
    # grant permissions on database tables and schemas
    pg_build(path=role_grant_path, database="aw_sales")
    logging.info("SUCCESS: Database build completed.")


def drop_pg_database():
    """
    tba
    """

    success: bool = False

    db_drop_path = f"{DESTINATION_PATH}\\db_database__DROP.sql"
    role_drop_path = f"{DESTINATION_PATH}\\db_role__DROP.sql"

    try:
        
        # drop database
        pg_build(path=db_drop_path, database=None)
        # drop role
        pg_build(path=role_drop_path, database=None)

        logging.info("SUCCESS: Database drop completed.")

    except Exception as e:
        logging.error(e)

    return success


def pg_build(path: str, database: str):
    """
    tba
    """

    success: bool = False

    try:
        
        query: str = read_query_from_file(path)

        if '$password' in query:
            query = Template(query).substitute(
                password =  os.getenv("AW_SALES_DB_PASSWORD"),
            )
        
        conn = set_pg_connection(database)
        
        success = execute_pg_query(conn, query)
    
    except Exception as e:  # pylint: disable=broad-except
        logging.error(e)

    return success
