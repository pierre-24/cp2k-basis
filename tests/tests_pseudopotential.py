import unittest
import pathlib
import numpy
import re

from cp2k_basis.parser import PruneAndRename
from cp2k_basis.pseudopotential import AtomicPseudopotentialsParser, avail_atom_per_pseudo_family


class PseudoTestCase(unittest.TestCase):
    def setUp(self):
        prune_and_rename = PruneAndRename([
            (re.compile(r'^.*-q\d{1,2}$'), ''),  # discard all *-q versions
        ])

        with (pathlib.Path(__file__).parent / 'POTENTIALS_EXAMPLE').open() as f:
            self.pseudos = AtomicPseudopotentialsParser(f.read(), prune_and_rename).atomic_pseudopotentials()

        self.symbols = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne']
        self.name = 'GTH-BLYP'

        for symbol in self.symbols:
            self.assertIn(symbol, self.pseudos)
            self.assertEqual(len(self.pseudos[symbol].pseudopotentials), 1)
            self.assertIn(self.name, self.pseudos[symbol].pseudopotentials)

    def test_avail_pseudo(self):

        pseudo_families = avail_atom_per_pseudo_family(self.pseudos)

        self.assertIn(self.name, pseudo_families)
        self.assertEqual(sorted(self.symbols), sorted(pseudo_families[self.name]))

    def test_repr(self):
        app = self.pseudos['Ne'].pseudopotentials['GTH-BLYP']

        parser = AtomicPseudopotentialsParser(str(app))
        parser.skip()  # skip comment
        app2 = parser.atomic_pseudopotential()

        self.assertEqual(app2.symbol, app.symbol)
        self.assertEqual(app2.names, app.names)
        self.assertEqual(app2.nelec, app.nelec)
        self.assertEqual(app2.lradius, app.lradius)
        self.assertTrue(numpy.array_equal(app2.lcoefficients, app.lcoefficients))

        for i in range(len(app.nlprojectors)):
            proj = app.nlprojectors[i]
            proj2 = app2.nlprojectors[i]

            self.assertEqual(proj2.radius, proj.radius)
            self.assertTrue(numpy.array_equal(proj2.coefficients, proj.coefficients))

    def test_prune_and_rename(self):

        prune_and_rename = PruneAndRename([
            (re.compile(r'^.*-q\d{1,2}$'), ''),  # discard all *-q versions
            (re.compile(r'GTH-(.*)'), 'XX-\\1')  # just for the fun of it, change the name of the remaining pseudo
        ])

        with (pathlib.Path(__file__).parent / 'POTENTIALS_EXAMPLE').open() as f:
            curated_pseudos = AtomicPseudopotentialsParser(f.read(), prune_and_rename).atomic_pseudopotentials()

        for symbol in self.symbols:
            self.assertEqual(list(curated_pseudos[symbol].pseudopotentials.keys()), ['XX-BLYP'])
