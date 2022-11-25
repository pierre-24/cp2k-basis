"""
Fetch the basis sets and pseudopotentials as described in the input, and pack them together as a library (HDF5 file).
See https://github.com/pierre-24/cp2k-basis/blob/master/DATA_SOURCES.yml for a description of the input, and
https://github.com/pierre-24/cp2k-basis/blob/master/library_file_format.md for a description of the output.
"""

import pathlib
import h5py
import yaml
import argparse
import requests
import re

from cp2k_basis import logger
from cp2k_basis.basis_set import AtomicBasisSetsParser
from cp2k_basis.parser import PruneAndRename
from cp2k_basis.pseudopotential import AtomicPseudopotentialsParser


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('source', type=argparse.FileType('r'))
    parser.add_argument('-o', '--output', default='library.h5', type=pathlib.Path)

    args = parser.parse_args()

    # load data
    data = yaml.load(args.source, yaml.Loader)

    basis_sets = {}
    pseudos = {}

    # fetch files
    for segment in data:
        if 'data' in segment:
            base_url = segment['base'].format(**segment['data'])
        else:
            base_url = segment['base']

        for file in segment['files']:
            full_url = base_url + file['name']
            logger.metadata('fetch {} [{}]'.format(full_url, file['type']))

            response = requests.get(full_url)

            rules = []
            for rule, dest in file['rules'].items():
                rules.append((re.compile(rule), dest))

            pp = PruneAndRename(rules)

            if file['type'] == 'BASIS_SETS':
                basis_sets = AtomicBasisSetsParser(response.content.decode('utf8')).atomic_basis_sets()

            elif file['type'] == 'POTENTIALS':
                pseudos = AtomicPseudopotentialsParser(
                    response.content.decode('utf8'),
                    prune_and_rename=pp,
                    source=full_url,
                    references=file['references']
                ).atomic_pseudopotentials(pseudos)

    with h5py.File(args.output, 'w') as f:
        for key, abs_ in basis_sets.items():
            abs_.dump_hdf5(f.create_group('basis_sets/{}'.format(key)))
        for key, app in pseudos.items():
            app.dump_hdf5(f.create_group('pseudopotentials/{}'.format(key)))


if __name__ == '__main__':
    main()
