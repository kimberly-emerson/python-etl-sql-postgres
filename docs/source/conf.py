# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
from decouple import config

sys.path.insert(0, os.path.abspath(config("SRC_PATH")))
sys.path.insert(0, os.path.abspath(f"{config("SRC_PATH")}\\db"))
sys.path.insert(0, os.path.abspath(f"{config("SRC_PATH")}\\build"))
sys.path.insert(0, os.path.abspath(f"{config("SRC_PATH")}\\extract"))
sys.path.insert(0, os.path.abspath(f"{config("SRC_PATH")}\\load"))
sys.path.insert(0, os.path.abspath(f"{config("SRC_PATH")}\\utils"))

project = 'ETL Orchestrator for PostgreSQL'
copyright = '2025, Kimberly Emerson'
author = 'Kimberly Emerson'

version = '0.1.0'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

# Napoleon settings for Google style docstrings
napoleon_google_docstring = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_include_private_with_doc = True

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
