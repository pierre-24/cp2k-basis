"""
This website provides an equivalent to the famous basis set exchange for the basis sets and GTH pseudopotentials
used in the CP2K program.
"""

import pathlib

import h5py
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import cp2k_basis
from cp2k_basis.basis_set import BasisSetsStorage
from cp2k_basis.pseudopotential import PseudopotentialsStorage


COMMON_CONTEXT = dict(
    site_name='cp2k-basis',
    site_version=cp2k_basis.__version__,
    author=cp2k_basis.__author__,
    code_repo='https://github.com/pierre-24/cp2k-basis',
    documentation='https://pierre-24.github.io/cp2k-basis',
    bootstrap_version='5.2.3',
    keywords='cp2k, basis sets, pseudopotentials, GTH pseudopotentials',
    twitter_account='@PierreBeaujean',
    description=__doc__,
)


limiter = Limiter(key_func=get_remote_address)


class Config:
    # Flask
    SERVER_NAME = '127.0.0.1:5000'
    PREFERRED_URL_SCHEME = 'http'

    # API
    API_LIMIT = '10/second'

    # library
    LIBRARY = 'library/library.h5'

    # to be filled by `load_library()`
    BASIS_SETS_STORAGE = None
    PSEUDOPOTENTIALS_STORAGE = None


def load_library(app: Flask):
    path = pathlib.Path(app.config['LIBRARY'])
    if not path.exists():
        raise FileNotFoundError('Library file `{}` does not exists'.format(path))

    with h5py.File(path) as f:
        bs_storage = BasisSetsStorage.read_hdf5(f)
        pp_storage = PseudopotentialsStorage.read_hdf5(f)

    app.config['BASIS_SETS_STORAGE'] = bs_storage
    app.config['PSEUDOPOTENTIALS_STORAGE'] = pp_storage


def create_app(instance_relative_config=True):

    # create and configure app
    app = Flask(__name__, instance_relative_config=instance_relative_config)
    app.config.from_object(Config())
    app.config.from_pyfile('settings.py', silent=True)

    # add other modules
    limiter.init_app(app)

    # load library
    load_library(app)

    # add blueprint(s)
    from cp2k_basis_webservice.blueprints import visitor_blueprint, api_blueprint
    app.register_blueprint(visitor_blueprint)
    app.register_blueprint(api_blueprint)

    return app
