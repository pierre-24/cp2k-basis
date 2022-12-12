# On basis sets and GTH pseudopotentials in CP2K

For the latest CP2K review, see [https://dx.doi.org/10.1063%2F5.0007045](https://dx.doi.org/10.1063%2F5.0007045) (May 2020).

## Basis sets

Solving the Schrödinger equation generally resort to the use of the LCAO (*linear combination of atomic orbitals*) approximation.
For computational reasons, while STO (slater-type orbitals, $\propto e^{r}$) should be used, GTO (gaussian type orbitals, $\propto e^{r^2}$) are preferred.

### Basis functions

In CP2K (as in other quantum chemistry programs), **basis functions** (i.e., atomic orbitals) are defined as:

$$\psi_{i,\ell m} (\mathbf r) = R_{i,\ell}(\mathbf r)\,Y_{\ell m}(\theta,\phi),$$

where $R(r)$ is the radial part, and $Y_{\ell m}$ is a [spherical harmonic](https://en.wikipedia.org/wiki/Spherical_harmonics) ($\ell$ is the angular momentum and $m\in[-\ell,\ell]$) for the angular part.
A weighted sum of **primitives** (Gaussian functions) is used for this part:

$$R_{i,\ell}(r) = r^\ell\,\sum_{j} c_{ij}\,e^{-\alpha_j\,r^2},$$

where $\alpha_{j}$ is the **exponent**, while $c_{ij}$ is the corresponding **contraction coefficient**. 
The two numbers defines the primitive $j$ in the basis function $\psi_i$.

Thus, a basis sets is a library of contractions for each shell (s-type [$\ell=0$], p-type [$\ell=1$], d-type [$\ell=2$], etc) of a given atom, containing the definition of the primitives (so a list of exponents and their corresponding contraction coefficients).
Since the radial part is the same for each possible orbital in a shell (i.e., each possible value of $m$), this is sufficient to define a basis set.

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
2. *diffuse functions*, which have very small exponents (corresponding to very "large" Gaussian functions).

Thus, the number of basis function for a given atom is very different from one basis set to the other.

!!! note
    One way to ease the communication is to report, for each shell, the number of primitives (uncontracted set) in the form `(uncontracted set)`, and the number of basis functions (contracted set) in the form `[contracted set]`.
    
    For example, in a double-zeta basis set defined by 3 gaussian per basis function, the result for carbn would be `(12s,6p)` and `[3s,2p]`. 
    The form `[12s6p|3s2p]`, combining the two is also found.

## Pseudopotentials

CP2K notoriously use an auxiliary plane wave (PW) basis set to perform its calculation with the GPW and GAPW methods.
To perform a PW calculation, one needs to include all possible basis sets below a given threshold. 
Increasing this threshold will monotonously improve the quality of the result (and the length of the calculation).
However, area where the electron density is rapidly changing requires PW with small wavelengths/high energy to be well described (i.e., large Fourier components), so high threshold, which would make the calculation impossible in practice.

But the area where such changes are important are mostly located near the nuclei, "thanks" to the ionic potential $V(r) = - \frac{Z}{r}$.
Hopefully, core and valence shell are generally well (spatially and energetically) separated, and the core electrons are relatively unperturbed by the surrounding.
So the idea behind [pseudopotentials](https://en.wikipedia.org/wiki/Pseudopotential) is to replace the effect of the nuclei and the core electrons (which are considered *frozen*) by an effective potential, and the valence electrons basis functions by ones with fewer nodes (but with the same behavior outside the core region).
Pseudopotentials are built from reference atomic calculations, which allow to account for some relativistic effects if the reference is calculated with such methods.

$$V(r) = \sum_\ell |Y_{\ell m}\rangle V_\ell(r) \langle Y_{\ell m} |.$$


<https://www.cp2k.org/_media/events:2019_ghent:gpw.pdf>

To be continued, but:

+ Finish pseudos;
+ Present the naming rule(s) of basis sets and pseudopontials;
+ Try to indicate which basis set goes with witch potential.
+ Parser?
