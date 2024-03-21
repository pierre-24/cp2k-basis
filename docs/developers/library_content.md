
# Content of the library

## Source

The following files are used to build [the current library](https://github.com/pierre-24/cp2k-basis/tree/dev/library):

+ Basis sets:
    + [ALL_BASIS_SETS](https://github.com/cp2k/cp2k/raw/ac0226eb549c7ef1ea50d0597d545f29d4c8fc87/data/ALL_BASIS_SETS)
    + [BASIS_ADMM](https://github.com/cp2k/cp2k/raw/ac0226eb549c7ef1ea50d0597d545f29d4c8fc87/data/BASIS_ADMM)
    + [BASIS_ADMM_MOLOPT](https://github.com/cp2k/cp2k/raw/ac0226eb549c7ef1ea50d0597d545f29d4c8fc87/data/BASIS_ADMM_MOLOPT)
    + [BASIS_ADMM_UZH](https://github.com/cp2k/cp2k/raw/ac0226eb549c7ef1ea50d0597d545f29d4c8fc87/data/BASIS_ADMM_UZH)
    + [BASIS_MOLOPT](https://github.com/cp2k/cp2k/raw/ac0226eb549c7ef1ea50d0597d545f29d4c8fc87/data/BASIS_MOLOPT)
    + [BASIS_MOLOPT_AcPP1](https://github.com/cp2k/cp2k/raw/ac0226eb549c7ef1ea50d0597d545f29d4c8fc87/data/BASIS_MOLOPT_AcPP1)
    + [BASIS_MOLOPT_LnPP1](https://github.com/cp2k/cp2k/raw/ac0226eb549c7ef1ea50d0597d545f29d4c8fc87/data/BASIS_MOLOPT_LnPP1)
    + [BASIS_MOLOPT_LnPP2](https://github.com/cp2k/cp2k/raw/ac0226eb549c7ef1ea50d0597d545f29d4c8fc87/data/BASIS_MOLOPT_LnPP2)
    + [BASIS_MOLOPT_UCL](https://github.com/cp2k/cp2k/raw/ac0226eb549c7ef1ea50d0597d545f29d4c8fc87/data/BASIS_MOLOPT_UCL)
    + [BASIS_MOLOPT_UZH](https://github.com/cp2k/cp2k/raw/ac0226eb549c7ef1ea50d0597d545f29d4c8fc87/data/BASIS_MOLOPT_UZH)
    + [BASIS_ZIJLSTRA](https://github.com/cp2k/cp2k/raw/ac0226eb549c7ef1ea50d0597d545f29d4c8fc87/data/BASIS_ZIJLSTRA)
    + [GTH_BASIS_SETS](https://github.com/cp2k/cp2k/raw/ac0226eb549c7ef1ea50d0597d545f29d4c8fc87/data/GTH_BASIS_SETS)

+ Pseudopotentials:
    + [AcPP1_POTENTIALS](https://github.com/cp2k/cp2k/raw/ac0226eb549c7ef1ea50d0597d545f29d4c8fc87/data/AcPP1_POTENTIALS)
    + [GTH_POTENTIALS](https://github.com/cp2k/cp2k/raw/ac0226eb549c7ef1ea50d0597d545f29d4c8fc87/data/GTH_POTENTIALS)
    + [LnPP1_POTENTIALS](https://github.com/cp2k/cp2k/raw/ac0226eb549c7ef1ea50d0597d545f29d4c8fc87/data/LnPP1_POTENTIALS)
    + [LnPP2_POTENTIALS](https://github.com/cp2k/cp2k/raw/ac0226eb549c7ef1ea50d0597d545f29d4c8fc87/data/LnPP2_POTENTIALS)
    + [POTENTIAL_UZH](https://github.com/cp2k/cp2k/raw/ac0226eb549c7ef1ea50d0597d545f29d4c8fc87/data/POTENTIAL_UZH)
  
## Detailed content



### Basis sets
 

| Name | Description | Atoms |
|------|-------------|-------|
| DZV-ALL | A double zeta valence basis set for all-electron calculations. | H, He |
| DZV-ALL-BLYP | A double zeta valence basis set for all-electron calculations, optimized for BLYP. | H |
| DZV-ALL-PADE | A double zeta valence basis set for all-electron calculations, optimized for PADE. | H, He, Li, Be |
| DZV-ALL-PADE-NEW | A double zeta valence basis set for all-electron calculations, optimized for PADE. | H, He, Li, Be |
| DZV-GTH | A double zeta valence basis set for H and He for GTH pseudopotentials | H, He |
| DZV-GTH-BLYP | A double zeta valence basis set for GTH pseudopotentials, optimized for BLYP. | H, He, Li, Be |
| DZV-GTH-BLYP-CONFINED | A double zeta valence basis set (CONFINED version for solids) for GTH pseudopotentials, optimized for BLYP. | H |
| DZV-GTH-PADE | A double zeta valence basis set for GTH pseudopotentials, optimized for PADE. | H, He, Li, Be |
| DZV-GTH-PADE-CONFINED | A double zeta valence basis set (CONFINED version for solids) for GTH pseudopotentials, optimized for PADE. | H |
| DZV-MOLOPT-GTH-AcLnPP1 | MOLOPT basis set (double zeta) to explore Lanthanide chemistry in complex environments, optimized for PBE. | La, Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu |
| DZV-MOLOPT-SR-GTH | A double zeta valence MOLOPT basis set, for solids (short-range) and GTH pseudopotentials | Ce |
| DZVP-ALL | A double zeta valence (+ 1 set of polarization) basis set for all-electron calculations. | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Cu |
| DZVP-ALL-BLYP | A double zeta valence (+ 1 set of polarization) basis set for all-electron calculations, optimized for BLYP. | H |
| DZVP-ALL-PADE | A double zeta valence (+ 1 set of polarization) basis set for all-electron calculations, optimized for PADE. | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar |
| DZVP-ALL-PADE-NEW | A double zeta valence (+ 1 set of polarization) basis set for all-electron calculations, optimized for PADE. | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar |
| DZVP-GTH | A double zeta valence (+ 1 set of polarization) basis set for GTH pseudopotentials | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, W |
| DZVP-GTH-BLYP | A double zeta valence (+ 1 set of polarization) basis set for GTH pseudopotentials, optimized for BLYP. | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K |
| DZVP-GTH-BLYP-CONFINED | A double zeta valence (+ 1 set of polarization) basis set (CONFINED  version for solids) for GTH pseudopotentials, optimized for BLYP. | H, O, Al, Si, K |
| DZVP-GTH-PADE | A double zeta valence (+ 1 set of polarization) basis set for GTH pseudopotentials, optimized for PADE. | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K |
| DZVP-GTH-PADE-CONFINED | A double zeta valence (+ 1 set of polarization) basis set (CONFINED version for solids) for GTH pseudopotentials, optimized for PADE. | H, C, O, Al, Si, K |
| DZVP-MOLOPT-GGA-GTH | A double zeta valence (+ 1 set polarization) MOLOPT basis set, optimized for the GTH pseudopotentials and the PBE functional (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| DZVP-MOLOPT-GTH | A double zeta valence (+ 1 set polarization) MOLOPT basis set, for gas and condensed phase and GTH pseudopotentials | H, C, N, O, F, Si, P, S, Cl, Cu, Br, U |
| DZVP-MOLOPT-GTH-AcLnPP1 | MOLOPT basis set (double zeta+polarization) to explore Actinide chemistry in complex environments, optimized for PBE. | Ac, Th, Pa, U, Np, Pu, Am, Cm, Bk, Cf, Es, Fm, Md, No, Lr |
| DZVP-MOLOPT-GTH-LnPP2 | MOLOPT basis set (double zeta + 1 set polarization), norm-Conserving 4f-in-Core Optimized for Trivalent Lanthanides | Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu |
| DZVP-MOLOPT-HYB-GTH | A double zeta valence (+ 1 set polarization) MOLOPT basis set, optimized for the GTH pseudopotentials and the PBE0 functional (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| DZVP-MOLOPT-MGGA-GTH | A double zeta valence (+ 1 set polarization) MOLOPT basis set, optimized for the GTH pseudopotentials and the SCAN functional (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| DZVP-MOLOPT-PBE-GTH | A double zeta valence (+ 1 set polarization) MOLOPT basis set, optimized for the GTH pseudopotentials and the PBE functional (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| DZVP-MOLOPT-PBE0-GTH | A double zeta valence (+ 1 set polarization) MOLOPT basis set, optimized for the GTH pseudopotentials and the PBE0 functional (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| DZVP-MOLOPT-SCAN-GTH | A double zeta valence (+ 1 set polarization) MOLOPT basis set, optimized for the GTH pseudopotentials and the SCAN functional (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| DZVP-MOLOPT-SR-GTH | A double zeta valence (+ 1 set polarization) MOLOPT basis set, for solids (short-range) and GTH pseudopotentials | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, La, Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| DZVP-MONTREAL-ALL | A double zeta valence (+ 1 set of polarization) basis set for all-electron calculations. | Li, Na |
| DZVPd-MOLOPT-SR-GTH | A double zeta valence (+ 1 set polarization) MOLOPT basis set, for solids (short-range) and GTH pseudopotentials | Na, Mg |
| FIT10 | An auxiliary minimal basis set [5s4p1d\|5s4p1d] for K-Ga, Rb-In, Cs-Ba and Hf-Tl with ADMM | K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl |
| FIT11 | An auxiliary minimal basis set [5s5p1d\|5s5p1d] for K-Ga, Rb-In, Cs-Ba and Hf-Tl with ADMM | K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl |
| FIT12 | An auxiliary minimal basis set [4s3p4d1f\|4s3p4d1f] for Sc-Ga, Y-In and Hf-Tl with ADMM | Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl |
| FIT13 | An auxiliary minimal basis set [4s4p4d1f\|4s4p4d1f] for some transition metals with ADMM | Sc, Ti, V, Cr, Mn, Fe, Ni, Ga, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, In, Hf, Ta, W, Re, Os, Ir, Pt, Tl |
| FIT3 | An auxiliary minimal basis set [3s3p\|3s3p] for H-F, Na-Cl and Br with ADMM | H, He, Li, Be, B, C, N, O, F, Na, Mg, Al, Si, P, S, Cl, Br |
| FIT4 | An auxiliary minimal basis set [4s\|4s] for lithium with ADMM | Li |
| FIT4-SR | An auxiliary minimal basis set [4s\|4s] for lithium with ADMMf for solid (short-range) | Li |
| FIT5 | An auxiliary minimal basis set basis set for ADMM | Li |
| FIT5-SR | An auxiliary minimal basis set [4s1p\|4s1p] (FIT4 with polarization) for lithium with ADMM for solid (short-range) | Li |
| FIT6 | An auxiliary minimal basis set [3s3p\|3s3p] for Ge-Br, Sn-I and Pb-At (plus Ca) with ADMM | Al, Ge, As, Se, Br, Sn, Sb, Te, I, Pb, Bi, Po, At |
| FIT7 | An auxiliary minimal basis set  [3s3p1d\|3s3p1d] (FIT6 with polarization) for Ge-Br, Sn-I and Pb-At (plus Al, K, Ca, Rb, Cs) with ADMM | Al, K, Ca, Ge, As, Se, Br, Rb, Sn, Sb, Te, I, Cs, Pb, Bi, Po, At |
| FIT8 | An auxiliary minimal basis set [4s3p1d\|4s3p1d] (FIT7 with polarization) for K, Ca, Rb, Sr, Cs, Ba (plus Ca) with ADMM | Al, K, Ca, Rb, Sr, Cs, Ba |
| FIT9 | An auxiliary minimal basis set [4s4p1d\|4s4p1d] for Ge-Br, Sn-I and Pb-At (plus Al, K, Ca, Cu, Zn, Ag, Cd, Au, Hg, Rb, Cs, Ba) with ADMM | O, Al, K, Ca, Cu, Zn, Ga, Ge, As, Se, Br, Rb, Sr, Ag, Cd, In, Sn, Sb, Te, I, Cs, Ba, Au, Hg, Tl, Pb, Bi, Po, At |
| QZV2P-GTH | A quadruple zeta valence (+ 2 set of polarization) basis set for GTH pseudopotentials | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar |
| QZV3P-GTH | A quadruple zeta valence (+ 3 set of polarization) basis set for GTH pseudopotentials | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar |
| QZVPP-MOLOPT-GGA-GTH | A MOLOPT basis set based on def-qzvpp, optimized for the small-core GTH pseudopotentials, the PBE functional, and the GAPW method (UZH). | Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| QZVPP-MOLOPT-GGA-ae | A MOLOPT basis set based on def-qzvpp, optimized for all-electron calculations, the PBE functional, and the GAPW method (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr |
| QZVPP-MOLOPT-PBE-GTH | A MOLOPT basis set based on def-qzvpp, optimized for the small-core GTH pseudopotentials, the PBE functional, and the GAPW method (UZH). | Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| QZVPP-MOLOPT-PBE-ae | A MOLOPT basis set based on def-qzvpp, optimized for all-electron calculations, the PBE functional, and the GAPW method (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr |
| SVP-MOLOPT-GGA-GTH | A MOLOPT basis set based on def-svp, optimized for small-core GTH pseudopotentials, the PBE functional, and the GAPW method (UZH). | Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| SVP-MOLOPT-GGA-ae | A MOLOPT basis set based on def-svp, optimized for all-electron calculations, the PBE functional, and the GAPW method (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr |
| SVP-MOLOPT-PBE-GTH | A MOLOPT basis set based on def-svp, optimized for small-core GTH pseudopotentials, the PBE functional, and the GAPW method (UZH). | Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| SVP-MOLOPT-PBE-ae | A MOLOPT basis set based on def-svp, optimized for all-electron calculations, the PBE functional, and the GAPW method (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr |
| SZV-GTH | A single zeta valence basis set for GTH pseudopotentials | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar |
| SZV-MOLOPT-GTH | A single zeta valence MOLOPT basis set, for gas and condensed phase and GTH pseudopotentials | H, C, N, O, F, Si, P, S, Cl, Cu, Br |
| SZV-MOLOPT-SR-GTH | A single zeta valence MOLOPT basis set, for solids (short-range) and GTH pseudopotentials | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| SZVP-MOLOPT-SR-GTH | A single zeta valence (+ 1 set polarization) MOLOPT basis set, for solids (short-range) and GTH pseudopotentials | Rh |
| TZV-ALL-PADE | A triple zeta valence basis set for all-electron calculations, optimized for PADE. | H, He |
| TZV2P-GTH | A triple zeta valence (+ 2 set of polarization) basis set for GTH pseudopotentials | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar |
| TZV2P-MOLOPT-GGA-GTH | A triple zeta valence (+ 2 sets polarization) MOLOPT basis set, optimized for the GTH pseudopotentials and the PBE functional (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| TZV2P-MOLOPT-GTH | A triple zeta valence (+ 2 sets polarization) MOLOPT basis set, for gas and condensed phase and GTH pseudopotentials | H, C, N, O, F, Si, P, S, Cl, Br |
| TZV2P-MOLOPT-GTH-LnPP2 | MOLOPT basis set (triple zeta + 2 set polarization), norm-Conserving 4f-in-Core Optimized for Trivalent Lanthanides | Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu |
| TZV2P-MOLOPT-HYB-GTH | A triple zeta valence (+ 2 sets polarization) MOLOPT basis set optimized for the GTH pseudopotentials and the PBE0 functional (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| TZV2P-MOLOPT-MGGA-GTH | A triple zeta valence (+ 2 sets polarization) MOLOPT basis set, optimized for the GTH pseudopotentials and the SCAN functional (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| TZV2P-MOLOPT-PBE-GTH | A triple zeta valence (+ 2 sets polarization) MOLOPT basis set, optimized for the GTH pseudopotentials and the PBE functional (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| TZV2P-MOLOPT-PBE0-GTH | A triple zeta valence (+ 2 sets polarization) MOLOPT basis set optimized for the GTH pseudopotentials and the PBE0 functional (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| TZV2P-MOLOPT-SCAN-GTH | A triple zeta valence (+ 2 sets polarization) MOLOPT basis set, optimized for the GTH pseudopotentials and the SCAN functional (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| TZV2P-MOLOPT-SR-GTH | A triple zeta valence (+ 2 sets polarization) MOLOPT basis set, for solids (short-range) and GTH pseudopotentials | Li, Be, B, Mg, Al, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Cs, Ba, La, Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At |
| TZV2PX-MOLOPT-GTH | A triple zeta valence (+ 2 sets polarization and 1f) MOLOPT basis set, for gas and condensed phase and GTH pseudopotentials | H, C, N, O, F, Si, P, S, Cl, Br |
| TZV2Pd-MOLOPT-SR-GTH | A triple zeta valence (+ 2 sets polarization) MOLOPT basis set, for solids (short-range) and GTH pseudopotentials | Na, Mg |
| TZVP-ALL | A triple zeta valence (+ 1 set of polarization) basis set for all-electron calculations. | Cu |
| TZVP-ALL-BLYP | A triple zeta valence (+ 1 set of polarization) basis set for all-electron calculations, optimized for BLYP. | O, F |
| TZVP-ALL-PADE | A triple zeta valence (+ 1 set of polarization) basis set for all-electron calculations, optimized for PADE. | H, He, B, C, N, O, F, Ne, Al, Si, P, S, Cl, Ar |
| TZVP-GTH | A triple zeta valence (+ 1 set of polarization) basis set for GTH pseudopotentials | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar |
| TZVP-MOLOPT-GGA-GTH | A triple zeta valence (+ 1 set polarization) MOLOPT basis set, optimized or the GTH pseudopotentials and the PBE functional (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| TZVP-MOLOPT-GTH | A triple zeta valence (+ 1 set polarization) MOLOPT basis set, for gas and condensed phase and GTH pseudopotentials | H, C, N, O, F, Si, P, S, Cl, Br |
| TZVP-MOLOPT-GTH-LnPP2 | MOLOPT basis set (triple zeta + 1 set polarization), norm-Conserving 4f-in-Core Optimized for Trivalent Lanthanides | Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu |
| TZVP-MOLOPT-HYB-GTH | A triple zeta valence (+ 1 set polarization) MOLOPT basis set, optimized for the GTH pseudopotentials and the PBE0 functional (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| TZVP-MOLOPT-MGGA-GTH | A triple zeta valence (+ 1 set polarization) MOLOPT basis set, optimized for the GTH pseudopotentials and the SCAN functional (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| TZVP-MOLOPT-PBE-GTH | A triple zeta valence (+ 1 set polarization) MOLOPT basis set, optimized or the GTH pseudopotentials and the PBE functional (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| TZVP-MOLOPT-PBE0-GTH | A triple zeta valence (+ 1 set polarization) MOLOPT basis set, optimized for the GTH pseudopotentials and the PBE0 functional (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| TZVP-MOLOPT-SCAN-GTH | A triple zeta valence (+ 1 set polarization) MOLOPT basis set, optimized for the GTH pseudopotentials and the SCAN functional (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| TZVP-MOLOPT-SR-GTH | A triple zeta valence (+ 1 set polarization) MOLOPT basis set, for solids (short-range) and GTH pseudopotentials | Li, Be, B, Mg, Al, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Cs, Ba, La, Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At |
| TZVPP-MOLOPT-GGA-GTH | A MOLOPT basis set based on def-tzvpp, optimized for small-core GTH pseudopotentials, the PBE functional, and the GAPW method (UZH). | Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| TZVPP-MOLOPT-GGA-ae | A MOLOPT basis set based on def-tzvpp, optimized for all-electron calculations, the PBE functional, and the GAPW method (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr |
| TZVPP-MOLOPT-PBE-GTH | A MOLOPT basis set based on def-tzvpp, optimized for small-core GTH pseudopotentials, the PBE functional, and the GAPW method (UZH). | Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| TZVPP-MOLOPT-PBE-ae | A MOLOPT basis set based on def-tzvpp, optimized for all-electron calculations, the PBE functional, and the GAPW method (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr |
| TZVPd-MOLOPT-SR-GTH | A triple zeta valence (+ 1 set polarization) MOLOPT basis set, for solids (short-range) and GTH pseudopotentials | Na, Mg |
| Zijlstra-2SP | 3SP basis set, targeted at very fast calculations | H, Li, Be, B, C, N, O, F, Al, Si, P, S, Cl |
| Zijlstra-3SP | 3SP basis set, targeted at very fast calculations. Author recommendation for this series. | H, Li, Be, B, C, N, O, F, Al, Si, P, S, Cl |
| Zijlstra-4SP | 3SP basis set, targeted at very fast calculations | H, Li, Be, B, C, N, O, F, Al, Si, P, S, Cl |
| admm-dz | An auxiliary double zeta basis set for ADMM | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| admm-dzp | An auxiliary double zeta basis set for ADMM | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| admm-tz2p | An auxiliary triple zeta (+ 2 set polarization) basis set for ADMM | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| admm-tzp | An auxiliary triple zeta (+ 1 set polarization) basis set for ADMM | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| aug-DZVP-GTH | An augmented double zeta valence (+ 1 set of polarization) basis set for GTH pseudopotentials | H, C, N, O, F, Si, P, S, Cl |
| aug-FIT3 | An auxiliary minimal basis set [4s4p\|4s4p] (with extra diffuses) for H-F, Na-Cl and Br with ADMM | H, C, N, O, F, Si, P, S, Cl |
| aug-QZV2P-GTH | An augmented quadruple zeta valence (+ 2 sets of polarization) basis set for GTH pseudopotentials | H, C, N, O, F, Si, P, S, Cl |
| aug-QZV3P-GTH | An augmented quadruple zeta valence (+ 3 sets of polarization) basis  set for GTH pseudopotentials | H, C, N, O, F, Si, P, S, Cl |
| aug-TZV2P-GTH | An augmented triple zeta valence (+ 2 sets of polarization) basis set for GTH pseudopotentials | H, C, N, O, F, Si, P, S, Cl |
| aug-TZVP-GTH | An augmented triple zeta valence (+ 1 set of polarization) basis set for GTH pseudopotentials | H, C, N, O, F, Si, P, S, Cl |
| aug-cFIT3 | An auxiliary minimal basis set [4s4p\|3s3p] (with extra diffuse and contracted) for H-F, Na-Cl and Br with ADMM | H, C, N, O, F, Si, P, S, Cl |
| aug-cpFIT3 | An auxiliary minimal basis set [4s4p1d\|3s3p1d] (with extra diffuses and polarization, contracted) for H-F, Na-Cl and Br with ADMM | H, C, N, O, F, Si, P, S, Cl |
| aug-pFIT3 | An auxiliary minimal basis set [4s4p1d\|4s4p1d] (with extra diffuses and polarization) for H-F, Na-Cl and Br with ADMM | H, C, N, O, F, Si, P, S, Cl |
| cFIT10 | An auxiliary minimal basis set [9s4p1d\|3s2p1d] for K-Ga, Rb-In, Cs-Ba and Hf-Tl with ADMM | K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl |
| cFIT11 | An auxiliary minimal basis set [9s5p1d\|3s2p1d] for K-Ga, Rb-In, Cs-Ba and Hf-Tl with ADMM | K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Cs, Ba, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl |
| cFIT12 | An auxiliary minimal basis set [4s3p4d1f\|2s2p2d1f] for Sc-Ga, Y-In and Hf-Tl with ADMM | Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl |
| cFIT13 | An auxiliary minimal basis set [4s4p4d1f\|2s2p2d1f] for some transition metals with ADMM | Sc, Ti, V, Cr, Mn, Fe, Ni, Ga, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, In, Hf, Ta, W, Re, Os, Ir, Pt, Tl |
| cFIT3 | An auxiliary minimal basis set [3s3p\|2s2p] (contracted) for H-F, Na-Cl and Br with ADMM | H, He, Li, Be, B, C, N, O, F, Na, Mg, Al, Si, P, S, Cl, Br |
| cFIT4 | An auxiliary minimal basis set [7s\|3s] for lithium with ADMM | Li |
| cFIT4-SR | An auxiliary minimal basis set [7s\|3s] for lithium with ADMM for solid (short-range) | Li |
| cFIT5 | An auxiliary minimal basis set [7s1p\|3s1p] (cFIT4 with polarization) for lithium int ADMM | Li |
| cFIT5-SR | An auxiliary minimal basis set [7s1p\|3s1p] (cFIT4 with polarization) for lithium with ADMM for solid (short-range) | Li |
| cFIT6 | An auxiliary minimal basis set [3s3p\|2s2p] (contraction of FIT6) for Ge-Br, Sn-I and Pb-At (plus Ca) with ADMM | Al, Ge, As, Se, Br, Sn, Sb, Te, I, Pb, Bi, Po, At |
| cFIT7 | An auxiliary minimal basis set [3s3p1d\|2s2p1d] (cFIT6 with polarization) for Ge-Br, Sn-I and Pb-At (plus Al, K, Ca, Rb, Cs) with ADMM | Al, K, Ca, Ge, As, Se, Br, Rb, Sn, Sb, Te, I, Cs, Pb, Bi, Po, At |
| cFIT8 | An auxiliary minimal basis set [7s3p1d\|3s2p1d] (cFIT7 with polarization) for K, Ca, Rb, Sr, Cs, Ba (plus Ca) with ADMM | Al, K, Ca, Rb, Sr, Cs, Ba |
| cFIT9 | An auxiliary minimal basis set [4s4p1d\|2s2p1d] for Ge-Br, Sn-I and Pb-At (plus Al, K, Ca, Cu, Zn, Ag, Cd, Au, Hg, Rb, Cs, Ba) with ADMM | Al, K, Ca, Cu, Zn, Ga, Ge, As, Se, Br, Rb, Sr, Ag, Cd, In, Sn, Sb, Te, I, Cs, Ba, Au, Hg, Tl, Pb, Bi, Po, At |
| cpFIT3 | An auxiliary minimal basis set [3s3p1d\|2s2p1d] (with polarization and contracted) for H-F, Na-Cl and Br with ADMM | H, He, Li, Be, B, C, N, O, F, Na, Mg, Al, Si, P, S, Cl, Br |
| pFIT3 | An auxiliary minimal basis set [3s3p1d\|3s3p1d] (with polarization) for H-F, Na-Cl and Br with ADMM | H, He, Li, Be, B, C, N, O, F, Na, Mg, Al, Si, P, S, Cl, Br |

### Pseudopotentials
 

| Name | Description | Atoms |
|------|-------------|-------|
| ALL | All-electron pseudopotentials (UZH) | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr |
| GTH-BLYP | GTH pseudopotentials, optimized for BLYP. | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Mo, Ru, Rh, Pd, Ag, In, Sb, Te, I, Xe, Cs, Ba, Ce, Gd, W, Au, Pb, Bi |
| GTH-BP | GTH pseudopotentials, optimized for BP. | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Zr, Ru, Te, Cs, Au |
| GTH-GGA | GTH pseudopotentials, optimized for PBE (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, La, Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| GTH-HCTH120 | GTH pseudopotentials, optimized for HCTH. | H, C, N, O, F, P, Ar |
| GTH-HCTH407 | GTH pseudopotentials, optimized for HCTH. | H, C, N, O |
| GTH-HYB | GTH pseudopotentials, optimized for PBE0 (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, La, Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| GTH-LDA | GTH pseudopotentials, optimized for PADE. | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, La, Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn, Ac, Th, Pa, U, Np, Pu, Am, Cm, Bk, Cf, Es, Fm, Md, No, Lr |
| GTH-MGGA | GTH pseudopotentials, optimized for SCAN (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, La, Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| GTH-OLYP | GTH pseudopotentials, optimized for OLYP. | H, B, C, N, O, F, P, S, Cl |
| GTH-PADE | GTH pseudopotentials, optimized for PADE. | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, La, Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn, Ac, Th, Pa, U, Np, Pu, Am, Cm, Bk, Cf, Es, Fm, Md, No, Lr |
| GTH-PBE | GTH pseudopotentials, optimized for PBE (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, La, Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| GTH-PBE-AcLnPP1 | GTH pseudopotentials to explore Lanthanide and Actinide chemistry in complex environments, optimized for PBE. | La, Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Ac, Th, Pa, U, Np, Pu, Am, Cm, Bk, Cf, Es, Fm, Md, No, Lr |
| GTH-PBE-LnPP2 | Norm-Conserving pseudopotential 4f-in-Core Optimized for Trivalent Lanthanides | Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu |
| GTH-PBE0 | GTH pseudopotentials, optimized for PBE0 (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, La, Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
| GTH-SCAN | GTH pseudopotentials, optimized for SCAN (UZH). | H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br, Kr, Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I, Xe, Cs, Ba, La, Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu, Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn |
