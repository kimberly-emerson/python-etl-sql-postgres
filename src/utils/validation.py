import logging

def validate_list(name, list: list):
    """
    tba
    """
    success = False

    if list:
        success = True
    else: 
        logging.warning(f"FAILURE: {name} is empty.")

    return success