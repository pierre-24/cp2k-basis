import pathlib
import h5py

from typing import Dict, Iterable, Union, Any, List, Callable

import numpy

try:
    from typing import Self
except ImportError:
    from typing import TypeVar
    Self = TypeVar('Self')


string_dt = h5py.special_dtype(vlen=str)


class BaseAtomicDataObject:
    """Base atomic data object.
    """

    def __init__(self, symbol: str, names: List[str], metadata: Dict[str, Union[str, Any]] = None):
        self.symbol = symbol
        self.names = names

        self.metadata = {}
        if metadata:
            self.metadata = metadata

    def dump_hdf5(self, group: h5py.Group):
        """Dump in HDF5"""

        # dump names
        ds_names = group.create_dataset('names', shape=(len(self.names), ), dtype=string_dt)
        ds_names[:] = self.names

        # dump info as attributes
        for key, value in self.metadata.items():
            if value:
                group.attrs[key] = value

    def _read_info(self, group: h5py.Group, name_size: int):

        ds_names = group['names']

        if ds_names.shape != (name_size, ):
            raise ValueError('Dataset `names` in {} must have length {}'.format(group.name, name_size))

        self.names = list(n.decode('utf8') for n in ds_names)

        for key, values in group.attrs.items():
            if type(values) == numpy.ndarray:
                self.metadata[key] = list(values)
            else:
                self.metadata[key] = values

    @classmethod
    def read_hdf5(cls, symbol: str, group: h5py.Group) -> Self:
        """Create from HDF5"""

        raise NotImplementedError()


class AtomicDataException(Exception):
    pass


class BaseAtomicStorage:
    """Base atomic storage, stores `AtomicDataObject` for a given atomic symbol.
    """

    object_type = BaseAtomicDataObject

    def __init__(self, symbol: str):
        self.symbol = symbol
        self.data_objects: Dict[str, BaseAtomicDataObject] = {}

    def add(self, obj: BaseAtomicDataObject, names: Iterable[str]):
        if type(obj) is not self.object_type:
            raise TypeError('`obj` must be of type {}'.format(self.object_type))

        for name in names:
            if name in self.data_objects:
                raise AtomicDataException('`{}` already exists for symbol {}'.format(name, self.symbol))

            self.data_objects[name] = obj

    def __str__(self) -> str:
        return ''.join(str(bs) for bs in self.data_objects.values())

    def dump_hdf5(self, group: h5py.Group):
        """Dump in HDF5"""

        for key, data in self.data_objects.items():
            # remove existing
            try:
                group.pop(key)
            except KeyError:
                pass

            # create new
            subgroup = group.create_group(key)
            data.dump_hdf5(subgroup)

    @classmethod
    def read_hdf5(cls, group: h5py.Group) -> Self:
        """Extract from HDF5"""

        symbol = pathlib.Path(group.name).name
        o = cls(symbol)

        for key, basis_group in group.items():
            o.add(cls.object_type.read_hdf5(symbol, basis_group), [key])

        return o


class Storage:
    """Stores `BaseAtomicStorage` for each possible atoms
    """

    object_type = BaseAtomicStorage

    def __init__(self, name: str):
        self.name = name
        self.atomic_storages: Dict[str, BaseAtomicStorage] = {}
        self.atoms_per_object_name: Dict[str, List[str]] = {}

    def update(
        self,
        data_objects: Iterable[BaseAtomicDataObject],
        filter_name: Callable[[Iterable[str]], Iterable[str]],
        add_metadata: Callable[[BaseAtomicDataObject], None]
    ):
        for obj in data_objects:
            symbol = obj.symbol

            # add to storages
            if symbol not in self.atomic_storages:
                self.atomic_storages[symbol] = self.object_type(symbol)

            add_metadata(obj)
            names = filter_name(obj.names)
            self.atomic_storages[symbol].add(obj, names)

            # add to reverse
            for name in names:
                if name not in self.atoms_per_object_name:
                    self.atoms_per_object_name[name] = []

                self.atoms_per_object_name[name].append(symbol)

    def __repr__(self):
        return '<Storage({})>'.format(self.name)

    def dump_hdf5(self, f: h5py.File):
        main_group = f.require_group(self.name)
        for key, data_object in self.atomic_storages.items():
            data_object.dump_hdf5(main_group.require_group(key))

    @classmethod
    def read_hdf5(cls, name: str, f: h5py.File):
        main_group = f[name]
        obj = cls(name)

        for key, group in main_group.items():
            storage = obj.object_type.read_hdf5(group)
            obj.atomic_storages[storage.symbol] = storage

        return obj
