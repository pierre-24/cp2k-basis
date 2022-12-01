import tempfile
import unittest
import pathlib
import re
import h5py

from cp2k_basis.basis_set import AtomicBasisSetsParser, BasisSet, BasisSetsStorage
from cp2k_basis.base_objects import FilterName
from tests import CompareAtomicDataObjectMixin


class BSTestCase(unittest.TestCase, CompareAtomicDataObjectMixin):
    def setUp(self):
        super().setUp()

        prune_and_rename = FilterName([
            (re.compile(r'^.*-q\d{1,2}$'), ''),  # discard all *-q versions
        ])

        self.storage = BasisSetsStorage()

        def add_metadata(abs_: BasisSet):
            abs_.metadata = {
                'source': 'BASIS_EXAMPLE',
                'references': ['10.1063/1.2770708']
            }

        with (pathlib.Path(__file__).parent / 'BASIS_EXAMPLE').open() as f:
            self.storage.update(
                AtomicBasisSetsParser(f.read()).iter_atomic_basis_set_variants(),
                filter_name=prune_and_rename,
                add_metadata=add_metadata
            )

        self.bs_names = [
            'SZV-MOLOPT-GTH', 'DZVP-MOLOPT-GTH', 'TZVP-MOLOPT-GTH', 'TZV2P-MOLOPT-GTH', 'TZV2PX-MOLOPT-GTH'
        ]

        for basis_name in self.bs_names:
            self.assertIn(basis_name, self.storage)

    def test_atomic_basis_set_str_ok(self):
        abs1 = self.storage['TZV2PX-MOLOPT-GTH']['C']

        parser = AtomicBasisSetsParser(str(abs1))
        parser.skip()  # skip comment
        abs2 = parser.atomic_basis_set_variant()

        self.assertAtomicBasisSetEqual(abs1, abs2)

    def test_basis_set_str_ok(self):
        name = 'TZV2PX-MOLOPT-GTH'
        bs1 = self.storage[name]

        parser = AtomicBasisSetsParser(str(bs1))
        bs2 = BasisSet(name)
        for abs_ in parser.iter_atomic_basis_set_variants():
            self.assertIn(name, abs_.names)
            bs2.add(abs_)

        for symbol in self.storage[name].data_objects.keys():
            self.assertAtomicBasisSetEqual(bs1[symbol], bs2[symbol])

    def test_basis_set_dump_hdf5_ok(self):
        path = tempfile.mktemp()
        name = 'TZV2PX-MOLOPT-GTH'

        # write h5file with basis set
        with h5py.File(path, 'w') as f:
            bs1 = self.storage[name]
            bs1.dump_hdf5(f.create_group('basis_sets/{}'.format(name)))

        # read it back and compare
        with h5py.File(path) as f:
            bs2 = BasisSet.iter_hdf5_variants()

            # check metadata
            self.assertEqual(bs1.metadata, bs2.metadata)

            # check content
            for symbol in ['C', 'H']:
                self.assertIn(symbol, bs2)
                self.assertAtomicBasisSetEqual(bs1[symbol], bs2[symbol])

    def test_storage_dump_hdf5_ok(self):
        path = tempfile.mktemp()

        # write h5file
        with h5py.File(path, 'w') as f:
            self.storage.dump_hdf5(f)

        with h5py.File(path) as f:
            storage = BasisSetsStorage.read_hdf5(f)

            for bs_name in self.storage:
                self.assertIn(bs_name, storage)

                for symbol in storage[bs_name]:
                    self.assertIn(symbol, storage[bs_name])
                    self.assertAtomicBasisSetEqual(storage[bs_name][symbol], self.storage[bs_name][symbol])
