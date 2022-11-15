import unittest

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

        contraction = abs.contractions[0]
        self.assertEqual(params['principle'], contraction.principle_n)
        self.assertEqual(params['l_min'], contraction.l_min)
        self.assertEqual(params['l_max'], contraction.l_max)
        self.assertEqual(params['ngauss'], contraction.ngauss)
        self.assertEqual([params['gaussians_per_l']], contraction.gaussians_per_l)
