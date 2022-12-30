import pathlib
import re
import unittest
import os

import yaml

from cp2k_basis.scripts.fetch_data import fetch_data
from cp2k_basis.scripts import SCHEMA_LIBRARY_SOURCE_FILE, SCHEMA_EXPLORE_SOURCE_FILE
from cp2k_basis.scripts.explore_file import explore_file

from tests import BaseDataObjectMixin


class FetchDataTestCase(unittest.TestCase, BaseDataObjectMixin):
    def setUp(self) -> None:
        self.path_source = pathlib.Path(__file__).parent / 'LIBRARY_SOURCE_EXAMPLE.yml'
        self.path_explore_source = pathlib.Path(__file__).parent / 'FETCH_SOURCE_EXAMPLE.yml'
        self.bs_storage_parsed = self.read_basis_set_from_file(pathlib.Path(__file__).parent / 'BASIS_EXAMPLE')
        self.pp_storage_parsed = self.read_pp_from_file(pathlib.Path(__file__).parent / 'POTENTIALS_EXAMPLE')

    def test_schema_ok(self):
        with self.path_source.open() as f:
            data_sources = yaml.load(f, yaml.Loader)
            self.assertTrue(SCHEMA_LIBRARY_SOURCE_FILE.is_valid(data_sources))

        with self.path_explore_source.open() as f:
            data_fetch_sources = yaml.load(f, yaml.Loader)
            self.assertTrue(SCHEMA_EXPLORE_SOURCE_FILE.is_valid(data_fetch_sources))

    def assertEqualToParsed(self, bs_storage, pp_storage, metadata):
        for bs_name in self.bs_storage_parsed:
            self.assertIn(bs_name, bs_storage)

            for pattern, values in metadata.items():
                p = re.compile(pattern)
                if p.match(bs_name):
                    self.assertEqual(bs_storage[bs_name].metadata, values)
                    break

            for symbol in self.bs_storage_parsed[bs_name]:
                self.assertIn(symbol, bs_storage[bs_name])

                for variant in self.bs_storage_parsed[bs_name][symbol]:
                    self.assertIn(variant, bs_storage[bs_name][symbol])
                    self.assertAtomicBasisSetEqual(
                        bs_storage[bs_name][symbol][variant], self.bs_storage_parsed[bs_name][symbol][variant])

        for ppf_name in self.pp_storage_parsed:
            self.assertIn(ppf_name, pp_storage)

            for pattern, values in metadata.items():
                p = re.compile(pattern)
                if p.match(ppf_name):
                    self.assertEqual(pp_storage[ppf_name].metadata, values)
                    break

            for symbol in self.pp_storage_parsed[ppf_name].data_objects.keys():
                self.assertIn(symbol, pp_storage[ppf_name])

                for variant in self.pp_storage_parsed[ppf_name][symbol]:
                    self.assertIn(variant, pp_storage[ppf_name][symbol])

                    self.assertAtomicPseudoEqual(
                        pp_storage[ppf_name][symbol][variant], self.pp_storage_parsed[ppf_name][symbol][variant])

    def test_explore_file_ok(self):

        with self.path_explore_source.open() as f:
            data_sources = yaml.load(f, yaml.Loader)

        pwd = pathlib.Path(self.path_explore_source).parent
        bs_storage, pp_storage = explore_file(data_sources, pwd)

        self.assertEqualToParsed(bs_storage, pp_storage, data_sources['metadata'])

    @unittest.skipUnless(os.environ.get('TEST_FETCH_DATA'), '`TEST_FETCH_DATA` is not set')
    def test_fetch_data_ok(self):
        # NOTE: this test will fail if the `BASIS_EXAMPLE` or `POTENTIAL_EXAMPLE` files are changed locally.

        with self.path_source.open() as f:
            data_sources = yaml.load(f, yaml.Loader)

        bs_storage, pp_storage = fetch_data(data_sources)

        self.assertEqualToParsed(bs_storage, pp_storage, data_sources['metadata'])
