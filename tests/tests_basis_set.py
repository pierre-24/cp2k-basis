import tempfile
import unittest
import pathlib
import re
import h5py
import numpy

from cp2k_basis.basis_set import AtomicBasisSetsParser, BasisSet, AtomicBasisSet, BasisSetsStorage
from cp2k_basis.base_objects import FilterName


class BSTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()

        prune_and_rename = FilterName([
            (re.compile(r'^.*-q\d{1,2}$'), ''),  # discard all *-q versions
        ])

        self.storage = BasisSetsStorage()

        def add_metadata(abs_: AtomicBasisSet):
            abs_.metadata = {
                'source': 'BASIS_EXAMPLE',
                'references': ['10.1063/1.2770708']
            }

        with (pathlib.Path(__file__).parent / 'BASIS_EXAMPLE').open() as f:
            self.storage.update(
                AtomicBasisSetsParser(f.read()).iter_atomic_basis_sets(),
                filter_name=prune_and_rename,
                add_metadata=add_metadata
            )

        self.bs_names = [
            'SZV-MOLOPT-GTH', 'DZVP-MOLOPT-GTH', 'TZVP-MOLOPT-GTH', 'TZV2P-MOLOPT-GTH', 'TZV2PX-MOLOPT-GTH']

        for basis_name in self.bs_names:
            self.assertIn(basis_name, self.storage)

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

    def test_atomic_basis_set_str_ok(self):
        abs1 = self.storage['TZV2PX-MOLOPT-GTH']['C']

        parser = AtomicBasisSetsParser(str(abs1))
        parser.skip()  # skip comment
        abs2 = parser.atomic_basis_set()

        self.assertAtomicBasisSetEqual(abs1, abs2)

    def test_basis_set_dump_hdf5_ok(self):
        path = tempfile.mktemp()
        name = 'TZV2PX-MOLOPT-GTH'

        # write h5file with basis set
        with h5py.File(path, 'w') as f:
            bs1 = self.storage[name]
            bs1.dump_hdf5(f.create_group('basis_sets/{}'.format(name)))

        # read it back and compare
        with h5py.File(path) as f:
            bs2 = BasisSet.read_hdf5(f['basis_sets/{}'.format(name)])

            for symbol in ['C', 'H']:
                self.assertIn(symbol, bs2)
                self.assertAtomicBasisSetEqual(bs1[symbol], bs2[symbol])

                # check metadata
                self.assertEqual(bs1[symbol].metadata, bs2[symbol].metadata)
