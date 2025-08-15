"""
tba
"""

import os
import logging
from db.postgresql import execute_pg_query, set_pg_connection
from utils.file_handler import get_query_list_from_file, load_json_file, read_query_from_file

DESTINATION_PATH = f"{os.getenv("SQL_PATH")}\\destination"


def insert_pg_tables(file: str, data: list):
    """
    tba
    """

    # instantiate success boolean variable to be returned
    success: bool = False
    
    try:
        # read mapping_destination.json file
        queries: tuple = load_json_file(file)
        
        # test if queries is not empty
        if queries[0]:

            # get destination query file list
            query_list = get_query_list_from_file("destination_query_insert", queries)

            logging.info("------ EXECUTE INSERT SQL SCRIPTS ------")
            
            for table in query_list[1]:
                
                # filter source data for destination table
                values = [t for t in data if t[0] == table[0]]

                 # construct full path to destination query file
                file = f"{DESTINATION_PATH}\\{table[1]}"
                
                # read query from file
                query = read_query_from_file(file)
                
                # query = query.replace(',)',')')                
                if not query:
                    logging.warning(f"{file} does not return a query.")
                    raise FileNotFoundError
                
            
                # set connection to postgresql database
                conn = set_pg_connection("aw_sales")
                
                # execute insert query
                execute_pg_query(conn,query=query,values=values[0][1])
                
                # set success variable
                success = True

                print(f"{file[49:len(file)]} executed.")
    
    except FileNotFoundError as error:
        logging.error(error)
        print(error)
    
    except Exception as e:  # pylint: disable=broad-except
        logging.error(e)
        print(e)

    # return success boolean
    return success
