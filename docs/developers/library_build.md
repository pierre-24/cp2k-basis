# Building, using and improving the library


This page describes how to manipulate the library of basis sets and pseudopotentials.

!!! info
    If you want to know how the basis sets and pseudopotentials are actually stored in the file, [check out this page](library_file_format.md).


## Building

!!! info
    The current library and the source YAML file are available [here](https://github.com/pierre-24/cp2k-basis/tree/master/library).

To be continued, but

+ Describe properly the format of the YAML input;
+ Describe the `cb_fetch_data` command.

## Using

Currently, the web interface is the only way to query the library.

However, you can have a quick overview of the content of the library using:

```bash
cb_explore_library library.h5
```


## Improving

To be continued, but:

+ Describe how to use `cb_explore_file` tools.
+ Patching and stuffs