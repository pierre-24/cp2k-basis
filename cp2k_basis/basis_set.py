from typing import List, Dict

from cp2k_basis.parser import BaseParser, TokenType


L_TO_SHELL = {
    0: 's',
    1: 'p',
    2: 'd',
    3: 'f',
    4: 'g',
    5: 'h'
}


class Contraction:
    def __init__(self, principle_n: int, l_min: int, l_max: int, ngauss: int, gaussians_per_l: List[int]):
        self.principle_n = principle_n
        self.l_min = l_min
        self.l_max = l_max
        self.ngauss = ngauss
        self.gaussians_per_l = gaussians_per_l


class AtomicBasisSet:
    def __init__(self, symbol: str, bs_name: str, full_name: str, contractions: List[Contraction]):
        self.symbol = symbol
        self.bs_name = bs_name
        self.full_name = full_name
        self.contractions = contractions

    def _l_max(self) -> int:
        l_max = 0
        for contraction in self.contractions:
            l_max = max(l_max, contraction.l_max)

        return l_max

    def _representation(self, contracted: bool = False, sep=',') -> str:
        l_max = self._l_max()
        repr = [0] * (l_max + 1)

        for contraction in self.contractions:
            for i in range(contraction.l_min, contraction.l_max + 1):
                repr[i] += (contraction.ngauss if not contracted else 1) * \
                    contraction.gaussians_per_l[i - contraction.l_min]

        return sep.join('{}{}'.format(repr[i], L_TO_SHELL[i]) for i in range(l_max + 1))

    def full_representation(self) -> str:
        return '({})'.format(self._representation(False))

    def contracted_representation(self) -> str:
        return '[{}]'.format(self._representation(True))

    def __repr__(self):
        return '{} [{}|{}]'.format(self.symbol, self._representation(False, ''), self._representation(True, ''))


class BasisSet:
    def __init__(self, name: str):
        self.atomic_bs: Dict[str, AtomicBasisSet] = {}
        self.name = name

    def add_atomic_basis_set(self, bs: AtomicBasisSet):
        if bs.symbol in self.atomic_bs:
            raise ValueError('Atomic basis set for {} already defined'.format(bs.symbol))

        self.atomic_bs[bs.symbol] = bs


class BasisSetParser(BaseParser):
    def __init__(self, inp: str):
        super().__init__(inp)

    def basis_sets(self) -> Dict[str, BasisSet]:
        """Basis set
        BASIS_SETS := ATOMIC_BASIS_SET* EOS
        """

        basis_sets = {}

        self.skip()

        while self.current_token.type != TokenType.EOS:
            atomic_basis_set = self.atomic_basis_set()

            if atomic_basis_set.bs_name not in basis_sets:
                basis_sets[atomic_basis_set.bs_name] = BasisSet(atomic_basis_set.bs_name)

            basis_sets[atomic_basis_set.bs_name].add_atomic_basis_set(atomic_basis_set)

            self.skip()

        self.eat(TokenType.EOS)
        return basis_sets

    def atomic_basis_set(self) -> AtomicBasisSet:
        """
        ATOMIC_BASIS_SET := WORD SPACE WORD (SPACE WORD)? NL INT NL CONTRACTION*
        """

        self.expect(TokenType.WORD)
        symbol = self.current_token.value
        self.next()
        self.eat(TokenType.SPACE)

        self.expect(TokenType.WORD)
        nickname = self.current_token.value
        full_name = None
        self.next()

        if self.current_token.type == TokenType.SPACE:
            self.next()
            if self.current_token.type == TokenType.WORD:
                full_name = self.current_token.value
                self.next()

        self.eat(TokenType.NL)
        self.skip()

        num_contraction = self.integer()

        self.skip()

        contractions = []
        for i in range(num_contraction):
            contractions.append(self.contraction())

        return AtomicBasisSet(symbol, nickname, full_name, contractions)

    def contraction(self) -> Contraction:
        """
        CONTRACTION := INT SPACE INT SPACE INT SPACE INT (SPACE INT)* NL (FLOAT (SPACE FLOAT)* NL)*
        """

        self.expect(TokenType.WORD)

        principle_n = self.integer()
        self.eat(TokenType.SPACE)
        l_min = self.integer()
        self.eat(TokenType.SPACE)
        l_max = self.integer()
        self.eat(TokenType.SPACE)
        ngauss = self.integer()
        self.eat(TokenType.SPACE)

        gaussians_per_l = [self.integer()]

        for i in range(1, l_max - l_min + 1):
            self.eat(TokenType.SPACE)
            gaussians_per_l.append(self.integer())

        self.skip()

        for i in range(ngauss):
            self.line('n' + 'n' * sum(gaussians_per_l))
            self.skip()

        return Contraction(principle_n, l_min, l_max, ngauss, gaussians_per_l)
