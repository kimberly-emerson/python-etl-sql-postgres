"""
Source Data Extraction Module
=============================

This module orchestrates the extraction of source data from SQL Server using
query metadata defined in a JSON mapping file. It integrates file handling,
query execution, and validation to support dynamic ETL workflows.

Overview
--------

The module performs the following operations:

- Loads a JSON mapping file containing source query metadata.
- Extracts and reads SQL select statements from disk.
- Executes each query against SQL Server.
- Aggregates results into a structured list.
- Validates the final dataset and logs progress.

Environment Configuration
-------------------------

- ``SQL_PATH``: Environment variable used to construct the path to source SQL
files.

Dependencies
------------

- ``logging``: Standard Python logging module.
- ``decouple.config``: For environment variable access.
- ``db.sql_server``:
  - ``execute_sql_query``: Executes SQL queries against SQL Server.
- ``utils.file_handler``:
  - ``read_json_file``: Loads JSON mappings.
  - ``get_query_list_from_file``: Extracts query metadata.
  - ``read_query_from_file``: Reads SQL query text from file.
- ``utils.validation.validate_list``: Validates that the final data list is
non-empty.

Constants
---------

- ``SOURCE_PATH``: Constructed from ``SQL_PATH`` and used to locate source SQL
files.

Functions
---------

.. function:: get_source_data(file: str = None)

   Extracts source data from SQL Server using query metadata from a JSON
   mapping file.

   :param file: Path to the JSON file containing source query metadata.
   :type file: str, optional
   :return: List of tuples containing table ID and query results.
   :rtype: list[tuple[int, Any]]

   **Execution Flow:**

   - Loads the JSON mapping file using ``read_json_file``.
   - Extracts select query metadata using ``get_query_list_from_file``.
   - Iterates over each source table:
     - Constructs the full path to the SQL select file.
     - Reads the SQL query using ``read_query_from_file``.
     - Executes the query using ``execute_sql_query``.
     - Appends the result to the data list.
   - Validates the final data list using ``validate_list``.

   **Logging Behavior:**

   - Logs a warning if a query file is missing or empty.
   - Logs an error if the JSON file is not found or if any exception occurs
   during execution.
   - Logs success if the data list is populated.

   **Example Usage:**

   .. code-block:: python

      data = get_source_data(file="mappings/mapping_source.json")
"""

import logging
from decouple import config

from db.sql_server import execute_sql_query
from utils.file_handler import (
    read_json_file,
    read_query_from_file,
    get_query_list_from_file,
)
from utils.validation import validate_list

SOURCE_PATH = f"{config("SQL_PATH")}\\source"


def get_source_data(file: str = None):
    """
     Extracts source data from SQL Server using query metadata from a JSON
    mapping file.

    :param file: Path to the JSON file containing source query metadata.
    :type file: str, optional
    :return: List of tuples containing table ID and query results.
    :rtype: list[tuple[int, Any]]

    **Execution Flow:**

    - Loads the JSON mapping file using ``read_json_file``.
    - Extracts select query metadata using ``get_query_list_from_file``.
    - Iterates over each source table:
      - Constructs the full path to the SQL select file.
      - Reads the SQL query using ``read_query_from_file``.
      - Executes the query using ``execute_sql_query``.
      - Appends the result to the data list.
    - Validates the final data list using ``validate_list``.

    **Logging Behavior:**

    - Logs a warning if a query file is missing or empty.
    - Logs an error if the JSON file is not found or if any exception occurs
    during execution.
    - Logs success if the data list is populated.

    **Example Usage:**

    .. code-block:: python

       data = get_source_data(file="mappings/mapping_source.json")
    """

    success = False

    # instantiate data list variable to be returned
    data: list = list()

    try:
        # read mapping_source.json file
        queries = read_json_file("Mapping Source", file)

        # test if queries is not empty
        if queries[0]:

            # get source query file list
            query_list = get_query_list_from_file("source_query_select", queries[1])

            for table in query_list[1]:

                # construct full path to source query file
                file = f"{SOURCE_PATH}\\{table[1]}"

                # read query from file
                query = read_query_from_file(file)

                # handle empty/missing query file
                if not query:

                    logging.warning(f"{file} does not return a query.")
                    raise FileNotFoundError

                # execute query using default postgres connection
                response = execute_sql_query(conn=None, query=query)

                # add query result to data list
                data.append((table[0], response))

    except FileNotFoundError as error:
        logging.error(error)

    except Exception as e:  # pylint: disable=broad-except
        logging.error(e)

    success = validate_list("Source Data", data)

    # return data list containing source data
    return data
