import tempfile
import unittest
import pathlib
import h5py

from cp2k_basis.basis_set import AtomicBasisSetsParser, BasisSet, BasisSetsStorage
from tests import BaseDataObjectMixin


class BSTestCase(unittest.TestCase, BaseDataObjectMixin):
    def setUp(self):
        super().setUp()

        def add_metadata(abs_: BasisSet):
            abs_.metadata = {
                'source': 'BASIS_EXAMPLE',
                'references': ['10.1063/1.2770708']
            }

        self.storage = self.read_basis_set_from_file(pathlib.Path(__file__).parent / 'BASIS_EXAMPLE', add_metadata)

        self.bs_names = [
            'SZV-MOLOPT-GTH', 'DZVP-MOLOPT-GTH', 'TZVP-MOLOPT-GTH', 'TZV2P-MOLOPT-GTH', 'TZV2PX-MOLOPT-GTH'
        ]

        for basis_name in self.bs_names:
            self.assertIn(basis_name, self.storage)

    def test_atomic_basis_set_str_ok(self):
        abs1 = self.storage['TZV2PX-MOLOPT-GTH']['C']['q4']

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
            bs2.add(abs_, next(self.filter_variant(abs_.names)))

        for symbol in self.storage[name]:
            for variant in self.storage[name][symbol]:
                self.assertAtomicBasisSetEqual(bs1[symbol][variant], bs2[symbol][variant])

    def test_storage_dump_hdf5_ok(self):
        path = tempfile.mktemp()

        # write h5file
        with h5py.File(path, 'w') as f:
            self.storage.dump_hdf5(f)

        # read back
        with h5py.File(path) as f:
            storage = BasisSetsStorage.read_hdf5(f)

            for bs_name in self.storage:
                self.assertIn(bs_name, storage)
                self.assertEqual(self.storage[bs_name].metadata, storage[bs_name].metadata)

                for symbol in self.storage[bs_name]:
                    self.assertIn(symbol, self.storage[bs_name])
                    for variant in self.storage[bs_name][symbol]:
                        self.assertAtomicBasisSetEqual(
                            storage[bs_name][symbol][variant], self.storage[bs_name][symbol][variant])
