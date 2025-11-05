"""
Module: logging_handler
======================+

This module initializes and configures the logging system for the application.
It supports both file-based and console logging, with dynamic log level
selection based on environment variables. It also ensures that error-level
logs are routed to a dedicated error log file for audit and debugging purposes.

Purpose
-------
- Dynamically configure logging level and output file based on environment
settings.
- Format logs consistently across file and console outputs.
- Route error-level logs to a separate file for traceability.

Environment Variables
---------------------
- LOGS_PATH : str
    Directory path where log files will be written.
- LOG_LEVEL : str
    Logging level to apply (e.g., INFO, DEBUG, ERROR).

Logging Behavior
----------------
- INFO → logs to `app.log`
- DEBUG → logs to `debug.log`
- ERROR → logs to `error.log`
- All logs are timestamped and formatted for readability.
- Console output uses simplified formatting.
- Error logs are duplicated to `error.log` regardless of global level.

Handlers
--------
- FileHandler : Writes logs to dynamically selected log file.
- StreamHandler : Outputs logs to stderr for console visibility.
- ErrorHandler : Captures and writes ERROR-level logs to `error.log`.

Example
-------
To enable DEBUG logging and route logs to a specific directory:

.. code-block:: bash

    export LOG_LEVEL=DEBUG
    export LOGS_PATH=/var/logs/my_app

Notes
-----
- Uses `decouple.config` for environment variable management.
- Compatible with modular applications requiring centralized logging.
- Designed for extensibility and integration with external monitoring tools.
"""

import logging
from decouple import config


LOGS_PATH = config("LOGS_PATH")

logger = logging.getLogger()
log_level = getattr(logging, config("LOG_LEVEL"), None)

log_file: str = None
match log_level:
    case logging.INFO:
        log_file = "app.log"
    case logging.DEBUG:
        log_file = "debug.log"
    case logging.ERROR:
        log_file = "error.log"
    case _:
        log_file = "app.log"


logging.basicConfig(
    filename=f"{LOGS_PATH}\\{log_file}",
    level=log_level,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# define a Handler which writes LOG_LEVEL messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(log_level)

# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')

# tell the handler to use this format
console.setFormatter(formatter)

# write ERROR messages to error log
error_file_handler = logging.FileHandler(f"{LOGS_PATH}\\error.log")
error_file_handler.setLevel(logging.ERROR)

# add the handler to the root logger
logger.addHandler(console)
# add error_file_handler to logger
logger.addHandler(error_file_handler)
