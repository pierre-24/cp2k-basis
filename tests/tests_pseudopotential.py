import tempfile
import unittest
import pathlib

import h5py
import numpy
import re

from cp2k_basis.parser import PruneAndRename
from cp2k_basis.pseudopotential import AtomicPseudopotentialsParser, AtomicPseudopotentials, AtomicPseudopotential


class PseudoTestCase(unittest.TestCase):
    def setUp(self):
        prune_and_rename = PruneAndRename([
            (re.compile(r'^.*-q\d{1,2}$'), ''),  # discard all *-q versions
        ])

        with (pathlib.Path(__file__).parent / 'POTENTIALS_EXAMPLE').open() as f:
            self.pseudos = AtomicPseudopotentialsParser(
                f.read(),
                prune_and_rename,
                source='POTENTIALS_EXAMPLE',
                references=['10.1103/PhysRevB.54.1703', '10.1103/PhysRevB.58.3641', '10.1007/s00214-005-0655-y']
            ).atomic_pseudopotentials()

        self.symbols = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne']
        self.name = 'GTH-BLYP'

        for symbol in self.symbols:
            self.assertIn(symbol, self.pseudos)
            self.assertEqual(len(self.pseudos[symbol].data_objects), 1)
            self.assertIn(self.name, self.pseudos[symbol].data_objects)

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

    def test_str(self):
        app1 = self.pseudos['Ne'].data_objects['GTH-BLYP']

        parser = AtomicPseudopotentialsParser(str(app1))
        parser.skip()  # skip comment
        app2 = parser.atomic_pseudopotential()

        self.assertPseudoEqual(app1, app2)

    def test_prune_and_rename(self):
        prune_and_rename = PruneAndRename([
            (re.compile(r'^.*-q\d{1,2}$'), ''),  # discard all *-q versions
            (re.compile(r'GTH-(.*)'), 'XX-\\1')  # just for the fun of it, change the name of the remaining pseudo
        ])

        with (pathlib.Path(__file__).parent / 'POTENTIALS_EXAMPLE').open() as f:
            curated_pseudos = AtomicPseudopotentialsParser(f.read(), prune_and_rename).atomic_pseudopotentials()

        for symbol in self.symbols:
            self.assertEqual(list(curated_pseudos[symbol].data_objects.keys()), ['XX-BLYP'])

    def test_hdf5(self):
        path = tempfile.mktemp()

        # write h5file
        with h5py.File(path, 'w') as f:
            for symbol in self.symbols:
                self.pseudos[symbol].dump_hdf5(f.create_group('pseudopotentials/{}'.format(symbol)))

        # read back
        with h5py.File(path) as f:
            for symbol in self.symbols:
                app = AtomicPseudopotentials.read_hdf5(f['pseudopotentials/{}'.format(symbol)])
                self.assertPseudoEqual(
                    self.pseudos[symbol].data_objects[self.name],
                    app.data_objects[self.name]
                )

                # check metadata
                self.assertEqual(
                    self.pseudos[symbol].data_objects[self.name].metadata,
                    app.data_objects[self.name].metadata
                )
