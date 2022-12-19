# The `library.h5` file format

!!! info
    A library file is in the [HDF5 format](https://www.hdfgroup.org/solutions/hdf5/), which divide the data in groups (i.e., "folders") and datasets (i.e., "files"), the latter being array of data.
    Groups and datasets can have attributes.

The basis set library root contains at least two main (storage) groups: `basis_sets` and `pseudopotentials`.
They are detailed below.

## The `basis_sets` group

This group contains one subgroup per basis set (a `basis set` group), for which the name is the basis set name.
In each `basis set` group, there is one subgroup for each atom (a `atomic bs` group).
Finally, in that `atomic bs` subgroup, there is one `atomic bs variant` group for each variant.
Thus, the following structure is valid:

```
*
|
+- basis_sets/         # `basis_sets` group
   |
   +- SZV-MOLOPT-GTH/  # a `basis set` group
   |  |
   |  +- C/            # an `atomic bs` group
   |  |  |
   |  |  +- q4/        # an `atomic bs variant` group (see below)
   |  |
   |  +- H/
   |  |  |
   |  |  +- q1/
   |  |
   |  +- ...
   |
   +- DZVP-MOLOPT-GTH/
      |
      +- C/
      |  |
      |  +- q4/
      |
      +- H/
      |  |
      |  +- q1/
      |
      +- ...
```

Each `atomic bs variant` group is composed of the following datasets, which are all mandatory:

| Name                        | Shape                   | Attributes           | Info                                                                                              |
|-----------------------------|-------------------------|----------------------|---------------------------------------------------------------------------------------------------|
| `info`                      | `(2,)`                  | ---                  | contains `(len(names), len(contractions))`                                                        |
| `names`                     | `(n,)`                  | ---                  | contains `n=len(names)` names                                                                     |
| `contraction_{i}_info`      | `(4+n,)`                | `nshell` [mandatory] | contains `(principle_n, l_min, l_max, nfunc, nshell[0], ..., nshell[n-1])` with `n=attrs[nshell]` |
| `contraction_{i}_exp_coefs` | `(nfunc,1+sum(nshell))` | ---                  | contains exponents in `[:, 0]` and coefficients in `[:, 1:]`                                      |

The two last datasets are repeated with `i=[0:len(contractions)]`.

Thus, the following structure, e.g., is valid:

```
*
|
+ basis_sets/TZVP-GTH/C/q4/   # contains two contractions
  |
  +- info                     # contains (2, 2)
  +- names                    # contains (TZVP-GTH-q4, TZVP-GTH)
  +- contraction_0_info       # contains (2, 0, 1, 5, 3, 3)
  |                           # and has attribute nshell=2
  +- contraction_0_exp_coefs  # of shape (5, 7)
  +- contraction_1_info       # contains (3, 2, 2, 1, 1)
  |                           # and has attribute nshell=1
  +- contraction_1_exp_coefs  # of shape (1, 2)
```

## The `pseudopotentials` group

Again, this group contains one subgroup per pseudopotential familly (a `pp family` group), which name is the family name.
In each `pp family` group, there is one subgroup for each basis set (a `atomic pp` group).
Finally, in that `atomic pp` subgroup, there is one `atomic pp variant` group for each variant.

Thus, the following structure is valid:

```
*
|
+- pseudopotentials/   # the `pseudopotentials` group
   |
   +- GTH-BLYP/        # a `pp family group`
   |  |
   |  +- C/            # an `atomic pp` group
   |  |  |
   |  |  +- q4/        # an `atomic pp variant` group (see below)
   |  |
   |  +- H/
   |  |  |
   |  |  +- q1/
   |  |
   |  +- ...
   |
   +- GTH-PBE/
      |
      +- C/
      |  |
      |  +- q4/
      |
      +- ...
```

Each `atomic pp variant` group is composed of the following datasets, which are all mandatory:

| Name                           | Shape      | Attributes          | Info                                                                                                                                                                                      |
|--------------------------------|------------|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `info`                         | `(3+n,)`   | `nelec` [mandatory] | contains `(len(names), len(lcoefs), len(nlprojectors), nelec[0], ... nelec[n-1])` with `n=attrs[nelec]`                                                                                   |
| `names`                        | `(n,)`     | ---                 | contains `n=len(names)` names                                                                                                                                                             |
| `local_radius_coefs`           | `(1+n,)`   | ---                 | contains `(lradius, lcoef[0],..., lcoefs[n-1])` with `n=len(lcoefs)`                                                                                                                      |
| `nlprojector_{i}_radius_coefs` | `(1+n,)`   | `nfunc` [mandatory] | contains `(nlradius, nlcoefs[triu(n)[0]], ..., nlcoefs[triu(n)[n-1]])` with `n=attrs[nfunc]` and `triu(N)` gives the list of the upper triangular indices of a square matrix of size `N`. |

The last dataset is repeated with `i=[0:len(nlprojectors)]`.

The following structure, e.g., is valid:

```
*
|
+- pseudopotentials/GTH-BLYP/Ne/q8/
   |
   +- info                        # contains (2, 2, 2, 2, 6)
   |                              # and has attribute nelec=2
   +- names                       # contains (GTH-BLYP-q8, GTH-BLYP)
   +- local_radius_coefs          # of shape (3,)
   +- nlprojector_0_radius_coefs  # of shape (4,)
   |                              # and has attribute nfunc=2
   +- nlprojector_1_radius_coefs  # of shape (2,)
                                  # and has attribute nfunc=1
```

## Metadata

The file may have the `date_build` attribute, indicating when it was created.

Each `basis set` and `pp familly` group might also have the following attributes:

| Name          | Type    | Description                                                         |
|---------------|---------|---------------------------------------------------------------------|
| `description` | `str`   | Description of the data                                             |
| `references`  | `array` | One-dimensional array of URLs to reference papers (DOI) or sources. |
| `kind`        | `array` | One-dimensional array of kinds                                      |

Each `atomic bs variant` and `atomic pp variant` may present a `source` attribute which indicate the URL to the source of this variant.

Those attributes are optional.


