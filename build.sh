#!/bin/sh
# SPDX-License-Identifier: MIT
set -eu
cd "$(dirname "$0")/source"
for program in lualatex biber; do
    command -v "$program" >/dev/null 2>&1 || {
        printf '%s\n' "Required program '$program' is missing. See BUILDING.md." >&2
        exit 1
    }
done
mkdir -p ../build
lualatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=../build -jobname=paper main.tex
biber --input-directory=../build --output-directory=../build paper
lualatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=../build -jobname=paper main.tex
lualatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=../build -jobname=paper main.tex
printf '%s\n' 'Built build/paper.pdf'
