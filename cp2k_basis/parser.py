from typing import Iterator, Callable
from enum import Enum, unique


@unique
class TokenType(Enum):
    WORD = 'WRD'
    SPACE = 'SPC'
    NL = 'NLW'
    EOS = '\0'


SPACES = [' ', '\t']
NLS = ['\n', '\r']


class Token:
    def __init__(self, typ_: TokenType, value: str, position: int = -1):
        self.type = typ_
        self.value = value
        self.position = position

    def __repr__(self):
        return 'Token({},{}{})'.format(
            self.type,
            self.value,
            '' if self.position < 0 else ', {}'.format(self.position)
        )


class Lexer:
    """Split string in words, separated by spaces or newlines
    """

    def __init__(self, inp):
        self.input = inp
        self.position = 0

    def _get_next_stop(self, must_be: Callable) -> int:
        end = self.position + 1
        while end < len(self.input) and must_be(self.input[end]):
            end += 1

        return end

    def tokenize(self) -> Iterator[Token]:
        while self.position < len(self.input):
            start = self.position

            if self.input[start] in SPACES:
                self.position = self._get_next_stop(must_be=lambda x: x in SPACES)
                yield Token(TokenType.SPACE, self.input[start:self.position], start)
            elif self.input[start] in NLS:
                self.position = self._get_next_stop(must_be=lambda x: x in NLS)
                yield Token(TokenType.NL, self.input[start:self.position], start)
            else:
                self.position = self._get_next_stop(must_be=lambda x: x not in SPACES and x not in NLS)
                yield Token(TokenType.WORD, self.input[start:self.position], start)

        yield Token(TokenType.EOS, '\0', self.position)


class ParserNode:
    pass
