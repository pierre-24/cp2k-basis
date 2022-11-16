from typing import List, Dict

from cp2k_basis.parser import BaseParser, TokenType


class AtomicPseudopotential:
    """Atomic GTH (Goedecker-Teter-Hutter) pseudopotential of CP2K
    """

    def __init__(
        self,
        symbol: str,
        names: List[str],
        e_per_shell: List[int],
        nlocal_coefs: int,
        nnonlocal_projectors: int
    ):
        self.symbol = symbol
        self.names = names
        self.e_per_shell = e_per_shell
        self.nlocal_coefs = nlocal_coefs
        self.nnonlocal_projectors = nnonlocal_projectors


class AtomicPseudoPotentials:
    def __init__(self, symbol: str):
        self.pseudopotentials: Dict[str, AtomicPseudopotential] = {}
        self.symbol = symbol

    def add_atomic_pseudopotential(self, ap: AtomicPseudopotential):

        for name in ap.names:
            if name in self.pseudopotentials:
                raise ValueError('pseudo {} already defined for {}'.format(name, self.symbol))

            self.pseudopotentials[name] = ap


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
        ATOMIC_PP := WORD SPACE WORD (SPACE WORD)* NL INT* NL LOCAL_PART NL INT NL PROJECTOR*
        LOCAL_PART :=  FLOAT INT FLOAT*
        PROJECTOR := FLOAT INT FLOAT* NL (FLOAT* NL)*
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
        e_per_shell = [self.integer()]

        while self.current_token.type not in [TokenType.NL, TokenType.EOS]:
            self.eat(TokenType.SPACE)
            e_per_shell.append(self.integer())

        self.eat(TokenType.NL)
        self.skip()

        # local part
        self.number()
        self.eat(TokenType.SPACE)
        nlocal_coefs = self.integer()

        if nlocal_coefs > 0:
            self.eat(TokenType.SPACE)
            self.line('n' * nlocal_coefs)
        else:
            self.eat(TokenType.NL)

        self.skip()

        # nonlocal projectors
        nnonlocal_projectors = self.integer()

        self.eat(TokenType.NL)
        self.skip()

        for proj_i in range(nnonlocal_projectors):
            self.number()
            self.eat(TokenType.SPACE)
            nprojectors = self.integer()
            for i in reversed(range(nprojectors)):
                self.eat(TokenType.SPACE)
                self.line('n' * (i + 1))

            self.skip()

        return AtomicPseudopotential(
            symbol,
            names,
            e_per_shell,
            nlocal_coefs,
            nnonlocal_projectors
        )
