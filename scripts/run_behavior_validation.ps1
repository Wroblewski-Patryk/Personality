param(
    [string]$PythonExe = ".\.venv\Scripts\python",
    [string]$ArtifactPath = "artifacts/behavior_validation/report.json",
    [switch]$PrintArtifactJson,
    [ValidateSet("operator", "ci")][string]$GateMode = "operator",
    [bool]$CiRequireTests = $true
)

$ErrorActionPreference = "Stop"

$args = @(
    ".\scripts\run_behavior_validation.py",
    "--python-exe", $PythonExe,
    "--artifact-path", $ArtifactPath,
    "--gate-mode", $GateMode
)
if ($CiRequireTests) {
    $args += "--ci-require-tests"
}
else {
    $args += "--no-ci-require-tests"
}
if ($PrintArtifactJson) {
    $args += "--print-artifact-json"
}

& $PythonExe @args
