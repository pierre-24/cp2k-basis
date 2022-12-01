import tempfile
import unittest
import pathlib
import h5py

from cp2k_basis.pseudopotential import AtomicPseudopotentialsParser, PseudopotentialFamily, PseudopotentialsStorage
from tests import BaseDataObjectMixin


class PseudoTestCase(unittest.TestCase, BaseDataObjectMixin):
    def setUp(self):

        def add_metadata(app: PseudopotentialFamily):
            app.metadata = {
                'source': 'POTENTIALS_EXAMPLE',
                'references': ['10.1103/PhysRevB.54.1703', '10.1103/PhysRevB.58.3641', '10.1007/s00214-005-0655-y']
            }

        self.storage = self.read_pp_from_file(pathlib.Path(__file__).parent / 'POTENTIALS_EXAMPLE', add_metadata)

        self.symbols = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne']
        self.name = 'GTH-BLYP'

        for symbol in self.symbols:
            self.assertEqual(len(self.storage.families), 1)
            self.assertIn(symbol, self.storage[self.name])

    def test_atomic_pseudopotential_str_ok(self):
        app1 = self.storage['GTH-BLYP']['Ne']['q8']

        parser = AtomicPseudopotentialsParser(str(app1))
        parser.skip()  # skip comment
        app2 = parser.atomic_pseudopotential_variant()

        self.assertAtomicPseudoEqual(app1, app2)

    def test_pseudopotential_family_str_ok(self):
        bs1 = self.storage[self.name]

        parser = AtomicPseudopotentialsParser(str(bs1))
        bs2 = PseudopotentialFamily(self.name)
        for app in parser.iter_atomic_pseudopotential_variants():
            self.assertIn(self.name, app.names)
            bs2.add(app, next(self.filter_variant(app.names)))

        for symbol in self.symbols:
            self.assertIn(symbol, bs2)
            for variant in bs1[symbol]:
                self.assertAtomicPseudoEqual(bs1[symbol][variant], bs2[symbol][variant])

    def test_storage_dump_hdf5_ok(self):
        path = tempfile.mktemp()

        # write h5file
        with h5py.File(path, 'w') as f:
            self.storage.dump_hdf5(f)

        # read back
        with h5py.File(path) as f:
            storage = PseudopotentialsStorage.read_hdf5(f)

            for bs_name in self.storage:
                self.assertIn(bs_name, storage)
                self.assertEqual(self.storage[bs_name].metadata, storage[bs_name].metadata)

                for symbol in self.storage[bs_name]:
                    self.assertIn(symbol, storage[bs_name])
                    for variant in self.storage[bs_name][symbol]:
                        self.assertAtomicPseudoEqual(
                            storage[bs_name][symbol][variant], self.storage[bs_name][symbol][variant])
