import pathlib
import unittest

import numpy

from cp2k_basis.basis_set import AtomicBasisSetsParser
from cp2k_basis.parser import Lexer, Token as TK, TokenType as TT, BaseParser, ParserSyntaxError
from cp2k_basis.pseudopotential import AtomicPseudopotentialsParser
from tests import BaseDataObjectMixin


class LexerTestCase(unittest.TestCase):

    def test_lexer_ok(self):
        expected = [
            TK(TT.WORD, 'ceci'),
            TK(TT.SPACE, ' '),
            TK(TT.WORD, 'est'),
            TK(TT.NL, '\n'),
            TK(TT.WORD, 'un'),
            TK(TT.SPACE, ' '),
            TK(TT.WORD, 'test'),
            TK(TT.SPACE, ' '),
            TK(TT.EOS, '\0')
        ]

        for i, token in enumerate(Lexer('ceci est\nun test ').tokenize()):
            self.assertEqual(token.type, expected[i].type)
            self.assertEqual(token.value, expected[i].value)


class BaseParserTestCase(unittest.TestCase):
    def test_numbers_ok(self):
        self.assertEqual(BaseParser('42').integer(), 42)
        self.assertEqual(BaseParser('42.25').number(), 42.25)

    def test_not_numbers_ko(self):
        with self.assertRaises(ParserSyntaxError):
            BaseParser('a').integer()

        with self.assertRaises(ParserSyntaxError):
            BaseParser('42a').integer()

    def test_comment_ok(self):
        parser = BaseParser('# tmp\n42')
        parser.comment()  # skip comment entirely
        self.assertEqual(parser.integer(), 42)

        parser = BaseParser('# tmp\n# re stuff\n \n42')
        parser.skip()  # skip comments & blank lines
        self.assertEqual(parser.integer(), 42)

    def test_line_ok(self):
        expected = [1, 'a', 2.32]
        self.assertEqual(BaseParser(' '.join('{}'.format(e) for e in expected)).line('iwn'), expected)

    def test_wrong_line_ko(self):
        with self.assertRaises(ParserSyntaxError):  # too short
            BaseParser('42 a').line('i')

        with self.assertRaises(ParserSyntaxError):  # incorrect
            BaseParser('42 a').line('wi')

        with self.assertRaises(ParserSyntaxError):  # too long
            BaseParser('42 a').line('iww')


SINGLE_ABS = """{symbol} {names}
1
{principle} {l_min} {l_max} {nfunc} {nshell}
{coefs}
"""


class BSParserTestCase(unittest.TestCase, BaseDataObjectMixin):
    def test_parse_atomic_basis_set_ok(self):
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

        abs = AtomicBasisSetsParser(SINGLE_ABS.format(**params)).atomic_basis_set_variant()

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

    def test_parse_basis_sets_ok(self):
        storage = self.read_basis_set_from_file(pathlib.Path(__file__).parent / 'BASIS_EXAMPLE')

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
            self.assertIn(bs_name, storage)
            self.assertIn('C', storage[bs_name])
            self.assertIn('q4', storage[bs_name]['C'])
            abs1 = storage[bs_name]['C']['q4']

            self.assertEqual(ncont, len(abs1.contractions))
            self.assertEqual(full, abs1.full_representation())
            self.assertEqual(contracted, abs1.contracted_representation())


ATOMIC_PP = """{symbol} {names}
{nelec}
{lradius} {nlocal} {local_coefs}
{nproj}
{nlprojectors}
"""


class PPParserTestCase(unittest.TestCase, BaseDataObjectMixin):
    def test_parse_atomic_pp_ok(self):

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

        app = AtomicPseudopotentialsParser(ATOMIC_PP.format(**params)).atomic_pseudopotential_variant()

        self.assertEqual(params['symbol'], app.symbol)
        self.assertEqual(params['names'], ' '.join(app.names))
        self.assertEqual(list(int(x) for x in params['nelec'].split()), app.nelec)
        self.assertEqual(params['lradius'], app.lradius)
        self.assertTrue(numpy.array_equal(lcoefficients, app.lcoefficients))
        self.assertEqual(len(app.nlprojectors), 2)

        for i, proj in enumerate(app.nlprojectors):
            self.assertEqual(proj.radius, nlradius[i])
            self.assertTrue(numpy.array_equal(proj.coefficients, nlprojectors[i]))

    def test_parse_pp_ok(self):
        storage = self.read_pp_from_file(pathlib.Path(__file__).parent / 'POTENTIALS_EXAMPLE')

        name = 'GTH-BLYP'
        symbols = [
            ('H', 'q1'),
            ('He', 'q2'),
            ('Li', 'q3'),
            ('Be', 'q4'),
            ('B', 'q3'),
            ('C', 'q4'),
            ('N', 'q5'),
            ('O', 'q6'),
            ('F', 'q7'),
            ('Ne', 'q8')
        ]

        for symbol, variant in symbols:
            self.assertIn(name, storage)
            self.assertIn(symbol, storage[name])
            self.assertIn(variant, storage[name][symbol])

            app = storage[name][symbol][variant]
            self.assertEqual(variant, 'q{}'.format(sum(app.nelec)))
