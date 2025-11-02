"""
Validation Utilities Module
===========================

This module provides utility functions for validating data structures, with
integrated logging support.

Overview
--------

The module imports a preconfigured logger from ``utils.logger`` and defines a
single validation function for checking list contents.

Dependencies
------------

- ``utils.logger.logging``: Custom logging configuration used to record
validation failures.

Functions
---------

.. function:: validate_list(name, list)

   Validates whether a given list is non-empty.

   :param name: A string identifier used in the log message to describe the
   list.
   :type name: str
   :param list: The list to validate.
   :type list: list
   :return: ``True`` if the list is non-empty, ``False`` otherwise.
   :rtype: bool

   :Example:

   .. code-block:: python

      from utils.validation import validate_list

      items = [1, 2, 3]
      if validate_list("items", items):
          print("List is valid.")
      else:
          print("List is empty.")

   :Notes:

   - If the list is empty, a warning is logged using the format:
   ``FAILURE: {name} is empty.``
   - This function is useful for precondition checks in data pipelines or
   configuration validation.
"""

from utils.logger import logging


def validate_list(name, list: list):
    """
    .. function:: validate_list(name, list)

   Validates whether a given list is non-empty and logs a warning if it is
   empty.

   :param name: A descriptive name used in the log message to identify the
   list.
   :type name: str
   :param list: The list to be validated.
   :type list: list
   :return: ``True`` if the list contains elements, ``False`` otherwise.
   :rtype: bool

   **Behavior:**

   - Returns ``True`` if the list is non-empty.
   - Returns ``False`` and logs a warning if the list is empty.
   - The warning message format is: ``FAILURE: {name} is empty.``

   **Example usage:**

   .. code-block:: python

      items = []
      if not validate_list("items", items):
          print("Validation failed: items list is empty.")
    """
    success = False

    if list:
        success = True
    else:
        logging.warning(f"FAILURE: {name} is empty.")

    return success
