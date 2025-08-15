"""
tba
"""
import os
import logging
from psycopg2 import connect, DatabaseError, IntegrityError, Error
from psycopg2.extras import execute_batch
from utils.file_handler import read_query_from_file

DESTINATION_PATH = f"{os.getenv("SQL_PATH")}\\destination"


def execute_pg_query(conn, query: str, values: list = []):
    """
    tba
    """
    success = False

    if conn is None:
        # 
        conn = set_pg_connection()
    
    cursor = conn.cursor()

    try:

        if values:
            # execute insert query if values list injected
            execute_batch(cursor, query, values, page_size=100)

        else:
            # execute other queries if no values list injected
            cursor.execute(query)
    
        logging.info(f"SUCCESS: {query}")

        conn.commit()

        cursor.close()

    except DatabaseError as error:
        if conn:
            conn.rollback()
            logging.error(error)

    except IntegrityError as error:
        if conn:
            conn.rollback()
            logging.error(error)

    except ValueError as error:
        if conn:
            conn.rollback()
            logging.error(error)
    
    except SyntaxError as error:
        if conn:
            conn.rollback()
            logging.error(error)
    
    except TypeError as error:
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


def set_pg_connection(database: str = None):
    """
    tba
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


def pg_build(path: str, database: str):
    """
    tba
    """
    success: bool = False

    try:
        
        query = read_query_from_file(path)

        if "AW_SALES_DB_PASSWORD" in query:
            password: str = os.getenv("AW_SALES_PASSWORD")
            query.replace('<AW_SALES_DB_PASSWORD>', password)
        
        conn = set_pg_connection(database)
        
        execute_pg_query(conn, query)
    
    except Exception as e:  # pylint: disable=broad-except
        logging.error(e)

    return success


def drop_pg_database():
    """
    tba
    """

    success: bool = False

    try:

        db_drop_path = f"{DESTINATION_PATH}\\db_database__DROP.sql"
        role_drop_path = f"{DESTINATION_PATH}\\db_role__DROP.sql"
        
        # drop database
        pg_build(path=db_drop_path, database=None)
        # drop role
        pg_build(path=role_drop_path, database=None)

        logging.info("SUCCESS: Database build completed.")

    except Exception as e:
        logging.error(e)

    return success