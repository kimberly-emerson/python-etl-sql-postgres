"""
tba
"""
import argparse
from decouple import config

from db.postgresql import build_pg_database, drop_pg_database, drop_pg_role
from build.create_destination_tables import create_pg_tables
from extract.get_source_data import get_source_data
from load.insert_source_data import insert_pg_tables
from utils.logger import logging
from utils.query_mapping_handler import (
    get_source_mapping_data,
    get_destination_mapping_data,
    write_mapping_data,
)

SQL_PATH = config("SQL_PATH")
MAPPING_FILE = f"{SQL_PATH}\\mapping.csv"
SOURCE_FILE = f"{SQL_PATH}\\mapping_source.json"
DESTINATION_FILE = f"{SQL_PATH}\\mapping_destination.json"


def main(args):
    """
    tba
    """
    logging.getLogger("main")
    test_database = f"{args.database}_test"

    logging.info(f"Running ETL for Database: {args.database}")

    logging.info("------ DROP DATABASES ------")
    # drop database
    drop_database(args.database)
    # drop test database
    drop_database(test_database)
    logging.info("------ DROP ROLE ------")
    # drop role
    drop_role(args.database)

    logging.info("------ BUILD QUERY/TABLE MAPPINGS ------")
    # define query/table mappings
    build_mapping_data(MAPPING_FILE, SOURCE_FILE, DESTINATION_FILE)

    logging.info("------ BUILD DATABASES ------")
    # build database
    build_database(args.database)
    # build test database
    build_database(test_database)

    logging.info("------ CREATE DATABASE TABLES ------")
    # create database tables
    create_database_tables(args.database, DESTINATION_FILE)
    # create test database tables
    create_database_tables(test_database, DESTINATION_FILE)

    logging.info("------ EXTRACT SOURCE DATA ------")
    # extract table data from source database
    source_data = extract_source_data(SOURCE_FILE)

    # load source data into destination database
    logging.info("------ LOAD DESTINATION DATA ------")
    load_destination_tables(args.database, DESTINATION_FILE, source_data)

    # load source data into destination test database
    if args.seed_test_database:
        load_destination_tables(test_database, DESTINATION_FILE, source_data)

    logging.info(f"✅ ETL for Database: {args.database} completed.")


def load_destination_tables(database, destination_file, source_data):
    # execute insert queries to insert source data
    success = insert_pg_tables(database, destination_file, source_data)
    return success


def extract_source_data(source_file):
    # execute select queries to get source data
    source_data = get_source_data(source_file)
    return source_data


def create_database_tables(database, destination_file):
    # database: execute create table queries
    create_pg_tables(database, destination_file)


def build_database(database):
    # create database
    # create role
    # grant database permissions
    # create schemas
    # grant schema and table permissions
    logging.info(f"Creating Database: {database}")
    build_pg_database(database)
    logging.info(f"SUCCESS: {database} database built successfully.")


def build_mapping_data(mapping_file, source_file, destination_file):
    """
    tba
    """
    logging.info("Building Source Query/Table Mapping")
    source = get_source_mapping_data(mapping_file)
    write_mapping_data(source, source_file)
    logging.info("SUCCESS: Source Query/Table Mapping Completing")

    logging.info("Building Destination Query/Table Mapping")
    destination = get_destination_mapping_data(mapping_file)
    write_mapping_data(destination, destination_file)
    logging.info("SUCCESS: Destination Query/Table Mapping Completing")


def drop_role(database):
    """
    tba
    """
    logging.info(f"Dropping role: {config("DB_ROLE")}.")
    success = drop_pg_role(database, use_admin=True)
    logging.info("✅ SUCCESS: role successfully dropped.")
    return success


def drop_database(database) -> bool:
    """
    tba
    """
    logging.info(f"Dropping database: {database}.")
    success = drop_pg_database(database)
    logging.info(f"✅ SUCCESS: {database} successfully dropped.")
    return success


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set ETL options")

    parser.add_argument(
        "-d",
        "--database",
        type=str,
        required=True,
        help="Database Name"
    )

    parser.add_argument(
        "-s",
        "--seed-test-database",
        type=str,
        required=True,
        help="Seed Test Database"
    )

    args = parser.parse_args()

    main(args)
