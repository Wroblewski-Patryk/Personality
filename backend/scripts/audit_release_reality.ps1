param(
    [string]$BaseUrl = "https://aviary.luckysparrow.ch",
    [string]$SelectedSha = "",
    [int]$TimeoutSeconds = 20,
    [string]$Output = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

if (Test-Path (Join-Path $repoRoot ".venv\Scripts\python.exe")) {
    $pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
}
elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonExe = "python"
}
else {
    throw "Python executable not found. Install Python or activate .venv."
}

$args = @(
    (Join-Path $PSScriptRoot "audit_release_reality.py"),
    "--base-url", $BaseUrl,
    "--timeout-seconds", ([string]$TimeoutSeconds)
)

if ($SelectedSha) {
    $args += @("--selected-sha", $SelectedSha)
}

if ($Output) {
    $args += @("--output", $Output)
}

Push-Location $repoRoot
try {
    & $pythonExe @args
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
