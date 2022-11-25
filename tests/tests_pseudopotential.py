import tempfile
import unittest
import pathlib

import h5py
import numpy
import re

from cp2k_basis.base_objects import FilterName
from cp2k_basis.pseudopotential import AtomicPseudopotentialsParser, AtomicPseudopotentialsStorage, \
    AtomicPseudopotential, PseudopotentialsStorage


class PseudoTestCase(unittest.TestCase):
    def setUp(self):
        prune_and_rename = FilterName([
            (re.compile(r'^.*-q\d{1,2}$'), ''),  # discard all *-q versions
        ])

        self.storage = PseudopotentialsStorage()

        def add_metadata(app: AtomicPseudopotential):
            app.metadata = {
                'source': 'POTENTIALS_EXAMPLE',
                'references': ['10.1103/PhysRevB.54.1703', '10.1103/PhysRevB.58.3641', '10.1007/s00214-005-0655-y']
            }

        with (pathlib.Path(__file__).parent / 'POTENTIALS_EXAMPLE').open() as f:
            self.storage.update(
                AtomicPseudopotentialsParser(f.read()).iter_atomic_pseudopotentials(), prune_and_rename, add_metadata)

        self.symbols = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne']
        self.name = 'GTH-BLYP'

        for symbol in self.symbols:
            self.assertIn(symbol, self.storage)
            self.assertEqual(len(self.storage[symbol].data_objects), 1)
            self.assertIn(self.name, self.storage[symbol])

    def assertPseudoEqual(self, app1: AtomicPseudopotential, app2: AtomicPseudopotential):
        self.assertEqual(app2.symbol, app1.symbol)
        self.assertEqual(app2.names, app1.names)
        self.assertEqual(app2.nelec, app1.nelec)
        self.assertEqual(app2.lradius, app1.lradius)
        self.assertTrue(numpy.array_equal(app2.lcoefficients, app1.lcoefficients))

        for i in range(len(app1.nlprojectors)):
            proj = app1.nlprojectors[i]
            proj2 = app2.nlprojectors[i]

            self.assertEqual(proj2.radius, proj.radius)
            self.assertTrue(numpy.array_equal(proj2.coefficients, proj.coefficients))

    def test_str_ok(self):
        app1 = self.storage['Ne']['GTH-BLYP']

        parser = AtomicPseudopotentialsParser(str(app1))
        parser.skip()  # skip comment
        app2 = parser.atomic_pseudopotential()

        self.assertPseudoEqual(app1, app2)

    def test_prune_and_rename_ok(self):
        storage = PseudopotentialsStorage()

        prune_and_rename = FilterName([
            (re.compile(r'^.*-q\d{1,2}$'), ''),  # discard all *-q versions
            (re.compile(r'GTH-(.*)'), 'XX-\\1')  # just for the fun of it, change the name of the remaining pseudo
        ])

        with (pathlib.Path(__file__).parent / 'POTENTIALS_EXAMPLE').open() as f:
            storage.update(AtomicPseudopotentialsParser(f.read()).iter_atomic_pseudopotentials(), prune_and_rename)

        for symbol in self.symbols:
            self.assertEqual(list(storage[symbol].data_objects.keys()), ['XX-BLYP'])

    def test_atomic_pseudopotentials_storage_dump_hdf5_ok(self):
        path = tempfile.mktemp()

        # write h5file
        with h5py.File(path, 'w') as f:
            for symbol in self.symbols:
                self.storage[symbol].dump_hdf5(f.create_group('pseudopotentials/{}'.format(symbol)))

        # read back
        with h5py.File(path) as f:
            for symbol in self.symbols:
                app = AtomicPseudopotentialsStorage.read_hdf5(f['pseudopotentials/{}'.format(symbol)])
                self.assertPseudoEqual(self.storage[symbol][self.name], app.data_objects[self.name])

                # check metadata
                self.assertEqual(self.storage[symbol][self.name].metadata, app.data_objects[self.name].metadata)
