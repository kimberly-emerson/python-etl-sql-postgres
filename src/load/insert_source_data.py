"""
PostgreSQL Table Insertion Module
=================================

This module automates the execution of PostgreSQL insert queries based on a
JSON mapping file and a list of source data. It integrates file handling,
query execution, and logging to support dynamic ETL workflows.

Overview
--------

The module performs the following operations:

- Loads a JSON mapping file containing destination query metadata.
- Extracts and reads SQL insert statements from disk.
- Filters source data by table ID.
- Executes parameterized insert queries against a PostgreSQL database.
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
  - ``execute_pg_query``: Executes parameterized SQL queries.
- ``utils.file_handler``:
  - ``load_json_file``: Loads JSON mappings.
  - ``get_query_list_from_file``: Extracts query metadata.
  - ``read_query_from_file``: Reads SQL query text from file.

Constants
---------

- ``DESTINATION_PATH``: Constructed from ``SQL_PATH`` and used to locate
insert query files.

Functions
---------

.. function:: insert_pg_tables(database: str, file: str, data: list)

   Executes PostgreSQL insert queries using metadata from a JSON mapping file.

   :param database: Name of the PostgreSQL database to connect to.
   :type database: str
   :param file: Path to the JSON file containing destination query metadata.
   :type file: str
   :param data: List of tuples where each tuple contains a table ID and
   associated values.
   :type data: list[tuple[int, list]]

   :return: ``True`` if at least one insert query was executed successfully,
   otherwise ``False``.
   :rtype: bool

   **Execution Flow:**

   - Loads the JSON mapping file using ``load_json_file``.
   - Extracts insert query metadata using ``get_query_list_from_file``.
   - Iterates over each destination table:
     - Filters the source data by table ID.
     - Constructs the full path to the SQL insert file.
     - Reads the SQL query using ``read_query_from_file``.
     - Executes the query using ``execute_pg_query`` with the filtered values.
   - Logs each step and prints the name of each executed file.

   **Logging Behavior:**

   - Logs a warning if a query file is missing or empty.
   - Logs an error if the JSON file is not found or if any exception occurs
   during execution.
   - Logs a success message for each executed insert query.

   **Example Usage:**

   .. code-block:: python

      success = insert_pg_tables(
          database="analytics_db",
          file="mappings/mapping_destination.json",
          data=[(101, [("val1", "val2")]), (102, [("val3", "val4")])]
      )
"""

import logging
from decouple import config

from db.postgresql import execute_pg_query, set_pg_connection
from utils.file_handler import (
    get_query_list_from_file,
    load_json_file,
    read_query_from_file,
)

DESTINATION_PATH = f"{config("SQL_PATH")}\\destination"


def insert_pg_tables(database: str, file: str, data: list):
    """
     Executes PostgreSQL insert queries using metadata from a JSON mapping file.

    :param database: Name of the PostgreSQL database to connect to.
    :type database: str
    :param file: Path to the JSON file containing destination query metadata.
    :type file: str
    :param data: List of tuples where each tuple contains a table ID and
    associated values.
    :type data: list[tuple[int, list]]

    :return: ``True`` if at least one insert query was executed successfully,
    otherwise ``False``.
    :rtype: bool

    **Execution Flow:**

    - Loads the JSON mapping file using ``load_json_file``.
    - Extracts insert query metadata using ``get_query_list_from_file``.
    - Iterates over each destination table:
      - Filters the source data by table ID.
      - Constructs the full path to the SQL insert file.
      - Reads the SQL query using ``read_query_from_file``.
      - Executes the query using ``execute_pg_query`` with the filtered values.
    - Logs each step and prints the name of each executed file.

    **Logging Behavior:**

    - Logs a warning if a query file is missing or empty.
    - Logs an error if the JSON file is not found or if any exception occurs
    during execution.
    - Logs a success message for each executed insert query.

    **Example Usage:**

    .. code-block:: python

       success = insert_pg_tables(
           database="analytics_db",
           file="mappings/mapping_destination.json",
           data=[(101, [("val1", "val2")]), (102, [("val3", "val4")])]
       )
    """

    # instantiate success boolean variable to be returned
    success: bool = False

    try:
        # read mapping_destination.json file
        queries: tuple = load_json_file(file)

        # test if queries is not empty
        if queries[0]:

            # get destination query file list
            query_list = get_query_list_from_file("destination_query_insert", queries)

            logging.info("------ EXECUTE INSERT SQL SCRIPTS ------")

            for table in query_list[1]:

                # filter source data for destination table
                values = [t for t in data if t[0] == table[0]]

                # construct full path to destination query file
                file = f"{DESTINATION_PATH}\\{table[1]}"

                # read query from file
                query = read_query_from_file(file)

                # query = query.replace(',)',')')
                if not query:
                    logging.warning(f"{file} does not return a query.")
                    raise FileNotFoundError

                # set connection to postgresql database
                conn = set_pg_connection(database)

                # execute insert query
                execute_pg_query(
                    conn, database=database, query=query, values=values[0][1]
                )

                # set success variable
                success = True

                print(f"{file[49:len(file)]} executed.")

    except FileNotFoundError as error:
        logging.error(error)

    except Exception as e:  # pylint: disable=broad-except
        logging.error(e)

    # return success boolean
    return success
