"""
main.py — ETL Orchestration Module
==================================
Coordinates a full ETL (Extract, Transform, Load) workflow for PostgreSQL
databases.

This module automates teardown, schema creation, query mapping generation,
data extraction, and data loading into production and test environments. It is
designed to support reproducible ETL pipelines with modular components and
environment-driven configuration.

Functions:
    - Drops and rebuilds PostgreSQL databases and roles.
    - Generates source and destination query mappings from a CSV file.
    - Extracts source data using parameterized SQL SELECT queries.
    - Loads extracted data into destination tables using INSERT queries.
    - Optionally seeds a test database with the same data.

Dependencies:
    - build.build_destination_database: DDL and permission utilities.
    - extract.get_source_data: Source data extraction logic.
    - load.insert_source_data: Destination data insertion logic.
    - utils.query_mapping_handler: Mapping generation from CSV.
    - utils.logging_handler: Structured logging.
    - decouple.config: Environment variable management.

Environment Variables:
    - SQL_PATH: Root directory for query files and mapping CSV.
    - DB_ROLE: Role name used for PostgreSQL access control.

Execution Steps:
    1. Drop existing databases and roles.
    2. Generate source and destination query mappings.
    3. Create databases, roles, schemas, and tables.
    4. Extract source data.
    5. Load data into destination and optionally test database.

Example:
    To orchestrate ETL for the `sales_db` database and seed a test database:

    ```bash
    python -m main.py --database sales_db --seed-test-database True
    ```

    This will:
        - Drop and rebuild `sales_db` and `sales_db_test`.
        - Generate query mappings.
        - Extract source data.
        - Load destination tables.
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
    Executes the full ETL pipeline for a specified PostgreSQL database and its
    optional test clone.

    This function coordinates teardown, query mapping generation, schema
    creation, data extraction, and data loading. It uses CLI arguments to
    determine the target database and whether to seed a test database with the
    same data.

    Args:
        args (argparse.Namespace): Parsed command-line arguments containing:
            - database (str): Name of the target PostgreSQL database.
            - seed_test_database (bool): Flag indicating whether to seed a
            test clone.

    Raises:
        SystemExit: If any critical step in the ETL pipeline fails.
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
    Loads source data into PostgreSQL destination tables using predefined
    query mappings.

    This function delegates the insertion logic to `dest.insert_pg_tables`,
    which executes the mapped SQL insert statements defined in the destination
    file. It logs the start and completion of the process, and exits the
    program if the insertion fails.

    Args:
        database (str): Name of the target PostgreSQL database.
        destination_file (str): Path to the JSON file containing destination
        query mappings.
        source_data (str): Serialized source data payload to be inserted.

    Raises:
        SystemExit: If the data insertion fails via `dest.insert_pg_tables`.
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

    This function reads a JSON file containing query mappings, executes the
    mapped SQL SELECT statements, and returns the resulting data payloads.

    Args:
        source_file (str): Path to the JSON file containing source query
        mappings.

    Returns:
        list: A list of extracted data payloads.

    Raises:
        SystemExit: If no data is returned from the source queries.
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

    This function reads a JSON file containing SQL table creation queries and
    executes them against the specified PostgreSQL database to build the
    required schema.

    Args:
        database (str): Name of the target PostgreSQL database.
        destination_file (str): Path to the JSON file containing table
        creation queries.

    Raises:
        SystemExit: If table creation fails due to invalid queries or
        connection issues.
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
    Grants table-level permissions for the specified PostgreSQL database.

    This function applies the necessary GRANT statements to enable access
    control for roles and users defined in the database schema.

    Args:
        database (str): Name of the target PostgreSQL database.

    Returns:
        bool: True if permissions are granted successfully.

    Raises:
        SystemExit: If permission grant fails due to invalid configuration or
        execution error.
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

    This function executes SQL statements to define and initialize schemas
    required for the target database.

    Args:
        database (str): Name of the target PostgreSQL database.

    Returns:
        bool: True if schemas are created successfully.

    Raises:
        SystemExit: If schema creation fails due to execution errors or
        invalid configuration.
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

    This function executes GRANT statements to assign access privileges at the
    database level, enabling role-based control over connections and
    operations.

    Args:
        database (str): Name of the target PostgreSQL database.

    Returns:
        bool: True if permissions are granted successfully.

    Raises:
        SystemExit: If permission grant fails due to configuration or
        execution errors.
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

    This function executes SQL statements to define a role with appropriate
    privileges for accessing and managing the target database.

    Args:
        database (str): Name of the target PostgreSQL database.

    Raises:
        SystemExit: If role creation fails due to execution errors or invalid
        configuration.
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
    Creates a PostgreSQL database with the specified name.

    This function executes SQL statements to initialize a new PostgreSQL
    database using the provided name.

    Args:
        database (str): Name of the database to create.

    Raises:
        SystemExit: If database creation fails due to execution errors or
        invalid configuration.
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
    Generates query or table mappings from a CSV file and writes the result to
    a JSON file.

    This function parses a CSV file containing table or query mappings and
    serializes the structured output to a JSON file. The mapping type
    determines whether the mappings are for source extraction or destination
    loading.

    Args:
        mapping_type (str): Type of mapping to generate; must be either
        'source' or 'destination'.
        mapping_file (str): Path to the CSV file containing table/query
        mappings.
        output_file (str): Path to the output JSON file where mappings will be
        written.

    Raises:
        SystemExit: If mapping generation fails due to invalid input or write
        errors.
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

    This function executes SQL statements to remove the role tied to the given
    database, typically as part of a teardown or reinitialization process.

    Args:
        database (str): Name of the target PostgreSQL database.

    Raises:
        SystemExit: If role drop fails due to execution errors or invalid
        configuration.
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

    This function executes SQL commands to remove the given database from the
    PostgreSQL server, typically as part of a teardown or reinitialization
    process.

    Args:
        database (str): Name of the database to drop.

    Raises:
        SystemExit: If the database drop operation fails due to execution
        errors or invalid configuration.
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
