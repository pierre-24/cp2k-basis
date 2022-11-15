from typing import List


class Contraction:
    def __init__(self, principle_n: int, l_min: int, l_max: int, gaussian_per_l: List[int]):
        self.principle_n = principle_n
        self.l_min = l_min
        self.l_max = l_max
        self.gaussian_per_l = gaussian_per_l


class AtomicBasisSet:
    def __init__(self, Z: int, full_name: str, contractions: List[Contraction]):
        self.Z = Z
        self.full_name = full_name
        self.contractions = contractions

    def contracted_representation(self) -> str:
        pass

    def full_representation(self) -> str:
        pass

    def __repr__(self):
        return '{} [{}|{}]'.format(self.Z, self.full_representation(), self.contracted_representation())


class BasisSet:
    def __int__(self, name: str):
        self.atomic_bs = {}
        self.name = name

    def add_atomic_basis_set(self, bs: AtomicBasisSet):
        if bs.Z in self.atomic_bs:
            raise ValueError('Atomic basis set for Z={} already defined'.format(bs.Z))

        self.atomic_bs[bs.Z] = bs
