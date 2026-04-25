param(
    [string]$BotToken = "",
    [string]$ExpectedWebhookUrl = "",
    [string]$RestoreWebhookUrl = "",
    [string]$SecretToken = "",
    [int]$ListenTimeoutSeconds = 2,
    [int]$ListenLimit = 5,
    [string]$RequiredChatId = ""
)

if (-not $BotToken) {
    $BotToken = [string]$env:TELEGRAM_BOT_TOKEN
}
if (-not $BotToken) {
    throw "Missing bot token. Pass -BotToken or set TELEGRAM_BOT_TOKEN."
}

if ($ListenTimeoutSeconds -lt 0) {
    throw "ListenTimeoutSeconds must be >= 0."
}
if ($ListenLimit -lt 1 -or $ListenLimit -gt 100) {
    throw "ListenLimit must be in range 1..100."
}

$telegramApiBase = "https://api.telegram.org/bot$BotToken"
$summary = [ordered]@{
    webhook_mode = [ordered]@{}
    listen_probe = [ordered]@{}
    restore = [ordered]@{}
    preconditions = [ordered]@{
        bot_started_by_user = "required"
        chat_id_available = "required_for_delivery_validation"
    }
    warnings = @()
}

function Invoke-TelegramApi {
    param(
        [Parameter(Mandatory = $true)][string]$Method,
        [hashtable]$Payload = @{}
    )

    $uri = "$telegramApiBase/$Method"
    $response = Invoke-RestMethod -Uri $uri -Method Post -ContentType "application/json" -Body ($Payload | ConvertTo-Json -Compress)
    if (-not $response.ok) {
        $description = [string]$response.description
        if (-not $description) {
            $description = "unknown_error"
        }
        throw "Telegram API '$Method' failed: $description"
    }
    return $response
}

$webhookInfo = Invoke-TelegramApi -Method "getWebhookInfo"
$currentWebhookUrl = [string]$webhookInfo.result.url
$pendingUpdates = 0
if ($null -ne $webhookInfo.result -and $null -ne $webhookInfo.result.pending_update_count) {
    $pendingUpdates = [int]$webhookInfo.result.pending_update_count
}
$summary.webhook_mode = [ordered]@{
    current_url = $currentWebhookUrl
    pending_update_count = $pendingUpdates
}

if ($ExpectedWebhookUrl) {
    $summary.webhook_mode.expected_url = $ExpectedWebhookUrl
    $summary.webhook_mode.matches_expected = [bool]($currentWebhookUrl -eq $ExpectedWebhookUrl)
    if ($currentWebhookUrl -ne $ExpectedWebhookUrl) {
        $summary.warnings += "webhook_url_mismatch"
    }
}

if (-not $RestoreWebhookUrl) {
    $RestoreWebhookUrl = $currentWebhookUrl
}

if (-not $RestoreWebhookUrl) {
    throw "Cannot restore webhook automatically: no current webhook URL and no -RestoreWebhookUrl provided."
}

$null = Invoke-TelegramApi -Method "deleteWebhook" -Payload @{drop_pending_updates = $false}
$updatesResponse = Invoke-TelegramApi -Method "getUpdates" -Payload @{
    timeout = $ListenTimeoutSeconds
    limit = $ListenLimit
}

$updates = @($updatesResponse.result)
$chatIds = @()
foreach ($item in $updates) {
    if ($null -ne $item.message -and $null -ne $item.message.chat -and $null -ne $item.message.chat.id) {
        $chatIds += [string]$item.message.chat.id
    }
}
$chatIds = @($chatIds | Select-Object -Unique)

$listenState = if ($updates.Count -gt 0) { "updates_received" } else { "no_updates" }
$summary.listen_probe = [ordered]@{
    state = $listenState
    updates_count = $updates.Count
    discovered_chat_ids = $chatIds
}

if ($RequiredChatId) {
    $requiredPresent = $chatIds -contains [string]$RequiredChatId
    $summary.listen_probe.required_chat_id = $RequiredChatId
    $summary.listen_probe.required_chat_id_present = $requiredPresent
    if (-not $requiredPresent) {
        throw "Required chat_id '$RequiredChatId' not found in getUpdates probe."
    }
}
elseif ($chatIds.Count -eq 0) {
    $summary.warnings += "no_chat_id_detected_verify_bot_start_handshake"
}

$restorePayload = @{url = $RestoreWebhookUrl}
if ($SecretToken) {
    $restorePayload.secret_token = $SecretToken
}
$restoreResponse = Invoke-TelegramApi -Method "setWebhook" -Payload $restorePayload
$summary.restore = [ordered]@{
    webhook_url = $RestoreWebhookUrl
    ok = [bool]$restoreResponse.ok
}

$summary | ConvertTo-Json -Depth 6
