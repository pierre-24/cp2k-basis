"""Output the source of the library for documentation purpose

Typically,
$ python ./library/library_content.py library/DATA_SOURCES.yml library/library.h5 > docs/developers/library_content.md
"""

import argparse
import yaml
import h5py
import pathlib

from cp2k_basis.basis_set import BasisSetsStorage
from cp2k_basis.pseudopotential import PseudopotentialsStorage
from cp2k_basis.elements import ElementSet


TEMPLATE = """
# Content of the library

## Source

The following files are used to build [the current library](https://github.com/pierre-24/cp2k-basis/tree/dev/library):

+ Basis sets:
    + {bs}

+ Pseudopotentials:
    + {pp}
  
## Detailed content

"""

TABLE_TEMPLATE = """

| Name | Description | Atoms |
|------|-------------|-------|"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data_source', type=argparse.FileType('r'))
    parser.add_argument('library', type=pathlib.Path)

    args = parser.parse_args()

    data_sources = yaml.load(args.data_source, yaml.Loader)

    content = {'basis_sets': [], 'pseudopotentials': []}

    for data_source in data_sources['repositories']:
        if 'data' in data_source:
            base_url = data_source['base'].format(**data_source['data'])
        else:
            base_url = data_source['base']

        for file_def in data_source['files']:
            if file_def.get('disabled', False):
                continue

            full_url = base_url + file_def['name']
            def_ = (file_def['name'], full_url)

            if file_def['type'] == 'BASIS_SETS':
                content['basis_sets'].append(def_)
            else:
                content['pseudopotentials'].append(def_)

    content['basis_sets'].sort(key=lambda x: x[0])
    content['pseudopotentials'].sort(key=lambda x: x[0])

    print(TEMPLATE.format(
        bs='\n    + '.join('[{}]({})'.format(x[0], x[1]) for x in content['basis_sets']),
        pp='\n    + '.join('[{}]({})'.format(x[0], x[1]) for x in content['pseudopotentials']),
    ))

    with h5py.File(args.library) as f:
        if 'basis_sets' in f:
            storage = BasisSetsStorage.read_hdf5(f)

            print('\n### Basis sets\n', TABLE_TEMPLATE)

            for bs in storage.values():
                print('| {} | {} | {} |'.format(
                    bs.name,
                    bs.metadata['description'].replace('|', '\\|'),
                    ', '.join(ElementSet.create(','.join(bs)).iter_sorted())))
        if 'pseudopotentials' in f:
            storage = PseudopotentialsStorage.read_hdf5(f)

            print('\n### Pseudopotentials\n', TABLE_TEMPLATE)

            for pp in storage.values():
                print('| {} | {} | {} |'.format(
                    pp.name,
                    pp.metadata['description'].replace('|', '\\|'),
                    ', '.join(ElementSet.create(','.join(pp)).iter_sorted())))


if __name__ == '__main__':
    main()
