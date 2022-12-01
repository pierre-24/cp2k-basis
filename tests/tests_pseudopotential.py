import tempfile
import unittest
import pathlib

import h5py
import re

from cp2k_basis.base_objects import Filter
from cp2k_basis.pseudopotential import AtomicPseudopotentialsParser, PseudopotentialFamily, PseudopotentialsStorage
from tests import BaseDataObjectMixin


class PseudoTestCase(unittest.TestCase, BaseDataObjectMixin):
    def setUp(self):
        prune_and_rename = Filter([
            (re.compile(r'^.*-q\d{1,2}$'), ''),  # discard all *-q versions
        ])

        self.storage = PseudopotentialsStorage()

        def add_metadata(app: PseudopotentialFamily):
            app.metadata = {
                'source': 'POTENTIALS_EXAMPLE',
                'references': ['10.1103/PhysRevB.54.1703', '10.1103/PhysRevB.58.3641', '10.1007/s00214-005-0655-y']
            }

        with (pathlib.Path(__file__).parent / 'POTENTIALS_EXAMPLE').open() as f:
            self.storage.update(
                AtomicPseudopotentialsParser(
                    f.read()).iter_atomic_pseudopotential_variants(), prune_and_rename, add_metadata)

        self.symbols = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne']
        self.name = 'GTH-BLYP'

        for symbol in self.symbols:
            self.assertEqual(len(self.storage.families), 1)
            self.assertIn(symbol, self.storage[self.name])

    def test_atomic_pseudopotential_str_ok(self):
        app1 = self.storage['GTH-BLYP']['Ne']

        parser = AtomicPseudopotentialsParser(str(app1))
        parser.skip()  # skip comment
        app2 = parser.atomic_pseudopotential_variant()

        self.assertAtomicPseudoEqual(app1, app2)

    def test_pseudopotential_family_str_ok(self):
        bs1 = self.storage[self.name]

        parser = AtomicPseudopotentialsParser(str(bs1))
        bs2 = PseudopotentialFamily(self.name)
        for app in parser.iter_atomic_pseudopotential_variants():
            self.assertIn(self.name, app.names)
            bs2.add(app)

        for symbol in self.symbols:
            self.assertAtomicPseudoEqual(bs1[symbol], bs2[symbol])

    def test_prune_and_rename_ok(self):
        storage = PseudopotentialsStorage()

        prune_and_rename = Filter([
            (re.compile(r'^.*-q\d{1,2}$'), ''),  # discard all *-q versions
            (re.compile(r'GTH-(.*)'), 'XX-\\1')  # just for the fun of it, change the name of the remaining pseudo
        ])

        with (pathlib.Path(__file__).parent / 'POTENTIALS_EXAMPLE').open() as f:
            storage.update(
                AtomicPseudopotentialsParser(f.read()).iter_atomic_pseudopotential_variants(), prune_and_rename)

        self.assertEqual(list(storage.families.keys()), ['XX-BLYP'])

    def test_pseudopotential_family_dump_hdf5_ok(self):
        path = tempfile.mktemp()

        # write h5file
        with h5py.File(path, 'w') as f:
            ppf1 = self.storage[self.name]
            ppf1.dump_hdf5(f.create_group('pseudopotentials/{}'.format(self.name)))

        # read back
        with h5py.File(path) as f:
            ppf2 = PseudopotentialFamily.iter_hdf5_variants()

            # check metadata
            self.assertEqual(ppf1.metadata, ppf2.metadata)

            # check content
            for symbol in self.symbols:
                self.assertAtomicPseudoEqual(ppf1[symbol], ppf2[symbol])

    def test_storage_dump_hdf5_ok(self):
        path = tempfile.mktemp()

        # write h5file
        with h5py.File(path, 'w') as f:
            self.storage.dump_hdf5(f)

        with h5py.File(path) as f:
            storage = PseudopotentialsStorage.read_hdf5(f)

            for bs_name in self.storage:
                self.assertIn(bs_name, storage)

                for symbol in storage[bs_name]:
                    self.assertIn(symbol, storage[bs_name])
                    self.assertAtomicPseudoEqual(storage[bs_name][symbol], self.storage[bs_name][symbol])
