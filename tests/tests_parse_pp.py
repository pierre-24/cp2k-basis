import unittest

from cp2k_basis.pseudopotential import PseudopotentialFamiliesParser

ATOMIC_PP = """{symbol} {full_name} {family_name}
{e_per_shell}
{local_r} {nlocal} {local_coefs}
{nproj}
{projectors}
"""


class PPParserTestCase(unittest.TestCase):
    def test_parse_atomic_pp(self):

        params = dict(
            symbol='K',
            full_name='GTH-BLYP-q9',
            family_name='GTH-BLYP',
            e_per_shell='3 6',
            local_r='0.40000000',
            nlocal=2,
            local_coefs='-2.88013377    -1.21143500',
            nproj=2,
            projectors='0.30634684 2 17.51002284 -5.61037883\n 7.24296793\n0.32105825 2 6.90321066 -2.19925814\n 2.60219733'  # noqa
        )

        app = PseudopotentialFamiliesParser(ATOMIC_PP.format(**params)).atomic_pseudopotential()

        self.assertEqual(params['symbol'], app.symbol)
        self.assertEqual(params['full_name'], app.full_name)
        self.assertEqual(params['family_name'], app.family_name)
        self.assertEqual(list(int(x) for x in params['e_per_shell'].split()), app.e_per_shell)
        self.assertEqual(params['nlocal'], app.nlocal_coefs)
        self.assertEqual(params['nproj'], app.nnonlocal_projectors)
