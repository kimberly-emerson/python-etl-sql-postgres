"""
Module: get_source_data
=======================

This module provides functionality to extract and validate source data from
SQL query files defined in a JSON mapping configuration. It reads query
definitions, executes them against a SQL Server database, and returns the
aggregated results for downstream processing.

Dependencies:
-------------
- db.sql_server: Executes SQL queries using a default connection.
- utils.file_handler: Handles reading of JSON and SQL files.
- utils.logging_handler: Provides structured logging.
- utils.validation_handler: Validates data structures post-query execution.
- decouple.config: Loads environment-specific configuration values.

Environment Variables:
----------------------
- SQL_PATH: Base path to the directory containing SQL source query files.

Usage:
------
This module is typically used in ETL pipelines or data ingestion workflows
where source queries are modularized and defined externally in JSON format.

Example:
--------
    success, data = get_source_data("mapping_source.json")
    if success:
        process(data)
"""

from typing import Tuple
from decouple import config

import db.sql_server as sqldb
import utils.file_handler as fh
from utils.logging_handler import logger as log
import utils.validation_handler as vh


SOURCE_PATH = f"{config("SQL_PATH")}\\source"


def get_source_data(file: str = None) -> Tuple[bool, list]:
    """
    Extracts and validates source data from SQL query files defined in a JSON
    mapping file.

    This function reads a JSON file containing metadata about source tables
    and their associated SQL query filenames. It loads each query, executes it
    using the default SQL Server connection, and aggregates the results into a
    list. Each query result is validated before inclusion.

    Parameters:
    -----------
    file : str, optional
        The filename of the JSON mapping file (e.g., 'mapping_source.json').
        If not provided, the default path will be used by the file handler.

    Returns:
    --------
    Tuple[bool, list]
        A tuple containing:
        - success (bool): True if all queries executed and validated
        successfully.
        - data (list): A list of query result sets, one per source table.

    Raises:
    -------
    FileNotFoundError:
        If any referenced SQL query file is missing or unreadable.

    ValueError:
        If the JSON mapping file is malformed or contains invalid entries.

    Notes:
    ------
    - Query files must be located in the directory defined by the SQL_PATH
    environment variable.
    - Each query file must return a valid SQL SELECT statement.
    - Logging is performed at each step for traceability and debugging.
    """

    success = False

    # instantiate data list variable to be returned
    data: list = list()

    try:
        # read mapping_source.json file
        success, queries = fh.read_json_file("Mapping Source", file)
        queries.sort(key=lambda x: int(x['table_id']))
        # test if queries is not empty
        if success:

            for table in queries:

                # construct full path to source query file
                item = table['source_query_select']
                path = f"{SOURCE_PATH}\\{item}"
                index = path.rfind('\\')+1

                # read query from file
                success, query = fh.read_query_from_file(path)

                # handle empty/missing query file
                if not success:
                    log.error(f"🔴 FAILED: {path[index:].strip()} does not \
                              return a query.")
                    raise FileNotFoundError

                # execute query using default postgres connection
                success, response = sqldb.execute_sql_query(
                    conn=None,
                    query=query
                )

                if success:
                    # add query result to data list
                    data.append((response))

                success = False
                success = vh.validate_list("Source Data", data)

                if success:
                    log.info(f"🟢 SUCCESS: {path[index:]} executed.")
                else:
                    log.error(f"🔴 FAILED: {path[index:]} not executed.")

            # return success bool and data list containing source data
            return success, data

    except (ValueError, FileNotFoundError) as error:
        log.error(error, exc_info=True)

    except Exception as e:  # pylint: disable=broad-except
        log.error(e, exc_info=True)
