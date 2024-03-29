import re
import sys

import h5py

from typing import Dict, Iterable, Union, Any, List, Callable, Tuple, Iterator

import more_itertools
import numpy

from cp2k_basis import logger
from cp2k_basis.elements import ElementSet, SYMB_TO_Z

string_dt = h5py.special_dtype(vlen=str)


l_logger = logger.getChild('base_objects')


class BaseAtomicVariantDataObject:
    def __init__(self, symbol: str, names: List[str], source: str = ''):
        self.symbol = symbol
        self.names = names
        self.source = source

    def preferred_name(self, family_name: str, variant: str) -> str:
        """Select one of the `self.names`, hopefully containing the family name and the variant.
        If not, try to select one that contains the variant, and if not the family name, and if not,
        return the first name.
        """

        try:
            return next(filter(lambda x: variant in x and family_name in x, self.names))
        except StopIteration:
            try:
                return next(filter(lambda x: variant in x, self.names))
            except StopIteration:
                try:
                    return next(filter(lambda x: family_name in x, self.names))
                except StopIteration:
                    return self.names[0]

    def dump_hdf5(self, group: h5py.Group):
        """Dump in HDF5"""

        # dump names
        ds_names = group.create_dataset('names', shape=(len(self.names), ), dtype=string_dt)
        ds_names[:] = self.names

        if self.source:
            group.attrs['source'] = self.source

    def _read_info(self, group: h5py.Group, name_size: int):
        """Read names
        """

        ds_names = group['names']

        if ds_names.shape != (name_size, ):
            raise ValueError('Dataset `names` in {} must have length {}'.format(group.name, name_size))

        self.names = list(n.decode('utf8') for n in ds_names)

        if 'source' in group.attrs:
            self.source = group.attrs['source']

    @classmethod
    def read_hdf5(cls, symbol: str, group: h5py.Group) -> 'BaseAtomicVariantDataObject':
        """Create from HDF5"""

        raise NotImplementedError()


class BaseAtomicDataObject:
    """Base atomic data object, stores `BaseAtomicVariantDataObject`
    """

    object_type = BaseAtomicVariantDataObject

    def __init__(self, family_name: str, symbol: str):
        self.symbol = symbol
        self.family_name = family_name
        self.variants: Dict[str, BaseAtomicVariantDataObject] = {}

    def add(self, obj: BaseAtomicVariantDataObject, variant: str):
        if type(obj) is not self.object_type:
            raise TypeError('`obj` must be of type {}'.format(self.object_type))

        if variant in self.variants:
            raise ValueError('`{}` already exists for symbol {}'.format(variant, obj.symbol))

        self.variants[variant] = obj

    def __repr__(self):
        return '<BaseAtomicDataObject({}, {})>'.format(repr(self.family_name), repr(self.symbol))

    def __str__(self) -> str:
        return ''.join(str(bs) for bs in self.variants.values())

    def __getitem__(self, item: str) -> BaseAtomicVariantDataObject:
        return self.variants[item]

    def __contains__(self, item: str) -> bool:
        return item in self.variants

    def __iter__(self) -> Iterable[str]:
        yield from self.variants.keys()

    def values(self) -> Iterable[BaseAtomicVariantDataObject]:
        """Yield all `AtomicDataObjects`
        """

        yield from self.variants.values()

    def tree(self, out=sys.stdout):
        """Print a tree"""

        print('   |  +- {}: {}'.format(self.symbol, ', '.join(self.variants.keys())), file=out)

    def dump_hdf5(self, group: h5py.Group):
        """Dump in HDF5"""

        for key, data in self.variants.items():
            subgroup = group.create_group(key)
            data.dump_hdf5(subgroup)

    @classmethod
    def iter_hdf5_variants(cls, symbol: str, group: h5py.Group) -> Iterable[Tuple[BaseAtomicVariantDataObject, str]]:
        """Yield a set of variant for a given symbol"""

        for key, variant_group in group.items():
            yield cls.object_type.read_hdf5(symbol, variant_group), key


class BaseFamilyStorage:
    """Base family storage, stores `AtomicDataObject` for a given family name.
    """

    object_type = BaseAtomicDataObject

    def __init__(self, family_name: str, metadata: Dict[str, Union[str, Any]] = None):
        self.name = family_name
        self.data_objects: Dict[str, BaseAtomicDataObject] = {}
        self.metadata = metadata if metadata else {}

    def add(self, obj: BaseAtomicVariantDataObject, variant: str):

        if obj.symbol not in self.data_objects:
            self.data_objects[obj.symbol] = self.object_type(self.name, obj.symbol)

        self.data_objects[obj.symbol].add(obj, variant)

    def __repr__(self):
        return '<BaseFamilyStorage({})>'.format(repr(self.name))

    def __str__(self) -> str:
        return ''.join(str(bs) for bs in self.data_objects.values())

    def __getitem__(self, item: str) -> BaseAtomicDataObject:
        return self.data_objects[item]

    def __contains__(self, item: str) -> bool:
        return item in self.data_objects

    def __iter__(self) -> Iterable[str]:
        yield from self.data_objects.keys()

    def values(self) -> Iterable[BaseAtomicDataObject]:
        """Yield all `AtomicDataObjects`
        """

        yield from self.data_objects.values()

    def tree(self, out=sys.stdout):
        """Print a tree"""

        print('   +- {}\n   |  metadata={}'.format(self.name, repr(self.metadata)), file=out)
        print('   |  |', file=out)
        for atomic in self.data_objects.values():
            atomic.tree(out)

        print('   |', file=out)

    def dump_hdf5(self, group: h5py.Group):
        """Dump in HDF5"""

        for key, data in self.data_objects.items():
            # remove existing
            try:
                group.pop(key)
            except KeyError:
                pass

            # create new group
            subgroup = group.create_group(key)
            data.dump_hdf5(subgroup)

            # dump metadata as attributes
            for key, value in self.metadata.items():
                if value:
                    group.attrs[key] = value

    @staticmethod
    def _read_metadata_hdf5(group: h5py.Group) -> dict:
        metadata = {}

        for key, values in group.attrs.items():
            if type(values) is numpy.ndarray:
                metadata[key] = list(values)
            else:
                metadata[key] = values

        return metadata

    @classmethod
    def iter_hdf5_variants(cls, group: h5py.Group) -> Iterable[Tuple[BaseAtomicVariantDataObject, str]]:
        """Yield a set of variants of the same family from HDF5"""

        for key, basis_group in group.items():
            yield from cls.object_type.iter_hdf5_variants(key, basis_group)


class StorageException(Exception):
    pass


class Storage:
    """Stores `BaseFamilyStorage` for each possible family name.
    """

    object_type = BaseFamilyStorage
    name = 'base_storage'

    def __init__(self):
        self.families: Dict[str, BaseFamilyStorage] = {}
        self.tags_per_family: Dict[str, List[str]] = {}
        self.elements_per_family: Dict[str, List[str]] = {}
        self.date_build = None

    def update(
        self,
        data_objects: Iterable[BaseAtomicVariantDataObject],
        filter_name: Union[Callable[[Iterable[str]], Iterable[str]], 'Filter'] = lambda x: x,
        filter_variant: Union[Callable[[Iterable[str]], Iterable[str]], 'Filter'] = lambda x: iter([]),
        add_metadata: Callable[[BaseFamilyStorage], None] = None
    ):
        """Add a set of variant to the storage.

        Use `filter_name` to extract the family names from `data_object.names`.

        Use `filter_variant` to extract the variant from `data_object.names` (will use the first result, or "qZ" if
        there is none, where Z is the number of valence electrons).

        Use `add_metadata` to add metadata to the family if any.
        """

        from cp2k_basis.pseudopotential import AtomicPseudopotentialVariant

        names_added = set()

        for obj in data_objects:
            names = list(filter_name(obj.names))

            if len(names) == 0:
                continue

            try:
                variant = next(filter_variant(obj.names))
                l_logger.debug('variant chosen from names {}'.format(obj.names))
            except StopIteration:
                l_logger.debug('assume all-electron, variant chosen from Z')
                variant = 'q{}'.format(SYMB_TO_Z[obj.symbol])  # assume all-electron!

            l_logger.info('adding {} to {} with variant {} (from {})'.format(
                repr(obj), repr(names), variant, obj.source))

            # check for pseudo
            if type(obj) is AtomicPseudopotentialVariant:
                s_variant = 'q{}'.format(sum(obj.nelec))
                if variant != s_variant:
                    l_logger.warn('variant is {}, but sum of valence electrons indicate that it should be {}'.format(
                        variant, s_variant))

            for name in names:
                names_added.add(name)

                self._update(obj, name, variant)

        if add_metadata:
            for name in names_added:
                l_logger.info('add metadata to {}'.format(name))
                add_metadata(self.families[name])

                if 'tags' in self.families[name].metadata:
                    self.tags_per_family[name] = self.families[name].metadata['tags']

    def _update(self, obj: BaseAtomicVariantDataObject, name: str, variant: str):

        symbol = obj.symbol

        if name not in self.families:
            self.families[name] = self.object_type(name)
            self.elements_per_family[name] = []

        self.families[name].add(obj, variant)
        self.elements_per_family[name].append(symbol)

    def __repr__(self):
        return '<Storage({})>'.format(repr(self.name))

    def __getitem__(self, item: str) -> BaseFamilyStorage:
        return self.families[item]

    def __contains__(self, item: str) -> bool:
        return item in self.families

    def __iter__(self) -> Iterable[str]:
        yield from self.families.keys()

    def values(self) -> Iterable[BaseFamilyStorage]:
        """Yield all `BaseFamilyStorage`"""
        yield from self.families.values()

    def tree(self, out=sys.stdout):
        """Print a tree"""
        print('*\n|\n+- {}\n   |'.format(self.name), file=out)
        for family in self.families.values():
            family.tree(out)

    def get_names(self, elements: ElementSet, search_name: str = '', search_tags: str = '') -> List[str]:
        """Get all defined names, eventually restricted to a subset of elements
        """

        if search_name:
            search_name = search_name.lower()

        names_list = []
        for name in self:
            if not search_tags or (name in self.tags_per_family and search_tags in self.tags_per_family[name]):
                if not search_name or search_name in name.lower():
                    if not elements or elements <= ElementSet(SYMB_TO_Z[i] for i in self.elements_per_family[name]):
                        names_list.append(name)

        return names_list

    def dump_hdf5(self, f: h5py.File):
        main_group = f.require_group(self.name)

        for key, data_object in self.families.items():
            data_object.dump_hdf5(main_group.require_group(key))

    @classmethod
    def read_hdf5(cls, f: h5py.File):
        main_group = f[cls.name]
        obj = cls()

        obj.date_build = f.attrs.get('date_build', None)

        for key, group in main_group.items():
            for obj_variant, variant in obj.object_type.iter_hdf5_variants(group):
                obj._update(obj_variant, key, variant)

            # add metadata
            obj.families[key].metadata = BaseFamilyStorage._read_metadata_hdf5(group)

            if 'tags' in obj.families[key].metadata:
                obj.tags_per_family[key] = obj.families[key].metadata['tags']

        return obj


class Filter:
    """Filter a list of string based on a set of rules of the form `(pattern, replacement)`, where
    `pattern` is a valid `re.Pattern` and `replacement` is a replacement value.

    For each element in the list, iter on all rules. If a pattern matches, then:
    + if its replacement is `None`, the element is discarded, or
    + `pattern.sub(replacement, element)` is yield instead.

    If there is no match after all the rules have been tried, then the value is also discarded.
    If you want to avoid this behavior, add a dummy rule at the end: `(re.compile(r'(.*)'), '\\1')`.
    """

    def __init__(self, rules: List[Tuple[re.Pattern, Union[str, None]]] = None):
        self.rules = rules if rules else []

    @classmethod
    def create(cls, filter_def: Dict[str, Union[str, None]]):
        rules = []
        if filter_def:
            for pattern, replacement in filter_def.items():
                rules.append((re.compile(pattern), replacement))

        return cls(rules)

    def __call__(self, iterable: Iterator[str]) -> Iterator[str]:
        for element in iterable:
            for rule_pattern, value in self.rules:
                if rule_pattern.match(element):
                    if value is not None:
                        yield rule_pattern.sub(value, element)
                    break


class FilterFirst(Filter):
    """Only get 1 or 0 result"""

    def __call__(self, iterable: Iterator[str]) -> Iterator[str]:
        try:
            yield next(super().__call__(iterable))
        except StopIteration:
            return


class FilterUnique(Filter):
    """Remove duplicate
    """

    def __call__(self, iterable: Iterator[str]) -> Iterator[str]:
        yield from more_itertools.unique_everseen(super().__call__(iterable))


class AddMetadata:
    """Add a set of metadata to a `BaseFamilyStorage`, based on a set of rules of the form
    `[(pattern1, metadata1), (pattern1, metadata1), ...]`, where:

    + `pattern1`, `pattern2`, etc is a valid `re.Pattern`, to be matched against `BaseFamilyStorage.name`, and
    + `metadata1`, `metadata`, etc is the value that the metadata field will take if pattern is matched

    The first pattern that is matched gives its value.
    """

    def __init__(self, rules: List[Tuple[re.Pattern, Dict[str, Any]]] = None):
        self.rules = rules

    @classmethod
    def create(cls, rules_def: Dict[str, Dict[str, Any]]):
        rules = []

        if rules_def:
            for rule_pattern, values in rules_def.items():
                rules.append((re.compile(rule_pattern), values))

        return cls(rules)

    def __call__(self, family_storage: BaseFamilyStorage):
        name = family_storage.name
        if self.rules:
            metadata_value = None
            for rule in self.rules:
                rule_pattern, values = rule
                if rule_pattern.match(name):
                    metadata_value = values
                    break

            if metadata_value:
                family_storage.metadata = metadata_value
