"""
Module: json_query_handler
==========================

This module provides utilities for reading JSON files and extracting query data
used in ETL pipelines or data orchestration workflows. It includes structured
logging, validation, and error handling to support robust backend operations.

Dependencies
------------
- json : For loading JSON content from disk.
- typing : For type annotations.
- utils.logging_handler.logger : Custom logger for structured logging.
- utils.validation_handler : Validation utilities for list integrity checks.

Functions
---------
- read_json_file : Loads and validates a JSON file containing query
definitions.
- load_json_file : Reads raw JSON content from disk and returns a success flag.
- read_query_from_file : Reads a raw SQL query from a text file.
- get_query_list_from_file : Extracts a list of query tuples from JSON content.
"""

import json
from typing import Tuple

from utils.logging_handler import logger as log
import utils.validation_handler as vh


def read_json_file(name: str, file: str) -> Tuple[bool, list]:
    """
    Load and validate a JSON file containing query definitions.

    This function reads a JSON file, validates its contents using a list
    integrity check, and returns a success flag along with the parsed data.

    Parameters
    ----------
    name : str
        A descriptive label used in logging to identify the source of the JSON
        file.
    file : str
        Path to the JSON file to be read.

    Returns
    -------
    Tuple[bool, list]
        A tuple containing:
        - success (bool): True if the file was read and validated successfully.
        - queries (list): Parsed list of query definitions.

    Logging
    -------
    Logs success or failure messages based on file read and validation outcome.

    Example
    -------
    >>> read_json_file("source", "source_queries.json")
    (True, [...])
    """

    # instantiate queries string variable
    queries: list = list()

    try:
        # load json data from file into queries variable
        success, queries = load_json_file(file)

        # test if queries variable is empty
        if success:
            log.info(f"🟢 SUCCESS: {name} JSON file read.")
        else:
            log.error(f"🔴 FAILED:{name} JSON file was not read.")

        success = False
        # test if queries list is not empty
        success = vh.validate_list(f"{name} JSON File", queries)

        # return success boolean and queries variable
        return success, queries

    except FileNotFoundError as error:
        log.error(error)

    except Exception as e:  # pylint: disable=broad-except
        log.error(e)


def load_json_file(file: str) -> Tuple[bool, list]:
    """
    Load raw JSON content from a file.

    This function opens a JSON file, parses its contents, and returns a
    success flag along with the loaded data.

    Parameters
    ----------
    file : str
        Path to the JSON file.

    Returns
    -------
    Tuple[bool, list]
        A tuple containing:
        - success (bool): True if the file was loaded successfully.
        - data (list): Parsed JSON content.

    Logging
    -------
    Logs errors for file not found, JSON decode issues, or unexpected
    exceptions.

    Example
    -------
    >>> load_json_file("queries.json")
    (True, [...])
    """

    success = False
    # instantiate data list variable
    data: list = list()

    try:
        # open json file
        with open(file, "r", encoding="UTF-8") as file:
            # append loaded json file to data list variable
            data = json.load(file)

            if not data:
                raise FileNotFoundError
            else:
                success = True

            # return data list variable with json data
            return success, data

    except FileNotFoundError as error:
        log.error(error, exc_info=True)

    except json.JSONDecodeError as error:
        log.error(error, exc_info=True)

    except Exception as e:  # pylint: disable=broad-except
        log.error(e, exc_info=True)


def read_query_from_file(path: str) -> Tuple[bool, str]:
    """
    Read a raw SQL query from a text file.

    This function opens a file containing a SQL query, strips newline and tab
    characters, and returns the cleaned query string.

    Parameters
    ----------
    path : str
        Path to the query file.

    Returns
    -------
    Tuple[bool, str]
        A tuple containing:
        - success (bool): True if the query was read successfully.
        - query (str): Cleaned SQL query string.

    Logging
    -------
    Logs errors for file not found or unexpected exceptions.

    Example
    -------
    >>> read_query_from_file("create_table.sql")
    (True, "CREATE TABLE ...") 
    """
    success = False
    # instantiate query list variable
    query: str = None

    try:
        # open query file
        with open(path, "r", encoding="UTF-8") as query:
            # read query file
            # load into query variable
            query = query.read().replace("\n", "").replace("\t", "")

        if query:
            success = True

        # return success bool and query list variable
        return success, query

    except FileNotFoundError as error:
        log.error(error, exc_info=True)

    except Exception as e:  # pylint: disable=broad-except
        log.error(e, exc_info=True)


def get_query_list_from_file(name: str, queries: str) -> Tuple[bool, list]:
    """
    Extract a list of query tuples from JSON content.

    This function iterates over a list of query dictionaries and constructs a
    list of (table_id, query_string) tuples for downstream execution or
    mapping.

    Parameters
    ----------
    name : str
        The key name used to extract query strings from each dictionary.
    queries : str
        A list of dictionaries containing query metadata.

    Returns
    -------
    Tuple[bool, list]
        A tuple containing:
        - success (bool): True if the query list was constructed successfully.
        - query_list (list): List of (table_id, query_string) tuples.

    Logging
    -------
    Logs success for each query added and failure if the list is empty.

    Example
    -------
    >>> get_query_list_from_file("destination_query_create", queries)
    (True, [(1, "CREATE TABLE ..."), (2, "CREATE TABLE ...")])
    """

    success = False
    # instantiate query_list list variable
    query_list: list = list()

    try:
        for query in queries:
            # append create query to query_list variable
            query_list.append((int(query["table_id"]), query[f"{name}"]))

            log.info(f"🟢 SUCCESS: {query[f'{name}']} added to query list.")

        # test if query_list is not empty
        success = vh.validate_list(f"{name}", query_list)

        if not success:
            log.error(f"🔴 FAILED: {query[f'{name}']} not added to query \
                        list.")

        # return success boolean and query_list variable
        return success, query_list

    except Exception as e:  # pylint: disable=broad-except
        log.error(e, exc_info=True)
