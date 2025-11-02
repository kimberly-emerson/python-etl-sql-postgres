"""
Mapping Data Utilities Module
=============================

This module provides functions for reading, filtering, and writing mapping
data used in query orchestration pipelines. It leverages ``pandas`` for CSV
ingestion and transformation, and logs errors using a custom logger.

Overview
--------

The module supports:

- Reading source mapping data from CSV files.
- Reading destination mapping data from CSV files.
- Writing processed mapping data to JSON format.

Dependencies
------------

- ``pandas``: For reading and transforming tabular data.
- ``utils.logger``: Custom logging configuration.

Functions
---------

.. function:: get_source_mapping_data(filename)

   Reads source mapping data from a CSV file, filters for application tables,
   and sorts the result.

   :param filename: Path to the source mapping CSV file.
   :type filename: str
   :return: Filtered and sorted DataFrame containing source mapping data.
   :rtype: pandas.DataFrame

   **Columns expected:**

   - ``source_query_select``
   - ``table_id``
   - ``execution_order``
   - ``is_app_table``

   Logs errors if the file is missing or unreadable.

.. function:: get_destination_mapping_data(filename)

   Reads destination mapping data from a CSV file, filters for application
   tables, and sorts the result.

   :param filename: Path to the destination mapping CSV file.
   :type filename: str
   :return: Filtered and sorted DataFrame containing destination mapping data.
   :rtype: pandas.DataFrame

   **Columns expected:**

   - ``destination_query_create``
   - ``destination_query_insert``
   - ``table_id``
   - ``execution_order``
   - ``is_app_table``

   Logs errors if the file is missing or unreadable.

.. function:: write_mapping_data(data, output_filename)

   Writes a DataFrame to a JSON file in record-oriented format.

   :param data: DataFrame containing mapping data.
   :type data: pandas.DataFrame
   :param output_filename: Path to the output JSON file.
   :type output_filename: str
   :return: None

   Logs errors if the write operation fails.
"""

import pandas as pd

from utils.logger import logging


def get_source_mapping_data(filename):
    """
    Reads source mapping data from a CSV file, filters for application tables,
    and sorts the result.

    :param filename: Path to the source mapping CSV file.
    :type filename: str
    :return: Filtered and sorted DataFrame containing source mapping data.
    :rtype: pandas.DataFrame

    **Columns expected:**

    - ``source_query_select``
    - ``table_id``
    - ``execution_order``
    - ``is_app_table``

    Logs errors if the file is missing or unreadable.
    """
    try:
        # specify columns
        columns = ["source_query_select", "table_id", "execution_order",
                   "is_app_table"]
        # read csv file into dataframe
        df = pd.read_csv(filename, usecols=columns)
        # filter data
        filtered_df = df[df["is_app_table"] == 1]
        # sort data
        data = filtered_df.sort_values(by=["execution_order",
                                           "source_query_select"])
        return data
    except FileNotFoundError as e:
        logging.error(e)
    except Exception as e:  # pylint disable=broad-except
        logging.error(e)


def get_destination_mapping_data(filename):
    """
    Reads destination mapping data from a CSV file, filters for application
    tables, and sorts the result.

    :param filename: Path to the destination mapping CSV file.
    :type filename: str
    :return: Filtered and sorted DataFrame containing destination mapping data.
    :rtype: pandas.DataFrame

    **Columns expected:**

    - ``destination_query_create``
    - ``destination_query_insert``
    - ``table_id``
    - ``execution_order``
    - ``is_app_table``

    Logs errors if the file is missing or unreadable.
    """
    try:
        # specify columns
        columns = [
            "destination_query_create",
            "destination_query_insert",
            "table_id",
            "execution_order",
            "is_app_table",
        ]
        # read csv file into dataframe
        df = pd.read_csv(filename, usecols=columns)
        # filter data
        filtered_df = df[df["is_app_table"] == 1]
        # sort data
        data = filtered_df.sort_values(
            by=["execution_order", "destination_query_insert"]
        )
        return data
    except FileNotFoundError as e:
        logging.error(e)
    except Exception as e:  # pylint disable=broad-except
        logging.error(e)


def write_mapping_data(data, output_filename):
    """
    Writes a DataFrame to a JSON file in record-oriented format.

    :param data: DataFrame containing mapping data.
    :type data: pandas.DataFrame
    :param output_filename: Path to the output JSON file.
    :type output_filename: str
    :return: None

    Logs errors if the write operation fails.
    """
    try:
        # write mapping data to output filename
        data.to_json(output_filename, orient="records")
    except Exception as e:  # pylint disable=broad-except
        logging.error(e)
