"""
Utility module for reading and processing JSON and query files.

This module provides two functions:
1. `read_json_file`: Reads a JSON file and returns its contents as a Python list.
2. `read_query_from_file`: Reads a query string from a file and sanitizes it by removing
   newline and tab characters.

Each function handles common file I/O errors gracefully by logging exceptions and returning
`None` when failures occur.

Functions:
    read_json_file(path=None):
        Loads a JSON file from the given path and returns its contents as a list.
        Assumes the JSON file contains a top-level array structure.

    read_query_from_file(path=None):
        Reads a query string from a file and removes newline and tab characters.

Usage Examples:
    >>> data = read_json_file("data.json")
    >>> if data:
    ...     for item in data:
    ...         print(item)

    >>> query = read_query_from_file("query.sql")
    >>> if query:
    ...     print(query)

Notes:
    - Both functions use UTF-8 encoding for file reading.
    - Errors such as file not found or malformed content are logged using the `logging` module.
    - Caller should validate returned values before use.
"""

import logging
import json

def read_json_file(path=None):
    """
    Module for reading and parsing JSON files into Python lists.

    This module provides a utility function `read_json_file` that attempts to open a JSON file
    from a given path and load its contents into a Python list. It handles common exceptions
    such as missing files and malformed JSON, logging errors accordingly.

    Functions:
        read_json_file(path=None):
            Opens a JSON file and returns its contents as a list. Returns None if an error occurs.

    Usage Example:
        >>> data = read_json_file("data.json")
        >>> if data:
        ...     for item in data:
        ...         print(item)

    Notes:
        - Assumes the JSON file contains a top-level array structure.
        - Uses UTF-8 encoding for file reading.
        - Logs errors instead of raising exceptions.
    """
    
    data = None

    try:
        with open(path, "r", encoding="UTF-8") as file:
            data = list(json.load(file))
    except FileNotFoundError as error:
        logging.error(error)
    except json.JSONDecodeError as error:
        logging.error(error)
    except Exception as e:  # pylint: disable=broad-except
        logging.error(e)

    return data


def read_query_from_file(path=None):
    """
    Reads and sanitizes a query string from a file.

    This function attempts to open the file at the specified path, read its contents,
    and remove all newline (`\n`) and tab (`\t`) characters. If the file is not found
    or another exception occurs during reading, the error is logged and `None` is returned.

    Parameters:
        path (str, optional): The file path to read the query from. Defaults to None.

    Returns:
        str or None: The sanitized query string if successful, otherwise None.
    """

    query = None

    try:
        with open(path, "r", encoding="UTF-8") as query:
            query = query.read().replace("\n", "").replace("\t", "")
    except FileNotFoundError as error:
        logging.error(error)
    except Exception as e:  # pylint: disable=broad-except
        logging.error(e)

    return query
