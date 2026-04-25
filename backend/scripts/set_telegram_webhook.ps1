param(
    [Parameter(Mandatory = $true)][string]$WebhookUrl,
    [string]$ApiBase = "http://localhost:8000",
    [string]$SecretToken = ""
)

$body = @{
    webhook_url = $WebhookUrl
}

if ($SecretToken -ne "") {
    $body.secret_token = $SecretToken
}

$json = $body | ConvertTo-Json

Invoke-RestMethod `
    -Uri "$ApiBase/telegram/set-webhook" `
    -Method Post `
    -Body $json `
    -ContentType "application/json"

