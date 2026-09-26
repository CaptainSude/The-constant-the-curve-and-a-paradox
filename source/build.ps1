$ErrorActionPreference = 'Stop'
Push-Location -LiteralPath $PSScriptRoot
try {
    & lualatex -interaction=nonstopmode -halt-on-error -file-line-error main.tex
    if ($LASTEXITCODE -ne 0) { throw 'LuaLaTeX first pass failed.' }
    & biber main
    if ($LASTEXITCODE -ne 0) { throw 'Biber failed.' }
    for ($paperPass = 1; $paperPass -le 2; $paperPass++) {
        & lualatex -interaction=nonstopmode -halt-on-error -file-line-error main.tex
        if ($LASTEXITCODE -ne 0) { throw "LuaLaTeX pass $paperPass failed." }
    }
    Write-Output (Join-Path $PSScriptRoot 'main.pdf')
}
finally { Pop-Location }
