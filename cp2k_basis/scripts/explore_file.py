import argparse
import re

from cp2k_basis.base_objects import FilterUnique, FilterFirst
from cp2k_basis.basis_set import AtomicBasisSetsParser, BasisSetsStorage
from cp2k_basis.pseudopotential import AtomicPseudopotentialsParser, PseudopotentialsStorage


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('source', type=argparse.FileType('r'))
    parser.add_argument('-t', '--type', type=str, choices=['B', 'P'], help='Basis sets (B) or pseudopotentials (P)')

    parser.add_argument('-n', '--name-rules', type=str, help='Naming rules')
    parser.add_argument('-v', '--variant-rules', type=str, help='Variant rules')

    args = parser.parse_args()

    # set default filters
    filter_name = FilterUnique([(re.compile(r'(.*)(-q.*)'), '\\1'), (re.compile('(.*)'), '\\1')])
    filter_variant = FilterFirst([(re.compile(r'.*-(q.*)'), '\\1')])

    # change filters if any
    if args.name_rules:
        filter_name = FilterUnique(
            [(re.compile(r1), r2) for r1, r2 in (r.split('::') for r in args.exclude.split(';'))])

    if args.variant_rules:
        filter_variant = FilterFirst(
            [(re.compile(r1), r2) for r1, r2 in (r.split('::') for r in args.exclude.split(';'))])

    if args.type == 'B':
        storage = BasisSetsStorage()
        storage.update(
            AtomicBasisSetsParser(args.source.read()).iter_atomic_basis_set_variants(),
            filter_name,
            filter_variant
        )
    else:
        storage = PseudopotentialsStorage()
        storage.update(
            AtomicPseudopotentialsParser(args.source.read()).iter_atomic_pseudopotential_variants(),
            filter_name,
            filter_variant
        )

    # print content
    storage.tree()


if __name__ == '__main__':
    main()
