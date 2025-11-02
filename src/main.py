"""
ETL Orchestration Module
=========================

This module coordinates a full ETL lifecycle for PostgreSQL databases,
including schema provisioning, role management, data extraction, and data
loading. It supports both production and test environments and is designed for
command-line execution.

Overview
--------

The module performs the following operations:

- Drops existing databases and roles.
- Builds query/table mappings from a CSV file.
- Creates databases, roles, schemas, and tables.
- Extracts source data from SQL Server.
- Loads data into PostgreSQL destination tables.
- Optionally seeds a test database.

Environment Configuration
-------------------------

The following environment variables must be defined:

- ``SQL_PATH``: Base path for SQL assets and mapping files.
- ``DB_ROLE``: Role name used for PostgreSQL provisioning.

File Paths
----------

- ``MAPPING_FILE``: Path to the CSV file containing table/query mappings.
- ``SOURCE_FILE``: Path to the generated source mapping JSON file.
- ``DESTINATION_FILE``: Path to the generated destination mapping JSON file.

Command-Line Interface
----------------------

.. code-block:: bash

   python main.py --database analytics --seed-test-database true

.. argparse::
   :module: main
   :func: parser.parse_args
   :prog: main.py

Functions
---------

.. function:: main(args)

   Entry point for the ETL process. Coordinates all steps from teardown to
   data load.

   :param args: Parsed command-line arguments.
   :type args: argparse.Namespace

.. function:: drop_database(database) -> bool

   Drops the specified PostgreSQL database.

   :param database: Name of the database to drop.
   :type database: str
   :return: ``True`` if the database was dropped successfully.
   :rtype: bool

.. function:: drop_role(database)

   Drops the PostgreSQL role associated with the target database.

   :param database: Name of the database whose role should be dropped.
   :type database: str
   :return: ``True`` if the role was dropped successfully.
   :rtype: bool

.. function:: build_mapping_data(mapping_file, source_file, destination_file)

   Generates source and destination query mappings from a CSV file and writes
   them to JSON.

   :param mapping_file: Path to the CSV mapping file.
   :type mapping_file: str
   :param source_file: Output path for source mapping JSON.
   :type source_file: str
   :param destination_file: Output path for destination mapping JSON.
   :type destination_file: str

.. function:: build_database(database)

   Creates the database, role, schemas, and grants permissions.

   :param database: Name of the database to build.
   :type database: str

.. function:: create_database_tables(database, destination_file)

   Executes SQL `CREATE TABLE` scripts for the specified database.

   :param database: Target database name.
   :type database: str
   :param destination_file: Path to the destination mapping JSON file.
   :type destination_file: str

.. function:: extract_source_data(source_file)

   Extracts source data from SQL Server using select queries.

   :param source_file: Path to the source mapping JSON file.
   :type source_file: str
   :return: List of tuples containing table ID and query results.
   :rtype: list[tuple[int, Any]]

.. function:: load_destination_tables(database, destination_file, source_data)

   Loads extracted source data into PostgreSQL destination tables.

   :param database: Target database name.
   :type database: str
   :param destination_file: Path to the destination mapping JSON file.
   :type destination_file: str
   :param source_data: Extracted source data.
   :type source_data: list
   :return: ``True`` if data was loaded successfully.
   :rtype: bool
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
     Entry point for the ETL process. Coordinates all steps from teardown to
    data load.

    :param args: Parsed command-line arguments.
    :type args: argparse.Namespace
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
    """
     Loads extracted source data into PostgreSQL destination tables.

    :param database: Target database name.
    :type database: str
    :param destination_file: Path to the destination mapping JSON file.
    :type destination_file: str
    :param source_data: Extracted source data.
    :type source_data: list
    :return: ``True`` if data was loaded successfully.
    :rtype: bool
    """

    # execute insert queries to insert source data
    success = insert_pg_tables(database, destination_file, source_data)
    return success


def extract_source_data(source_file):
    """
     Extracts source data from SQL Server using select queries.

    :param source_file: Path to the source mapping JSON file.
    :type source_file: str
    :return: List of tuples containing table ID and query results.
    :rtype: list[tuple[int, Any]]
    """
    # execute select queries to get source data
    source_data = get_source_data(source_file)
    return source_data


def create_database_tables(database, destination_file):
    """
     Executes SQL `CREATE TABLE` scripts for the specified database.

    :param database: Target database name.
    :type database: str
    :param destination_file: Path to the destination mapping JSON file.
    :type destination_file: str
    """
    # database: execute create table queries
    create_pg_tables(database, destination_file)


def build_database(database):
    """
     Creates the database, role, schemas, and grants permissions.

    :param database: Name of the database to build.
    :type database: str
    """
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
     Generates source and destination query mappings from a CSV file and writes
    them to JSON.

    :param mapping_file: Path to the CSV mapping file.
    :type mapping_file: str
    :param source_file: Output path for source mapping JSON.
    :type source_file: str
    :param destination_file: Output path for destination mapping JSON.
    :type destination_file: str
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
     Drops the PostgreSQL role associated with the target database.

    :param database: Name of the database whose role should be dropped.
    :type database: str
    :return: ``True`` if the role was dropped successfully.
    :rtype: bool
    """
    logging.info(f"Dropping role: {config("DB_ROLE")}.")
    success = drop_pg_role(database, use_admin=True)
    logging.info("✅ SUCCESS: role successfully dropped.")
    return success


def drop_database(database) -> bool:
    """
     Drops the specified PostgreSQL database.

    :param database: Name of the database to drop.
    :type database: str
    :return: ``True`` if the database was dropped successfully.
    :rtype: bool
    """
    logging.info(f"Dropping database: {database}.")
    success = drop_pg_database(database)
    logging.info(f"✅ SUCCESS: {database} successfully dropped.")
    return success


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set ETL options")

    parser.add_argument(
        "-d", "--database", type=str, required=True, help="Database Name"
    )

    parser.add_argument(
        "-s", "--seed-test-database", type=str,
        required=True, help="Seed Test Database"
    )

    args = parser.parse_args()

    main(args)
