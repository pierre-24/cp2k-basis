from typing import List, Dict

import numpy

from cp2k_basis.parser import BaseParser, TokenType


class NonLocalProjector:
    def __init__(self, radius: float, nfunc: int, coefficients: numpy.ndarray):
        if coefficients.shape != (nfunc, nfunc):
            raise ValueError('number of coefficient must be equal to `nfunc * nfunc`')

        self.radius = radius
        self.nfunc = nfunc
        self.coefficients = coefficients


class AtomicPseudopotential:
    """Atomic GTH (Goedecker-Teter-Hutter) pseudopotential of CP2K
    """

    def __init__(
        self,
        symbol: str,
        names: List[str],
        nelec: List[int],
        lradius: float,
        lcoefficients: numpy.ndarray,
        nlprojectors: List[NonLocalProjector]
    ):
        self.symbol = symbol
        self.names = names
        self.nelec = nelec
        self.lradius = lradius
        self.lcoefficients = lcoefficients
        self.nlprojectors = nlprojectors


class AtomicPseudoPotentials:
    def __init__(self, symbol: str):
        self.pseudopotentials: Dict[str, AtomicPseudopotential] = {}
        self.symbol = symbol

    def add_atomic_pseudopotential(self, ap: AtomicPseudopotential):

        for name in ap.names:
            if name in self.pseudopotentials:
                raise ValueError('pseudo {} already defined for {}'.format(name, self.symbol))

            self.pseudopotentials[name] = ap


def avail_atom_per_pseudo_family(basis: Dict[str, AtomicPseudoPotentials]) -> Dict[str, List[str]]:
    per_name = {}

    for pseudo in basis.values():
        for name in pseudo.pseudopotentials:
            if name not in per_name:
                per_name[name] = []
            per_name[name].append(pseudo.symbol)

    return per_name


class AtomicPseudopotentialsParser(BaseParser):
    def __init__(self, inp: str):
        super().__init__(inp)

    def atomic_pseudopotentials(self) -> Dict[str, AtomicPseudoPotentials]:
        """
        PP_FAMILIES := ATOMIC_PP* EOS
        """

        pps = {}

        self.skip()

        while self.current_token.type != TokenType.EOS:
            atomic_pp = self.atomic_pseudopotential()

            # todo: no family name!

            if atomic_pp.symbol not in pps:
                pps[atomic_pp.symbol] = AtomicPseudoPotentials(atomic_pp.symbol)

            pps[atomic_pp.symbol].add_atomic_pseudopotential(atomic_pp)

            self.skip()

        self.eat(TokenType.EOS)
        return pps

    def atomic_pseudopotential(self) -> AtomicPseudopotential:
        """
        ATOMIC_PP := WORD SPACE WORD (SPACE WORD)* NL INT* NL LOCAL_PART NL NLOCAL_PART
        LOCAL_PART :=  FLOAT INT FLOAT*
        NLOCAL_PART := INT NL PROJECTOR*
        """

        # first line
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

        # electron per shell
        nelec = [self.integer()]

        while self.current_token.type not in [TokenType.NL, TokenType.EOS]:
            self.eat(TokenType.SPACE)
            nelec.append(self.integer())

        self.eat(TokenType.NL)
        self.skip()

        # local part
        lradius = self.number()
        self.eat(TokenType.SPACE)
        n_lcoefficients = self.integer()

        if n_lcoefficients > 0:
            self.eat(TokenType.SPACE)
            lcoefficients = numpy.array(self.line('n' * n_lcoefficients))
        else:
            lcoefficients = numpy.array([])
            self.eat(TokenType.NL)

        self.skip()

        # nonlocal part
        n_nlprojectors = self.integer()
        nlprojectors = []
        self.eat(TokenType.NL)
        self.skip()

        for proj_i in range(n_nlprojectors):
            nlprojectors.append(self.nlprojector())

        return AtomicPseudopotential(
            symbol,
            names,
            nelec,
            lradius,
            lcoefficients,
            nlprojectors
        )

    def nlprojector(self) -> NonLocalProjector:
        """
        PROJECTOR := FLOAT INT FLOAT* NL (FLOAT* NL)*
        """

        nlradius = self.number()
        self.eat(TokenType.SPACE)
        nfunc = self.integer()

        coefficients = numpy.zeros((nfunc, nfunc))

        for i in reversed(range(nfunc)):
            self.eat(TokenType.SPACE)
            j = nfunc - i - 1
            coefficients[j, j:] = self.line('n' * (i + 1))

        self.skip()

        return NonLocalProjector(nlradius, nfunc, coefficients)
