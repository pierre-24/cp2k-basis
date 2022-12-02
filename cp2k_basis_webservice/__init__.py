"""
Implementation of a working webservice
"""

import pathlib

import h5py
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from cp2k_basis.basis_set import BasisSetsStorage
from cp2k_basis.pseudopotential import PseudopotentialsStorage


limiter = Limiter(key_func=get_remote_address)


class Config:
    # Flask
    SERVER_NAME = '127.0.0.1:5000'
    PREFERRED_URL_SCHEME = 'http'

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
