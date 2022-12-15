# On basis sets and GTH pseudopotentials in CP2K

!!! info
    For the latest CP2K review, see [10.1063/5.0007045](https://dx.doi.org/10.1063/5.0007045) (May 2020).
    The GPW method is described, e.g., [here](https://www.cp2k.org/_media/events:2019_ghent:gpw.pdf).

## Basis sets

Solving the Schrödinger equation generally resort to the use of the LCAO (*linear combination of atomic orbitals*) approximation.
For computational reasons, while STO (slater-type orbitals, $\propto e^{r}$) should be used, GTO (gaussian type orbitals, $\propto e^{r^2}$) are preferred.

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

However, for reasons that will become clear in the next section, CP2K does not only use all-electron basis sets.

## GTH pseudopotentials

Indeed, CP2K is able use an auxiliary plane wave (PW) basis set to perform its calculation with the GPW (and GAPW) method.
To perform a such calculation, one needs to include all possible PW below a given threshold. 
In fact, increasing this threshold will monotonously improve the quality of the result (and the length of the calculation!).
However, area where the electron density is rapidly changing requires PW with small wavelengths/high energy to be well described (i.e., large Fourier components), so high threshold, which would make the calculation impossible in practice.
In practice, area where such changes are important are mostly located near the nuclei, "thanks" its ionic potential $V(r) = - \frac{Z}{r}$.

Hopefully, core and valence shell are generally well (spatially and energetically) separated, and core electrons are relatively unperturbed by the surrounding (chemically inert).

So the idea behind [pseudopotentials](https://en.wikipedia.org/wiki/Pseudopotential) is to replace the effect of the nuclei and the core electrons (which are considered *frozen*) by an effective potential (below a given threshold $r_c$), and the valence electrons basis functions by ones with fewer nodes (since they do not need to be orthogonal to the, now removed, valence orbital), but with the same behavior outside the core region (for $r > r_c$).

??? example  "Derivation of a pseudopotential"

    Say one has a set of  (orthogonal) core states $\{|\chi_n\rangle\}$ (with their corresponding eigenvalue $\{E_n\}$).
    The goal is to construct a pseudo-state $|\phi\rangle$ for a valence state $|\psi\rangle$ (with its corresponding eigenvalue $E$), in the form:
    
    $$|\psi\rangle = |\phi\rangle + \sum_n a_n |\chi_n\rangle.$$

    Since the core and valence state must be orthogonal, $\langle \chi_m | \psi \rangle = 0 = \langle \chi_m | \phi \rangle + a_m$, so that

    $$|\psi\rangle = |\phi\rangle - \sum_n |\chi_n\rangle \langle \chi_n | \phi\rangle.$$

    Substituting in Schrödinger equation for $|\psi\rangle$ gives

    $$\hat H |\phi\rangle + \sum_n (E-E_n) |\chi_n\rangle \langle \chi_n | \phi\rangle = E|\phi\rangle.$$
    
    The pseudo-state thus obeys $[\hat H + \hat V_{n\ell}]\, |\phi\rangle = E\,|\phi\rangle$ with:

    $$\hat V_{n\ell} = \sum_{n\ell} (E-E_{n\ell})\,|\chi_{n\ell}\rangle \langle \chi_{n\ell} |.$$

    where the energy of $|\phi\rangle$ is the same as the one of $|\psi\rangle$, thanks to the pseudopotential $\hat V_{n\ell}$.
    This extra potential depends on the quantum numbers $n$ and $\ell$ due to its spherical symmetry.
    Furthermore, since $E > E_{n\ell}$, it is a repulsive potenial.

In practice, pseudopotential expressions are separated into a fully nonlocal form, thanks to the Kleinman-Bylander Transformation (see [10.1103/PhysRevLett.48.1425](https://dx.doi.org/10.1103/PhysRevLett.48.1425)).
Latter on, Goedecker, Teter and Hutter (GTH, see [10.1103/PhysRevB.54.1703](https://dx.doi.org/10.1103/PhysRevB.54.1703)) derived expressions those two parts which are suited for real and Fourier space integration and only requires a few adjustable parameters (in blue):

$$\hat V_{PP} = \hat V_{loc} +  \sum_{\ell}^{\textcolor{blue}{\ell_{max}}} \hat V_{nl,\ell},$$

with

$$V_{loc}(r) = -\frac{Z'}{r}\,\text{erf}\left[\frac{\bar r}{\sqrt 2}\right] + \exp\left[-\frac{\bar r^2}{2}\right] \sum_{i=1}^4 \textcolor{blue}{C_i}\,\bar r^{2i-2}, \text{ with } \bar r = \frac{r}{\textcolor{blue}{r_c}},$$

and 

$$V_{nl,\ell} = \sum_{ij}^{\textcolor{blue}{N}} \textcolor{blue}{h_{\ell,ij}} \,|p_{\ell,i}\rangle \langle p_{\ell,j}|, \text{ with } p_{\ell,i}(r) = N_{\ell,i}(r)\,\exp\left[-\frac{\bar r^2}{2}\right] \text{ and } \bar r = \frac{r}{\textcolor{blue}{r_{nl,\ell}}}.$$

In the former, $Z'$ is the ionic charge (i.e., the charge of the nucleus minus the one of the core electrons), while in the latter, $N_\ell(r)$ is a combination of spherical harmonic multiplied by a $\ell$-dependent radial function.

All the parameters in blue, together with the number of core electrons in each shell, **define a GTH pseudopotential** in CP2K (see, e.g., [10.1007/s00214-005-0655-y](https://dx.doi.org/10.1007/s00214-005-0655-y)).
In particular, they are given as a local part plus a set of nonlinear projectors.

!!! note
    It is totally possible, for a given atom, to have pseudopotentials with a different number of core electrons embeded in the potential: while a small number of core electrons ensure a good transferability (but lengthen the calculation), a large number results in a smoother potential.

## Pairing GTH pseudopotentials with basis sets

!!! warning
    In practice, the number electron is dictated by the pseudopotential (which lists the number of valence electrons in each shell).
    CP2K will blindly use whatever basis set you give, since it has no way to check the information on the basis set side (not even the names, which are merely conventions).

From the previous paragraph, it appears that one has to pair a given pseudopotential with a correctly defined basis set, that has been designed with the correct amount of core electron removed and that contains smoother (pseudo-) basis functions.
Names of pseudopotentials and basis sets help to achieve this association:

+ GTH pseudopotential are generally named `GTH-<XFC>`, where `<XCF>` is the name of a XC-functional. 
  It is thus strongly suggested to use them together with the XCF in question.

    For a given atom, such potentials are nicknamed `GTH-<XFC>-q<N>`, where `<N>` is the number of valence electrons considered while building the potential.
    For example, a pseudopotential for carbon is nicknamed `GTH-BLYP-q4`, indicate that this pseudopotential was designed with BLYP, and that was built using 4 valence electrons (so it embedded a total of 2 core electrons).

+ Basis sets are generally named `<XZ>-<NAME>-<XCF>-GTH` or `<XZ>-GTH-<XCF>` (though this is definitely not an absolute rule!), where `<XZ>` describe the content of the basis set (e.g., `DZV` for double zeta, `TZVP` for triple zeta with extra polarization, etc), `<NAME>` is the name of the family (e.g., `MOLOPT`) and `<XCF>` is the name of the XCF used to optimize the basis set. 
  The `<XCF>` may not be present in the name: for example, `TZVP-MOLOPT-GTH` should work with all XCF, while `TZVP-MOLOPT-PBE-GTH` was specifically designed with PBE. 
  The latter probably gives better results and should (probably) be preferred.
  
    Again, for each atom, a suffix `-q<N>` is added, indicated how much valence electrons were not considered while building this basis set.
    For example, for carbon, the nickname `DZVP-MOLOPT-GTH-q4` indicates that this is a double-zeta basis set (plus polarization functions) of the `MOLOPT` family, designed to work with GTH pseudopotentials embedding 2 core electrons.

!!! note "Where are the basis sets and GTH pseudopotentials?"
    When running a CP2K calculation, you have to provide two files, containing the basis set(s) and pseudopotential(s) used in your calculation:

    ```
    &DFT
        BASIS_SET_FILE_NAME  BASIS_SET
        POTENTIAL_FILE_NAME  GTH_POTENTIALS
    &END DFT
    ```

    Basis sets and pseudopotentials are scattered across different file in the [CP2K `data` folder](https://github.com/cp2k/cp2k/tree/master/data).
    However, [the web interface of this project](webserver.md) proposes an easier way to build your own taylor-made `BASIS_SET` and `GTH_POTENTIALS` files.
    This is equivalent, since the data are obtained from the same source and just presented with a shiny interface ;)

    If you are interested, the format of those two files is described [here](../developers/bs_and_pseudo_file_format.md)

## Working with all-electron basis sets

!!! info
    The GAPW method is introduced, e.g., [here](https://www.cp2k.org/_media/events:2015_cecam_tutorial:iannuzzi_gpw_gapw_b.pdf) or in [10.1007/s002140050523](https://dx.doi.org/10.1007/s002140050523).

There also exists a special pseudopotential, `ALL`, which should be used for all-electron calculations.
This is the pseudopotential of choice for GAPW calculations. 
It can be used with your usual all-electron basis sets (such as STO-3G, e.g., [found in the BSE](http://www.basissetexchange.org/)).
A curated list is available in the [`EMSL_BASIS_SETS` file](https://github.com/cp2k/cp2k/blob/master/data/EMSL_BASIS_SETS).

Specially designed basis sets were also derived (found, e.g., in the [`ALL_BASIS_SETS` file](https://github.com/cp2k/cp2k/blob/master/data/ALL_BASIS_SETS)), which contains `ALL` in their name or ends by `-ae`.
The `-q<N>` number, if it exists (it is generally omitted), should be equal to the atomic number.