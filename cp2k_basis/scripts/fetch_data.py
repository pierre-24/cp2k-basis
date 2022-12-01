"""
Fetch the basis sets and pseudopotentials as described in the input, and pack them together as a library (HDF5 file).
See https://github.com/pierre-24/cp2k-basis/blob/master/DATA_SOURCES.yml for a description of the input, and
https://github.com/pierre-24/cp2k-basis/blob/master/docs/library_file_format.md for a description of the output.
"""

import pathlib
from typing import List

import h5py
import yaml
import argparse
import requests
import re

from cp2k_basis import logger
from cp2k_basis.basis_set import AtomicBasisSetsParser, BasisSetsStorage
from cp2k_basis.base_objects import FilterName, Storage, AddMetadata
from cp2k_basis.pseudopotential import AtomicPseudopotentialsParser, PseudopotentialsStorage


def fetch_data(data_sources: dict) -> List[Storage]:
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
            name_rules = []
            if 'filter_name' in file:
                for rule_pattern, rule_value in file['filter_name'].items():
                    name_rules.append((re.compile(rule_pattern), rule_value))

            filter_name = FilterName(name_rules)

            # build the rules for the metadata
            metadata_rules = {}
            if 'metadata' in file:
                for key, rule_set in file['metadata'].items():
                    metadata_rules[key] = []
                    for rule_pattern, rule_value in rule_set.items():
                        metadata_rules[key].append((re.compile(rule_pattern), rule_value))

            metadata_rules['source'] = [(re.compile(r'.*',), full_url)]  # add rule for source

            add_metadata = AddMetadata(metadata_rules)

            # fetch data and store them
            if file['type'] == 'BASIS_SETS':
                iterator = AtomicBasisSetsParser(response.content.decode('utf8')).iter_atomic_basis_set_variants()
                bs_storage.update(iterator, filter_name, add_metadata)

            elif file['type'] == 'POTENTIALS':
                iterator = AtomicPseudopotentialsParser(response.content.decode('utf8')).iter_atomic_pseudopotentials()
                pp_storage.update(iterator, filter_name, add_metadata)

    return [bs_storage, pp_storage]


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('source', type=argparse.FileType('r'))
    parser.add_argument('-o', '--output', default='library.h5', type=pathlib.Path)

    args = parser.parse_args()

    # load data
    data_sources = yaml.load(args.source, yaml.Loader)
    bs_storage, pp_storage = fetch_data(data_sources)

    # write library
    with h5py.File(args.output, 'w') as f:
        bs_storage.dump_hdf5(f)
        pp_storage.dump_hdf5(f)


if __name__ == '__main__':
    main()
