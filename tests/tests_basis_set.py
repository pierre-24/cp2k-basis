import tempfile
import unittest
import pathlib
import re
import h5py
import numpy

from cp2k_basis.basis_set import BasisSetParser, avail_atom_per_basis, AtomicBasisSets
from cp2k_basis.parser import PruneAndRename

SINGLE_ABS = """{symbol} {names}
1
{principle} {l_min} {l_max} {nfunc} {nshell}
{coefs}
"""


class BSParserTestCase(unittest.TestCase):
    def test_atomic_basis_set(self):
        coefs = numpy.array([
            [0.3425250914E+01, 0.1543289673],
            [0.6239137298, 0.5353281423],
            [0.1688554040, 0.4446345422]]
        )

        coefs_str = '{:>20.12f} {: .12f}\n{:>20.12f} {: .12f}\n{:>20.12f} {: .12f}'.format(*coefs.ravel())

        params = dict(  # good ol' STO-3G
            names=' '.join(['STO-3G', 'STO-3G-q0']),
            symbol='H',
            principle=1,
            l_min=0,
            l_max=0,
            nfunc=3,
            nshell=1,
            coefs=coefs_str
        )

        abs = BasisSetParser(SINGLE_ABS.format(**params)).atomic_basis_set()

        self.assertEqual(params['names'], ' '.join(abs.names))
        self.assertEqual(params['symbol'], abs.symbol)
        self.assertEqual(1, len(abs.contractions))

        self.assertEqual(abs.full_representation(), '(3s)')
        self.assertEqual(abs.contracted_representation(), '[1s]')

        contraction = abs.contractions[0]
        self.assertEqual(params['principle'], contraction.principle_n)
        self.assertEqual(params['l_min'], contraction.l_min)
        self.assertEqual(params['l_max'], contraction.l_max)
        self.assertEqual(params['nfunc'], contraction.nfunc)
        self.assertEqual([params['nshell']], contraction.nshell)

        self.assertTrue(numpy.array_equal(contraction.exponents, coefs[:, 0]))
        self.assertTrue(numpy.array_equal(contraction.coefficients.T[0], coefs[:, 1]))

    def test_full_basis_set(self):
        with (pathlib.Path(__file__).parent / 'BASIS_EXAMPLE').open() as f:
            basis_sets = BasisSetParser(f.read()).basis_sets()

        self.assertIn('C', basis_sets)
        self.assertIn('H', basis_sets)

        # check basis sets for C
        repr_C = (
            ('SZV-MOLOPT-GTH', 1, '(7s,7p)', '[1s,1p]'),  # "STO-7G"
            ('DZVP-MOLOPT-GTH', 1, '(14s,14p,7d)', '[2s,2p,1d]'),  # "7-77G(p,d)"
            ('TZVP-MOLOPT-GTH', 1, '(21s,21p,7d)', '[3s,3p,1d]'),  # "7-777G(p,d)"
            ('TZVP-GTH', 2, '(15s,15p,1d)', '[3s,3p,1d]'),  # "5-555G(p,d)"
            ('TZV2P-MOLOPT-GTH', 1, '(21s,21p,14d)', '[3s,3p,2d]'),  # "7-777G(2p,2d)"
            ('TZV2PX-MOLOPT-GTH', 1, '(21s,21p,14d,7f)', '[3s,3p,2d,1f]')  # "7-777G(2pd,2df)"
        )

        for bs_name, ncont, full, contracted in repr_C:
            self.assertIn(bs_name, basis_sets['C'].basis_sets)
            abs1 = basis_sets['C'].basis_sets[bs_name]

            self.assertIn(bs_name + '-q4', basis_sets['C'].basis_sets)  # the -q4 version is also there
            self.assertEqual(abs1, basis_sets['C'].basis_sets[bs_name + '-q4'])

            self.assertEqual(ncont, len(abs1.contractions))
            self.assertEqual(full, abs1.full_representation())
            self.assertEqual(contracted, abs1.contracted_representation())


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
