# Library of basis sets and pseudopotentials

More info on basis sets and pseudopotentials in CP2K are available [here](../docs/basis_sets_and_pseudos.md).

Created from [`DATA_SOURCES.yml`](./DATA_SOURCES.yml), using:

```bash
# put LOGLEVEL=INFO in front of the command to follow its advance
cb_fetch_data ./DATA_SOURCES.yml -o library.h5
```

You can explore the content of the library using:

```bash
cb_explore_library library.h5
```
