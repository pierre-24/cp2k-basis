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
|                           # and has attribute nshell=2
|- contraction_0_exp_coefs  # of shape (5, 7)
|- contraction_1_info       # contains (3, 2, 2, 1, 1)
|                           # and has attribute nshell=1
|- contraction_1_exp_coefs  # of shape (1, 2)
```


## The `pseudopotentials` group

Again, this group contains one subgroup per atom (the `atom` group), named by its symbol.
In each `atom` group, there is one subgroup for each basis set (the `pseudopotential` group).
Thus, the following structure is valid:

```
pseudopotentials/
|- C/
|  |- GTH-BLYP
|  |- GTH-PBE
|  |- ...
|- H/
   |- GTH-BLYP
   |- GTH-PBE
   |- ...
```

Each `pseudopotential` group is composed of the following datasets:

- `info`, of shape `(3 + n,)` and contains `(len(names), len(lcoefs), len(nlprojectors), nelec[0], ... nelec[n-1])`)
  where `n` is the number of shells, to be found as attribute `nshell` of this dataset.
- `names`, which contains the various name of this basis set and which length should match the one give in the `info` dataset.
- `local_radius_coefs`, which contains `(lradius, lcoef[0],..., lcoefs[m-1])`, where `m=len(lcoefs)` given in the first dataset.
- For each non local projector, `nlprojector_{i}_radius_coefs`, of shape `(1+p,)`, which contains `(nlradius, nlcoefs[triu(0)], ..., nlcoefs[triu(p-1)])`, 
  where `p` is the number of upper triangle indices, computed for the `nfunc` attribute of this dataset and `triu(i)` gives the triangular index `i`.

The following structure, e.g., is valid:

```
pseudopotentials/Ne/GTH-BLYP/
|- info                        # contains (2, 2, 2, 2, 6)
|                              # and has attribute nelec=2
|- names                       # contains (GTH-BLYP-q8, GTH-BLYP)
|- local_radius_coefs          # of shape (3,)
|- nlprojector_0_radius_coefs  # of shape (4,)
|                              # and has attribute nfunc=2
|- nlprojector_1_radius_coefs  # of shape (2,)
                               # and has attribute nfunc=1
```