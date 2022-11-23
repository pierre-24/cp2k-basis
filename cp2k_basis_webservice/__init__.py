"""
Implementation of a working webservice
"""

import os
import pathlib

import h5py
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from cp2k_basis.atoms import SYMB_TO_Z
from cp2k_basis.basis_set import AtomicBasisSets
from cp2k_basis.pseudopotential import AtomicPseudopotentials


limiter = Limiter(key_func=get_remote_address)


class Config:
    LIBRARY = 'library.h5'

    BASIS_SETS_PER_ATOM = []
    ATOMS_PER_BASIS_SET = []
    PSEUDOPOTENTIALS_PER_ATOM = []
    ATOMS_PER_PSEUDOPOTENTIAL = []


def load_library(app: Flask):

    basis_sets_per_atom = {}
    atom_per_bs = {}
    pseudos_per_atom = {}
    atom_per_pseudo = {}

    path = pathlib.Path(app.config['LIBRARY'])
    if not path.exists():
        raise FileNotFoundError('Library file `{}` does not exists'.format(path))

    with h5py.File(path) as f:
        if 'basis_sets' in f:
            for symbol, group in f['basis_sets'].items():
                if symbol not in SYMB_TO_Z:
                    continue

                atomic_basis_sets = AtomicBasisSets.read_hdf5(group)
                basis_sets_per_atom[symbol] = atomic_basis_sets
                for name in atomic_basis_sets.basis_sets.keys():
                    if name not in atom_per_bs:
                        atom_per_bs[name] = []
                    atom_per_bs[name].append(symbol)

        if 'pseudopotentials' in f:
            for symbol, group in f['pseudopotentials'].items():
                if symbol not in SYMB_TO_Z:
                    continue

                atomic_pseudos = AtomicPseudopotentials.read_hdf5(group)
                pseudos_per_atom[symbol] = atomic_pseudos
                for name in atomic_pseudos.pseudopotentials.keys():
                    if name not in atom_per_pseudo:
                        atom_per_pseudo[name] = []
                    atom_per_pseudo[name].append(symbol)

    app.config['BASIS_SETS_PER_ATOM'] = basis_sets_per_atom
    app.config['ATOMS_PER_BASIS_SET'] = atom_per_bs
    app.config['PSEUDOPOTENTIALS_PER_ATOM'] = pseudos_per_atom
    app.config['ATOMS_PER_PSEUDOPOTENTIAL'] = atom_per_pseudo


def create_app():

    # create and configure app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config())
    app.config.from_pyfile('settings.py', silent=True)

    # add other modules
    limiter.init_app(app)

    # load library
    load_library(app)

    # add blueprint(s)
    from cp2k_basis_webservice.blueprint import visitor_blueprint
    app.register_blueprint(visitor_blueprint)

    return app
