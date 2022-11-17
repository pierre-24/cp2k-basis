import unittest
import pathlib

import numpy

from cp2k_basis.basis_set import BasisSetParser, avail_atom_per_basis

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
            abs = basis_sets['C'].basis_sets[bs_name]

            self.assertIn(bs_name + '-q4', basis_sets['C'].basis_sets)  # the -q4 version is also there
            self.assertEqual(abs, basis_sets['C'].basis_sets[bs_name + '-q4'])

            self.assertEqual(ncont, len(abs.contractions))
            self.assertEqual(full, abs.full_representation())
            self.assertEqual(contracted, abs.contracted_representation())

    def test_avail_atom_per_basis(self):
        with (pathlib.Path(__file__).parent / 'BASIS_EXAMPLE').open() as f:
            basis_sets = BasisSetParser(f.read()).basis_sets()

        bs_per_atom = avail_atom_per_basis(basis_sets)
        found_bs = ['SZV-MOLOPT-GTH', 'DZVP-MOLOPT-GTH', 'TZVP-MOLOPT-GTH', 'TZV2P-MOLOPT-GTH', 'TZV2PX-MOLOPT-GTH']

        for basis_name in found_bs:
            self.assertEqual(['C', 'H'], sorted(bs_per_atom[basis_name]))
