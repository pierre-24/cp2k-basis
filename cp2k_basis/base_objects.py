import pathlib
import re

import h5py

from typing import Dict, Iterable, Union, Any, List, Callable, Tuple, Iterator

import numpy


string_dt = h5py.special_dtype(vlen=str)


class BaseAtomicDataObject:
    """Base atomic data object.
    """

    def __init__(self, symbol: str, names: List[str]):
        self.symbol = symbol
        self.names = names

    def dump_hdf5(self, group: h5py.Group):
        """Dump in HDF5"""

        # dump names
        ds_names = group.create_dataset('names', shape=(len(self.names), ), dtype=string_dt)
        ds_names[:] = self.names

    def _read_info(self, group: h5py.Group, name_size: int):

        ds_names = group['names']

        if ds_names.shape != (name_size, ):
            raise ValueError('Dataset `names` in {} must have length {}'.format(group.name, name_size))

        self.names = list(n.decode('utf8') for n in ds_names)

    @classmethod
    def read_hdf5(cls, symbol: str, group: h5py.Group) -> 'BaseAtomicDataObject':
        """Create from HDF5"""

        raise NotImplementedError()


class AtomicDataException(Exception):
    pass


class BaseFamilyStorage:
    """Base family storage, stores `AtomicDataObject` for a given family name.
    """

    object_type = BaseAtomicDataObject

    def __init__(self, name: str, metadata: Dict[str, Union[str, Any]] = None):
        self.name = name
        self.data_objects: Dict[str, BaseAtomicDataObject] = {}
        self.metadata = metadata if metadata else {}

    def add(self, obj: BaseAtomicDataObject):
        if type(obj) is not self.object_type:
            raise TypeError('`obj` must be of type {}'.format(self.object_type))

        if obj.symbol in self.data_objects:
            raise AtomicDataException('`{}` already exists for symbol {}'.format(self.name, obj.symbol))

        self.data_objects[obj.symbol] = obj

    def __str__(self) -> str:
        return ''.join(str(bs) for bs in self.data_objects.values())

    def __getitem__(self, item: str) -> BaseAtomicDataObject:
        return self.data_objects[item]

    def __contains__(self, item: str) -> bool:
        return item in self.data_objects

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

    @classmethod
    def read_hdf5(cls, group: h5py.Group) -> 'BaseFamilyStorage':
        """Extract from HDF5"""

        name = pathlib.Path(group.name).name
        o = cls(name)

        for key, basis_group in group.items():
            o.add(cls.object_type.read_hdf5(key, basis_group))

        for key, values in group.attrs.items():
            if type(values) == numpy.ndarray:
                o.metadata[key] = list(values)
            else:
                o.metadata[key] = values

        return o


class StorageException(Exception):
    pass


class Storage:
    """Stores `BaseFamilyStorage` for each possible family name.
    """

    object_type = BaseFamilyStorage
    name = 'base_storage'

    def __init__(self):
        self.families: Dict[str, BaseFamilyStorage] = {}
        self.families_per_atom: Dict[str, List[str]] = {}

    def update(
        self,
        data_objects: Iterable[BaseAtomicDataObject],
        filter_name: Union[Callable[[Iterable[str]], Iterable[str]], 'FilterName'] = lambda x: x,
        add_metadata: Callable[[BaseFamilyStorage], None] = None
    ):
        for obj in data_objects:

            # prepare reverse
            symbol = obj.symbol
            if symbol not in self.families_per_atom:
                self.families_per_atom[symbol] = []

            # add to storage & reverse
            names = list(filter_name(obj.names))

            for name in names:
                if name not in self.families:
                    self.families[name] = self.object_type(name)
                    if add_metadata:
                        add_metadata(self.families[name])

                self.families[name].add(obj)
                self.families_per_atom[symbol].append(name)

    def __repr__(self):
        return '<Storage({})>'.format(repr(self.name))

    def __getitem__(self, item: str) -> BaseFamilyStorage:
        return self.families[item]

    def __contains__(self, item: str) -> bool:
        return item in self.families

    def get_atomic_data_objects(self, family_name: str, atoms: List[str] = None) -> Iterable[BaseAtomicDataObject]:
        """Get a (sub)set of `AtomicDataObject` in a given family
        """

        if family_name not in self:
            raise StorageException('`{}` not in this storage'.format(family_name))

        if atoms is None:
            atoms = self[family_name].data_objects.keys()

        for atom in atoms:
            try:
                yield self[family_name][atom]
            except KeyError:
                raise StorageException('Atom {} does not exists for {}'.format(atom, family_name))

    def dump_hdf5(self, f: h5py.File):
        main_group = f.require_group(self.name)
        for key, data_object in self.families.items():
            data_object.dump_hdf5(main_group.require_group(key))

    @classmethod
    def read_hdf5(cls, f: h5py.File):
        main_group = f[cls.name]
        obj = cls()

        for key, group in main_group.items():
            family = obj.object_type.read_hdf5(group)

            # copy content
            obj.update(family.data_objects.values(), lambda x: [key])

            # copy metadata
            obj.families[key].metadata = family.metadata

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
