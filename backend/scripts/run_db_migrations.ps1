param(
    [string]$Revision = "head"
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
$alembicConfig = Join-Path $repoRoot "backend\alembic.ini"

Push-Location $repoRoot
try {
    & $pythonExe -m alembic -c $alembicConfig upgrade $Revision
}
finally {
    Pop-Location
}
