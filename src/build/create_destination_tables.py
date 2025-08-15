"""
tba
"""

import os
import logging
from db.postgresql import execute_pg_query, set_pg_connection
from utils.file_handler import read_json_file, get_query_list_from_file, read_query_from_file
from utils.validation import validate_list

DESTINATION_PATH = f"{os.getenv("SQL_PATH")}\\destination"


def create_pg_tables(file: str):
    
    try:
        queries = read_json_file("Destination Mapping", file)
        
        if queries[0]:
            query_list = get_query_list_from_file("destination_query_create",queries[1])

            for table in query_list[1]:

                file = f"{DESTINATION_PATH}\\{table[1]}"
                
                query = read_query_from_file(file)
                
                if not query:
                    logging.warning(f"{file} does not return a query.")
                    raise FileNotFoundError
                
                conn = set_pg_connection("aw_sales")
                
                execute_pg_query(conn,query=query)
                
                print(f"{file[49:len(file)]} executed.")

    except FileNotFoundError as error:
        logging.error(error)

    except Exception as e:  # pylint: disable=broad-except
        logging.error(e)
