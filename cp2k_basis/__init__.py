"""
Implementation of a parser for CP2K basis sets and pseudopotentials, and of their storage as an HDF5 file.
"""

import logging
import os


__version__ = '0.5.2'
__author__ = 'Pierre Beaujean'
__maintainer__ = 'Pierre Beaujean'
__email__ = 'pierre.beaujean@unamur.be'
__status__ = 'Development'

# logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get('LOGLEVEL', 'WARNING'))
