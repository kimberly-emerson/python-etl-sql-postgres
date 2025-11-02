"""
Logging Configuration Module
============================

This module sets up application-wide logging using Python's built-in
``logging`` module and environment-based configuration via ``python-decouple``.

Overview
--------

The module configures both file-based and console logging. It reads the log
file path from an environment variable and sets up a root logger with a
detailed format for file logs and a simplified format for console output.

Environment Configuration
-------------------------

The following environment variable must be defined in a ``.env`` file or
system environment:

- ``LOGS_PATH``: Directory path where the log file ``app.log`` will be created.

Dependencies
------------

- ``logging``: Standard Python logging library.
- ``decouple``: Used to retrieve environment variables safely.

Logging Setup
-------------

- **File Logging**:
  - Output file: ``{LOGS_PATH}\\app.log``
  - Log level: ``DEBUG``
  - Format: ``%(asctime)s - %(levelname)s - %(name)s - %(message)s``
  - Date format: ``%Y-%m-%d %H:%M:%S``

- **Console Logging**:
  - Output stream: ``sys.stderr``
  - Log level: ``DEBUG``
  - Format: ``%(name)-12s: %(levelname)-8s %(message)s``

Usage
-----

This module is typically imported at the entry point of the application to
ensure consistent logging behavior across all modules.

Example::

    import logging
    from my_logging_module import setup_logging  # if wrapped in a function

    logger = logging.getLogger(__name__)
    logger.info("Application started.")

Notes
-----

- The console handler is added to the root logger, so all loggers will inherit
this behavior unless explicitly overridden.
- Ensure the ``LOGS_PATH`` directory exists before running the application to
avoid file creation errors.
"""

import logging
from decouple import config

LOGS_PATH = config("LOGS_PATH")


logging.basicConfig(
    filename=f"{LOGS_PATH}\\app.log",
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)
