import unittest

from cp2k_basis.parser import Lexer, Token as TK, TokenType as TT


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
