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

$backendRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$projectRoot = (Resolve-Path (Join-Path $backendRoot "..")).Path
$localTmp = Join-Path $projectRoot ".tmp\\pip"
New-Item -ItemType Directory -Path $localTmp -Force | Out-Null
$env:TMP = $localTmp
$env:TEMP = $localTmp

if (-not (Test-Path (Join-Path $projectRoot ".venv"))) {
    Push-Location $projectRoot
    try {
        Invoke-CheckedCommand -Exe $PythonExe -Args @("-m", "venv", ".venv")
    }
    finally {
        Pop-Location
    }
}

if ($UpgradePip) {
    Push-Location $projectRoot
    try {
        Invoke-CheckedCommand -Exe ".\.venv\Scripts\python" -Args @(
            "-m", "pip", "install", "--upgrade", "pip", "--disable-pip-version-check"
        )
    }
    finally {
        Pop-Location
    }
}

Push-Location $backendRoot
try {
    Invoke-CheckedCommand -Exe "..\.venv\Scripts\python" -Args @(
        "-m", "pip", "install", "-e", ".[dev]", "--disable-pip-version-check"
    )
}
finally {
    Pop-Location
}

if (-not (Test-Path (Join-Path $projectRoot ".env"))) {
    Copy-Item (Join-Path $projectRoot ".env.example") (Join-Path $projectRoot ".env")
}

Write-Host "Windows environment is ready."
Write-Host "1) Fill secrets in .env"
Write-Host "2) Run tests: Push-Location .\\backend; ..\\.venv\\Scripts\\python -m pytest -q; Pop-Location"
Write-Host "3) Start stack: docker compose up --build"
