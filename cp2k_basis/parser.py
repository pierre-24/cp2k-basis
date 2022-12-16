from typing import Iterator, Callable, List, Union
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
    def __init__(self, typ_: TokenType, value: str, position: int = -1, line: int = -1):
        self.type = typ_
        self.value = value
        self.position = position
        self.line = line

    def __repr__(self):
        return '<Token({},{}{}{})>'.format(
            self.type,
            self.value,
            '' if self.position < 0 else ', {}'.format(self.position),
            '' if self.line < 0 else ', {}'.format(self.line)
        )


class Lexer:
    """Split string in words, separated by spaces or newlines
    """

    def __init__(self, inp):
        self.input = inp
        self.position = 0
        self.line = 1

    def _get_next_stop(self, must_be: Callable) -> int:
        end = self.position + 1
        while end < len(self.input) and must_be(self.input[end]):
            end += 1

        return end

    def tokenize(self) -> Iterator[Token]:
        while self.position < len(self.input):
            start = self.position
            line_start = self.line

            if self.input[start] in SPACES:
                self.position = self._get_next_stop(must_be=lambda x: x in SPACES)
                yield Token(TokenType.SPACE, self.input[start:self.position], start, line_start)
            elif self.input[start] in NLS:
                self.position = self._get_next_stop(must_be=lambda x: x in NLS)
                yield Token(TokenType.NL, self.input[start:self.position], start, line_start)
                self.line += self.input[start:self.position].count('\n')
            else:
                self.position = self._get_next_stop(must_be=lambda x: x not in SPACES and x not in NLS)
                yield Token(TokenType.WORD, self.input[start:self.position], start, line_start)

        yield Token(TokenType.EOS, '\0', self.position)


class ParserSyntaxError(Exception):
    pass


class ParserNode:
    pass


class BaseParser:
    def __init__(self, inp: str, source: str = ''):
        self.lexer = Lexer(inp)
        self.tokenizer = self.lexer.tokenize()
        self.current_token: Token = None
        self.source = source

        self.next()

    def next(self):
        """Get next token"""

        try:
            self.current_token = next(self.tokenizer)
        except StopIteration:
            self.current_token = Token(TokenType.EOS, '\0')

    def expect(self, typ: TokenType):
        if self.current_token.type != typ:
            raise ParserSyntaxError('expected {}, got {}'.format(typ, self.current_token))

    def eat(self, typ: TokenType):
        if self.current_token.type == typ:
            self.next()
        else:
            raise ParserSyntaxError('expected {}, got {}'.format(typ, self.current_token))

    def comment(self) -> None:
        """
        COMMENT := '#' (WORD | SPACE)* NL?
        """

        self.expect(TokenType.WORD)

        if self.current_token.value[0] != '#':
            raise ParserSyntaxError('expected WORD starting with `#` for COMMENT')

        self.eat(TokenType.WORD)
        while self.current_token.type not in [TokenType.NL, TokenType.EOS]:
            self.next()

        if self.current_token.type == TokenType.NL:
            self.next()

    def skip(self):
        """Go to the next non-comment word
        """

        while True:
            if self.current_token.type == TokenType.EOS:
                break
            elif self.current_token.type != TokenType.WORD:
                self.next()
            else:
                if self.current_token.value[0] == '#':
                    self.comment()
                else:
                    break

    def integer(self) -> int:
        """Parse integer
        """
        self.expect(TokenType.WORD)

        try:
            number = int(self.current_token.value)
        except ValueError:
            raise ParserSyntaxError('expected integer, got {}'.format(self.current_token.value))

        self.next()
        return number

    def number(self) -> float:
        """Parser float
        """
        self.expect(TokenType.WORD)

        try:
            number = float(self.current_token.value)
        except ValueError:
            raise ParserSyntaxError('expected number, got {}'.format(self.current_token.value))

        self.next()
        return number

    def line(self, definition: str) -> List[Union[int, float, str]]:
        """
        LINE := (integer | number | WORD)* NL
        """
        result = []

        for d in definition:
            if d == 'i':
                result.append(self.integer())
            elif d == 'n':
                result.append(self.number())
            elif d == 'w':
                self.expect(TokenType.WORD)
                result.append(self.current_token.value)
                self.next()

            if len(result) < len(definition):
                self.eat(TokenType.SPACE)

        if self.current_token.type != TokenType.EOS:
            self.eat(TokenType.NL)

        return result
