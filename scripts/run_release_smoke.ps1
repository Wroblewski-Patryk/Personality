param(
    [Parameter(Mandatory = $true)][string]$BaseUrl,
    [string]$Text = "AION manual smoke test",
    [string]$UserId = "manual-smoke",
    [switch]$IncludeDebug
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName System.Net.Http

function Invoke-JsonUtf8 {
    param(
        [Parameter(Mandatory = $true)][ValidateSet("GET", "POST")][string]$Method,
        [Parameter(Mandatory = $true)][string]$Uri,
        [byte[]]$BodyBytes = $null
    )

    $handler = [System.Net.Http.HttpClientHandler]::new()
    $client = [System.Net.Http.HttpClient]::new($handler)
    try {
        $request = [System.Net.Http.HttpRequestMessage]::new([System.Net.Http.HttpMethod]::$Method, $Uri)
        if ($Method -eq "POST") {
            $content = [System.Net.Http.ByteArrayContent]::new($BodyBytes)
            $content.Headers.ContentType = [System.Net.Http.Headers.MediaTypeHeaderValue]::Parse("application/json; charset=utf-8")
            $request.Content = $content
        }

        $response = $client.SendAsync($request).GetAwaiter().GetResult()
        $response.EnsureSuccessStatusCode() | Out-Null
        $bytes = $response.Content.ReadAsByteArrayAsync().GetAwaiter().GetResult()
        $json = [System.Text.Encoding]::UTF8.GetString($bytes)
        return $json | ConvertFrom-Json
    }
    finally {
        if ($null -ne $client) {
            $client.Dispose()
        }
        if ($null -ne $handler) {
            $handler.Dispose()
        }
    }
}

$trimmedBaseUrl = $BaseUrl.TrimEnd("/")
$traceId = [guid]::NewGuid().ToString()
$eventUrl = "$trimmedBaseUrl/event"
if ($IncludeDebug) {
    $eventUrl = "${eventUrl}?debug=true"
}

$payload = @{
    source    = "api"
    subsource = "manual_smoke"
    text      = $Text
    meta      = @{
        user_id  = $UserId
        trace_id = $traceId
    }
}

$json = $payload | ConvertTo-Json -Depth 6 -Compress
$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($json)

$health = Invoke-JsonUtf8 -Method GET -Uri "$trimmedBaseUrl/health"
if ($health.status -ne "ok") {
    throw "Health check failed: unexpected status '$($health.status)'."
}

$response = Invoke-JsonUtf8 -Method POST -Uri $eventUrl -BodyBytes $bodyBytes

if (-not $response.event_id) {
    throw "Smoke request failed: response is missing event_id."
}

if (-not $response.reply -or -not $response.reply.message) {
    throw "Smoke request failed: response is missing reply.message."
}

if (-not $response.runtime -or -not $response.runtime.role) {
    throw "Smoke request failed: response is missing runtime.role."
}

if ($IncludeDebug -and -not $response.debug) {
    throw "Smoke request failed: debug=true was requested but debug payload is missing."
}

$summary = @{
    base_url             = $trimmedBaseUrl
    health_status        = $health.status
    reflection_healthy   = $health.reflection.healthy
    event_id             = $response.event_id
    trace_id             = $response.trace_id
    reply_message        = $response.reply.message
    reply_language       = $response.reply.language
    runtime_role         = $response.runtime.role
    runtime_action       = $response.runtime.action_status
    reflection_triggered = $response.runtime.reflection_triggered
    debug_included       = [bool]$response.debug
}

$summary | ConvertTo-Json -Depth 6
