"""
This is an example on how to use `cp2k_basis` to read the library and play with it.
"""

import h5py

from cp2k_basis.basis_set import BasisSetsStorage
from cp2k_basis.pseudopotential import PseudopotentialsStorage

# read from H5 file
with h5py.File('library.h5') as f:
    bs_storage = BasisSetsStorage().read_hdf5(f)
    pp_storage = PseudopotentialsStorage.read_hdf5(f)

# list available basis sets
print(', '.join(name for name in bs_storage))

# print whole basis set
basis_set = 'DZV-ALL'
assert basis_set in bs_storage

print(bs_storage[basis_set])

# available elements for a given potential
family_name = 'GTH-BLYP'
assert family_name in pp_storage

print(', '.join(element for element in pp_storage[family_name]))

# available variants
elmt = 'C'
assert elmt in pp_storage[family_name]
print(list(variant for variant in pp_storage[family_name][elmt]))

# print pseudopotential for C (q4 variant) in GTH-BLYP
variant = 'q4'
assert variant in pp_storage[family_name][elmt]
print(pp_storage[family_name][elmt][variant])