"""
tba
"""

import os
import logging

from db.postgresql import build_pg_database, drop_pg_database
from build.create_destination_tables import create_pg_tables
from build.truncate_destination_tables import truncate_pg_tables
from extract.get_source_data import get_source_data
from load.insert_source_data import insert_pg_tables
from utils.query_mapping_handler import (
  get_source_mapping_data,
  get_destination_mapping_data,
  write_mapping_data
)

SQL_PATH = os.getenv('SQL_PATH')
SOURCE_FILE = f"{SQL_PATH}\\mapping_source.json"
DESTINATION_FILE = f"{SQL_PATH}\\mapping_destination.json"
TRUNCATE_FILE = f"{SQL_PATH}\\destination\\db_tables__TRUNCATE.sql"


def main():
    """
    tba
    """

    logging.getLogger('main')

    source = get_source_mapping_data(f"{SQL_PATH}\\mapping.csv")
    write_mapping_data(source, SOURCE_FILE)

    destination = get_destination_mapping_data(f"{SQL_PATH}\\mapping.csv")
    write_mapping_data(destination, DESTINATION_FILE)

    build = os.getenv("AW_SALES_DB_BUILD")

    match build:

        case "0":

            logging.info("------ TRUNCATE TABLES ------")
            # execute truncate queries in destination
            truncate_pg_tables(TRUNCATE_FILE)

        case "1":

            logging.info("------ DROP DATABASE ------")
            # drop database
            # drop role
            drop_pg_database()

            logging.info("------ BUILD DATABASE ------")
            # create database
            # create role
            # grant database permissions
            # create schemas
            # grant schema and table permissions
            build_pg_database()

            logging.info("------ CREATE TABLES ------")
            # execute create table queries
            create_pg_tables(DESTINATION_FILE)

    logging.info("------ GET SOURCE DATA ------")
    # execute select queries to get source data
    source_data = get_source_data(SOURCE_FILE)

    logging.info("------ INSERT SOURCE DATA ------")
    # execute insert queries to insert source data
    insert_pg_tables(DESTINATION_FILE, source_data)


if __name__ == "__main__":
    main()
