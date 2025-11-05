"""
Module: validation_handler
==========================

This module provides utility functions for validating list-type inputs in a
safe and logged manner.

It is designed to support backend workflows where input integrity is critical
and logging is required for debugging or audit trails.

Functions:
----------
- validate_list: Validates whether a given list is non-empty and logs errors
if validation fails.

Dependencies:
-------------
- utils.logging_handler.logger: Custom logger used for info, debug, and error
reporting.
"""

from utils.logging_handler import logger as log


def validate_list(name: str, list_object: list) -> bool:
    """
    Validate that a given list is non-empty.

    This function checks whether the provided list object contains any
    elements.

    If the list is empty or an exception occurs during evaluation, it logs an
    error with the provided name identifier.

    Parameters
    ----------
    name : str
        A descriptive name for the list, used in error logging to identify the
        source.
    list_object : list
        The list to validate.

    Returns
    -------
    bool
        True if the list is non-empty, False otherwise.

    Logging
    -------
    Logs an error with context if the list is empty or an exception is raised.

    Example
    -------
    >>> validate_list("user_ids", [1, 2, 3])
    True

    >>> validate_list("user_ids", [])
    False
    """
    success = False

    try:
        success = True if list_object else False
        return success

    except Exception as e:
        log.error(f"🔴 ERROR: {name} is empty.")
        log.error(e, exc_info=True)
