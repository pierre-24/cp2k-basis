import re

import h5py

from typing import Dict, Iterable, Union, Any, List, Callable, Tuple, Iterator

import numpy

from cp2k_basis.elements import ElementSet, SYMB_TO_Z

string_dt = h5py.special_dtype(vlen=str)


class BaseAtomicVariantDataObject:
    def __init__(self, symbol: str, names: List[str]):
        self.symbol = symbol
        self.names = names

    def dump_hdf5(self, group: h5py.Group):
        """Dump in HDF5"""

        # dump names
        ds_names = group.create_dataset('names', shape=(len(self.names), ), dtype=string_dt)
        ds_names[:] = self.names

    def _read_info(self, group: h5py.Group, name_size: int):
        """Read names
        """

        ds_names = group['names']

        if ds_names.shape != (name_size, ):
            raise ValueError('Dataset `names` in {} must have length {}'.format(group.name, name_size))

        self.names = list(n.decode('utf8') for n in ds_names)

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

    def __str__(self) -> str:
        return ''.join(str(bs) for bs in self.variants.values())

    def __getitem__(self, item: str) -> BaseAtomicVariantDataObject:
        return self.variants[item]

    def __contains__(self, item: str) -> bool:
        return item in self.variants

    def __iter__(self) -> Iterable[str]:
        yield from self.variants.keys()

    def dump_hdf5(self, group: h5py.Group):
        """Dump in HDF5"""

        for key, data in self.variants.items():
            subgroup = group.create_group(key)
            data.dump_hdf5(subgroup)

    @classmethod
    def iter_hdf5_variants(cls, symbol: str, group: h5py.Group) -> Iterable[BaseAtomicVariantDataObject]:
        """Yield a set of variant for a given symbol"""

        for key, variant_group in group.items():
            yield cls.object_type.read_hdf5(symbol, variant_group)


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
            self.data_objects[obj.symbol] = self.object_type(obj.symbol, self.name)

        self.data_objects[obj.symbol].add(obj, variant)

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
            if type(values) == numpy.ndarray:
                metadata[key] = list(values)
            else:
                metadata[key] = values

        return metadata

    @classmethod
    def iter_hdf5_variants(cls, group: h5py.Group) -> Iterable[BaseAtomicVariantDataObject]:
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
        self.families_per_element: Dict[str, List[str]] = {}
        self.elements_per_family: Dict[str, List[str]] = {}

    def update(
        self,
        data_objects: Iterable[BaseAtomicVariantDataObject],
        filter_name: Union[Callable[[Iterable[str]], Iterable[str]], 'FilterName'] = lambda x: x,
        add_metadata: Callable[[BaseFamilyStorage], None] = None
    ):
        for obj in data_objects:

            # prepare reverse
            symbol = obj.symbol
            if symbol not in self.families_per_element:
                self.families_per_element[symbol] = []

            # add to storage & reverse
            names = list(filter_name(obj.names))  # TODO: family name
            variant = 'q0'  # TODO: variant

            for name in names:
                if name not in self.families:
                    self.families[name] = self.object_type(name)
                    self.elements_per_family[name] = []
                    if add_metadata:
                        add_metadata(self.families[name])

                self.families[name].add(obj, variant)
                self.elements_per_family[name].append(symbol)
                self.families_per_element[symbol].append(name)

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

    def get_names_for_elements(self, elements: ElementSet) -> List[str]:
        """Get all defined names, eventually restricted to a subset of elements
        """

        names_list = []
        if not elements:
            names_list = list(self)
        else:
            for name in self:
                if elements <= ElementSet(SYMB_TO_Z[i] for i in self.elements_per_family[name]):
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

        for key, group in main_group.items():
            obj.update(obj.object_type.iter_hdf5_variants(group), lambda x: [key])

            # add metadata
            obj.families[key].metadata = BaseFamilyStorage._read_metadata_hdf5(group)

        return obj


class FilterName:
    """Curate a list of name based on a set of rules of the form `(pattern, replacement)`, where `pattern` is a valid
    `re.Pattern`.

    If a pattern matches, then its `replacement` is yield instead.
    If `replacement` is empty, then the name is simply discarded.
    """

    def __init__(self, rules: List[Tuple[re.Pattern, str]]):
        self.rules = rules

    def __call__(self, names: Iterator[str]) -> Iterator[str]:
        for name in names:
            matched = False
            for rule_pattern, value in self.rules:
                if rule_pattern.match(name):
                    if len(value) != 0:
                        yield rule_pattern.sub(value, name)
                    matched = True
                    break

            if not matched:
                yield name


class AddMetadata:
    """Add a set of metadata to a `BaseFamilyStorage`, based on a set of rules of the form
    `{'name1': [(pattern1, value1), (pattern2, value2)], 'name2': [...], ...}`, where:

    + `name1`, `name2`, etc is the name of the metadata,
    + `pattern1`, `pattern2`, etc is a valid `re.Pattern`, to be matched against `BaseFamilyStorage.name`, and
    + `value1`, `value2`, etc is the value the metadata will take if pattern is matched

    The first pattern that is matched gives its value to the metadata.
    If no pattern is matched, then the metadata is not added.
    """

    def __init__(self, rules: Dict[str, List[Tuple[re.Pattern, str]]]):
        self.rules = rules

    def __call__(self, family_storage: BaseFamilyStorage):
        name = family_storage.name

        for key, rules_set in self.rules.items():
            metadata_value = None
            for rule_pattern, rule_value in rules_set:
                if rule_pattern.match(name):
                    metadata_value = rule_value
                    break

            if metadata_value:
                family_storage.metadata[key] = metadata_value
