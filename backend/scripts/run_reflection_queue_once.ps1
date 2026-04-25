param(
    [int]$Limit = 10,
    [switch]$AllowInProcess
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
$arguments = @((Join-Path $PSScriptRoot "run_reflection_queue_once.py"), "--limit", "$Limit")
if ($AllowInProcess) {
    $arguments += "--allow-in-process"
}

Push-Location $repoRoot
try {
    & $pythonExe @arguments
}
finally {
    Pop-Location
}
