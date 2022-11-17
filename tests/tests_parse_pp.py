import unittest
import pathlib
import numpy
import re

from cp2k_basis.parser import PruneAndRename
from cp2k_basis.pseudopotential import AtomicPseudopotentialsParser, avail_atom_per_pseudo_family

ATOMIC_PP = """{symbol} {names}
{nelec}
{lradius} {nlocal} {local_coefs}
{nproj}
{nlprojectors}
"""


class PPParserTestCase(unittest.TestCase):
    def test_parse_atomic_pp(self):

        lradius = 0.4
        lcoefficients = numpy.array([-2.88013377, -1.21143500])

        nlradius = [0.30634684, 0.3210582]
        nlprojectors = numpy.array([
            [
                [17.51002284, -5.61037883],
                [0, 7.24296793]
            ],
            [
                [6.90321066, -2.19925814],
                [0, 2.60219733]
            ]
        ])

        nlprojectors_str = '{} {} {} {}\n {}\n{} {} {} {}\n {}'.format(
            nlradius[0], 2, *nlprojectors[0, 0], *nlprojectors[0, 1, 1:],
            nlradius[1], 2, *nlprojectors[1][0], *nlprojectors[1, 1, 1:]
        )

        params = dict(
            symbol='K',
            names=' '.join(['GTH-BLYP-q9', 'GTH-BLYP']),
            nelec='3 6',
            lradius=lradius,
            nlocal=2,
            local_coefs=' '.join(str(x) for x in lcoefficients),
            nproj=2,
            nlprojectors=nlprojectors_str
        )

        app = AtomicPseudopotentialsParser(ATOMIC_PP.format(**params)).atomic_pseudopotential()

        self.assertEqual(params['symbol'], app.symbol)
        self.assertEqual(params['names'], ' '.join(app.names))
        self.assertEqual(list(int(x) for x in params['nelec'].split()), app.nelec)
        self.assertEqual(params['lradius'], app.lradius)
        self.assertTrue(numpy.array_equal(lcoefficients, app.lcoefficients))
        self.assertEqual(len(app.nlprojectors), 2)

        for i, proj in enumerate(app.nlprojectors):
            self.assertEqual(proj.radius, nlradius[i])
            self.assertTrue(numpy.array_equal(proj.coefficients, nlprojectors[i]))

    def test_full_pp(self):
        with (pathlib.Path(__file__).parent / 'POTENTIALS_EXAMPLE').open() as f:
            pseudos = AtomicPseudopotentialsParser(f.read()).atomic_pseudopotentials()

        name = 'GTH-BLYP'
        symbols = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne']

        for symbol in symbols:
            self.assertIn(symbol, pseudos)
            app = pseudos[symbol]
            self.assertIn(name, app.pseudopotentials)

            name_pair = '{}-q{}'.format(name, sum(app.pseudopotentials[name].nelec))
            self.assertIn(name_pair, app.pseudopotentials)
            self.assertEqual(app.pseudopotentials[name_pair], app.pseudopotentials[name])

    def test_avail_pseudo(self):
        with (pathlib.Path(__file__).parent / 'POTENTIALS_EXAMPLE').open() as f:
            pseudos = AtomicPseudopotentialsParser(f.read()).atomic_pseudopotentials()

        name = 'GTH-BLYP'
        symbols = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne']

        pseudo_families = avail_atom_per_pseudo_family(pseudos)

        self.assertIn(name, pseudo_families)
        self.assertEqual(sorted(symbols), sorted(pseudo_families[name]))

    def test_repr(self):
        with (pathlib.Path(__file__).parent / 'POTENTIALS_EXAMPLE').open() as f:
            pseudos = AtomicPseudopotentialsParser(f.read()).atomic_pseudopotentials()

        app = pseudos['Ne'].pseudopotentials['GTH-BLYP']

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
        symbols = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne']

        with (pathlib.Path(__file__).parent / 'POTENTIALS_EXAMPLE').open() as f:
            pseudos = AtomicPseudopotentialsParser(f.read()).atomic_pseudopotentials()

        extended = re.compile(r'^.*-q\d{1,2}$')

        for symbol in symbols:
            self.assertTrue(any(k == 'GTH-BLYP' for k in pseudos[symbol].pseudopotentials.keys()))
            self.assertTrue(any(extended.match(k) for k in pseudos[symbol].pseudopotentials.keys()))

        prune_and_rename = PruneAndRename([
            (extended, ''),  # discard all *-q versions
            (re.compile(r'GTH-(.*)'), 'XX-\\1')  # just for the fun of it, change the name of the remaining pseudo
        ])

        with (pathlib.Path(__file__).parent / 'POTENTIALS_EXAMPLE').open() as f:
            curated_pseudos = AtomicPseudopotentialsParser(f.read(), prune_and_rename).atomic_pseudopotentials()

        for symbol in symbols:
            self.assertEqual(list(curated_pseudos[symbol].pseudopotentials.keys()), ['XX-BLYP'])
