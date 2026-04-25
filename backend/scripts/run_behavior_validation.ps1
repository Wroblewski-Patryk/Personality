param(
    [string]$PythonExe = ".\.venv\Scripts\python",
    [string]$ArtifactPath = "artifacts/behavior_validation/report.json",
    [switch]$PrintArtifactJson,
    [ValidateSet("operator", "ci")][string]$GateMode = "operator",
    [bool]$CiRequireTests = $true,
    [string]$ArtifactInputPath = "",
    [string]$IncidentEvidenceInputPath = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonCommand = $PythonExe
if (-not [System.IO.Path]::IsPathRooted($pythonCommand)) {
    $pythonCommand = Join-Path $repoRoot ($pythonCommand -replace '^[.][\\/]', '')
}

$args = @(
    (Join-Path $PSScriptRoot "run_behavior_validation.py"),
    "--python-exe", $PythonExe,
    "--artifact-path", $ArtifactPath,
    "--gate-mode", $GateMode
)
if ($ArtifactInputPath) {
    $args += @("--artifact-input-path", $ArtifactInputPath)
}
if ($IncidentEvidenceInputPath) {
    $args += @("--incident-evidence-input-path", $IncidentEvidenceInputPath)
}
if ($CiRequireTests) {
    $args += "--ci-require-tests"
}
else {
    $args += "--no-ci-require-tests"
}
if ($PrintArtifactJson) {
    $args += "--print-artifact-json"
}

Push-Location $repoRoot
try {
    & $pythonCommand @args
}
finally {
    Pop-Location
}
