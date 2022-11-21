# `library.h5` file format

The basis set library root contains at least two groups: `basis_sets` and `pseudopotentials`.
They are detailed below.

## The `basis_sets` group

This group contains one subgroup per atom (the `atom` group), named by its symbol.
In each `atom` group, there is one subgroup for each basis set (the `basis set` group).
Thus, the following structure is valid:

```
basis_sets/
|- C/
|  |- SZV-MOLOPT-GTH/
|  |- SZV-MOLOPT-GTH/
|  |- DZVP-MOLOPT-GTH/
|  |- ...
|- H/
   |- SZV-MOLOPT-GTH/
   |- SZV-MOLOPT-GTH/
   |- DZVP-MOLOPT-GTH/
   |- ...
```

Each `basis set` group is composed of the following datasets:
- `info`, which is of shape `(2,)` and contains `(len(names), len(contractions))`, for checking purposes
- `names`, which contains the various name of this basis set and which length should match the one give in the `info` dataset
- For each contraction `i` (`i in range(nfunc)`), two datasets
  - `contraction_{i}_info`, of shape `(4 + n,)` which contains `(principle_n, l_min, l_max, nfunc, nshell[0], ..., nshell[n-1])`.
     `n`, the number of shells, is to be found as attribute `nshell` of this dataset.
  - `contraction_{}_exp_coefs`, of shape `(nfunc, n+1)`, which contains the exponents are in `[:, 0]`, while the coefficients are found in `[:, 1:]`.

Thus, the following structure, e.g., is valid:

```
basis_sets/C/TZVP-GTH/      # contains two contractions
|- info                     # contains (2, 2)
|- names                    # contains (TZVP-GTH-q4, TZVP-GTH)
|- contraction_0_info       # contains (2, 0, 1, 5, 3, 3)
|- contraction_0_exp_coefs  # of shape (5, 7)
|- contraction_1_info       # contains (3, 2, 2, 1, 1)
|- contraction_1_exp_coefs  # of shape (1, 2)
```