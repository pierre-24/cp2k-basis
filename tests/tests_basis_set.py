import tempfile
import unittest
import pathlib
import re
import h5py
import numpy

from cp2k_basis.basis_set import AtomicBasisSetsParser, AtomicBasisSets, AtomicBasisSet
from cp2k_basis.parser import PruneAndRename


class BSTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()

        prune_and_rename = PruneAndRename([
            (re.compile(r'^.*-q\d{1,2}$'), ''),  # discard all *-q versions
        ])

        with (pathlib.Path(__file__).parent / 'BASIS_EXAMPLE').open() as f:
            self.basis_sets = AtomicBasisSetsParser(
                f.read(),
                prune_and_rename,
                source='BASIS_EXAMPLE',
                references=['10.1063/1.2770708']
            ).atomic_basis_sets()

        self.bs_names = [
            'SZV-MOLOPT-GTH', 'DZVP-MOLOPT-GTH', 'TZVP-MOLOPT-GTH', 'TZV2P-MOLOPT-GTH', 'TZV2PX-MOLOPT-GTH']

        for basis_name in self.bs_names:
            self.assertIn(basis_name, self.basis_sets['C'].data_objects)

    def assertAtomicBasisSetEqual(self, abs1: AtomicBasisSet, abs2: AtomicBasisSet):
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

    def test_str(self):
        abs1 = self.basis_sets['C'].data_objects['TZV2PX-MOLOPT-GTH']

        parser = AtomicBasisSetsParser(str(abs1))
        parser.skip()  # skip comment
        abs2 = parser.atomic_basis_set()

        self.assertAtomicBasisSetEqual(abs1, abs2)

    def test_hdf5(self):
        path = tempfile.mktemp()

        # write h5file with basis sets for C
        with h5py.File(path, 'w') as f:
            abs1 = self.basis_sets['C']
            abs1.dump_hdf5(f.create_group('basis_sets/C'))

        # read it back and compare
        with h5py.File(path) as f:
            abs2 = AtomicBasisSets.read_hdf5(f['basis_sets/C'])

            for basis_name in self.bs_names:
                self.assertIn(basis_name, abs2.data_objects)
                self.assertAtomicBasisSetEqual(abs1.data_objects[basis_name], abs2.data_objects[basis_name])

                # check metadata
                self.assertEqual(
                    abs1.data_objects[basis_name].metadata, abs2.data_objects[basis_name].metadata)
