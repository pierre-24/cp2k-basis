from typing import List, Iterable

import h5py
import numpy

from cp2k_basis import logger
from cp2k_basis.base_objects import BaseAtomicDataObject, BaseFamilyStorage, Storage
from cp2k_basis.parser import BaseParser, TokenType


class NonLocalProjector:

    HDF5_DS_RADIUS_COEFS = 'nlprojector_{}_radius_coefs'

    def __init__(self, radius: float, nfunc: int, coefficients: numpy.ndarray):
        if coefficients.shape != (nfunc, nfunc):
            raise ValueError('number of coefficient must be equal to `nfunc * nfunc`')

        self.radius = radius
        self.nfunc = nfunc
        self.coefficients = coefficients

    def __str__(self) -> str:
        r = '{:16.8f} {:>3}'.format(self.radius, self.nfunc)

        for i in range(self.nfunc):
            if i != 0:  # pad
                r += '                    ' + ' ' * 15 * i
            r += (' {:14.8f}' * (self.nfunc - i)).format(*self.coefficients[i, i:]) + '\n'

        if self.nfunc == 0:
            r += '\n'

        return r

    def __repr__(self):
        return '<NonLocalProjector({}, {})>'.format(self.radius, self.nfunc)

    def dump_hdf5(self, group: h5py.Group, i: int):
        """Dump HDF5"""

        triu = list(self.coefficients[numpy.triu_indices(self.nfunc)])

        dset_radius_coefs = group.create_dataset(
            NonLocalProjector.HDF5_DS_RADIUS_COEFS.format(i), shape=(len(triu) + 1,), dtype='d')

        dset_radius_coefs[0] = self.radius
        dset_radius_coefs[1:] = triu
        dset_radius_coefs.attrs['nfunc'] = self.nfunc

    @classmethod
    def read_hdf5(cls, group: h5py.Group, i: int):
        """
        Read HDF5 group
        """

        dset_radius_coefs = group[NonLocalProjector.HDF5_DS_RADIUS_COEFS.format(i)]
        nfunc = dset_radius_coefs.attrs['nfunc']

        triu_indices = numpy.triu_indices(nfunc)

        if dset_radius_coefs.shape != (len(triu_indices[0]) + 1, ):
            raise ValueError('Dataset `{}` in {} must have length {}'.format(
                NonLocalProjector.HDF5_DS_RADIUS_COEFS.format(i), group.name, len(triu_indices) + 1))

        coefs = numpy.zeros((nfunc, nfunc))
        coefs[triu_indices] = dset_radius_coefs[1:]

        return cls(dset_radius_coefs[0], nfunc, coefs)


class AtomicPseudopotential(BaseAtomicDataObject):
    """Atomic GTH (Goedecker-Teter-Hutter) pseudopotential of CP2K
    """

    HDF5_DS_RADIUS_COEF = 'local_radius_coefs'

    def __init__(
        self,
        symbol: str,
        names: List[str],
        nelec: List[int],
        lradius: float,
        lcoefficients: numpy.ndarray,
        nlprojectors: List[NonLocalProjector]
    ):
        super().__init__(symbol, names)

        self.nelec = nelec
        self.lradius = lradius
        self.lcoefficients = lcoefficients
        self.nlprojectors = nlprojectors

    def __str__(self) -> str:
        r = '#\n{}  {}\n  {}\n'.format(
            self.symbol, ' '.join(self.names), ' '.join('{:>4}'.format(x) for x in self.nelec))

        # local part
        n = self.lcoefficients.shape[0]
        r += '{:16.8f} {:>3}'.format(self.lradius, n)
        r += (' {:14.8f}' * n).format(*self.lcoefficients) + '\n'

        # nonlocal part
        r += '  {:>4}\n'.format(len(self.nlprojectors))

        for proj in self.nlprojectors:
            r += str(proj)

        return r

    def __repr__(self):
        return 'AtomicPseudopotential({}, {}, {})'.format(repr(self.symbol), repr(self.names), repr(self.nelec))

    def dump_hdf5(self, group: h5py.Group):
        """Dump in HDF5"""
        logger.info('dump pseudopotential for {} in {}'.format(self.symbol, group.name))

        super().dump_hdf5(group)

        ds_info = group.create_dataset('info', shape=(3 + len(self.nelec), ), dtype='i')
        ds_info[:3] = [len(self.names), len(self.lcoefficients), len(self.nlprojectors)]
        ds_info[3:] = self.nelec
        ds_info.attrs['nelec'] = len(self.nelec)

        ds_local_radius_coefs = group.create_dataset(
            AtomicPseudopotential.HDF5_DS_RADIUS_COEF, (1 + self.lcoefficients.shape[0]), dtype='d')

        ds_local_radius_coefs[0] = self.lradius
        ds_local_radius_coefs[1:] = self.lcoefficients

        for i, contraction in enumerate(self.nlprojectors):
            contraction.dump_hdf5(group, i)

    @classmethod
    def read_hdf5(cls, symbol: str, group: h5py.Group):
        logger.info('read pseudopotential for {} in {}'.format(symbol, group.name))

        ds_info = group['info']
        ds_radius_coefs = group[AtomicPseudopotential.HDF5_DS_RADIUS_COEF]

        n = ds_info.attrs['nelec']

        # checks
        if ds_info.shape != (3 + n, ):
            raise ValueError('Dataset `info` in {} must have length {}'.format(group.name, 3 + n))

        if ds_radius_coefs.shape != (ds_info[1] + 1,):
            raise ValueError('Dataset `{}` in {} must have length {}'.format(
                AtomicPseudopotential.HDF5_DS_RADIUS_COEF, group.name, ds_info[1] + 1))

        # fetch
        nelec = list(ds_info[3:])
        lradius = ds_radius_coefs[0]
        lcoefs = ds_radius_coefs[1:]

        projectors = []

        for i in range(ds_info[2]):
            projectors.append(NonLocalProjector.read_hdf5(group, i))

        obj = cls(symbol, [], nelec, lradius, lcoefs, projectors)
        obj._read_info(group, ds_info[0])

        return obj


class PseudopotentialFamily(BaseFamilyStorage):
    object_type = AtomicPseudopotential


class PseudopotentialsStorage(Storage):
    object_type = PseudopotentialFamily
    name = 'pseudopotentials'


class AtomicPseudopotentialsParser(BaseParser):

    def iter_atomic_pseudopotentials(self) -> Iterable[PseudopotentialFamily]:
        """
        ATOMIC_PPs := ATOMIC_PP* EOS
        """

        self.skip()

        while self.current_token.type != TokenType.EOS:
            yield self.atomic_pseudopotential()

            self.skip()

        self.eat(TokenType.EOS)

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

        logger.info('parse pseudopotential for {} in {}'.format(symbol, ', '.join(names)))

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
