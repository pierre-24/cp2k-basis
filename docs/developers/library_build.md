# Building, using and improving the library

This page describes how to manipulate the library of basis sets and pseudopotentials.

!!! info
    If you want to know how the basis sets and pseudopotentials are actually stored in the file, [check out this page](library_file_format.md).


## Building the library (with `cb_fetch_data`)

!!! info
    The current library and the source YAML file are available [here](https://github.com/pierre-24/cp2k-basis/tree/master/library).

### Creating a library from the YAML source file

From an existing YAML source file `DATA_SOURCE.yml` with the format described below, just use

```bash
cb_fetch_data DATA_SOURCES.yml -o library.h5
```

This will create a [`library.h5` file](library_file_format.md), which might be exploited [latter on](#using-the-library).

If you want to have insight on what is happening, you might want to use:

```bash
LOGLEVEL=INFO cb_fetch_data DATA_SOURCES.yml -o library.h5
```

which is more verbose.

### YAML source file format

#### Repositories
 
Building the library requires a YAML file which describe all the sources for the basis sets and pseudopotentials .
It is composed of a list of repositories, for which the general structure is:

```yaml
--- List of repositories
- base: <URL1>
  data:  # dictionary of keywords (optional)
  files: # list of files (mandatory)
- base: <URL2>
# (...)
```

Each of the item of the list describe a repository. 
A repository is thus defined by a base url (`base`), which is a template.
Keyword inside curly braces will be replaced by their value given in the `keyword` dictionary (following the [Python `format()` syntax](https://docs.python.org/3/library/string.html#format-string-syntax)).

??? example
    With:

    ```yaml
    - base: https://github.com/cp2k/cp2k/raw/{commit}/data/
      data:
        commit: '786bc82ff9ded3e1f761cba6d8e25c3c9fe19bb1'
    ```
    
    the base URL will be `https://github.com/cp2k/cp2k/raw/786bc82ff9ded3e1f761cba6d8e25c3c9fe19bb1/data/`.

Finally, each repository has different files (listed `files`).

#### Files

Each file is described using the following structure:

```yaml
name: <NAME>
type: BASIS_SETS
family_name:  # dictionary (mandatory)
variant:  # dictionary (mandatory)
metadata: # dictionary (optional)
```

Each file has a `name` and a type linked to its content, which is either `BASIS_SETS` or `POTENTIALS`.
While gathering the file, `cb_fetch_data` will download it from `<BASE_URL>/<NAME>`. 

??? example
    From the following structure:
    
    ```yaml
    - base: https://github.com/cp2k/cp2k/raw/{commit}/data/
      data:
        commit: '786bc82ff9ded3e1f761cba6d8e25c3c9fe19bb1'
      files:
        - name: BASIS_MOLOPT
          type: BASIS_SETS
    ```
    
    The URL <https://github.com/cp2k/cp2k/raw/786bc82ff9ded3e1f761cba6d8e25c3c9fe19bb1/data/BASIS_MOLOPT> will be used to fetch the file.

!!! note
    It is possible to apply a patch (in the [unified `diff` format](https://www.gnu.org/software/diffutils/manual/html_node/Unified-Format.html)) by adding a `patch` option, whose value should be a path (relative to the directory where the YAML file is) to a patch file.
    This is useful to correct small inconsistencies or mistake.

#### Sorting out the content of the file

As you can see if you check out a file in the [CP2K `data/` folder](https://github.com/cp2k/cp2k/tree/786bc82ff9ded3e1f761cba6d8e25c3c9fe19bb1/data), each file contains different basis sets (or pseudopotential) for different atom, so one should help  `cb_fetch_data` to sort out everything.

There are definition for each atom, followed by nicknames which indicates which basis set/pseudopotential this is.
There may be multiple nickname, though there is usually two, of the form `<name> <name>-qX`, where `<name>` is the family name and the `-qX` variant indicate [the number of valence electrons](../users/basis_sets_and_pseudos.md#pairing-gth-pseudopotentials-with-basis-sets).

??? example
    In, e.g., [`BASIS_MOLOPT`](https://github.com/cp2k/cp2k/raw/786bc82ff9ded3e1f761cba6d8e25c3c9fe19bb1/data/BASIS_MOLOPT), one has:
    
    ```text
    H  SZV-MOLOPT-GTH SZV-MOLOPT-GTH-q1
    # ...
    H  DZVP-MOLOPT-GTH DZVP-MOLOPT-GTH-q1
    # ...
    H  TZVP-MOLOPT-GTH TZVP-MOLOPT-GTH-q1
    # ...
    C  SZV-MOLOPT-GTH SZV-MOLOPT-GTH-q4
    # ...
    ```

From the nicknames `cb_fetch_data` should figure out in which family (i.e., the basis set or pseudopotential) it will store this definition.
Since the naming is not systematic (not always of the form `<name>-qX`), one has to resort to a heavier tool which can show some flexibility.
Thus, this is performed thanks to the `family_name` dictionary, which contains a REGEX as the key and a replacement as the value.
All the nickname are checked against the REGEX, in the order given in the file.

- If a REGEX matches, then the search stops and:
  - If the replacement is `~` (the `null` value in YAML), the name is discarted
  - Otherwise, the replacement is yield, using `pattern.replace(name, replacement)`
- If at the end, no REGEX matches, the name is just discarded.

??? example
    With:

    ```yaml
    - base: https://github.com/cp2k/cp2k/raw/{commit}/data/
      data:
        commit: '786bc82ff9ded3e1f761cba6d8e25c3c9fe19bb1'
      files:
        - name: BASIS_MOLOPT
          type: BASIS_SETS
          family_name:
            '^(.*)(-q\d{1,2})$': '\1'
    ```

    `cb_fetch_data` will apply the REGEX to every nickname, and will end up with a list of family names. 
    With `SZV-MOLOPT-GTH SZV-MOLOPT-GTH-q1`, the result will be in both cases `SZV-MOLOPT-GTH`.

Then, the `variant` dictionary is used to determine the variant (i.e., the number of valence electron, in the form `qXX`) from the nicknames.
The rules are the same as with `family_name`, but only the **first** result will be used.

??? example
    With:

    ```yaml
    - base: https://github.com/cp2k/cp2k/raw/{commit}/data/
      data:
        commit: '786bc82ff9ded3e1f761cba6d8e25c3c9fe19bb1'
      files:
        - name: BASIS_MOLOPT
          type: BASIS_SETS
          variant:
            '^.*-(q\d{1,2})$': '\1'
    ```

    `cb_fetch_data` will apply the REGEX to every nickname, and will take **the first** result.
    With `SZV-MOLOPT-GTH SZV-MOLOPT-GTH-q1`, the first nickname yield no result, while the second yield `q1`, which will be used.

#### Adding metadata to the families

Finaly, `cb_fetch_data`, it will add metadata to those families.
To do so, the `metdata` dictionary will be used, with the key being name of the metadata and the value being a key(REGEX)-value dictionary, which again allow for some flexibility.
This time, the **family name** (not the nicknames) will be matched against each key, and if there is a match, this value will be used for the metadata.
Note that in this case, there is no replacement, the bare value is used.

??? example
    With:

    ```yaml
    - base: https://github.com/cp2k/cp2k/raw/{commit}/data/
      data:
        commit: '786bc82ff9ded3e1f761cba6d8e25c3c9fe19bb1'
      files:
        - name: BASIS_MOLOPT
          type: BASIS_SETS
          metadata:
            references:
              '.*': [https://github.com/cp2k/cp2k-data]
            description:
              '^SZV-MOLOPT-GTH$': A double zeta basis set
              '.*': MOLOPT basis set.
    ```
    
    For the basis set `SZV-MOLOPT-GTH`, the metadata will contain two fields: `references` and `description` (which will contain "A double zeta basis set")
    For the basis set `DZVP-MOLOPT-GTH` (or any other basis, thanks to the use of `.*`), the fields in the metadata will be the same, but the value of `description` is different ("MOLOPT basis set.").

For the moment, `references` and `description` are the two metadata reported for every basis set and pseudopotential.

## Using the library

Currently, the web interface is the only way to query the library.

However, you can have a quick overview of the content of the library using:

```bash
cb_explore_library library.h5
```

You can also use the [Python `cp2k_basis` library](https://github.com/pierre-24/cp2k-basis/tree/master/cp2k_basis).

!!! example
    See [there](https://github.com/pierre-24/cp2k-basis/tree/master/library/example.py) for some of Python code to access the library and query its content.

## Improving the library

To improve the library, it might be easier to work directly with the file in question.
This is possible with the `cb_explore_file` command.

### An example: adding `BASIS_MOLOPT_UCL`

[Issue #6](https://github.com/pierre-24/cp2k-basis/issues/6) requested the addtion of [`BASIS_MOLOPT_UCL`](https://github.com/cp2k/cp2k/blob/master/data/BASIS_MOLOPT_UCL) to the library.
This will be used as an example.

First of all, download the file (notice the `/raw/`):

```bash
wget https://github.com/cp2k/cp2k/raw/master/data/BASIS_MOLOPT_UCL
```

Then create a `source.yml` file:

```bash
touch source.yml
```

This file will follow the same syntax as the one described above [for files](#files), so the following skeleton can be used

```yaml
- name: BASIS_MOLOPT_UCL
  type: BASIS_SETS
  family_name:
  variant:
  metadata:
```

You can now run `cb_explore_file` ... But nothing much happens:

```text
$ cb_explore_file source.yml
*
|
+- basis_sets
   |
*
|
+- pseudopotentials
   |
```

This is normal: as described [above](#sorting-out-the-content-of-the-file), if no rule matches the nickname, they are just discarded.
This is the case here, since there is no rule.
Hopefully, the solution in this case is pretty straightforward: the name can be easily extracted from nicknames such as `TZVP-MOLOPT-SR-GTH-q3`, and so is the variant.

??? example
    With the following `source.yml`,
    ```yaml
    - name: BASIS_MOLOPT_UCL
      type: BASIS_SETS
      family_name:
        '^(.*)(-q\d{1,2})$': '\1'
      variant:
        '^.*-(q\d{1,2})$': '\1'
      metadata:    
    ```
    
    The result is better:

    ```text
    $ cb_explore_file source.yml 
    *
    |
    +- basis_sets
       |
       +- TZVP-MOLOPT-SR-GTH
       |  metadata={'source': 'BASIS_MOLOPT_UCL'}
       |  |
       |  +- Li: q3
       |  +- Be: q4
       (...)
    ```
    
    The following basis sets were extracted:
    
    ```text
    $ cb_explore_file source.yml | grep "   +-" 
       +- TZVP-MOLOPT-SR-GTH
       +- TZV2P-MOLOPT-SR-GTH
       +- DZVPd-MOLOPT-SR-GTH
       +- TZVPd-MOLOPT-SR-GTH
       +- TZV2Pd-MOLOPT-SR-GTH
       +- SZV-MOLOPT-SR-GTH
       +- DZVP-MOLOPT-SR-GTH
       +- SZV-MOLOPT-GTH
       +- DZVP-MOLOPT-GTH
       +- TZVP-MOLOPT-GTH
       +- TZV2P-MOLOPT-GTH
       +- TZV2PX-MOLOPT-GTH
       +- DZV-MOLOPT-SR-GTH
    ```

Now you just need to add the metadata and iterate on the result until you are happy.

??? example
    With the following `source.yml`,
    ```yaml
    - name: BASIS_MOLOPT_UCL
      type: BASIS_SETS
      family_name:
        '^(.*)(-q\d{1,2})$': '\1'
      variant:
        '^.*-(q\d{1,2})$': '\1'
      metadata:
        references:
          '.*': [ https://github.com/cp2k/cp2k-data ]
        description:
          'TZVP-MOLOPT-SR-GTH': Short-range triple zeta (+ polarization) basis set.
          '.*': MOLOPT basis set 
    ```
    
    Metadata were added to the basis sets:
    
    ```text
    $ cb_explore_file source.yml 
    *
    |
    +- basis_sets
       |
       +- TZVP-MOLOPT-SR-GTH
       |  metadata={'references': ['https://github.com/cp2k/cp2k-data'], 'description': 'Short-range triple zeta (+ polarization) basis set.', 'source': 'BASIS_MOLOPT_UCL'}
       |  |
       |  +- Li: q3
       |  +- Be: q4
       (...)
       +- TZV2P-MOLOPT-SR-GTH
       |  metadata={'references': ['https://github.com/cp2k/cp2k-data'], 'description': 'MOLOPT basis set', 'source': 'BASIS_MOLOPT_UCL'}
       |  +- Li: q3
       (...)
    ```

When you are happy with the result (one can do better than that!), you can add it to the main [`DATA_SOURCES.yml`](https://github.com/pierre-24/cp2k-basis/blob/dev/library/DATA_SOURCES.yml) and do a pull request (see, e.g., [there](https://github.com/pierre-24/cp2k-basis/pull/11))!