# Configuration file for the Sphinx documentation builder.

import os
import sys
import logging

# Set up logging for debugging purposes
logging.basicConfig(filename='config.log', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

try:
    # Add the parent directory to the system path
    sys.path.insert(0, os.path.abspath(".."))
except Exception as e:
    logging.error(f"Error inserting parent directory to sys.path: {e}")
    print("An error occurred while setting up the project path. Please check the logs for more details.")

#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "NewsAI"
copyright = "2024, Devasy Patel, Hemang Joshi, Vraj Patel"
author = "Devasy Patel, Hemang Joshi, Vraj Patel"
release = "1.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "myst_parser",  # Add this line
]
# Include markdown support
myst_enable_extensions = [
    "colon_fence",
    "html_image",
]
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",  # Add this line to recognize markdown files
}
# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

try:
    # Additional settings that might raise exceptions
    if not os.path.isdir('_static'):
        raise FileNotFoundError("The '_static' directory does not exist.")
except FileNotFoundError as fnf_error:
    logging.error(fnf_error)
    print(f"An error occurred: {fnf_error}. Please check your static file path.")
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")
    print("An unexpected error occurred during configuration setup. Please check the logs.")
