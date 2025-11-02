"""
JSON Query Utilities Module
===========================

This module provides utility functions for reading and validating JSON files
and query text files. It integrates logging and validation to ensure robust
data ingestion workflows.

Overview
--------

The module supports the following operations:

- Reading JSON files and validating their contents.
- Loading raw JSON data from disk.
- Reading SQL or text-based queries from files.
- Extracting query tuples from JSON structures.

Dependencies
------------

- ``json``: Standard Python JSON parser.
- ``utils.logger``: Custom logging configuration.
- ``utils.validation.validate_list``: Utility for checking non-empty lists
with logging.

Functions
---------

.. function:: read_json_file(name: str, file: str)

   Reads and validates a JSON file.

   :param name: A label used in log messages to identify the file.
   :type name: str
   :param file: Path to the JSON file.
   :type file: str
   :return: Tuple of (success flag, parsed JSON list).
   :rtype: tuple[bool, list]

   Logs success or failure and validates that the JSON content is a non-empty
   list.

.. function:: load_json_file(file: str)

   Loads raw JSON data from a file.

   :param file: Path to the JSON file.
   :type file: str
   :return: Parsed JSON data as a list.
   :rtype: list

   Handles file not found and JSON decoding errors with logging.

.. function:: read_query_from_file(path: str)

   Reads a query from a plain text file and strips newlines and tabs.

   :param path: Path to the query file.
   :type path: str
   :return: Query string with whitespace removed.
   :rtype: str

   Logs file access or read errors.

.. function:: get_query_list_from_file(name: str, queries: str)

   Extracts a list of query tuples from a JSON-like structure.

   :param name: Key name to extract from each query dictionary.
   :type name: str
   :param queries: List of dictionaries containing query metadata.
   :type queries: list[dict]
   :return: Tuple of (success flag, list of (table_id, query) tuples).
   :rtype: tuple[bool, list[tuple[int, str]]]

   Logs each successful query extraction and validates the final list.
"""

import json

from utils.logger import logging
from utils.validation import validate_list


def read_json_file(name: str, file: str):
    """
    Reads and validates a JSON file.

    :param name: A label used in log messages to identify the file.
    :type name: str
    :param file: Path to the JSON file.
    :type file: str
    :return: Tuple of (success flag, parsed JSON list).
    :rtype: tuple[bool, list]

    Logs success or failure and validates that the JSON content is a non-empty
    list.
    """

    # instantiate queries string variable
    queries: list = list()

    try:
        # load json data from file into queries variable
        queries = load_json_file(file)

        # test if queries variable is empty
        if queries:
            logging.info(f"SUCCESS: {name} JSON file read.")
        else:
            logging.warning(f"FAILURE:{name} JSON file was not read.")

    except FileNotFoundError as error:
        logging.error(error)

    except Exception as e:  # pylint: disable=broad-except
        logging.error(e)

    # test if queries list is not empty
    success = validate_list(f"{name} JSON File", queries)

    # return success boolean and queries variable
    return (success, queries)


def load_json_file(file: str):
    """
     Loads raw JSON data from a file.

    :param file: Path to the JSON file.
    :type file: str
    :return: Parsed JSON data as a list.
    :rtype: list

    Handles file not found and JSON decoding errors with logging.
    """

    # instantiate data list variable
    data: list = list()

    try:
        # open json file
        with open(file, "r", encoding="UTF-8") as file:
            # append loaded json file to data list variable
            data = json.load(file)

    except FileNotFoundError as error:
        logging.error(error)

    except json.JSONDecodeError as error:
        logging.error(error)

    except Exception as e:  # pylint: disable=broad-except
        logging.error(e)

    # return data list variable with json data
    return data


def read_query_from_file(path: str):
    """
     Reads a query from a plain text file and strips newlines and tabs.

    :param path: Path to the query file.
    :type path: str
    :return: Query string with whitespace removed.
    :rtype: str

    Logs file access or read errors.
    """

    # instantiate query list variable
    query: str = None

    try:
        # open query file
        with open(path, "r", encoding="UTF-8") as query:
            # read query file
            # load into query list variable
            query = query.read().replace("\n", "").replace("\t", "")

    except FileNotFoundError as error:
        logging.error(error)

    except Exception as e:  # pylint: disable=broad-except
        logging.error(e)

    # return query list variable
    return query


def get_query_list_from_file(name: str, queries: str):
    """
     Extracts a list of query tuples from a JSON-like structure.

    :param name: Key name to extract from each query dictionary.
    :type name: str
    :param queries: List of dictionaries containing query metadata.
    :type queries: list[dict]
    :return: Tuple of (success flag, list of (table_id, query) tuples).
    :rtype: tuple[bool, list[tuple[int, str]]]

    Logs each successful query extraction and validates the final list.
    """

    # instantiate query_list list variable
    query_list: list = list()

    try:
        for query in queries:
            # append create query to query_list variable
            query_list.append((int(query["table_id"]), query[f"{name}"]))

            logging.info(f"SUCCESS: {query[f'{name}']} added to query list.")

    except Exception as e:  # pylint: disable=broad-except
        logging.error(e)

    # test if query_list is not empty
    success = validate_list(f"{name}", query_list)

    # return success boolean and query_list variable
    return (success, query_list)
