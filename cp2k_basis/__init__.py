"""
Implementation of a parser for CP2K basis sets and pseudopotentials, and of their storage as an HDF5 file.
"""

import logging
import os

# logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get('LOGLEVEL', 'WARNING'))
