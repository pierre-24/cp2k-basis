import unittest
import pathlib

from cp2k_basis.basis_set import BasisSetParser

SINGLE_ABS = """
{symbol} {nickname} {full_name}
1
{principle} {l_min} {l_max} {ngauss} {gaussians_per_l}
{coefs}
"""


class BaseParserTestCase(unittest.TestCase):
    def test_simple_basis_set(self):
        params = dict(  # good ol' STO-3G
            nickname='STO-3G',
            full_name='STO-3G-q0',
            symbol='H',
            principle=1,
            l_min=0,
            l_max=0,
            ngauss=3,
            gaussians_per_l=1,
            coefs='0.3425250914E+01 0.1543289673\n0.6239137298 0.5353281423\n0.1688554040 0.4446345422'
        )

        bs = BasisSetParser(SINGLE_ABS.format(**params)).basis_sets()

        self.assertIn(params['nickname'], bs)
        self.assertIn(params['symbol'], bs[params['nickname']].atomic_bs)

        abs = bs[params['nickname']].atomic_bs[params['symbol']]
        self.assertEqual(params['full_name'], abs.full_name)
        self.assertEqual(params['symbol'], abs.symbol)
        self.assertEqual(1, len(abs.contractions))

        self.assertEqual(abs.full_representation(), '(3s)')
        self.assertEqual(abs.contracted_representation(), '[1s]')

        contraction = abs.contractions[0]
        self.assertEqual(params['principle'], contraction.principle_n)
        self.assertEqual(params['l_min'], contraction.l_min)
        self.assertEqual(params['l_max'], contraction.l_max)
        self.assertEqual(params['ngauss'], contraction.ngauss)
        self.assertEqual([params['gaussians_per_l']], contraction.gaussians_per_l)

    def test_full_basis_set(self):
        with (pathlib.Path(__file__).parent / 'BASIS_EXAMPLE').open() as f:
            basis_sets = BasisSetParser(f.read()).basis_sets()

        found_bs = ['SZV-MOLOPT-GTH', 'DZVP-MOLOPT-GTH', 'TZVP-MOLOPT-GTH', 'TZV2P-MOLOPT-GTH', 'TZV2PX-MOLOPT-GTH']

        repr_C = (
            ('(7s,7p)', '[1s,1p]'),  # "STO-7G"
            ('(14s,14p,7d)', '[2s,2p,1d]'),  # "7-77G(p,d)"
            ('(21s,21p,7d)', '[3s,3p,1d]'),  # "7-777G(p,d)"
            ('(21s,21p,14d)', '[3s,3p,2d]'),  # "7-777G(2p,2d)"
            ('(21s,21p,14d,7f)', '[3s,3p,2d,1f]')  # "7-777G(2pd,2df)"
        )

        for i, bs_name in enumerate(found_bs):
            self.assertIn(bs_name, basis_sets)
            self.assertIn('C', basis_sets[bs_name].atomic_bs)
            self.assertIn('H', basis_sets[bs_name].atomic_bs)

            self.assertEqual(basis_sets[bs_name].atomic_bs['H'].full_name, bs_name + '-q1')
            self.assertEqual(basis_sets[bs_name].atomic_bs['C'].full_name, bs_name + '-q4')

            self.assertEqual(repr_C[i][0], basis_sets[bs_name].atomic_bs['C'].full_representation())
            self.assertEqual(repr_C[i][1], basis_sets[bs_name].atomic_bs['C'].contracted_representation())
