# REST API reference

!!! info
    A public API is available at `https://cp2k-basis.pierrebeaujean.net/api/`.

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
    (...)
  },
  "result": {
    (...)
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
        (...)
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

| Field             | Type           | Description                                                                                                 |
|-------------------|----------------|-------------------------------------------------------------------------------------------------------------|
| `query.type`      | string         | `BASIS_SET` or `PSEUDOPOTENTIAL`                                                                            |
| `query.name`      | string         | The name you requested                                                                                      |
| `query.elements`  | list of string | Value of the `elements` option, if provided                                                                 |
| `result.data`     | string         | The resulting basis set or pseudopotential, in CP2K format                                                  |
| `result.elements` | list of string | Elements for which there is data (matches the option `elements` if set)                                     |
| `result.variants` | dictionary     | For each element, dictionary containing all variants and the corresponding name to be used for such variant |
| `result.metadata` | dictionary     | Dictionary of metadata about this pseudopotential/basis set. See below for content.                         |

[Example](https://cp2k-basis.pierrebeaujean.net/api/basis/SZV-MOLOPT-SR-GTH/data?elements=Rh):

```bash
curl https://cp2k-basis.pierrebeaujean.net/api/basis/SZV-MOLOPT-SR-GTH/data?elements=Rh
```

```json
{
  "query": {
    "elements": [
      "Rh"
    ],
    "name": "SZV-MOLOPT-SR-GTH",
    "type": "BASIS_SET"
  },
  "result": {
    "data": "# URL: http://127.0.0.1:5000/api/basis/SZV-MOLOPT-SR-GTH/data?elements=Rh\n# DATETIME: 02/12/2022 @ 17:18\n# ---\n# Rh [12s6p6d|2s1p1d]\nRh  SZV-MOLOPT-SR-GTH SZV-MOLOPT-SR-GTH-q17\n1\n2 0 2 6 2 1 1\n  3.157817444361  0.760084070950  0.239207051701 -0.336193318541 -0.176446839307\n  2.683291075925 -0.255650224037 -0.091067207483  0.373953992584  0.261743358411\n  1.140786095845 -1.025626679377 -0.520689753906  0.300684698668  0.174717739794\n  0.492081007160 -0.234415477939 -0.274976137245  0.141457244144  0.188746290944\n  0.192543904978  0.046321838032  0.534686741279  0.007751787318  0.112894420897\n  0.066486620394  0.135748106274  0.896548625743  0.000117823467  0.021703317232\n# Rh [6s6p6d|1s1p1d]\nRh  SZV-MOLOPT-SR-GTH-q9\n1\n2 0 2 6 1 1 1\n  3.902721449032  0.016652865171 -0.008699428728 -0.112417659954\n  1.999830271997 -0.133395648426  0.046572987907  0.348017742874\n  0.879887627395  0.373099930807 -0.153463590375  0.381775351795\n  0.363794442257  0.298777744612 -0.052550610965  0.335875585916\n  0.140096726529 -0.924610879301  0.949493319446  0.146687236468\n  0.042562039477 -0.455102584336  0.423881871378  0.013082339937\n",
    "elements": [
      "Rh"
    ],
    "metadata": {
      "description": "A single zeta valence MOLOPT basis set, for solids (short-range, less diffuse basis functions) and GTH potentials.",
      "references": ["https://dx.doi.org/10.1063/1.2770708"],
      "source": "https://github.com/cp2k/cp2k/raw/786bc82ff9ded3e1f761cba6d8e25c3c9fe19bb1/data/BASIS_MOLOPT"
    },
    "variants": {
      "Rh": {
        "q17": "SZV-MOLOPT-SR-GTH-q17",
        "q9": "SZV-MOLOPT-SR-GTH-q9"
      }
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