import unittest
import re

import yaml

from cp2k_basis.base_objects import Filter, FilterFirst, FilterUnique, AddMetadata, BaseFamilyStorage


class FilterTestCase(unittest.TestCase):
    def test_filter_ok(self):
        src = ['a', 'a', 'b', 'c']

        # filter all
        self.assertEqual(list(Filter([])(src)), [])
        self.assertEqual(list(Filter([(re.compile(r'.*'), None)])(src)), [])

        # keep all
        self.assertEqual(list(Filter([(re.compile(r'(.*)'), '\\1')])(src)), src)

        # keep one
        self.assertEqual(list(Filter([(re.compile(r'(a)'), '\\1')])(src)), src[0:2])

        # discard one, keep the rest
        self.assertEqual(list(Filter([(re.compile(r'(a)'), None), (re.compile(r'(.*)'), '\\1')])(src)), src[2:])

    def test_create_filter_ok(self):
        src = ['a', 'a', 'b', 'c']

        # explicit
        filter_def = {
            '^a$': None,
            '^(.*)$': '\\1',
        }

        filter = Filter.create(filter_def)
        self.assertEqual(list(filter(src)), src[2:])

        # from yaml
        filter_def = yaml.load('"^a$": null\n"^(.*)$": \\1', Loader=yaml.Loader)
        filter = Filter.create(filter_def)
        self.assertEqual(list(filter(src)), src[2:])

    def test_filter_first_ok(self):
        src = ['a', 'b', 'c']

        # get first
        iterator = FilterFirst([(re.compile(r'(.*)'), '\\1')])(src)
        self.assertEqual(next(iterator), src[0])
        with self.assertRaises(StopIteration):
            next(iterator)

        # one one
        iterator = FilterFirst([(re.compile(r'(b)'), '\\1')])(src)
        self.assertEqual(next(iterator), src[1])
        with self.assertRaises(StopIteration):
            next(iterator)

        # get nothing
        iterator = FilterFirst([(re.compile(r'(x)'), '\\1')])(src)
        with self.assertRaises(StopIteration):
            next(iterator)

    def test_filter_unique_ok(self):
        src = ['a', 'a', 'b', 'c']

        # keep all
        self.assertEqual(list(FilterUnique([(re.compile(r'(.*)'), '\\1')])(src)), src[1:])

        # keep only one 'a'
        self.assertEqual(list(FilterUnique([(re.compile(r'(a)'), '\\1')])(src)), src[0:1])


class AddMetadataTestCase(unittest.TestCase):
    def test_add_metadata_ok(self):
        src = ['a', 'b', 'c']

        add_metadata = AddMetadata([
            (re.compile('a'), {'name': 'named', 'only_a': 'x'}),
            (re.compile('(.*)'), {'name': 'named'})
        ])

        for name in src:
            family_storage = BaseFamilyStorage(name)
            add_metadata(family_storage)

            self.assertEqual(family_storage.metadata['name'], 'named')
            if name == 'a':
                self.assertEqual(family_storage.metadata['only_a'], 'x')
            else:
                self.assertNotIn('only_a', family_storage.metadata)

    def test_add_metadata_create_ok(self):
        src = ['a', 'b', 'c']
        rules = {
            'b': {
                'name': 'y',
                'only_b': 'x'
            },
            '.*': {
                'name': 'y'
            }
        }

        add_metadata = AddMetadata.create(rules)

        for name in src:
            family_storage = BaseFamilyStorage(name)
            add_metadata(family_storage)

            self.assertEqual(family_storage.metadata['name'], 'y')
            if name == 'b':
                self.assertEqual(family_storage.metadata['only_b'], 'x')
            else:
                self.assertNotIn('only_b', family_storage.metadata)
