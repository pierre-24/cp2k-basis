import numpy

from typing import List, Dict, Callable, Iterable

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
    def __init__(
            self,
            principle_n: int,
            l_min: int,
            l_max: int,
            nfunc: int,
            nshell: List[int],
            exponents: numpy.ndarray,
            coefficients: numpy.ndarray
    ):
        if exponents.shape != (nfunc, ):
            raise ValueError('number of exponent must be equal to `nfunc`')

        if coefficients.shape != (nfunc, sum(nshell)):
            raise ValueError('number of coefficient must be equal to `nfunc * sum(nshell)`')

        self.principle_n = principle_n
        self.l_min = l_min
        self.l_max = l_max
        self.nfunc = nfunc
        self.nshell = nshell
        self.exponents = exponents
        self.coefficients = coefficients

    def __repr__(self) -> str:
        r = ' {} {} {} {} {}\n'.format(
            self.principle_n,
            self.l_min,
            self.l_max,
            self.nfunc,
            ' '.join(str(x) for x in self.nshell))

        fmt = '{:>20.12f}' + ' {: .12f}' * sum(self.nshell) + '\n'
        for i in range(self.nfunc):
            r += fmt.format(self.exponents[i], *self.coefficients[i])

        return r


class AtomicBasisSet:
    def __init__(self, symbol: str, names: List[str], contractions: List[Contraction]):
        self.symbol = symbol
        self.names = names
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
                repr[i] += (contraction.nfunc if not contracted else 1) * contraction.nshell[i - contraction.l_min]

        return sep.join('{}{}'.format(repr[i], L_TO_SHELL[i]) for i in range(l_max + 1))

    def full_representation(self) -> str:
        return '({})'.format(self._representation(False))

    def contracted_representation(self) -> str:
        return '[{}]'.format(self._representation(True))

    def __repr__(self) -> str:
        r = '# {} {} {} -> {}\n'.format(
            self.symbol, self.names[0], self.full_representation(), self.contracted_representation())
        r += ' {}  {}\n {}\n'.format(self.symbol, ' '.join(self.names), len(self.contractions))

        r += ''.join(str(c) for c in self.contractions)

        return r


class AtomicBasisSets:
    """Set of basis set for a given atom
    """

    def __init__(self, symbol: str):
        self.basis_sets: Dict[str, AtomicBasisSet] = {}
        self.symbol = symbol

    def add_atomic_basis_set(self, bs: AtomicBasisSet, names: Iterable[str]):

        for name in names:
            if name in self.basis_sets:
                raise ValueError('{} already exists for atom {}'.format(name, self.symbol))

            self.basis_sets[name] = bs

    def __repr__(self) -> str:
        return '\n'.join(str(bs) for bs in self.basis_sets.values())


def avail_atom_per_basis(basis: Dict[str, AtomicBasisSets]) -> Dict[str, List[str]]:
    per_name = {}

    for atomic_basis in basis.values():
        for name in atomic_basis.basis_sets:
            if name not in per_name:
                per_name[name] = []
            per_name[name].append(atomic_basis.symbol)

    return per_name


class BasisSetParser(BaseParser):
    def __init__(self, inp: str, prune_and_rename: Callable[[Iterable[str]], Iterable[str]] = lambda x: x):
        super().__init__(inp)
        self.prune_and_rename = prune_and_rename

    def basis_sets(self) -> Dict[str, AtomicBasisSets]:
        """Basis set
        BASIS_SETS := ATOMIC_BASIS_SET* EOS
        """

        basis_sets = {}

        self.skip()

        while self.current_token.type != TokenType.EOS:
            atomic_basis_set = self.atomic_basis_set()

            if atomic_basis_set.symbol not in basis_sets:
                basis_sets[atomic_basis_set.symbol] = AtomicBasisSets(atomic_basis_set.symbol)

            basis_sets[atomic_basis_set.symbol].add_atomic_basis_set(
                atomic_basis_set, self.prune_and_rename(atomic_basis_set.names))

            self.skip()

        self.eat(TokenType.EOS)
        return basis_sets

    def atomic_basis_set(self) -> AtomicBasisSet:
        """
        ATOMIC_BASIS_SET := WORD SPACE WORD (SPACE WORD)* NL INT NL CONTRACTION*
        """

        self.expect(TokenType.WORD)
        symbol = self.current_token.value
        self.next()
        self.eat(TokenType.SPACE)

        self.expect(TokenType.WORD)
        names = [self.current_token.value]
        self.next()

        while self.current_token.type != TokenType.NL:
            self.eat(TokenType.SPACE)
            self.expect(TokenType.WORD)
            names.append(self.current_token.value)
            self.next()

        self.eat(TokenType.NL)
        self.skip()

        num_contraction = self.integer()

        self.skip()

        contractions = []
        for i in range(num_contraction):
            contractions.append(self.contraction())

        return AtomicBasisSet(symbol, names, contractions)

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
        nfunc = self.integer()
        self.eat(TokenType.SPACE)

        nshell = [self.integer()]

        for i in range(1, l_max - l_min + 1):
            self.eat(TokenType.SPACE)
            nshell.append(self.integer())

        self.skip()

        exponents = numpy.zeros(nfunc)
        coefficients = numpy.zeros((nfunc, sum(nshell)))

        for i in range(nfunc):
            c = self.line('n' + 'n' * sum(nshell))
            exponents[i] = c[0]
            coefficients[i] = c[1:]
            self.skip()

        return Contraction(principle_n, l_min, l_max, nfunc, nshell, exponents, coefficients)
