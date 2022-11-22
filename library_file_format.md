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

Each `basis set` group is composed of the following datasets, which are all mandatory:

| Name                        | Shape                   | Attributes           | Info                                                                                              |
|-----------------------------|-------------------------|----------------------|---------------------------------------------------------------------------------------------------|
| `info`                      | `(2,)`                  | ---                  | contains `(len(names), len(contractions))`                                                        |
| `names`                     | `(n,)`                  | ---                  | contains `n=len(names)` names                                                                     |
| `contraction_{i}_info`      | `(4+n,)`                | `nshell` [mandatory] | contains `(principle_n, l_min, l_max, nfunc, nshell[0], ..., nshell[n-1])` with `n=attrs[nshell]` |
| `contraction_{i}_exp_coefs` | `(nfunc,1+sum(nshell))` | ---                  | contains exponents in `[:, 0]` and coefficients in `[:, 1:]`                                      |

The two last datasets are repeated with `i=[0:len(contractions)]`.

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

Each `basis set` group might have the following attributes:

+ `source`, which contains the URL to the original basis set, and
+ `references`, which contains a comma-separated list of DOI corresponding to the basis set.

Those two attributes are optional: if an attribute is missing, an empty value is assumed.

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

Each `pseudopotential` group is composed of the following datasets, which are all mandatory:

| Name                           | Shape      | Attributes           | Info                                                                                                                                                                                      |
|--------------------------------|------------|----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `info`                         | `(3+n,)`   | `nshell` [mandatory] | contains `(len(names), len(lcoefs), len(nlprojectors), nelec[0], ... nelec[n-1])` with `n=attrs[nshell]`                                                                                  |
| `names`                        | `(n,)`     | ---                  | contains `n=len(names)` names                                                                                                                                                             |
| `local_radius_coefs`           | `(1+n,)`   | ---                  | contains `(lradius, lcoef[0],..., lcoefs[n-1])` with `n=len(lcoefs)`                                                                                                                      |
| `nlprojector_{i}_radius_coefs` | `(1+n,)`   | `nfunc` [mandatory]  | contains `(nlradius, nlcoefs[triu(n)[0]], ..., nlcoefs[triu(n)[n-1]])` with `n=attrs[nfunc]` and `triu(N)` gives the list of the upper triangular indices of a square matrix of size `N`. |

The last dataset is repeated with `i=[0:len(nlprojectors)]`.

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

Each `pseudopotential` group might also have the `source` and `references` attributes, with the same definition as above.