# About this project.

**TL;DR:** This project, develloped by [Pierre Beaujean](https://pierrebeaujean.net/), provides an easy way to select matching basis sets and GTH pseudopotentials for your CP2K calculation.
For the rest, go to the [basis set exchange](https://www.basissetexchange.org/) 😃

## What?

!!! info
    If you are not familiar with the concept of basis set and pseudopotentials, check out [this introduction](users/basis_sets_and_pseudos.md).

### Why CP2K?

[CP2K](https://www.cp2k.org/) is a quantum chemistry program that can perform atomistic simulations.
It is especially known for [mixing Gaussian and plane wave](https://www.cp2k.org/quickstep#gpw) approaches, which are useful to perform *ab initio* molecular dynamics, [among others](https://www.cp2k.org/features).

### Why this if there is the basis set exchange?

The [basis set exchange](https://www.basissetexchange.org/) (BSE), developed by [MolSSI](https://molssi.org/) is a trustworthy provider of basis sets and effective core potentials (ECP) since a long time ago. 
It even provides an output for CP2K. 
In fact, this project has no intention of replacing the BSE, and users should happily continue to use it to fetch ECP and all-electrons basis sets.

However, CP2K calculations [can also use a pair of matching GTH potentials and corresponding basis sets](users/basis_sets_and_pseudos.md), which are not available on the BSE.
This is actually one of the first thing you learn [when you try to use the CP2K program](https://www.cp2k.org/howto).
This is where this project is useful, by allowing the users to look through the library of available basis sets and pseudopotentials [with a web interface similar to the BSE](users/webserver.md).

Behind the scene, it also provides [a library](https://github.com/pierre-24/cp2k-basis/tree/master/cp2k_basis) to read, write and store CP2K basis sets and potentials.

### Alternatives?

+ The [official `cp2k-data` repository](https://github.com/cp2k/cp2k-data/), which might contain more up to date version of GTH potentials.
+ [This webpage](https://htmlpreview.github.io/?https://github.com/cp2k/cp2k-data/blob/master/potentials/Goedecker/index.html), which provide an easy way to explore the previous repository.
+ Other tools (related to input and output) are also listed [in the CP2K documentation](https://www.cp2k.org/tools).

## How?

For the moment, the basis sets and GTH pseudopotentials are taken from the [`/data` directory of the CP2K repository](https://github.com/cp2k/cp2k/tree/master/data).

This project is developed using [Python 3](https://python.org), [`numpy`](https://numpy.org/) and [`h5py`](https://www.h5py.org/) (for the storage).

The webserver is powered by [Flask 2](https://flask.palletsprojects.com/).

This documentation is built using [mkdocs](https://www.mkdocs.org/).

## Who?

My name is [Pierre Beaujean](https://pierrebeaujean.net), and I'm a Ph.D. in quantum chemistry from the [University of Namur](https://unamur.be) (Belgium).
I'm the main (and only) developer of this project, used in our lab.
I use CP2K in the frame of my post-doctoral research, and I developed this project for all the reasons listed above.

I'm happy to [welcome your contributions](developers/install.md#install-and-contribute)!