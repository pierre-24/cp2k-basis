import argparse
import pathlib
from typing import Tuple

import yaml

from cp2k_basis.base_objects import AddMetadata, Storage
from cp2k_basis.basis_set import BasisSetsStorage
from cp2k_basis.pseudopotential import PseudopotentialsStorage
from cp2k_basis.scripts import SCHEMA_EXPLORE_SOURCE_FILE

from cp2k_basis.scripts.fetch_data import extract_from_file


def explore_file(data_sources: dict, pwd: pathlib.Path = '.') -> Tuple[Storage, Storage]:
    # validata input
    data_sources = SCHEMA_EXPLORE_SOURCE_FILE.validate(data_sources)

    # create storage
    bs_storage = BasisSetsStorage()
    pp_storage = PseudopotentialsStorage()

    # read metadata
    add_metadata = AddMetadata()
    if 'metadata' in data_sources:
        add_metadata = AddMetadata.create(data_sources['metadata'])

    for file_def in data_sources['files']:
        if file_def.get('disabled', False):
            continue

        with open(pwd / file_def['name']) as f:
            extract_from_file(f.read(), file_def, bs_storage, pp_storage, '', add_metadata, pwd)

    return bs_storage, pp_storage


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('source', type=argparse.FileType('r'))

    args = parser.parse_args()

    pwd = pathlib.Path(args.source.name).parent
    data_sources = yaml.load(args.source, Loader=yaml.Loader)

    bs_storage, pp_storage = explore_file(data_sources, pwd)

    bs_storage.tree()
    pp_storage.tree()


if __name__ == '__main__':
    main()
