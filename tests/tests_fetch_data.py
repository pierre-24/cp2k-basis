import pathlib
import re
import unittest
import os

import yaml

from cp2k_basis.scripts.fetch_data import fetch_data
from cp2k_basis.base_objects import FilterName
from cp2k_basis.basis_set import BasisSetsStorage, AtomicBasisSetsParser
from cp2k_basis.pseudopotential import PseudopotentialsStorage, AtomicPseudopotentialsParser

from tests import CompareAtomicDataObjectMixin


class FetchDataTestCase(unittest.TestCase, CompareAtomicDataObjectMixin):
    def setUp(self) -> None:
        self.path_source = pathlib.Path(__file__).parent / 'LIBRARY_SOURCE_EXAMPLE.yml'

        filter_name = FilterName([(re.compile(r'.*-q.*'), '')])  # basically remove all -q* version

        self.bs_storage_parsed = BasisSetsStorage()
        with (pathlib.Path(__file__).parent / 'BASIS_EXAMPLE').open() as f:
            self.bs_storage_parsed.update(
                AtomicBasisSetsParser(f.read()).iter_atomic_basis_set_variants(),
                filter_name
            )

        self.pp_storage_parsed = PseudopotentialsStorage()
        with (pathlib.Path(__file__).parent / 'POTENTIALS_EXAMPLE').open() as f:
            self.pp_storage_parsed.update(
                AtomicPseudopotentialsParser(f.read()).iter_atomic_pseudopotentials(),
                filter_name
            )

    @unittest.skipUnless(os.environ.get('TEST_FETCH_DATA'), '`TEST_FETCH_DATA` is not set')
    def test_fetch_data_ok(self):
        # NOTE: this test will fail if the `BASIS_EXAMPLE` or `POTENTIAL_EXAMPLE` files are changed locally.

        with self.path_source.open() as f:
            data_sources = yaml.load(f, yaml.Loader)

        bs_storage, pp_storage = fetch_data(data_sources)

        for bs_name in self.bs_storage_parsed.families.keys():
            self.assertIn(bs_name, bs_storage)
            # TODO: check metadata

            for symbol in self.bs_storage_parsed[bs_name].data_objects.keys():
                self.assertIn(symbol, bs_storage[bs_name])

                self.assertAtomicBasisSetEqual(bs_storage[bs_name][symbol], self.bs_storage_parsed[bs_name][symbol])

        for ppf_name in self.pp_storage_parsed.families.keys():
            self.assertIn(ppf_name, pp_storage)

            for symbol in self.pp_storage_parsed[ppf_name].data_objects.keys():
                self.assertIn(symbol, pp_storage[ppf_name])

                self.assertAtomicPseudoEqual(pp_storage[ppf_name][symbol], self.pp_storage_parsed[ppf_name][symbol])
