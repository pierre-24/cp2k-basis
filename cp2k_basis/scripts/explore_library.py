"""Explore the content of a library in HDF5
"""

import argparse
import pathlib
import h5py

from cp2k_basis.basis_set import BasisSetsStorage
from cp2k_basis.pseudopotential import PseudopotentialsStorage


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=pathlib.Path)

    args = parser.parse_args()

    with h5py.File(args.source) as f:
        if 'basis_sets' in f:
            storage = BasisSetsStorage.read_hdf5(f)
            storage.tree()
        else:
            print('No `basis_sets` storage')
        if 'pseudopotentials' in f:
            storage = PseudopotentialsStorage.read_hdf5(f)
            storage.tree()
        else:
            print('No `pseudopotentials` storage')


if __name__ == '__main__':
    main()
