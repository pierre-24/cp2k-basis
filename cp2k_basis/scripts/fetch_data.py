"""
Fetch the basis sets and pseudopotentials as described in the input, and pack them together as a library (HDF5 file).
See https://github.com/pierre-24/cp2k-basis/blob/master/DATA_SOURCES.yml for a description of the input, and
https://github.com/pierre-24/cp2k-basis/blob/master/docs/library_file_format.md for a description of the output.
"""

import pathlib
from typing import Tuple

import h5py
import yaml
import argparse
import requests
import re

from cp2k_basis import logger
from cp2k_basis.basis_set import AtomicBasisSetsParser, BasisSetsStorage
from cp2k_basis.base_objects import FilterFirst, FilterUnique, Storage, AddMetadata
from cp2k_basis.pseudopotential import AtomicPseudopotentialsParser, PseudopotentialsStorage


def fetch_data(data_sources: dict) -> Tuple[Storage, Storage]:
    """Fetch data from files that are found in repositories.
    """

    # storages
    bs_storage = BasisSetsStorage()
    pp_storage = PseudopotentialsStorage()

    # fetch files
    for data_source in data_sources:
        if 'data' in data_source:
            base_url = data_source['base'].format(**data_source['data'])
        else:
            base_url = data_source['base']

        for file in data_source['files']:
            full_url = base_url + file['name']
            logger.info('fetch {} [{}]'.format(full_url, file['type']))

            response = requests.get(full_url)

            # build the rules for the name
            filter_name = FilterUnique([(re.compile(r'.*'), '\\0')])
            if 'family_name' in file:
                filter_name = FilterUnique.create(file['family_name'])

            filter_variant = FilterFirst([(re.compile(r'.*'), 'q0')])
            if 'variant' in file:
                filter_variant = FilterFirst.create(file['variant'])

            # build the rules for the metadata
            add_metadata = AddMetadata({})
            if 'metadata' in file:
                add_metadata = AddMetadata.create(file['metadata'])

            add_metadata.rules['source'] = [(re.compile(r'.*',), full_url)]  # add rule for source

            # fetch data and store them
            if file['type'] == 'BASIS_SETS':
                iterator = AtomicBasisSetsParser(response.content.decode('utf8')).iter_atomic_basis_set_variants()
                bs_storage.update(iterator, filter_name, filter_variant, add_metadata)

            elif file['type'] == 'POTENTIALS':
                iterator = AtomicPseudopotentialsParser(
                    response.content.decode('utf8')).iter_atomic_pseudopotential_variants()
                pp_storage.update(iterator, filter_name, filter_variant, add_metadata)

    return bs_storage, pp_storage


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('source', type=argparse.FileType('r'))
    parser.add_argument('-o', '--output', default='library.h5', type=pathlib.Path)

    args = parser.parse_args()

    # load data
    data_sources = yaml.load(args.source, yaml.Loader)
    bs_storage, pp_storage = fetch_data(data_sources)

    bs_storage.tree()
    pp_storage.tree()

    # write library
    logger.info('writing in {}'.format(args.output))
    with h5py.File(args.output, 'w') as f:
        bs_storage.dump_hdf5(f)
        pp_storage.dump_hdf5(f)


if __name__ == '__main__':
    main()
