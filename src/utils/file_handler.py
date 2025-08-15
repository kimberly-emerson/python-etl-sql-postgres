"""
"""

import logging
import json
from utils.validation import validate_list


def read_json_file(name: str, file: str):   
    """
    tba
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
    tba
    """
    # instantiate query_list list variable
    query_list: list = list()

    try:        
        for query in queries:
            # append create query to query_list variable
            query_list.append((int(query['table_id']), query[f'{name}']))
            
            logging.info(f"SUCCESS: {query[f'{name}']} added to query list.")

    except Exception as e:  # pylint: disable=broad-except
        logging.error(e)

    # test if query_list is not empty
    success = validate_list(f"{name}", query_list)

    # return success boolean and query_list variable
    return (success, query_list)