import pathlib

import h5py
import numpy

from typing import List, Dict, Callable, Iterable, Union

from cp2k_basis import logger
from cp2k_basis.parser import BaseParser, TokenType, PruneAndRename

L_TO_SHELL = {
    0: 's',
    1: 'p',
    2: 'd',
    3: 'f',
    4: 'g',
    5: 'h'
}

string_dt = h5py.special_dtype(vlen=str)


class Contraction:

    HDF5_DS_INFO = 'contraction_{}_info'
    HDF5_DS_EXP_COEFS = 'contraction_{}_exp_coefs'

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

    def dump_hdf5(self, group: h5py.Group, i: int):
        dset_info = group.create_dataset(Contraction.HDF5_DS_INFO.format(i), shape=(4 + len(self.nshell)), dtype='i')
        dset_info.attrs['nshell'] = len(self.nshell)

        lst = [self.principle_n, self.l_min, self.l_max, self.nfunc]
        lst.extend(self.nshell)
        dset_info[:] = lst

        dset_exp_coefs = group.create_dataset(
            Contraction.HDF5_DS_EXP_COEFS.format(i), shape=(self.nfunc, sum(self.nshell) + 1), dtype='d')

        dset_exp_coefs[:, 0] = self.exponents
        dset_exp_coefs[:, 1:] = self.coefficients

    @classmethod
    def read_hdf5(cls, group: h5py.Group, i: int):
        """
        Read HDF5 group
        """

        dset_info = group[Contraction.HDF5_DS_INFO.format(i)]
        dset_exp_coefs = group[Contraction.HDF5_DS_EXP_COEFS.format(i)]

        # checks
        nshell = dset_info.attrs.get('nshell', -1)

        if dset_info.shape != (4 + nshell,):
            raise ValueError('{} must contains {} data'.format(dset_info.name, 4 + nshell))

        principle_n, l_min, l_max, nfunc = dset_info[:4]
        nshell = list(dset_info[4:])

        if dset_exp_coefs.shape != (nfunc, sum(nshell) + 1):
            raise ValueError('{} must contains {}x{} data'.format(dset_exp_coefs.name, nfunc, sum(nshell) + 1))

        return cls(principle_n, l_min, l_max, nfunc, nshell, dset_exp_coefs[:, 0], dset_exp_coefs[:, 1:])


class AtomicBasisSet:
    def __init__(
        self,
        symbol: str,
        names: List[str],
        contractions: List[Contraction],
        source: str = None,
        references: List[str] = None
    ):
        self.symbol = symbol
        self.names = names
        self.contractions = contractions
        self.source = source
        self.references = references

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

    def dump_hdf5(self, group: h5py.Group):
        """Dump in HDF5"""

        logger.info('dump basis set for {} in {}'.format(self.symbol, group.name))

        if self.source:
            group.attrs['source'] = self.source
        if self.references:
            group.attrs['references'] = ','.join(self.references)

        ds_info = group.create_dataset('info', shape=(2, ), dtype='i')
        ds_info[:] = [len(self.names), len(self.contractions)]

        ds_names = group.create_dataset('names', shape=(len(self.names), ), dtype=string_dt)
        ds_names[:] = self.names

        for i, contraction in enumerate(self.contractions):
            contraction.dump_hdf5(group, i)

    @classmethod
    def read_hdf5(cls, symbol: str, group: h5py.Group) -> 'AtomicBasisSet':
        logger.info('read basis set for {} in {}'.format(symbol, group.name))

        ds_info = group['info']
        ds_names = group['names']

        # checks
        if ds_info.shape != (2, ):
            raise ValueError('Dataset `info` in {} must have length 2'.format(group.name))

        if ds_names.shape != (ds_info[0], ):
            raise ValueError('Dataset `names` in {} must have length {}'.format(group.name, ds_info[0]))

        # read contractions
        contractions = []

        for i in range(ds_info[1]):
            contractions.append(Contraction.read_hdf5(group, i))

        source = group.attrs.get('source', None)
        references = group.attrs['references'].split(',') if 'references' in group.attrs else None

        return cls(
            symbol,
            names=list(n.decode('utf8') for n in ds_names),
            contractions=contractions,
            source=source,
            references=references
        )


class AtomicBasisSets:
    """Set of basis set for a given atom
    """

    def __init__(self, symbol: str):
        self.basis_sets: Dict[str, AtomicBasisSet] = {}
        self.symbol = symbol

    def add_atomic_basis_set(self, bs: AtomicBasisSet, names: Iterable[str]):

        if type(bs) is not AtomicBasisSet:
            raise TypeError('`bs` must be AtomicBasisSet')

        for name in names:
            if name in self.basis_sets:
                raise ValueError('{} already exists for atom {}'.format(name, self.symbol))

            self.basis_sets[name] = bs

    def __repr__(self) -> str:
        return ''.join(str(bs) for bs in self.basis_sets.values())

    def dump_hdf5(self, group: h5py.Group):
        """Dump in HDF5"""

        for key, basis in self.basis_sets.items():
            # remove existing
            try:
                group.pop(key)
            except KeyError:
                pass

            # create new
            subgroup = group.create_group(key)
            basis.dump_hdf5(subgroup)

    @classmethod
    def read_hdf5(cls, group: h5py.Group) -> 'AtomicBasisSets':
        symbol = pathlib.Path(group.name).name
        o = cls(symbol)

        for key, basis_group in group.items():
            o.add_atomic_basis_set(AtomicBasisSet.read_hdf5(symbol, basis_group), [key])

        return o


def avail_atom_per_basis(basis: Dict[str, AtomicBasisSets]) -> Dict[str, List[str]]:
    per_name = {}

    for atomic_basis in basis.values():
        for name in atomic_basis.basis_sets:
            if name not in per_name:
                per_name[name] = []
            per_name[name].append(atomic_basis.symbol)

    return per_name


class AtomicBasisSetsParser(BaseParser):
    def __init__(
        self,
        inp: str,
        prune_and_rename: Union[Callable[[Iterable[str]], Iterable[str]], PruneAndRename] = lambda x: x,
        source: str = None,
        references: List[str] = None
    ):
        super().__init__(inp)
        self.prune_and_rename = prune_and_rename
        self.source = source
        self.references = references

    def basis_sets(self, basis_sets: Dict[str, AtomicBasisSets] = None) -> Dict[str, AtomicBasisSets]:
        """Basis set
        BASIS_SETS := ATOMIC_BASIS_SET* EOS
        """

        if basis_sets is None:
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

        logger.info('parse basis set for {} in {}'.format(symbol, ', '.join(names)))

        self.eat(TokenType.NL)
        self.skip()

        num_contraction = self.integer()

        self.skip()

        contractions = []
        for i in range(num_contraction):
            contractions.append(self.contraction())

        return AtomicBasisSet(
            symbol,
            names,
            contractions,
            self.source,
            self.references
        )

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

        # skip anything remaining on this line (see `U` in $CP2K/cp2l/data/BASIS_MOLOPT)
        while self.current_token.type not in [TokenType.NL, TokenType.EOS]:
            self.next()

        self.skip()

        exponents = numpy.zeros(nfunc)
        coefficients = numpy.zeros((nfunc, sum(nshell)))

        for i in range(nfunc):
            c = [self.number()]
            for j in range(sum(nshell)):
                self.eat(TokenType.SPACE)
                c.append(self.number())
            exponents[i] = c[0]
            coefficients[i] = c[1:]

            # skip anything remaining on this line (see `O` in $CP2K/cp2l/data/GTH_BASIS_SET)
            while self.current_token.type not in [TokenType.NL, TokenType.EOS]:
                self.next()

            self.skip()

        return Contraction(principle_n, l_min, l_max, nfunc, nshell, exponents, coefficients)
