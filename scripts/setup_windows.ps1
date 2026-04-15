param(
    [string]$PythonExe = "python",
    [switch]$UpgradePip
)

$ErrorActionPreference = "Stop"

function Invoke-CheckedCommand {
    param(
        [string]$Exe,
        [string[]]$Args
    )

    & $Exe @Args
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed ($LASTEXITCODE): $Exe $($Args -join ' ')"
    }
}

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$localTmp = Join-Path $projectRoot ".tmp\\pip"
New-Item -ItemType Directory -Path $localTmp -Force | Out-Null
$env:TMP = $localTmp
$env:TEMP = $localTmp

if (-not (Test-Path ".venv")) {
    Invoke-CheckedCommand -Exe $PythonExe -Args @("-m", "venv", ".venv")
}

if ($UpgradePip) {
    Invoke-CheckedCommand -Exe ".\.venv\Scripts\python" -Args @(
        "-m", "pip", "install", "--upgrade", "pip", "--disable-pip-version-check"
    )
}

Invoke-CheckedCommand -Exe ".\.venv\Scripts\python" -Args @(
    "-m", "pip", "install", "-e", ".[dev]", "--disable-pip-version-check"
)

if (-not (Test-Path ".env")) {
    Copy-Item .env.example .env
}

Write-Host "Windows environment is ready."
Write-Host "1) Fill secrets in .env"
Write-Host "2) Run tests: .\\.venv\\Scripts\\python -m pytest -q"
Write-Host "3) Start stack: docker compose up --build"
