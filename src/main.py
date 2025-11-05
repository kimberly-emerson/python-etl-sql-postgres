"""
main.py — ETL Orchestration Module
==================================

Coordinates a full ETL (Extract, Transform, Load) workflow for PostgreSQL
databases, including teardown, schema creation, query mapping generation,
data extraction, and data loading into production and test environments.

Overview
--------
This module automates the following ETL stages:

- Drops and rebuilds PostgreSQL databases and roles
- Generates source and destination query mappings from a CSV file
- Extracts source data using parameterized SQL SELECT queries
- Loads extracted data into destination tables using INSERT queries
- Optionally seeds a test database with the same data

Dependencies
------------
The module integrates with the following components:

- ``build.build_destination_database``: PostgreSQL DDL and permission utilities
- ``extract.get_source_data``: Source data extraction logic
- ``load.insert_source_data``: Destination data insertion logic
- ``utils.query_mapping_handler``: Mapping generation from CSV
- ``utils.logging_handler``: Structured logging
- ``decouple.config``: Environment variable management

Environment Variables
---------------------
- ``SQL_PATH``: Root directory for query files and mapping CSV
- ``DB_ROLE``: Role name used for PostgreSQL access control

Execution Steps
---------------
1. Drop existing databases and roles
2. Generate source and destination query mappings
3. Create databases, roles, schemas, and tables
4. Extract source data
5. Load data into destination and optionally test database

Command-Line Usage
------------------
.. code-block:: bash

    python -m main.py --database sales_db -seed-test-database True

This will:

- Drop and rebuild `sales_db` and `sales_db_test`
- Generate query mappings
- Extract source data
- Load destination tables
"""

import sys
import pandas as pd
import argparse
from decouple import config

import build.build_destination_database as pgdb
import extract.get_source_data as srcdata
import load.insert_source_data as dest
from utils.logging_handler import logger as log
import utils.query_mapping_handler as qmh


SQL_PATH = config("SQL_PATH")
MAPPING_FILE = f"{SQL_PATH}\\mapping.csv"
SOURCE_FILE = f"{SQL_PATH}\\mapping_source.json"
DESTINATION_FILE = f"{SQL_PATH}\\mapping_destination.json"


def main(args):
    """
    Executes the full ETL pipeline for a given database and its test clone.

    :param args: Parsed CLI arguments with `database` and `seed_test_database`
    attributes.
    :type args: argparse.Namespace

    :raises SystemExit: If any critical step in the pipeline fails.
    """

    test_database = f"{args.database}_test"

    log.info("===============================================================")
    log.info(f"⚫ STARTING: ETL for Database {args.database}")

    log.info("🔷 DROP DATABASES")
    # drop database
    drop_database(args.database)
    # drop test database
    drop_database(test_database)

    log.info("🔷 DROP ROLE")
    # drop role
    drop_role(args.database)

    log.info("🔷 BUILD QUERY/TABLE MAPPINGS")
    # define source query/table mappings
    build_mapping_data("source", MAPPING_FILE, SOURCE_FILE)
    # define destination query/table mappings
    build_mapping_data("destination", MAPPING_FILE, DESTINATION_FILE)

    log.info("🔷 BUILD DATABASES")
    # build database
    create_database(args.database)
    create_role(args.database)
    grant_database_permissions(args.database)
    create_database_schemas(args.database)
    grant_table_permissions(args.database)

    # build test database
    create_database(test_database)
    grant_database_permissions(test_database)
    create_database_schemas(test_database)
    grant_table_permissions(test_database)

    log.info("🔷 CREATE DATABASE TABLES")
    # create database tables
    create_database_tables(args.database, DESTINATION_FILE)
    # create test database tables
    create_database_tables(test_database, DESTINATION_FILE)

    log.info("🔷 EXTRACT SOURCE DATA")
    # extract table data from source database
    source_data = extract_source_data(SOURCE_FILE)

    # load source data into destination database
    log.info("🔷 LOAD DESTINATION DATA")
    load_destination_tables(args.database, DESTINATION_FILE, source_data)

    # load source data into destination test database
    if args.seed_test_database:
        load_destination_tables(test_database, DESTINATION_FILE, source_data)

    log.info(f"🏁 COMPLETED: ETL for Database: {args.database}.")
    log.info("===============================================================")


def load_destination_tables(
        database: str,
        destination_file: str,
        source_data: str):
    """
    Loads extracted source data into PostgreSQL destination tables.

    :param database: Target PostgreSQL database name.
    :type database: str
    :param destination_file: Path to JSON file containing destination query
    mappings.
    :type destination_file: str
    :param source_data: List of extracted data payloads to be inserted.
    :type source_data: list

    :raises SystemExit: If data insertion fails.
    """

    log.info("➡️ STARTING: Loading Destination Tables")
    # execute insert queries to insert source data
    success = dest.insert_pg_tables(database, destination_file, source_data)

    if not success:
        sys.exit("⛓️‍💥 EXITING: Destination Tables not loaded.")

    log.info("☑️ COMPLETED: Destination Tables loaded.")
    log.info("---------------------------------------------------------------")


def extract_source_data(source_file: str) -> list:
    """
    Extracts source data using SQL SELECT queries defined in a JSON mapping
    file.

    :param source_file: Path to JSON file containing source query mappings.
    :type source_file: str

    :return: Extracted data payloads.
    :rtype: list

    :raises SystemExit: If no data is returned.
    """

    # get source data
    log.info("➡️ STARTING: Extracting Source Data")
    # execute select queries to get source data
    success, source_data = srcdata.get_source_data(source_file)

    if not success:
        sys.exit("⛓️‍💥 EXITING: No source data returned.")

    log.info("☑️ COMPLETED: Source Data extracted.")
    log.info("---------------------------------------------------------------")

    return source_data


def create_database_tables(database: str, destination_file: str):
    """
    Creates PostgreSQL tables using destination query definitions.

    :param database: Target database name.
    :type database: str
    :param destination_file: Path to JSON file containing table creation
    queries.
    :type destination_file: str

    :raises SystemExit: If table creation fails.
    """

    # database: execute create table queries
    log.info(f"➡️ STARTING: Creating {database} Tables.")
    success = pgdb.create_pg_tables(database, destination_file)

    if not success:
        sys.exit(f"⛓️‍💥 EXITING: {database} Tables not created.")

    log.info(f"☑️ COMPLETED: {database} Tables created.")
    log.info("---------------------------------------------------------------")


def grant_table_permissions(database) -> bool:
    """
    Grants table-level permissions for the specified database.

    :param database: Target database name.
    :type database: str

    :return: True if permissions granted successfully.
    :rtype: bool

    :raises SystemExit: If permission grant fails.
    """

    # grant database permissions
    log.info("➡️ STARTING: Granting Table Permissions")
    success = pgdb.grant_pg_table_permissions(database)

    if not success:
        sys.exit("⛓️‍💥 EXITING: Table Permissions not granted.")

    log.info("☑️ COMPLETED: Table Permissions granted.")
    log.info("---------------------------------------------------------------")


def create_database_schemas(database) -> bool:
    """
    Creates schemas for the specified PostgreSQL database.

    :param database: Target database name.
    :type database: str

    :return: True if schemas created successfully.
    :rtype: bool

    :raises SystemExit: If schema creation fails.
    """
    # grant database permissions
    log.info("➡️ STARTING: Creating Database Schemas.")
    success = pgdb.create_pg_database_schemas(database)

    if not success:
        sys.exit("⛓️‍💥 EXITING: Database Schemas not created.")

    log.info("☑️ COMPLETED: Database Schemas created.")
    log.info("---------------------------------------------------------------")


def grant_database_permissions(database) -> bool:
    """
    Grants database-level permissions for the specified PostgreSQL database.

    :param database: Target database name.
    :type database: str

    :return: True if permissions granted successfully.
    :rtype: bool

    :raises SystemExit: If permission grant fails.
    """

    # grant database permissions
    log.info("➡️ STARTING: Granting Database Permissions")
    success = pgdb.grant_pg_database_permissions(database)

    if not success:
        sys.exit("⛓️‍💥 EXITING: Database Permissions not granted.")

    log.info("☑️ COMPLETED: Database Permissions granted.")
    log.info("---------------------------------------------------------------")


def create_role(database: str):
    """
    Creates a PostgreSQL role for the specified database.

    :param database: Target database name.
    :type database: str

    :raises SystemExit: If role creation fails.
    """

    # create role
    log.info(f"➡️ STARTING: Creating Role {config("DB_ROLE")}")
    success = pgdb.create_pg_role(database)

    if not success:
        sys.exit("⛓️‍💥 EXITING: Role not created.")

    log.info(f"☑️ COMPLETED: Role {config("DB_ROLE")} created.")
    log.info("---------------------------------------------------------------")


def create_database(database: str):
    """
    Creates a PostgreSQL database.

    :param database: Name of the database to create.
    :type database: str

    :raises SystemExit: If database creation fails.
    """

    # create database
    log.info(f"➡️ STARTING: Creating Database {database}.")
    success = pgdb.create_pg_database(database)

    if not success:
        sys.exit("⛓️‍💥 EXITING: Database not created.")

    log.info(f"☑️ COMPLETED: Database {database} created.")
    log.info("---------------------------------------------------------------")


def build_mapping_data(mapping_type: str, mapping_file: str, output_file: str):
    """
    Generates query/table mappings from a CSV file and writes to JSON.

    :param mapping_type: Either 'source' or 'destination'.
    :type mapping_type: str
    :param mapping_file: Path to the CSV file containing table/query mappings.
    :type mapping_file: str
    :param output_file: Path to the output JSON file.
    :type output_file: str

    :raises SystemExit: If mapping generation fails.
    """

    success = False
    mapping = pd.DataFrame()
    log.info(
        f"➡️ STARTING: Building {mapping_type.title()} Query/Table Mapping."
    )

    match mapping_type:
        case "source":
            mapping = qmh.get_source_mapping_data(mapping_file)
        case "destination":
            mapping = qmh.get_destination_mapping_data(mapping_file)
        case _:
            log.error(f"FAILED: {mapping_type.title()} mapping not defined.")

    if not mapping.empty:
        success = qmh.write_mapping_data(mapping, output_file)

    if not success:
        sys.exit("⛓️‍💥 EXITING: Query/Table Mapping failed.")

    log.info(
        f"☑️ COMPLETED: {mapping_type.title()} Query/Table Mapping completed."
    )
    log.info("---------------------------------------------------------------")


def drop_role(database: str):
    """
    Drops the PostgreSQL role associated with the specified database.

    :param database: Target database name.
    :type database: str

    :raises SystemExit: If role drop fails.
    """

    log.info(f"➡️ STARTING: Dropping role {config("DB_ROLE")}.")
    success = pgdb.drop_pg_role(database, use_default=True)

    if not success:
        sys.exit("⛓️‍💥 EXITING: Role failed to drop.")

    log.info(f"☑️ COMPLETED: Role {config("DB_ROLE")} dropped.")
    log.info("---------------------------------------------------------------")


def drop_database(database: str):
    """
    Drops the specified PostgreSQL database.

    :param database: Name of the database to drop.
    :type database: str

    :raises SystemExit: If database drop fails.
    """

    log.info(f"➡️ STARTING: Dropping database: {database}.")
    success = pgdb.drop_pg_database(database)

    if not success:
        sys.exit("⛓️‍💥 EXITING: Database failed to drop.")

    log.info(f"☑️ COMPLETED: Database {database} dropped.")
    log.info("---------------------------------------------------------------")


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
