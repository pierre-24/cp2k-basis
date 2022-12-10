# On basis sets and GTH pseudopotentials in CP2K

## Basis sets

Solving the Schrödinger equation generally resort to the use of the LCAO (*linear combination of atomic orbitals*) approximation.
For computational reasons, while STO (slater-type orbitals, $\propto e^{r}$) should be used, GTO (gaussian type orbitals) are preferred.

### Basis functions

The expression of a spherical primitive GTO centered in $\mathbf A$ is given by:

$$g_{u,\ell m}(\mathbf A, \mathbf r) = |\mathbf r|^\ell\,e^{-\alpha_u (\mathbf r-\mathbf A)^2}\,Y_{\ell m}(\mathbf r - \mathbf A),$$

where $\alpha_u$ is **the exponent** and $Y_{\ell m}$ is a [spherical harmonic](https://en.wikipedia.org/wiki/Spherical_harmonics) ($\ell$ is the angular momentum and $m\in[-\ell,\ell]$).
Generally, an atomic orbital $\psi_{\ell m}$, also called a **basis function**, is given by a set of contracted primitives:

$$\psi_{\ell m} (\mathbf A, \mathbf r) = \sum_u d_u\,g_{u,\ell m}(\mathbf A, \mathbf r),$$

where $d_u$ form a set of **contraction coefficients**.

In CP2K (as in other quantum chemistry programs), basis sets are defined by a set of contractions, each for a given shell $\ell$ (s-type, p-type, d-type, etc) containing primitives (so a list of exponents and their corresponding contraction coefficients).
The same coefficients and exponents are used for each atomic orbital in a shell (i.e., each possible value of $m$).

!!! note "But basis function can be grouped!"
    Some basis functions (even with different $\ell$) may be grouped to share the same exponent. 

    This is the case, e.g., in the (in)famous STO-3G (3 gaussians for each basis function) in which so-called "SP" basis functions are found, defined by using a common exponent but different contraction coefficient for each of the 3 gaussians defining the actual s-type and p-type basis function.
    
    MOLOPT basis sets (see below) are built on this principle.

### Improving the basis set by adding more basis functions

Multiple-$\zeta$ basis sets use $\zeta$ basis functions for each atomic orbitals in the atom. 
For example, double-$\zeta$ basis sets use two basis function for each atomic orbital (e.g., a total of 10 basis function for the carbon).
They may be grouped to share the same exponent, or not.

On top of that, two other kind of basis function might be added:

1. *polarization functions*, which have a larger angular momentum than those of the ground state of the atom (e.g., d-type basis functions for the carbon), and
2. *diffuse functions*, which have very small exponents (corresponding to very "large" gaussians).

Thus, the number of basis function for a given atom is very different from one basis set to the other.

!!! note
    One way to ease the communication is to report, for each shell, the number of primitives (uncontracted set) and the number of basis functions (contracted set) in the form `(uncontracted set)`, `[contracted set]`.
    
    For example, in a double-zeta basis set defined by 3 gaussian per basis function, the result would be `(12s,6p)` and `[3s,2p]`. 
    The form `[12s6p|3s2p]` is also found, and reported by the webserver.

## Pseudopotentials

See <https://journals.aps.org/prb/abstract/10.1103/PhysRevB.54.1703>, <https://journals.aps.org/prb/abstract/10.1103/PhysRevB.58.3641>, <http://www.physics.metu.edu.tr/~hande/teaching/741-lectures/lecture-08.pdf>




To be continued, but:

+ Introduce both basis sets and pseudos;
+ Present the naming rule(s) of basis sets and pseudopontials;
+ Try to indicate which basis set goes with witch potential.
+ Parser?
