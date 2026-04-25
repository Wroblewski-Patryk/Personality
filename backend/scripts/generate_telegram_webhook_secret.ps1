param(
    [int]$Bytes = 32,
    [string]$EnvPath = ".env",
    [switch]$UpdateEnv
)

$ErrorActionPreference = "Stop"

if ($Bytes -lt 16) {
    throw "Bytes must be >= 16 for sufficient entropy."
}

$buffer = New-Object byte[] $Bytes
[System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($buffer)

$secret = [Convert]::ToBase64String($buffer)
$secret = $secret.Replace("+", "-").Replace("/", "_").TrimEnd("=")

if ($UpdateEnv) {
    if (-not (Test-Path $EnvPath)) {
        throw "Env file not found: $EnvPath"
    }

    $content = Get-Content -Raw -Path $EnvPath
    if ($content -match "(?m)^TELEGRAM_WEBHOOK_SECRET=") {
        $content = [System.Text.RegularExpressions.Regex]::Replace(
            $content,
            "(?m)^TELEGRAM_WEBHOOK_SECRET=.*$",
            "TELEGRAM_WEBHOOK_SECRET=$secret"
        )
    } else {
        if ($content.Length -gt 0 -and -not $content.EndsWith("`n")) {
            $content += "`r`n"
        }
        $content += "TELEGRAM_WEBHOOK_SECRET=$secret`r`n"
    }

    $resolved = (Resolve-Path $EnvPath).Path
    [System.IO.File]::WriteAllText($resolved, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Output "Updated $EnvPath"
}

Write-Output "TELEGRAM_WEBHOOK_SECRET=$secret"
