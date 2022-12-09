import argparse
import pathlib

import yaml

from cp2k_basis.basis_set import BasisSetsStorage
from cp2k_basis.pseudopotential import PseudopotentialsStorage

from cp2k_basis.scripts.fetch_data import extract_from_file


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('source', type=argparse.FileType('r'))

    args = parser.parse_args()

    pwd = pathlib.Path(args.source.name).parent
    bs_storage = BasisSetsStorage()
    pp_storage = PseudopotentialsStorage()

    data_sources = yaml.load(args.source, Loader=yaml.Loader)

    for file_def in data_sources:
        if file_def.get('disabled', False):
            continue

        with open(pwd / file_def['name']) as f:
            extract_from_file(f.read(), file_def, bs_storage, pp_storage, '', pwd)

    bs_storage.tree()
    pp_storage.tree()


if __name__ == '__main__':
    main()
