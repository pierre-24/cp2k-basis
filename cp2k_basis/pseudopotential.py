from typing import List, Dict

from cp2k_basis.parser import BaseParser, TokenType


class AtomicPseudopotential:
    """Atomic GTH (Goedecker-Teter-Hutter) pseudopotential of CP2K
    """

    def __init__(
        self,
        symbol: str,
        family_name: str,
        full_name: str,
        e_per_shell: List[int],
        nlocal_coefs: int,
        nnonlocal_projectors: int
    ):
        self.symbol = symbol
        self.family_name = family_name
        self.full_name = full_name
        self.e_per_shell = e_per_shell
        self.nlocal_coefs = nlocal_coefs
        self.nnonlocal_projectors = nnonlocal_projectors


class PseudopotentialFamily:
    def __init__(self, name: str):
        self.atomic_p: Dict[str, AtomicPseudopotential] = {}
        self.name = name

    def add_atomic_pseudopotential(self, ap: AtomicPseudopotential):
        if ap.symbol in self.atomic_p:
            raise ValueError('Atomic basis set for {} already defined'.format(ap.symbol))

        self.atomic_p[ap.symbol] = ap


class PseudopotentialFamiliesParser(BaseParser):
    def __init__(self, inp: str):
        super().__init__(inp)

    def pseudopotential_families(self):
        """
        PP_FAMILIES := ATOMIC_PP* EOS
        """

        pp_families = {}

        self.skip()

        while self.current_token.type != TokenType.EOS:
            atomic_pp = self.atomic_pseudopotential()

            # todo: no family name!

            if atomic_pp.family_name not in pp_families:
                pp_families[atomic_pp.family_name] = PseudopotentialFamily(atomic_pp.family_name)

            pp_families[atomic_pp.family_name].add_atomic_pseudopotential(atomic_pp)

            self.skip()

        self.eat(TokenType.EOS)
        return pp_families

    def atomic_pseudopotential(self) -> AtomicPseudopotential:
        """
        ATOMIC_PP := WORD SPACE WORD (SPACE WORD)? NL INT* NL LOCAL_PART NL INT NL PROJECTOR*
        LOCAL_PART :=  FLOAT INT FLOAT*
        PROJECTOR := FLOAT INT FLOAT* NL (FLOAT* NL)*
        """

        # first line
        self.expect(TokenType.WORD)
        symbol = self.current_token.value
        self.next()
        self.eat(TokenType.SPACE)

        self.expect(TokenType.WORD)
        full_name = self.current_token.value
        family_name = None
        self.next()

        if self.current_token.type == TokenType.SPACE:
            self.next()
            if self.current_token.type == TokenType.WORD:
                family_name = self.current_token.value
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
            family_name,
            full_name,
            e_per_shell,
            nlocal_coefs,
            nnonlocal_projectors
        )
