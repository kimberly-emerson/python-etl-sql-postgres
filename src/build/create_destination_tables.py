"""
PostgreSQL Table Creation Module
================================

This module automates the creation of PostgreSQL tables using SQL scripts
defined in a JSON mapping file. It integrates file handling, query execution,
and logging to support dynamic schema provisioning workflows.

Overview
--------

The module performs the following operations:

- Loads a JSON mapping file containing destination table creation metadata.
- Extracts SQL `CREATE TABLE` statements from disk.
- Executes each statement against a PostgreSQL database.
- Logs progress and errors throughout the process.

Environment Configuration
-------------------------

- ``SQL_PATH``: Environment variable used to construct the path to destination
SQL files.

Dependencies
------------

- ``logging``: Standard Python logging module.
- ``decouple.config``: For environment variable access.
- ``db.postgresql``:
  - ``set_pg_connection``: Establishes a PostgreSQL connection.
  - ``execute_pg_query``: Executes SQL queries.
- ``utils.file_handler``:
  - ``read_json_file``: Loads JSON mappings.
  - ``get_query_list_from_file``: Extracts query metadata.
  - ``read_query_from_file``: Reads SQL query text from file.

Constants
---------

- ``DESTINATION_PATH``: Constructed from ``SQL_PATH`` and used to locate
destination SQL files.

Functions
---------

.. function:: create_pg_tables(database: str, file: str)

   Executes PostgreSQL `CREATE TABLE` queries using metadata from a JSON
   mapping file.

   :param database: Name of the PostgreSQL database to connect to.
   :type database: str
   :param file: Path to the JSON file containing destination query metadata.
   :type file: str
   :return: None

   **Execution Flow:**

   - Loads the JSON mapping file using ``read_json_file``.
   - Extracts table creation metadata using ``get_query_list_from_file``.
   - Iterates over each destination table:
     - Constructs the full path to the SQL creation file.
     - Reads the SQL query using ``read_query_from_file``.
     - Executes the query using ``execute_pg_query`` with a non-admin
     connection.
   - Logs each step and prints the name of each executed file.

   **Logging Behavior:**

   - Logs a warning if a query file is missing or empty.
   - Logs an error if the JSON file is not found or if any exception occurs
   during execution.
   - Logs a success message for each executed `CREATE TABLE` query.

   **Example Usage:**

   .. code-block:: python

      create_pg_tables(
          database="analytics_db",
          file="mappings/mapping_destination.json"
      )
"""

import logging
from decouple import config

from db.postgresql import execute_pg_query, set_pg_connection
from utils.file_handler import (
    read_json_file,
    get_query_list_from_file,
    read_query_from_file,
)

DESTINATION_PATH = f"{config("SQL_PATH")}\\destination"


def create_pg_tables(database: str, file: str):
    """
     Executes PostgreSQL `CREATE TABLE` queries using metadata from a JSON
     mapping file.

    :param database: Name of the PostgreSQL database to connect to.
    :type database: str
    :param file: Path to the JSON file containing destination query metadata.
    :type file: str
    :return: None

    **Execution Flow:**

    - Loads the JSON mapping file using ``read_json_file``.
    - Extracts table creation metadata using ``get_query_list_from_file``.
    - Iterates over each destination table:
      - Constructs the full path to the SQL creation file.
      - Reads the SQL query using ``read_query_from_file``.
      - Executes the query using ``execute_pg_query`` with a non-admin
      connection.
    - Logs each step and prints the name of each executed file.

    **Logging Behavior:**

    - Logs a warning if a query file is missing or empty.
    - Logs an error if the JSON file is not found or if any exception occurs
    during execution.
    - Logs a success message for each executed `CREATE TABLE` query.

    **Example Usage:**

    .. code-block:: python

       create_pg_tables(
           database="analytics_db",
           file="mappings/mapping_destination.json"
       )
    """

    try:
        queries = read_json_file("Destination Mapping", file)

        if queries[0]:
            query_list = get_query_list_from_file(
                "destination_query_create", queries[1]
            )

            logging.info("------ EXECUTE CREATE SQL SCRIPTS ------")

            for table in query_list[1]:

                file = f"{DESTINATION_PATH}\\{table[1]}"

                query = read_query_from_file(file)

                if not query:
                    logging.warning(f"{file} does not return a query.")
                    raise FileNotFoundError

                conn = set_pg_connection(database, use_admin=False)

                execute_pg_query(conn, database, query)

                print(f"{file[49:len(file)]} executed.")

    except FileNotFoundError as error:
        logging.error(error)

    except Exception as e:  # pylint: disable=broad-except
        logging.error(e)
