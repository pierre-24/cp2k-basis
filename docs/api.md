# REST API reference

## Preamble

### Request

This API can be used to retrieve two types (`<type>`) of data, either basis sets (`basis`) or pseudopotentials (`pseudopotentials`).
Each of them has a name (`<name>`).

Options are added as query string: `/api/example?option1=value&option2=value`.

### On the `elements` option

Every time the option `elements` can be used,
+ you can use a list of comma separated atomic symbols, e.g., `C,H,N,O`,
+ but also ranges, e.g., `H,C-O`, and
+ Z numbers can be used instead of symbols, e,g., `H,6-8`.

Elements are limited to Z ≤ 92, i.e., hydrogen to uranium.
If you want to perform calculations outside this range, you probably have other problems on your plate than finding a basis set ;)


### Response format

The response is in JSON, and always contains two main fields:

```json
{
  "query": {
    "type": "TYPE",
    ...
  },
  "result": {
    ...
  }
}
```

`query` contains the request, to which `result` is the answer.
In the following, fields will be detailed using the syntax for object attributes in JS, e.g., `query.type`. 

## Routes

### `/api/data`

Get, for basis sets and pseudopotentials, which elements are defined, and for each element, which basis set/pseudopotentials are defined.
There is no option.

Output:

| Field                     | Type       | Description                                                                                                                                                                           |
|---------------------------|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `query.type`              | string     | Always `ALL`                                                                                                                                                                          |
| `result.basis_sets`       | dictionary | Contains two fields: `per_name`, which lists elements available for a given basis set, and `per_elements`, which lists all basis set names available for a given element.             |
| `result.pseudopotentials` | dictionary | Contains two fields: `per_name`, which lists elements available for a given pseudopotential, and `per_elements`, which lists all pseudopotential names available for a given element. |


[Example](https://cp2k-basis.pierrebeaujean.net/api/data):

```bash
curl https://cp2k-basis.pierrebeaujean.net/api/data
```

```json
{
  "query": {
    "type": "ALL"
  },
  "result": {
    "basis_sets": {
      "per_element": {
        "Ag": [
          "DZVP-MOLOPT-SR-GTH",
          "SZV-MOLOPT-SR-GTH"
        ],
        (...)
      },
      "per_name": {
        "DZV-GTH": [
          "H",
          "He"
        ],
        (...)
      }
    },
    "pseudopotentials": {
      "per_element": {
        "Ag": [
          "GTH-BLYP",
          "GTH-LDA",
          "GTH-PADE",
          "GTH-PBE"
        ],
        (...)
      },
      "per_name": {
        "GTH-BLYP": [
          "Ag",
          "Al",
          (...)
        ],
      }
    }
  }
}
```

### `/api/names`

List all available basis set and pseudopotential names available, eventually for a set of elements.

Options:

| Option     | Argument | Description                                  |
|------------|----------|----------------------------------------------|
| `elements` | String   | Restrict the output to a subset of elements. |

Output:

| Field                     | Type           | Description                                 |
|---------------------------|----------------|---------------------------------------------|
| `query.type`              | string         | Always `ALL`                                |
| `query.elements`          | list of string | Value of the `elements` option, if provided |
| `result.basis_sets`       | list of string | List of basis set names available           |
| `result.pseudopotentials` | list of string | List of pseudopotential names available     |

[Example](https://cp2k-basis.pierrebeaujean.net/api/names?elements=Ti):

```bash
curl https://cp2k-basis.pierrebeaujean.net/api/names?elements=Ti
```

```json
{
  "query": {
    "elements": [
      "Ti"
    ],
    "type": "ALL"
  },
  "result": {
    "basis_sets": [
      "DZVP-MOLOPT-SR-GTH",
      "SZV-MOLOPT-SR-GTH"
    ],
    "pseudopotentials": [
      "GTH-BLYP",
      "GTH-BP",
      "GTH-LDA",
      "GTH-PADE",
      "GTH-PBE"
    ]
  }
}
```

### `/api/<type>/<name>/data`

Obtain data in the CP2K format.

Options:

| Option     | Argument | Description                                                                                                                        |
|------------|----------|------------------------------------------------------------------------------------------------------------------------------------|
| `elements` | String   | Restrict the output to a subset of elements. If some elements are not defined for this basis set/pseudopotential, a 404 is raised. |
| `header`   | Boolean  | Add an header to `result.data` (default is true)                                                                                   |


Output:

| Field                    | Type           | Description                                                                                                           |
|--------------------------|----------------|-----------------------------------------------------------------------------------------------------------------------|
| `query.type`             | string         | `BASIS_SET` or `PSEUDOPOTENTIAL`                                                                                      |
| `query.name`             | string         | The name you requested                                                                                                |
| `query.elements`         | list of string | Value of the `elements` option, if provided                                                                           |
| `result.data`            | string         | The resulting basis set or pseudopotential, in CP2K format                                                            |
| `result.elements`        | list of string | Elements for which there is data (matches the option `elements` if set)                                               |
| `result.alternate_names` | dictionary     | For each element, list of alternate (generally of the form `<name>-qX` with `X` the number of valence electron) names |
| `result.metadata`        | dictionary     | Dictionary of metadata about this pseudopotential/basis set. See below for content.                                   |

[Example](https://cp2k-basis.pierrebeaujean.net/api/basis/DZVP-GTH/data?elements=H,C):

```bash
curl https://cp2k-basis.pierrebeaujean.net/api/basis/DZVP-GTH/data?elements=H,C
```

```json
{
  "query": {
    "elements": [
      "H",
      "C"
    ],
    "name": "DZVP-GTH",
    "type": "BASIS_SET"
  },
  "result": {
    "alternate_names": {
      "C": [
        "DZVP-GTH-q4"
      ],
      "H": [
        "DZVP-GTH-q1"
      ]
    },
    "data": "# URL: https://cp2k-basis.pierrebeaujean.net/api/basis/DZVP-GTH/data?elements=H,C\n# DATETIME: 01/12/2022 @ 12:36\n# ---\n# H [8s1p|2s1p]\n H  DZVP-GTH-q1 DZVP-GTH\n 2\n 1 0 0 4 2\n      8.374435000900 -0.028338046100  0.000000000000\n      1.805868146000 -0.133381005200  0.000000000000\n      0.485252832800 -0.399567606300  0.000000000000\n      0.165823693200 -0.553102754100  1.000000000000\n 2 1 1 1 1\n      0.727000000000  1.000000000000\n# C [8s8p1d|2s2p1d]\n C  DZVP-GTH-q4 DZVP-GTH\n 2\n 2 0 1 4 2 2\n      4.336237643600  0.149079787200  0.000000000000 -0.087812361900  0.000000000000\n      1.288183851300 -0.029264003100  0.000000000000 -0.277556030000  0.000000000000\n      0.403776714900 -0.688204051000  0.000000000000 -0.471229509300  0.000000000000\n      0.118787765700 -0.396442690600  1.000000000000 -0.405803929100  1.000000000000\n 3 2 2 1 1\n      0.550000000000  1.000000000000\n",
    "elements": [
      "H",
      "C"
    ],
    "metadata": {
      "description": "A double zeta valence (+ 1 set of polarization) basis set for GTH potentials.",
      "references": [
        "https://dx.doi.org/10.1016/j.cpc.2004.12.014"
      ],
      "source": "https://github.com/cp2k/cp2k/raw/786bc82ff9ded3e1f761cba6d8e25c3c9fe19bb1/data/GTH_BASIS_SETS"
    }
  }
}
```

### `/api/<type>/<name>/metadata`

Obtain metadata about a basis set or pseudopotential. There is no option.

Output:

| Field                | Type           | Description                                                  |
|----------------------|----------------|--------------------------------------------------------------|
| `query.type`         | string         | `BASIS_SET` or `PSEUDOPOTENTIAL`                             |
| `query.name`         | string         | The name you requested                                       |
| `result.elements`    | list of string | Elements for which the basis set/pseudopotential are defined |
| `result.description` | string         | Small description.                                           |
| `result.references`  | list of string | List of URL to articles or repositories                      |
| `result.source`      | string         | URL to the file which was used to create the data            |

[Example](https://cp2k-basis.pierrebeaujean.net/api/pseudopotentials/GTH-BLYP/metadata):

```bash
curl https://cp2k-basis.pierrebeaujean.net/api/pseudopotentials/GTH-BLYP/metadata
```

```json
{
  "query": {
    "name": "GTH-BLYP",
    "type": "PSEUDOPOTENTIAL"
  },
  "result": {
    "description": "GTH potentials for BLYP.",
    "elements": [
      "Ag",
      "Al",
      (...)
    ],
    "references": [
      "https://dx.doi.org/10.1103/PhysRevB.54.1703",
      "https://dx.doi.org/10.1103/PhysRevB.58.3641",
      "https://dx.doi.org/10.1007/s00214-005-0655-y",
      "https://github.com/cp2k/cp2k-data"
    ],
    "source": "https://github.com/cp2k/cp2k/raw/786bc82ff9ded3e1f761cba6d8e25c3c9fe19bb1/data/GTH_POTENTIALS"
  }
}
```