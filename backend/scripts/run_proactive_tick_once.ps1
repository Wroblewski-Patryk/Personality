$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"

Push-Location $repoRoot
try {
    & $pythonExe "$PSScriptRoot\run_proactive_tick_once.py" @args
}
finally {
    Pop-Location
}
