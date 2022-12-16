"""
Fetch the basis sets and pseudopotentials as described in the input, and pack them together as a library (HDF5 file).
See https://github.com/pierre-24/cp2k-basis/blob/master/library/DATA_SOURCES.yml for a description of the input, and
https://github.com/pierre-24/cp2k-basis/blob/master/docs/library_file_format.md for a description of the output.
"""
import datetime
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

l_logger = logger.getChild('fetch_data')


def extract_from_file(
        content: str,
        file_def: dict,
        bs_storage: BasisSetsStorage,
        pp_storage: PseudopotentialsStorage,
        base_url: str,
        add_metadata: AddMetadata,
        pwd: pathlib.Path = pathlib.Path('.')
):

    # build the rules for the name
    filter_name = FilterUnique([(re.compile(r'^(.*)$'), '\\1')])
    if 'family_name' in file_def:
        filter_name = FilterUnique.create(file_def['family_name'])

    filter_variant = FilterFirst([])
    if 'variant' in file_def:
        filter_variant = FilterFirst.create(file_def['variant'])

    # apply patch, if any
    if 'patch' in file_def:
        l_logger.info('will apply patch `{}`'.format(file_def['patch']))
        with open(pwd / file_def['patch']) as f:
            content = diffpatch.apply_patch(content, f.read())

    # fetch data and store them:
    if file_def['type'] == 'BASIS_SETS':
        iterator = AtomicBasisSetsParser(
            content, source=base_url + file_def['name']).iter_atomic_basis_set_variants()
        bs_storage.update(iterator, filter_name, filter_variant, add_metadata)

    elif file_def['type'] == 'POTENTIALS':
        iterator = AtomicPseudopotentialsParser(
            content, source=base_url + file_def['name']).iter_atomic_pseudopotential_variants()
        pp_storage.update(iterator, filter_name, filter_variant, add_metadata)


def fetch_data(data_sources: dict, pwd: pathlib.Path = pathlib.Path('.')) -> Tuple[Storage, Storage]:
    """Fetch data from files that are found in repositories.
    """

    # storages
    bs_storage = BasisSetsStorage()
    pp_storage = PseudopotentialsStorage()

    # read metadata
    add_metadata = AddMetadata()
    if 'metadata' in data_sources:
        add_metadata = AddMetadata.create(data_sources['metadata'])

    # fetch files
    for data_source in data_sources['repositories']:
        if 'data' in data_source:
            base_url = data_source['base'].format(**data_source['data'])
        else:
            base_url = data_source['base']

        for file_def in data_source['files']:
            if file_def.get('disabled', False):
                continue

            full_url = base_url + file_def['name']
            l_logger.info('fetch {} [{}]'.format(full_url, file_def['type']))

            response = requests.get(full_url)

            extract_from_file(
                response.content.decode('utf8'), file_def, bs_storage, pp_storage, base_url, add_metadata, pwd)

    return bs_storage, pp_storage


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('source', type=argparse.FileType('r'))
    parser.add_argument('-o', '--output', default='library.h5', type=pathlib.Path)

    args = parser.parse_args()

    pwd = pathlib.Path(args.source.name).parent

    # load data
    l_logger.info('reading {}'.format(args.source.name))
    data_sources = yaml.load(args.source, yaml.Loader)
    bs_storage, pp_storage = fetch_data(data_sources, pwd)

    bs_storage.tree()
    pp_storage.tree()

    # write library
    l_logger.info('writing in {}'.format(args.output))
    with h5py.File(args.output, 'w') as f:
        f.attrs['date_build'] = datetime.datetime.now().isoformat()
        bs_storage.dump_hdf5(f)
        pp_storage.dump_hdf5(f)


if __name__ == '__main__':
    main()
