import argparse
import re

from cp2k_basis.elements import print_availability
from cp2k_basis.base_objects import FilterName
from cp2k_basis.basis_set import AtomicBasisSetsParser, BasisSetsStorage
from cp2k_basis.pseudopotential import AtomicPseudopotentialsParser, PseudopotentialsStorage


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('source', type=argparse.FileType('r'))
    parser.add_argument('-t', '--type', type=str, choices=['B', 'P'], help='Basis sets (B) or pseudopotentials (P)')
    parser.add_argument('-E', '--exclude', type=str, help='Exclusion rules')

    args = parser.parse_args()

    # load data
    filter_name = lambda x: x  # noqa
    if args.exclude:
        filter_name = FilterName([(re.compile(r1), r2) for r1, r2 in (r.split('::') for r in args.exclude.split(';'))])

    if args.type == 'B':
        storage = BasisSetsStorage()
        storage.update(
            AtomicBasisSetsParser(args.source.read()).iter_atomic_basis_set_variants(), filter_name)
    else:
        storage = PseudopotentialsStorage()
        storage.update(
            AtomicPseudopotentialsParser(args.source.read()).iter_atomic_pseudopotential_variants(), filter_name)

    for name in storage:
        print_availability(name, list(storage[name]))


if __name__ == '__main__':
    main()
