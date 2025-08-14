import os
import logging
import utils.logger
from db.sql_server import execute_sql_query
from utils.file_handler import read_json_file, read_query_from_file, get_query_list_from_file

SOURCE_PATH = f"{os.getenv("SQL_PATH")}\\source"


def get_source_data(file: str = None):
    
    loggerSource = logging.getLogger('source')
    logging.info("------ GET SOURCE DATA ------")

    # instantiate data list variable to be returned
    data: list = list()

    try:
        # read mapping_source.json file
        queries = read_json_file("Mapping Source", file)
        
        # test if queries is not empty
        if queries[0]:

            # get source query file list
            query_list = get_query_list_from_file("source_query_select", queries[1])

            for table in query_list[1]:
                # construct full path to source query file
                file = f"{SOURCE_PATH}\\{table[1]}"
                
                # read query from file
                query = read_query_from_file(file)
                
                # handle empty/missing query file
                if not query:

                    logging.warning(f"{file} does not return a query.")
                    raise FileNotFoundError
                
                # execute query using default postgres connection
                response = execute_sql_query(conn = None, query = query)

                print(f"{file[44:len(file)]} added.")
                
                # add query result to data list
                data.append((table[0], response))

    except FileNotFoundError as error:
        logging.error(error)

    except Exception as e:  # pylint: disable=broad-except
        logging.error(e)

    # return data list containing source data
    return data
