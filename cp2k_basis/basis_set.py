import h5py
import numpy

from typing import List, Iterable

from cp2k_basis import logger
from cp2k_basis.elements import L_TO_SHELL
from cp2k_basis.parser import BaseParser, TokenType
from cp2k_basis.base_objects import BaseAtomicVariantDataObject, BaseAtomicDataObject, BaseFamilyStorage, Storage

l_logger = logger.getChild('basis_set')


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

    def __str__(self) -> str:
        r = '{} {} {} {} {}\n'.format(
            self.principle_n,
            self.l_min,
            self.l_max,
            self.nfunc,
            ' '.join(str(x) for x in self.nshell))

        fmt = '{:>16.12f}' + ' {: .12f}' * sum(self.nshell) + '\n'
        for i in range(self.nfunc):
            r += fmt.format(self.exponents[i], *self.coefficients[i])

        return r

    def __repr__(self):
        return '<Contraction({}, {}, {}, {}, {})>'.format(
            self.principle_n, self.l_min, self.l_max, repr(self.nshell), self.nfunc
        )

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


class AtomicBasisSetVariant(BaseAtomicVariantDataObject):
    def __init__(self, symbol: str, names: List[str], contractions: List[Contraction]):
        super().__init__(symbol, names)
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

    def __str__(self) -> str:
        r = '# {} [{}|{}]\n'.format(
            self.symbol, self._representation(False, sep=''), self._representation(True, sep=''))
        r += '{}  {}\n{}\n'.format(self.symbol, ' '.join(self.names), len(self.contractions))

        r += ''.join(str(c) for c in self.contractions)

        return r

    def __repr__(self):
        return '<AtomicBasisSet({}, {})>'.format(repr(self.symbol), repr(self.names))

    def dump_hdf5(self, group: h5py.Group):
        """Dump in HDF5"""

        l_logger.info('dump atomic basis set variant for {} in {}'.format(self.symbol, group.name))

        super().dump_hdf5(group)

        ds_info = group.create_dataset('info', shape=(2, ), dtype='i')
        ds_info[:] = [len(self.names), len(self.contractions)]

        for i, contraction in enumerate(self.contractions):
            contraction.dump_hdf5(group, i)

    @classmethod
    def read_hdf5(cls, symbol: str, group: h5py.Group) -> 'AtomicBasisSetVariant':
        l_logger.info('read atomic basis set variant in {}'.format(group.name))

        # checks
        ds_info = group['info']
        if ds_info.shape != (2, ):
            raise ValueError('Dataset `info` in {} must have length 2'.format(group.name))

        # read contractions
        contractions = []

        for i in range(ds_info[1]):
            contractions.append(Contraction.read_hdf5(group, i))

        # create object
        obj = cls(
            symbol,
            names=[],
            contractions=contractions
        )

        obj._read_info(group, ds_info[0])

        return obj


class AtomicBasisSet(BaseAtomicDataObject):
    object_type = AtomicBasisSetVariant


class BasisSet(BaseFamilyStorage):
    """Set of basis set for a given atom
    """

    object_type = AtomicBasisSet


class BasisSetsStorage(Storage):
    object_type = BasisSet
    name = 'basis_sets'


class AtomicBasisSetsParser(BaseParser):

    def iter_atomic_basis_set_variants(self) -> Iterable[AtomicBasisSetVariant]:
        """Basis set
        BASIS_SETS := ATOMIC_BASIS_SET* EOS
        """

        self.skip()

        while self.current_token.type != TokenType.EOS:
            yield self.atomic_basis_set_variant()

            self.skip()

        self.eat(TokenType.EOS)

    def atomic_basis_set_variant(self) -> AtomicBasisSetVariant:
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
            if self.current_token.type != TokenType.NL:
                self.expect(TokenType.WORD)
                names.append(self.current_token.value)
                self.next()

        l_logger.info('parse basis set for {} in {}'.format(symbol, ', '.join(names)))

        self.eat(TokenType.NL)
        self.skip()

        num_contraction = self.integer()

        self.skip()

        contractions = []
        for i in range(num_contraction):
            l_logger.debug('read contraction {}'.format(i))
            contractions.append(self.contraction())

        return AtomicBasisSetVariant(symbol, names, contractions)

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
