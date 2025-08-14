"""
tba
"""

import os
import logging
from db.postgresql import build_pg_database
from build.create_destination_tables import create_pg_tables
from build.truncate_destination_tables import truncate_pg_tables
from extract.get_source_data import get_source_data
from load.insert_source_data import insert_pg_tables
    
LOGS_PATH = os.getenv("LOGS_PATH")
SQL_PATH = os.getenv('SQL_PATH')
SOURCE_FILE = f"{SQL_PATH}\\mapping_source.json"
DESTINATION_FILE = f"{SQL_PATH}\\mapping_destination.json"
TRUNCATE_FILE = f"{SQL_PATH}\\destination\\db_tables__TRUNCATE.sql"

logging.basicConfig(
    filename=f"{LOGS_PATH}\\app.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def main():
    """
    tba
    """

    build = os.getenv("AW_SALES_DB_BUILD")
    
    if build == "1":
    
        # create database
        # create role
        # grant database permissions
        # create schemas
        # grant schema and table permissions
        build_pg_database()

        # execute create table queries    
        create_pg_tables(DESTINATION_FILE)

    # execute truncate queries in destination
    # truncate_pg_tables(TRUNCATE_FILE)
    
    # execute select queries to get source data
    source_data = get_source_data(SOURCE_FILE)

    # execute insert queries to insert source data
    insert_pg_tables(DESTINATION_FILE, source_data)
 

if __name__ == "__main__":
    main()
