"""
Module: insert_source_data
==========================

This module handles the insertion of structured data into PostgreSQL tables
using parameterized SQL queries defined in a JSON mapping file. It reads query
templates, binds data values, and executes inserts against a target database.

Dependencies:
-------------
- db.postgresql: Manages PostgreSQL connection setup.
- db.postgresql_queries: Executes parameterized SQL insert operations.
- utils.file_handler: Loads JSON mappings and reads SQL query files.
- utils.logging_handler: Provides structured logging for success and error
tracking.
- decouple.config: Loads environment-specific configuration values.

Environment Variables:
----------------------
- SQL_PATH: Base path to the directory containing SQL destination query files.

Usage:
------
This module is typically used in ETL workflows or data migration pipelines
where data must be inserted into PostgreSQL tables based on external query
templates.

Example:
--------
    success = insert_pg_tables(
        database="analytics_db",
        file="mapping_destination.json",
        data=transformed_data
    )
    if success:
        log.info("All destination inserts completed successfully.")
"""

from decouple import config

import db.postgresql as pgdb
import db.postgresql_queries as q
import utils.file_handler as fh
from utils.logging_handler import logger as log


DESTINATION_PATH = f"{config("SQL_PATH")}\\destination"


def insert_pg_tables(database: str, file: str, data: list) -> bool:
    """
    Inserts data into PostgreSQL tables using SQL queries defined in a JSON
    mapping file.

    This function reads a destination mapping file that specifies table IDs
    and associated SQL insert query filenames. It loads each query, binds the
    corresponding data values, and executes the insert operation using a
    PostgreSQL connection.

    Parameters:
    -----------
    database : str
        The name of the target PostgreSQL database.

    file : str
        The filename of the JSON mapping file ('mapping_destination.json') 
        that defines the insert query files and table IDs.

    data : list
        A list of data payloads to be inserted. Each item corresponds to a
        table ID defined in the mapping file.

    Returns:
    --------
    bool
        True if all insert operations succeed; False if any query fails or an
        exception occurs.

    Raises:
    -------
    FileNotFoundError:
        If any referenced SQL query file is missing or unreadable.

    Exception:
        For any unexpected errors during query execution or connection setup.

    Notes:
    ------
    - Query files must be located in the directory defined by the SQL_PATH
    environment variable.
    - Each query file must contain a valid parameterized SQL INSERT statement.
    - Logging is performed for each query execution to aid in debugging and
    traceability.
    """

    # instantiate success boolean variable to be returned
    success: bool = False

    try:
        # read mapping_destination.json file
        success, queries = fh.load_json_file(file)
        queries.sort(key=lambda x: int(x['table_id']))

        # test if queries is not empty
        if success:

            for table in queries:
                # construct full path to destination query file
                item = table['destination_query_insert']
                path = f"{DESTINATION_PATH}\\{item}"
                index = path.rfind('\\')+1
                data_index = int(table['table_id'])-1
                values = data[data_index]

                # read query from file
                success, query = fh.read_query_from_file(path)

                # set connection to postgresql database
                conn = pgdb.set_pg_connection(database)

                # execute insert query
                q.pg_query(
                    conn,
                    database=database,
                    query=query,
                    values=values
                )

                # set success variable
                success = True

                if success:
                    log.info(f"🟢 SUCCESS: {path[index:]} executed.")
                else:
                    log.error(f"🔴 FAILED: {path[index:]} not executed.")

        # return success boolean
        return success

    except FileNotFoundError as error:
        log.error(error, exc_info=True)

    except Exception as e:  # pylint: disable=broad-except
        log.error(e, exc_info=True)
