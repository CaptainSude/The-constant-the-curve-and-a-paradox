# Building the paper

The ready-to-read final edition is [`paper.pdf`](paper.pdf). All five figure PDFs and the STIX Two fonts are included; Python is not needed to compile the paper.

## Requirements

Use a current TeX Live or MiKTeX installation providing **LuaLaTeX** and **Biber**. The source uses `fontspec`, `unicode-math`, `biblatex`, and the standard packages listed in [`source/main.tex`](source/main.tex). Compile with LuaLaTeX. The fonts are loaded from `source/fonts/`, so they need not be installed on the computer.

## Build from the repository root

**Windows / PowerShell**

```powershell
./build.ps1
```

**Linux / macOS / a POSIX shell**

```sh
sh build.sh
```

Both scripts run LuaLaTeX, Biber, and two more LuaLaTeX passes. They place the result at **`build/paper.pdf`**, together with the temporary build files. The published `paper.pdf` is preserved. Build files are excluded from Git.

If a package is missing, install it using your TeX distribution's package manager and rerun the build. Biber and `biblatex` should come from the same up-to-date distribution.

## Manual build / online LaTeX editors

Upload the contents of `source/` to the editor, select **LuaLaTeX**, and set `main.tex` as the main document. Keep the `sections/`, `fonts/`, and `figures/` directories intact. The project requires Biber for the bibliography.

For a local manual build:

```sh
cd source
lualatex -interaction=nonstopmode -halt-on-error -file-line-error main.tex
biber main
lualatex -interaction=nonstopmode -halt-on-error -file-line-error main.tex
lualatex -interaction=nonstopmode -halt-on-error -file-line-error main.tex
```

This produces `source/main.pdf`. The existing `source/build.ps1` performs the same recipe on Windows. Different TeX versions can change PDF metadata or typesetting details; a rebuild is not expected to have the identical binary hash of the published PDF.

## Optional illustrations and calculations

Use Python 3.12 or later. Install the optional dependencies in an environment of your choice:

```sh
python -m pip install -r requirements.txt
```

From the repository root:

```sh
python source/code/build_core_figures.py
python source/code/build_locked_boxes.py
python source/code/build_two_averages.py
python source/code/verify_twin_certificate.py
python source/code/estimate_factor_entropy.py
python source/code/compute_deletion_times.py
python source/code/estimate_midpoint_roots.py --check-taylor-cutoff 149
```

The figure builders overwrite their corresponding files in `source/figures/`. The density preview uses 180,000 samples, primes through 2,000, and seed 271828. Settings and numerical scope are recorded in [`source/visual_data_manifest.json`](source/visual_data_manifest.json).

| Calculation | Scope |
| --- | --- |
| `verify_twin_certificate.py` | Exact rational arithmetic and an infinite-tail bound; Python standard library only. |
| `compute_deletion_times.py` | Exact finite sieve and recurrence, through one million by default. |
| `estimate_factor_entropy.py` | Numerical quadrature; the series remainder is bounded, but quadrature is not interval-certified. |
| `estimate_midpoint_roots.py` | Roots of finite approximations; no certificate for the limiting entire function's roots is supplied. |
| Density illustration | A labelled Monte Carlo preview, not a certified approximation. |

The mathematical arguments are in the manuscript and its appendices. These optional scripts reproduce illustrations and calculations.
