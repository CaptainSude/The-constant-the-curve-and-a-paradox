# The constant, the curve and a paradox

**Sol, Astra and Captain Sude**  
Final version - 25 September 2026

The paper starts with the Goldbach constant. Sampling its digits leads to probability curves and spectra; the locked-box game enters when coprimality raises a reconstruction question. The main text develops the examples and consequences. Longer proofs remain in the same manuscript, in linked appendices.

The contents and a symbol guide precede the Goldbach opening. There is no abstract: the mathematical story unfolds from its first construction. A dedicated section gathers the conjecture and open questions, with links to the discoveries that prompted them. The main narrative uses 12-point STIX Two, with 11-point proof appendices, upright theorem statements and five vector figures.

## Build the paper

Install a current TeX distribution with LuaLaTeX, Biber, `biblatex`, `fontspec`, `unicode-math` and the standard packages named in `main.tex`. The STIX Two fonts are bundled with their license.

From this directory run:

```text
lualatex -interaction=nonstopmode -halt-on-error main.tex
biber main
lualatex -interaction=nonstopmode -halt-on-error main.tex
lualatex -interaction=nonstopmode -halt-on-error main.tex
```

On Windows, `build.ps1` performs those steps. The result is `main.pdf`. Figure PDFs are included, so Python is not required to build the manuscript.

## Reproduce the illustrations and calculations

Use Python 3.12 or later. The figure builders need NumPy and Matplotlib; the midpoint-root calculation needs mpmath. The optional dependencies are listed in [requirements.txt](../requirements.txt). Paths are relative to this source package.

```text
python code/build_core_figures.py
python code/build_locked_boxes.py
python code/build_two_averages.py
python code/verify_twin_certificate.py
python code/estimate_factor_entropy.py
python code/compute_deletion_times.py
python code/estimate_midpoint_roots.py --check-taylor-cutoff 149
```

The figures appear in narrative order; their filenames retain production order:

| Figure | File stem | What the picture establishes |
| --- | --- | --- |
| 1 | `01_digits_and_divisors` | Exact finite digit and divisor examples, including an explicitly artificial disabled lane. |
| 2 | `05_two_averages` | Numerical roots of two exact quadratic polynomials for the same artificial mask. |
| 3 | `02_prime_density` | A conditional Monte Carlo preview with fixed seed and finite prime cutoff; the Taylor-support pattern comes from the theorem. |
| 4 | `04_locked_boxes` | A schematic of the game, not an empirical recovery trial. |
| 5 | `03_delete_seven` | Exact finite deletion rounds in the stated displayed range. |

The numerical calculations have different scopes:

- `verify_twin_certificate.py` uses exact rational arithmetic and an infinite-tail bound. It certifies four negative directions, without giving a new twin-prime count or proving infinitude.
- `estimate_factor_entropy.py` evaluates a positive moment recursion on two quadrature grids. The series remainder bound is rigorous; the quadrature has no interval error certificate.
- `compute_deletion_times.py` uses an exact sieve and recurrence, through one million by default. It reproduces the reported deletion-round table and counts. Those counts are finite evidence, separate from the proved asymptotic clock law.
- `estimate_midpoint_roots.py` reproduces roots of finite polynomial approximations at the three Euler cutoffs in the paper. These roots are **uncertified** as roots of the limiting entire function; no Euler-tail or contour certificate is supplied.

`visual_data_manifest.json` records the illustration settings and numerical scope. The density preview is not a certified approximation.

## Mathematical and numerical scope

The manuscript contains the mathematical arguments and references for imported results. The numerical scope of the accompanying calculations is described above and in the manifest. Goldbach, RH and the twin-prime conjecture remain open in this work.

The repository [README](../README.md) provides a reading guide; [BUILDING.md](../BUILDING.md) covers compilation and calculations. The paper and its sources are under CC BY 4.0, scripts under MIT, and bundled fonts under their original SIL Open Font License; see [LICENSE.md](../LICENSE.md).

## Files

- `main.tex`: master source and typography.
- `sections/`: narrative chapters, proof appendices and notation guide.
- `references.bib`: bibliography.
- `figures/`: vector figures, previews and finite data.
- `fonts/`: STIX Two fonts and license.
- `code/`: portable figure builders and calculation checks.
