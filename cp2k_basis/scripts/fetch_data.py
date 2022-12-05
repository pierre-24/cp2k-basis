"""
Fetch the basis sets and pseudopotentials as described in the input, and pack them together as a library (HDF5 file).
See https://github.com/pierre-24/cp2k-basis/blob/master/library/DATA_SOURCES.yml for a description of the input, and
https://github.com/pierre-24/cp2k-basis/blob/master/docs/library_file_format.md for a description of the output.
"""

import pathlib
from typing import Tuple
import diffpatch

import h5py
import yaml
import argparse
import requests
import re

from cp2k_basis import logger
from cp2k_basis.basis_set import AtomicBasisSetsParser, BasisSetsStorage
from cp2k_basis.base_objects import FilterFirst, FilterUnique, Storage, AddMetadata
from cp2k_basis.pseudopotential import AtomicPseudopotentialsParser, PseudopotentialsStorage


def extract_from_file(
        content: str, file_def: dict, bs_storage: BasisSetsStorage, pp_storage: PseudopotentialsStorage, base_url: str):

    # build the rules for the name
    filter_name = FilterUnique([(re.compile(r'^(.*)$'), '\\1')])
    if 'family_name' in file_def:
        filter_name = FilterUnique.create(file_def['family_name'])

    filter_variant = FilterFirst([(re.compile(r'^.*$'), 'q0')])
    if 'variant' in file_def:
        filter_variant = FilterFirst.create(file_def['variant'])

    # build the rules for the metadata
    add_metadata = AddMetadata({})
    if 'metadata' in file_def:
        add_metadata = AddMetadata.create(file_def['metadata'])

    add_metadata.rules['source'] = [(re.compile(r'.*', ), base_url + file_def['name'])]  # add rule for source

    # apply patch, if any
    if 'patch' in file_def:
        with open(file_def['patch']) as f:
            content = diffpatch.apply_patch(content, f.read())

    # fetch data and store them
    if file_def['type'] == 'BASIS_SETS':
        iterator = AtomicBasisSetsParser(content).iter_atomic_basis_set_variants()
        bs_storage.update(iterator, filter_name, filter_variant, add_metadata)

    elif file_def['type'] == 'POTENTIALS':
        iterator = AtomicPseudopotentialsParser(content).iter_atomic_pseudopotential_variants()
        pp_storage.update(iterator, filter_name, filter_variant, add_metadata)


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

        for file_def in data_source['files']:
            if file_def.get('disabled', False):
                continue

            full_url = base_url + file_def['name']
            logger.info('fetch {} [{}]'.format(full_url, file_def['type']))

            response = requests.get(full_url)

            extract_from_file(response.content.decode('utf8'), file_def, bs_storage, pp_storage, base_url)

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
