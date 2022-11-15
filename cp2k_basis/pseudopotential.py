from typing import List, Dict


class AtomicPseudopotential:
    """Atomic GTH (Goedecker-Teter-Hutter) pseudopotential
    """

    def __init__(
        self,
        symbol: str,
        set_name: str,
        full_name: str,
        e_per_shells: List[int],
        nlocal_coefs: int,
        nnonlocal_projectors: int
    ):
        self.symbol = symbol
        self.set_name = set_name
        self.full_name = full_name
        self.e_per_shells = e_per_shells
        self.nlocal_coefs = nlocal_coefs
        self.nnonlocal_projectors = nnonlocal_projectors


class PseudopotentialSet:
    def __init__(self, name: str):
        self.atomic_p: Dict[str, AtomicPseudopotential] = {}
        self.name = name

    def add_atomic_pseudopotential(self, ap: AtomicPseudopotential):
        if ap.symbol in self.atomic_p:
            raise ValueError('Atomic basis set for {} already defined'.format(ap.symbol))

        self.atomic_p[ap.symbol] = ap
