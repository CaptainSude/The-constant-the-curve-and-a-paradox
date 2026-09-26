# SPDX-License-Identifier: MIT
$ErrorActionPreference = 'Stop'
$paperBuildDir = Join-Path $PSScriptRoot 'build'
foreach ($paperCommand in @('lualatex', 'biber')) {
    if (-not (Get-Command $paperCommand -ErrorAction SilentlyContinue)) {
        throw "Required program '$paperCommand' is missing. See BUILDING.md."
    }
}
New-Item -ItemType Directory -Path $paperBuildDir -Force | Out-Null
Push-Location -LiteralPath (Join-Path $PSScriptRoot 'source')
try {
    & lualatex -interaction=nonstopmode -halt-on-error -file-line-error "-output-directory=$paperBuildDir" -jobname=paper main.tex
    if ($LASTEXITCODE -ne 0) { throw 'LuaLaTeX first pass failed.' }
    & biber "--input-directory=$paperBuildDir" "--output-directory=$paperBuildDir" paper
    if ($LASTEXITCODE -ne 0) { throw 'Biber failed.' }
    for ($paperPass = 1; $paperPass -le 2; $paperPass++) {
        & lualatex -interaction=nonstopmode -halt-on-error -file-line-error "-output-directory=$paperBuildDir" -jobname=paper main.tex
        if ($LASTEXITCODE -ne 0) { throw "LuaLaTeX pass $paperPass failed." }
    }
    Write-Output "Built $(Join-Path $paperBuildDir 'paper.pdf')"
}
finally { Pop-Location }
