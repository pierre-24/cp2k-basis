import pathlib
import unittest
import os

import h5py
import yaml

from cp2k_basis.scripts.fetch_data import fetch_data
from cp2k_basis.basis_set import BasisSetsStorage
from cp2k_basis.pseudopotential import PseudopotentialsStorage


class FetchDataTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.path_source = pathlib.Path(__file__).parent / 'LIBRARY_SOURCE_EXAMPLE.yml'

        with h5py.File(pathlib.Path(__file__).parent / 'LIBRARY_EXAMPLE.h5') as f:
            self.bs_storage = BasisSetsStorage.read_hdf5(f)
            self.pp_storage = PseudopotentialsStorage.read_hdf5(f)

    @unittest.skipUnless(os.environ.get('TEST_FETCH_DATA'), '`TEST_FETCH_DATA` is not set')
    def test_fetch_data(self):
        with self.path_source.open() as f:
            data_sources = yaml.load(f, yaml.Loader)

        bs_storage, pp_storage = fetch_data(data_sources)

        for bs_name in self.bs_storage.families.keys():
            self.assertIn(bs_name, bs_storage)
            self.assertEqual(self.bs_storage[bs_name].metadata, bs_storage[bs_name].metadata)
            for symbol in self.bs_storage[bs_name].data_objects.keys():
                self.assertIn(symbol, bs_storage[bs_name])

        for ppf_name in self.pp_storage.families.keys():
            self.assertIn(ppf_name, pp_storage)
            self.assertEqual(self.pp_storage[ppf_name].metadata, pp_storage[ppf_name].metadata)
            for symbol in self.pp_storage[ppf_name].data_objects.keys():
                self.assertIn(symbol, pp_storage[ppf_name])
