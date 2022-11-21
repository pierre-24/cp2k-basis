import tempfile
import unittest
import pathlib
import re
import h5py
import numpy

from cp2k_basis.basis_set import BasisSetParser, avail_atom_per_basis, AtomicBasisSets
from cp2k_basis.parser import PruneAndRename


class BSTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()

        prune_and_rename = PruneAndRename([
            (re.compile(r'^.*-q\d{1,2}$'), ''),  # discard all *-q versions
        ])

        with (pathlib.Path(__file__).parent / 'BASIS_EXAMPLE').open() as f:
            self.basis_sets = BasisSetParser(f.read(), prune_and_rename).basis_sets()

        self.bs_names = [
            'SZV-MOLOPT-GTH', 'DZVP-MOLOPT-GTH', 'TZVP-MOLOPT-GTH', 'TZV2P-MOLOPT-GTH', 'TZV2PX-MOLOPT-GTH']

        for basis_name in self.bs_names:
            self.assertIn(basis_name, self.basis_sets['C'].basis_sets)

    def assertAtomicBasisSetEqual(self, abs1, abs2):
        self.assertEqual(abs2.names, abs1.names)
        self.assertEqual(abs2.symbol, abs1.symbol)
        self.assertEqual(len(abs2.contractions), len(abs1.contractions))

        for i in range(len(abs1.contractions)):
            contraction1 = abs1.contractions[i]
            contraction2 = abs2.contractions[i]

            self.assertEqual(contraction2.principle_n, contraction1.principle_n)
            self.assertEqual((contraction2.l_min, contraction2.l_max), (contraction1.l_min, contraction1.l_max))
            self.assertEqual(contraction2.nfunc, contraction1.nfunc)
            self.assertEqual(contraction2.nshell, contraction1.nshell)

            self.assertTrue(numpy.array_equal(contraction2.exponents, contraction1.exponents))
            self.assertTrue(numpy.array_equal(contraction2.coefficients, contraction1.coefficients))

    def test_repr(self):
        abs1 = self.basis_sets['C'].basis_sets['TZV2PX-MOLOPT-GTH']

        parser = BasisSetParser(str(abs1))
        parser.skip()  # skip comment
        abs2 = parser.atomic_basis_set()

        self.assertAtomicBasisSetEqual(abs1, abs2)

    def test_avail_atom_per_basis(self):

        bs_per_atom = avail_atom_per_basis(self.basis_sets)

        for basis_name in self.bs_names:
            self.assertEqual(['C', 'H'], sorted(bs_per_atom[basis_name]))

    def test_hdf5(self):
        path = tempfile.mktemp()

        # write h5file with basis sets for C
        with h5py.File(path, 'w') as f:
            abs1 = self.basis_sets['C']
            bs_group = f.create_group('basis_sets')
            abs1.dump_hdf5(bs_group.create_group('C'))

        # read it back and compare
        with h5py.File(path) as f:
            abs2 = AtomicBasisSets.read_hdf5(f['basis_sets/C'])

            for basis_name in self.bs_names:
                self.assertIn(basis_name, abs2.basis_sets)
                self.assertAtomicBasisSetEqual(abs1.basis_sets[basis_name], abs2.basis_sets[basis_name])
