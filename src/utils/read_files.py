"""
Query Reader Module

This module provides functionality for reading and sanitizing query strings from text files.
It is designed to support use cases where SQL or other structured queries are stored externally
and need to be loaded into a Python application.

Features:
- Removes newline and tab characters from query files for cleaner formatting.
- Logs errors if the file is missing or unreadable.

Dependencies:
- logging: Used to report file access errors.

Functions:
- read_query_from_file(path=None): Reads a query from the specified file path and 
returns a sanitized string.

Example:
    query = read_query_from_file("queries/select_users.sql")
    if query:
        execute_query(query)

"""

import logging


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
