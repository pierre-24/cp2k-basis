import pathlib
import re

import numpy

from cp2k_basis.base_objects import Filter, FilterStrategy
from cp2k_basis.basis_set import AtomicBasisSetVariant, BasisSetsStorage, AtomicBasisSetsParser
from cp2k_basis.pseudopotential import AtomicPseudopotentialVariant, AtomicPseudopotentialsParser, \
    PseudopotentialsStorage


class BaseDataObjectMixin:

    filter_name = Filter([(re.compile(r'(.*)(-q.*)'), '\\1')], strategy=FilterStrategy.Unique)
    filter_variant = Filter([(re.compile(r'.*-(q.*)'), '\\1')], strategy=FilterStrategy.First)

    def read_basis_set_from_file(self, path: pathlib.Path):

        bs_storage_parsed = BasisSetsStorage()
        with path.open() as f:
            bs_storage_parsed.update(
                AtomicBasisSetsParser(f.read()).iter_atomic_basis_set_variants(),
                self.filter_name,
                self.filter_variant
            )

        return bs_storage_parsed

    def read_pp_from_file(self, path: pathlib.Path):
        pp_storage_parsed = PseudopotentialsStorage()
        with path.open() as f:
            pp_storage_parsed.update(
                AtomicPseudopotentialsParser(f.read()).iter_atomic_pseudopotential_variants(),
                self.filter_name,
                self.filter_variant
            )

        return pp_storage_parsed

    def assertAtomicBasisSetEqual(self, abs1: AtomicBasisSetVariant, abs2: AtomicBasisSetVariant):
        self.assertEqual(abs2.names, abs1.names)
        self.assertEqual(abs2.symbol, abs1.symbol)
        self.assertEqual(len(abs2.contractions), len(abs1.contractions))

        for i in range(len(abs1.contractions)):
            contraction1 = abs1.contractions[i]
            contraction2 = abs2.contractions[i]

            self.assertEqual(contraction2.principle_n, contraction1.principle_n)
            self.assertEqual((contraction2.l_min, contraction2.l_max), (contraction1.l_min, contraction1.l_max))
            self.assertEqual(contraction2.nfunc, contraction1.nfunc)
            self.assertEqual(contraction2.nshell, contraction1.nshell)

            self.assertTrue(numpy.array_equal(contraction2.exponents, contraction1.exponents))
            self.assertTrue(numpy.array_equal(contraction2.coefficients, contraction1.coefficients))

    def assertAtomicPseudoEqual(self, app1: AtomicPseudopotentialVariant, app2: AtomicPseudopotentialVariant):
        self.assertEqual(app2.symbol, app1.symbol)
        self.assertEqual(app2.names, app1.names)
        self.assertEqual(app2.nelec, app1.nelec)
        self.assertEqual(app2.lradius, app1.lradius)
        self.assertTrue(numpy.array_equal(app2.lcoefficients, app1.lcoefficients))

        for i in range(len(app1.nlprojectors)):
            proj = app1.nlprojectors[i]
            proj2 = app2.nlprojectors[i]

            self.assertEqual(proj2.radius, proj.radius)
            self.assertTrue(numpy.array_equal(proj2.coefficients, proj.coefficients))
