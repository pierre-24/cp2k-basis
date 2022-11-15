import unittest

from cp2k_basis.parser import Lexer, Token as TK, TokenType as TT, BaseParser, ParserSyntaxError


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
