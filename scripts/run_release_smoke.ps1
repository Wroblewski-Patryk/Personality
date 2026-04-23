param(
    [Parameter(Mandatory = $true)][string]$BaseUrl,
    [string]$Text = "AION manual smoke test",
    [string]$UserId = "manual-smoke",
    [switch]$IncludeDebug,
    [string]$DeploymentEvidencePath = "",
    [int]$DeploymentEvidenceMaxAgeMinutes = 60,
    [string]$IncidentEvidenceBundlePath = ""
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

function Has-Property {
    param(
        [object]$Object,
        [Parameter(Mandatory = $true)][string]$Name
    )
    return $null -ne $Object -and $Object.PSObject.Properties.Name -contains $Name
}

function ConvertFrom-JsonCompat {
    param(
        [Parameter(Mandatory = $true)][string]$Json
    )

    $command = Get-Command ConvertFrom-Json -ErrorAction Stop
    if ($command.Parameters.ContainsKey("Depth")) {
        return $Json | ConvertFrom-Json -Depth 8
    }

    return $Json | ConvertFrom-Json
}

function Validate-DeploymentEvidence {
    param(
        [string]$Path,
        [int]$MaxAgeMinutes
    )

    $result = @{
        checked     = $false
        path        = $Path
        age_minutes = $null
        status_code = $null
    }

    if (-not $Path) {
        return $result
    }

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Deployment evidence verification failed: file not found '$Path'."
    }

    try {
        $raw = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
        $evidence = ConvertFrom-JsonCompat -Json $raw
    }
    catch {
        throw "Deployment evidence verification failed: invalid JSON in '$Path'."
    }

    if ([string]$evidence.kind -ne "coolify_deploy_webhook_evidence") {
        throw "Deployment evidence verification failed: unexpected kind '$($evidence.kind)'."
    }

    if ($null -eq $evidence.response) {
        throw "Deployment evidence verification failed: response block is missing."
    }

    $responseOk = [bool]$evidence.response.ok
    $statusCode = 0
    try {
        $statusCode = [int]$evidence.response.status_code
    }
    catch {
        $statusCode = 0
    }

    if (-not $responseOk -or $statusCode -lt 200 -or $statusCode -ge 300) {
        throw "Deployment evidence verification failed: webhook response is not successful."
    }

    $generatedAtRaw = [string]$evidence.generated_at
    if (-not $generatedAtRaw) {
        throw "Deployment evidence verification failed: generated_at is missing."
    }

    try {
        $generatedAt = [datetimeoffset]::Parse($generatedAtRaw).ToUniversalTime()
    }
    catch {
        throw "Deployment evidence verification failed: generated_at is invalid '$generatedAtRaw'."
    }

    $ageMinutes = ([datetimeoffset]::UtcNow - $generatedAt).TotalMinutes
    if ($ageMinutes -gt $MaxAgeMinutes) {
        throw "Deployment evidence verification failed: evidence age $([math]::Round($ageMinutes, 2)) min exceeds $MaxAgeMinutes min."
    }

    return @{
        checked     = $true
        path        = $Path
        age_minutes = [math]::Round($ageMinutes, 2)
        status_code = $statusCode
    }
}

function Validate-IncidentEvidenceBundle {
    param(
        [string]$Path
    )

    $result = @{
        checked                  = $false
        path                     = $Path
        manifest_schema_version  = $null
        capture_mode             = $null
        trace_id                 = $null
        event_id                 = $null
        behavior_report_attached = $false
        policy_surface_complete  = $null
        health_status            = $null
        debug_posture_state      = $null
        debug_exception_state    = $null
        telegram_round_trip_state = $null
        attention_coordination_mode = $null
        attention_contract_store_state = $null
        attention_runtime_topology_selected_mode = $null
        proactive_policy_owner = $null
        proactive_enabled = $null
        proactive_production_baseline_state = $null
        retrieval_policy_owner = $null
        retrieval_provider_requested = $null
        retrieval_provider_effective = $null
        retrieval_execution_class = $null
        retrieval_baseline_state = $null
        retrieval_provider_drift_state = $null
        retrieval_alignment_state = $null
    }

    if (-not $Path) {
        return $result
    }

    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        throw "Incident evidence bundle verification failed: directory not found '$Path'."
    }

    $manifestPath = Join-Path -Path $Path -ChildPath "manifest.json"
    $incidentEvidencePath = Join-Path -Path $Path -ChildPath "incident_evidence.json"
    $healthSnapshotPath = Join-Path -Path $Path -ChildPath "health_snapshot.json"

    foreach ($requiredPath in @($manifestPath, $incidentEvidencePath, $healthSnapshotPath)) {
        if (-not (Test-Path -LiteralPath $requiredPath)) {
            throw "Incident evidence bundle verification failed: required file missing '$requiredPath'."
        }
    }

    try {
        $manifest = ConvertFrom-JsonCompat -Json (Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8)
        $incidentEvidence = ConvertFrom-JsonCompat -Json (Get-Content -LiteralPath $incidentEvidencePath -Raw -Encoding UTF8)
        $healthSnapshot = ConvertFrom-JsonCompat -Json (Get-Content -LiteralPath $healthSnapshotPath -Raw -Encoding UTF8)
    }
    catch {
        throw "Incident evidence bundle verification failed: invalid JSON inside '$Path'."
    }

    if ([string]$manifest.kind -ne "incident_evidence_bundle_manifest") {
        throw "Incident evidence bundle verification failed: unexpected manifest kind '$($manifest.kind)'."
    }
    if ([string]$manifest.policy_owner -ne "incident_evidence_export_policy") {
        throw "Incident evidence bundle verification failed: unexpected manifest policy owner '$($manifest.policy_owner)'."
    }
    if ([string]$incidentEvidence.kind -ne "runtime_incident_evidence") {
        throw "Incident evidence bundle verification failed: unexpected incident evidence kind '$($incidentEvidence.kind)'."
    }
    if ([string]$incidentEvidence.policy_owner -ne "incident_evidence_export_policy") {
        throw "Incident evidence bundle verification failed: unexpected incident evidence policy owner '$($incidentEvidence.policy_owner)'."
    }
    if ([string]$healthSnapshot.status -ne "ok") {
        throw "Incident evidence bundle verification failed: unexpected health snapshot status '$($healthSnapshot.status)'."
    }

    $manifestTraceId = [string]$manifest.trace_id
    $manifestEventId = [string]$manifest.event_id
    if ($manifestTraceId -and [string]$incidentEvidence.trace_id -ne $manifestTraceId) {
        throw "Incident evidence bundle verification failed: manifest trace_id does not match incident evidence."
    }
    if ($manifestEventId -and [string]$incidentEvidence.event_id -ne $manifestEventId) {
        throw "Incident evidence bundle verification failed: manifest event_id does not match incident evidence."
    }

    $behaviorReportAttached = $false
    if ($null -ne $manifest.files -and $manifest.files.PSObject.Properties.Name -contains "behavior_validation_report") {
        $behaviorReportPath = Join-Path -Path $Path -ChildPath ([string]$manifest.files.behavior_validation_report)
        if (-not (Test-Path -LiteralPath $behaviorReportPath)) {
            throw "Incident evidence bundle verification failed: manifest references missing behavior_validation_report '$behaviorReportPath'."
        }
        $behaviorReportAttached = $true
    }

    $policySurfaceComplete = $false
    if ($null -ne $incidentEvidence.policy_surface_coverage -and $incidentEvidence.policy_surface_coverage.PSObject.Properties.Name -contains "complete") {
        $policySurfaceComplete = [bool]$incidentEvidence.policy_surface_coverage.complete
    }
    if (-not $policySurfaceComplete) {
        throw "Incident evidence bundle verification failed: policy surface coverage is incomplete."
    }

    $debugPosture = Assert-DedicatedAdminDebugPosture -RuntimePolicy $incidentEvidence.policy_posture.runtime_policy -FailurePrefix "Incident evidence bundle verification failed"
    $telegramConversation = $incidentEvidence.policy_posture."conversation_channels.telegram"
    if ($null -eq $telegramConversation) {
        throw "Incident evidence bundle verification failed: conversation_channels.telegram posture is missing."
    }
    if ([string]$telegramConversation.policy_owner -ne "telegram_conversation_reliability_telemetry") {
        throw "Incident evidence bundle verification failed: unexpected conversation_channels.telegram policy_owner '$($telegramConversation.policy_owner)'."
    }
    $validTelegramRoundTripStates = @(
        "provider_backed_ready",
        "missing_bot_token"
    )
    if ($validTelegramRoundTripStates -notcontains [string]$telegramConversation.round_trip_state) {
        throw "Incident evidence bundle verification failed: unexpected conversation_channels.telegram round_trip_state '$($telegramConversation.round_trip_state)'."
    }
    $attention = $incidentEvidence.policy_posture.attention
    if ($null -eq $attention) {
        throw "Incident evidence bundle verification failed: attention posture is missing."
    }
    if ([string]$attention.attention_policy_owner -ne "durable_attention_inbox_policy") {
        throw "Incident evidence bundle verification failed: unexpected attention policy owner '$($attention.attention_policy_owner)'."
    }
    if ([string]$attention.coordination_mode -ne "durable_inbox") {
        throw "Incident evidence bundle verification failed: unexpected attention coordination mode '$($attention.coordination_mode)'."
    }
    if ($null -eq $attention.deployment_readiness) {
        throw "Incident evidence bundle verification failed: attention deployment_readiness is missing."
    }
    if ([string]$attention.deployment_readiness.selected_coordination_mode -ne "durable_inbox") {
        throw "Incident evidence bundle verification failed: unexpected attention deployment_readiness.selected_coordination_mode '$($attention.deployment_readiness.selected_coordination_mode)'."
    }
    if ([string]$attention.deployment_readiness.contract_store_state -ne "repository_backed_contract_store_active") {
        throw "Incident evidence bundle verification failed: unexpected attention contract_store_state '$($attention.deployment_readiness.contract_store_state)'."
    }
    if (-not [bool]$attention.deployment_readiness.store_available) {
        throw "Incident evidence bundle verification failed: attention durable store is not available."
    }
    $runtimeTopologyAttention = $incidentEvidence.policy_posture."runtime_topology.attention_switch"
    if ($null -eq $runtimeTopologyAttention) {
        throw "Incident evidence bundle verification failed: runtime_topology.attention_switch posture is missing."
    }
    if ([string]$runtimeTopologyAttention.policy_owner -ne "runtime_topology_finalization") {
        throw "Incident evidence bundle verification failed: unexpected runtime_topology.attention_switch policy_owner '$($runtimeTopologyAttention.policy_owner)'."
    }
    if ([string]$runtimeTopologyAttention.selected_mode -ne "durable_inbox") {
        throw "Incident evidence bundle verification failed: unexpected runtime_topology.attention_switch selected_mode '$($runtimeTopologyAttention.selected_mode)'."
    }
    if (-not [bool]$runtimeTopologyAttention.production_default_change_ready) {
        throw "Incident evidence bundle verification failed: runtime_topology.attention_switch production_default_change_ready is not true."
    }
    $proactive = $incidentEvidence.policy_posture.proactive
    if ($null -eq $proactive) {
        throw "Incident evidence bundle verification failed: proactive posture is missing."
    }
    if ([string]$proactive.policy_owner -ne "proactive_runtime_policy") {
        throw "Incident evidence bundle verification failed: unexpected proactive policy_owner '$($proactive.policy_owner)'."
    }
    if (-not [bool]$proactive.enabled) {
        throw "Incident evidence bundle verification failed: proactive enabled flag is not true."
    }
    if (-not [bool]$proactive.production_baseline_ready) {
        throw "Incident evidence bundle verification failed: proactive production_baseline_ready is not true."
    }
    if ([string]$proactive.production_baseline_state -eq "disabled_by_policy") {
        throw "Incident evidence bundle verification failed: proactive production baseline is still disabled_by_policy."
    }
    $retrieval = $incidentEvidence.policy_posture.memory_retrieval
    $retrievalAlignment = Assert-RetrievalAlignmentPosture `
        -MemoryRetrieval $retrieval `
        -FailurePrefix "Incident evidence bundle verification failed"
    $learnedState = $incidentEvidence.policy_posture.learned_state
    if ($null -eq $learnedState) {
        throw "Incident evidence bundle verification failed: learned_state posture is missing."
    }
    if ([string]$learnedState.policy_owner -ne "learned_state_inspection_policy") {
        throw "Incident evidence bundle verification failed: unexpected learned_state policy_owner '$($learnedState.policy_owner)'."
    }
    if ([string]$learnedState.internal_inspection_path -ne "/internal/state/inspect") {
        throw "Incident evidence bundle verification failed: unexpected learned_state internal_inspection_path '$($learnedState.internal_inspection_path)'."
    }
    $v1Readiness = $incidentEvidence.policy_posture.v1_readiness
    if ($null -eq $v1Readiness) {
        throw "Incident evidence bundle verification failed: v1_readiness posture is missing."
    }
    if ([string]$v1Readiness.policy_owner -ne "v1_release_readiness_policy") {
        throw "Incident evidence bundle verification failed: unexpected v1_readiness policy_owner '$($v1Readiness.policy_owner)'."
    }
    if ([string]$v1Readiness.product_stage -ne "v1_no_ui_life_assistant") {
        throw "Incident evidence bundle verification failed: unexpected v1_readiness product_stage '$($v1Readiness.product_stage)'."
    }
    if ([string]$v1Readiness.conversation_gate_state -ne "conversation_surface_ready") {
        throw "Incident evidence bundle verification failed: unexpected v1_readiness conversation_gate_state '$($v1Readiness.conversation_gate_state)'."
    }
    if ([string]$v1Readiness.learned_state_gate_state -ne "inspection_surface_ready") {
        throw "Incident evidence bundle verification failed: unexpected v1_readiness learned_state_gate_state '$($v1Readiness.learned_state_gate_state)'."
    }

    return @{
        checked                  = $true
        path                     = $Path
        manifest_schema_version  = [string]$manifest.schema_version
        capture_mode             = [string]$manifest.capture_mode
        trace_id                 = [string]$incidentEvidence.trace_id
        event_id                 = [string]$incidentEvidence.event_id
        behavior_report_attached = $behaviorReportAttached
        policy_surface_complete  = $policySurfaceComplete
        health_status            = [string]$healthSnapshot.status
        debug_posture_state      = [string]$debugPosture.debug_posture_state
        debug_exception_state    = [string]$debugPosture.debug_exception_state
        telegram_round_trip_state = [string]$telegramConversation.round_trip_state
        attention_coordination_mode = [string]$attention.coordination_mode
        attention_contract_store_state = [string]$attention.deployment_readiness.contract_store_state
        attention_runtime_topology_selected_mode = [string]$runtimeTopologyAttention.selected_mode
        proactive_policy_owner = [string]$proactive.policy_owner
        proactive_enabled = [bool]$proactive.enabled
        proactive_production_baseline_state = [string]$proactive.production_baseline_state
        retrieval_policy_owner = [string]$retrievalAlignment.retrieval_policy_owner
        retrieval_provider_requested = [string]$retrievalAlignment.provider_requested
        retrieval_provider_effective = [string]$retrievalAlignment.provider_effective
        retrieval_execution_class = [string]$retrievalAlignment.execution_class
        retrieval_baseline_state = [string]$retrievalAlignment.production_baseline_state
        retrieval_provider_drift_state = [string]$retrievalAlignment.provider_drift_state
        retrieval_alignment_state = [string]$retrievalAlignment.alignment_state
    }
}

function Assert-DedicatedAdminDebugPosture {
    param(
        [object]$RuntimePolicy,
        [Parameter(Mandatory = $true)][string]$FailurePrefix
    )

    if ($null -eq $RuntimePolicy) {
        throw "${FailurePrefix}: incident evidence runtime_policy posture is missing."
    }
    if ([string]$RuntimePolicy.event_debug_admin_policy_owner -ne "dedicated_admin_debug_ingress_policy") {
        throw "${FailurePrefix}: unexpected incident-evidence debug admin policy owner '$($RuntimePolicy.event_debug_admin_policy_owner)'."
    }
    if ([string]$RuntimePolicy.event_debug_admin_ingress_target_path -ne "/internal/event/debug") {
        throw "${FailurePrefix}: unexpected incident-evidence debug admin ingress target '$($RuntimePolicy.event_debug_admin_ingress_target_path)'."
    }
    if ([string]$RuntimePolicy.event_debug_shared_ingress_mode -ne "break_glass_only") {
        throw "${FailurePrefix}: incident-evidence shared debug ingress is not retired to break-glass-only mode."
    }
    if ([string]$RuntimePolicy.event_debug_shared_ingress_posture -ne "shared_route_break_glass_only") {
        throw "${FailurePrefix}: unexpected incident-evidence shared debug posture '$($RuntimePolicy.event_debug_shared_ingress_posture)'."
    }
    if ([bool]$RuntimePolicy.event_debug_query_compat_enabled) {
        throw "${FailurePrefix}: incident-evidence query debug compatibility route is still enabled."
    }
    if (-not [bool]$RuntimePolicy.event_debug_shared_ingress_retirement_ready) {
        throw "${FailurePrefix}: incident-evidence shared debug retirement gate is not ready."
    }
    if (-not [bool]$RuntimePolicy.event_debug_shared_ingress_sunset_ready) {
        throw "${FailurePrefix}: incident-evidence shared debug sunset posture is not ready."
    }

    $debugExceptionReason = [string]$RuntimePolicy.event_debug_shared_ingress_sunset_reason
    $debugExceptionState = switch ($debugExceptionReason) {
        "shared_debug_route_disabled_with_debug_payload_off" { "shared_debug_disabled" }
        "shared_debug_route_break_glass_only" { "shared_debug_break_glass_only" }
        default { "" }
    }
    if (-not $debugExceptionState) {
        throw "${FailurePrefix}: incident-evidence debug rollback exception posture is not explicit."
    }

    return @{
        debug_posture_state   = "dedicated_admin_only"
        debug_exception_state = $debugExceptionState
    }
}

function Assert-RetrievalAlignmentPosture {
    param(
        [object]$MemoryRetrieval,
        [Parameter(Mandatory = $true)][string]$FailurePrefix
    )

    if ($null -eq $MemoryRetrieval) {
        throw "${FailurePrefix}: memory_retrieval posture is missing."
    }
    if ([string]$MemoryRetrieval.retrieval_lifecycle_policy_owner -ne "retrieval_lifecycle_policy") {
        throw "${FailurePrefix}: unexpected memory_retrieval policy_owner '$($MemoryRetrieval.retrieval_lifecycle_policy_owner)'."
    }
    if ([string]$MemoryRetrieval.semantic_embedding_provider_requested -ne "openai") {
        throw "${FailurePrefix}: unexpected memory_retrieval semantic_embedding_provider_requested '$($MemoryRetrieval.semantic_embedding_provider_requested)'."
    }
    if ([string]$MemoryRetrieval.semantic_embedding_provider_effective -ne "openai") {
        throw "${FailurePrefix}: unexpected memory_retrieval semantic_embedding_provider_effective '$($MemoryRetrieval.semantic_embedding_provider_effective)'."
    }
    if ([string]$MemoryRetrieval.semantic_embedding_model_requested -ne "text-embedding-3-small") {
        throw "${FailurePrefix}: unexpected memory_retrieval semantic_embedding_model_requested '$($MemoryRetrieval.semantic_embedding_model_requested)'."
    }
    if ([string]$MemoryRetrieval.semantic_embedding_model_effective -ne "text-embedding-3-small") {
        throw "${FailurePrefix}: unexpected memory_retrieval semantic_embedding_model_effective '$($MemoryRetrieval.semantic_embedding_model_effective)'."
    }
    if ([string]$MemoryRetrieval.semantic_embedding_execution_class -ne "provider_owned_openai_api") {
        throw "${FailurePrefix}: unexpected memory_retrieval semantic_embedding_execution_class '$($MemoryRetrieval.semantic_embedding_execution_class)'."
    }
    if ([string]$MemoryRetrieval.semantic_embedding_production_baseline_state -ne "aligned_openai_provider_owned") {
        throw "${FailurePrefix}: unexpected memory_retrieval semantic_embedding_production_baseline_state '$($MemoryRetrieval.semantic_embedding_production_baseline_state)'."
    }
    if ([string]$MemoryRetrieval.retrieval_lifecycle_provider_drift_state -ne "aligned_target_provider") {
        throw "${FailurePrefix}: unexpected memory_retrieval retrieval_lifecycle_provider_drift_state '$($MemoryRetrieval.retrieval_lifecycle_provider_drift_state)'."
    }
    if ([string]$MemoryRetrieval.retrieval_lifecycle_alignment_state -ne "aligned_with_defined_lifecycle_baseline") {
        throw "${FailurePrefix}: unexpected memory_retrieval retrieval_lifecycle_alignment_state '$($MemoryRetrieval.retrieval_lifecycle_alignment_state)'."
    }
    $pendingGaps = @($MemoryRetrieval.retrieval_lifecycle_pending_gaps)
    if ($pendingGaps.Count -ne 0) {
        throw "${FailurePrefix}: memory_retrieval retrieval_lifecycle_pending_gaps is not empty."
    }

    return @{
        retrieval_policy_owner = [string]$MemoryRetrieval.retrieval_lifecycle_policy_owner
        provider_requested = [string]$MemoryRetrieval.semantic_embedding_provider_requested
        provider_effective = [string]$MemoryRetrieval.semantic_embedding_provider_effective
        model_requested = [string]$MemoryRetrieval.semantic_embedding_model_requested
        model_effective = [string]$MemoryRetrieval.semantic_embedding_model_effective
        execution_class = [string]$MemoryRetrieval.semantic_embedding_execution_class
        production_baseline_state = [string]$MemoryRetrieval.semantic_embedding_production_baseline_state
        provider_drift_state = [string]$MemoryRetrieval.retrieval_lifecycle_provider_drift_state
        alignment_state = [string]$MemoryRetrieval.retrieval_lifecycle_alignment_state
        pending_gaps = @()
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
$deploymentEvidenceCheck = Validate-DeploymentEvidence -Path $DeploymentEvidencePath -MaxAgeMinutes $DeploymentEvidenceMaxAgeMinutes
$incidentEvidenceBundleCheck = Validate-IncidentEvidenceBundle -Path $IncidentEvidenceBundlePath

$health = Invoke-JsonUtf8 -Method GET -Uri "$trimmedBaseUrl/health"
if ($health.status -ne "ok") {
    throw "Health check failed: unexpected status '$($health.status)'."
}

$runtimePolicy = $health.runtime_policy
if ($null -eq $runtimePolicy) {
    throw "Health check failed: response is missing runtime_policy."
}

$expectedInternalDebugIngressPath = "/internal/event/debug"
$expectedSharedDebugIngressPath = "/event/debug"

if (-not (Has-Property -Object $runtimePolicy -Name "event_debug_internal_ingress_path")) {
    throw "Health check failed: runtime_policy is missing event_debug_internal_ingress_path."
}
if (-not (Has-Property -Object $runtimePolicy -Name "event_debug_admin_policy_owner")) {
    throw "Health check failed: runtime_policy is missing event_debug_admin_policy_owner."
}
if (-not (Has-Property -Object $runtimePolicy -Name "event_debug_admin_ingress_target_path")) {
    throw "Health check failed: runtime_policy is missing event_debug_admin_ingress_target_path."
}
if ([string]$runtimePolicy.event_debug_admin_ingress_target_path -ne $expectedInternalDebugIngressPath) {
    throw "Health check failed: unexpected event_debug_admin_ingress_target_path '$($runtimePolicy.event_debug_admin_ingress_target_path)'."
}
if (-not (Has-Property -Object $runtimePolicy -Name "event_debug_admin_posture_state")) {
    throw "Health check failed: runtime_policy is missing event_debug_admin_posture_state."
}
if ([string]$runtimePolicy.event_debug_internal_ingress_path -ne $expectedInternalDebugIngressPath) {
    throw "Health check failed: unexpected event_debug_internal_ingress_path '$($runtimePolicy.event_debug_internal_ingress_path)'."
}
if (-not (Has-Property -Object $runtimePolicy -Name "event_debug_shared_ingress_path")) {
    throw "Health check failed: runtime_policy is missing event_debug_shared_ingress_path."
}
if ([string]$runtimePolicy.event_debug_shared_ingress_path -ne $expectedSharedDebugIngressPath) {
    throw "Health check failed: unexpected event_debug_shared_ingress_path '$($runtimePolicy.event_debug_shared_ingress_path)'."
}
if (-not (Has-Property -Object $runtimePolicy -Name "event_debug_shared_ingress_mode")) {
    throw "Health check failed: runtime_policy is missing event_debug_shared_ingress_mode."
}
$sharedIngressMode = [string]$runtimePolicy.event_debug_shared_ingress_mode
if (@("compatibility", "break_glass_only") -notcontains $sharedIngressMode) {
    throw "Health check failed: unexpected event_debug_shared_ingress_mode '$sharedIngressMode'."
}
if (-not (Has-Property -Object $runtimePolicy -Name "event_debug_shared_ingress_break_glass_required")) {
    throw "Health check failed: runtime_policy is missing event_debug_shared_ingress_break_glass_required."
}
$sharedBreakGlassRequired = [bool]$runtimePolicy.event_debug_shared_ingress_break_glass_required
$expectedSharedBreakGlassRequired = $sharedIngressMode -eq "break_glass_only"
if ($sharedBreakGlassRequired -ne $expectedSharedBreakGlassRequired) {
    throw "Health check failed: inconsistent shared ingress break-glass requirement."
}
if (-not (Has-Property -Object $runtimePolicy -Name "event_debug_shared_ingress_posture")) {
    throw "Health check failed: runtime_policy is missing event_debug_shared_ingress_posture."
}
$sharedIngressPosture = [string]$runtimePolicy.event_debug_shared_ingress_posture
$expectedSharedIngressPosture = if ($expectedSharedBreakGlassRequired) {
    "shared_route_break_glass_only"
}
else {
    "shared_route_compatibility"
}
if ($sharedIngressPosture -ne $expectedSharedIngressPosture) {
    throw "Health check failed: inconsistent shared ingress posture '$sharedIngressPosture'."
}
if (-not (Has-Property -Object $runtimePolicy -Name "event_debug_shared_ingress_retirement_blockers")) {
    throw "Health check failed: runtime_policy is missing event_debug_shared_ingress_retirement_blockers."
}
$debugRetirementBlockers = @($runtimePolicy.event_debug_shared_ingress_retirement_blockers)
$expectedDebugRetirementBlockers = @()
if ($debugEnabledForSunset) {
    if ($sharedIngressMode -eq "compatibility") {
        $expectedDebugRetirementBlockers += "shared_debug_route_still_primary"
    }
    if ([bool]$runtimePolicy.event_debug_query_compat_enabled) {
        $expectedDebugRetirementBlockers += "query_debug_compatibility_still_enabled"
    }
}
if (($debugRetirementBlockers -join ",") -ne ($expectedDebugRetirementBlockers -join ",")) {
    throw "Health check failed: inconsistent event_debug_shared_ingress_retirement_blockers."
}
if (-not (Has-Property -Object $runtimePolicy -Name "event_debug_shared_ingress_retirement_ready")) {
    throw "Health check failed: runtime_policy is missing event_debug_shared_ingress_retirement_ready."
}
if ([bool]$runtimePolicy.event_debug_shared_ingress_retirement_ready -ne ($expectedDebugRetirementBlockers.Count -eq 0)) {
    throw "Health check failed: inconsistent event_debug_shared_ingress_retirement_ready."
}
if (-not (Has-Property -Object $runtimePolicy -Name "startup_schema_compatibility_posture")) {
    throw "Health check failed: runtime_policy is missing startup_schema_compatibility_posture."
}
$startupSchemaCompatibilityPosture = [string]$runtimePolicy.startup_schema_compatibility_posture
if (@("migration_only", "compatibility_create_tables") -notcontains $startupSchemaCompatibilityPosture) {
    throw "Health check failed: unexpected startup_schema_compatibility_posture '$startupSchemaCompatibilityPosture'."
}
if (-not (Has-Property -Object $runtimePolicy -Name "startup_schema_compatibility_sunset_ready")) {
    throw "Health check failed: runtime_policy is missing startup_schema_compatibility_sunset_ready."
}
$startupSchemaCompatibilitySunsetReady = [bool]$runtimePolicy.startup_schema_compatibility_sunset_ready
if (-not (Has-Property -Object $runtimePolicy -Name "startup_schema_compatibility_sunset_reason")) {
    throw "Health check failed: runtime_policy is missing startup_schema_compatibility_sunset_reason."
}
$startupSchemaCompatibilitySunsetReason = [string]$runtimePolicy.startup_schema_compatibility_sunset_reason
$expectedStartupSchemaSunsetReady = $startupSchemaCompatibilityPosture -eq "migration_only"
$expectedStartupSchemaSunsetReason = if ($expectedStartupSchemaSunsetReady) {
    "migration_only_baseline_active"
}
else {
    "create_tables_compatibility_active"
}
if ($startupSchemaCompatibilitySunsetReady -ne $expectedStartupSchemaSunsetReady) {
    throw "Health check failed: inconsistent startup schema sunset readiness."
}
if ($startupSchemaCompatibilitySunsetReason -ne $expectedStartupSchemaSunsetReason) {
    throw "Health check failed: inconsistent startup schema sunset reason '$startupSchemaCompatibilitySunsetReason'."
}
if (-not (Has-Property -Object $runtimePolicy -Name "event_debug_shared_ingress_sunset_ready")) {
    throw "Health check failed: runtime_policy is missing event_debug_shared_ingress_sunset_ready."
}
$sharedIngressSunsetReady = [bool]$runtimePolicy.event_debug_shared_ingress_sunset_ready
if (-not (Has-Property -Object $runtimePolicy -Name "event_debug_shared_ingress_sunset_reason")) {
    throw "Health check failed: runtime_policy is missing event_debug_shared_ingress_sunset_reason."
}
$sharedIngressSunsetReason = [string]$runtimePolicy.event_debug_shared_ingress_sunset_reason
$debugEnabledForSunset = if (Has-Property -Object $runtimePolicy -Name "event_debug_enabled") {
    [bool]$runtimePolicy.event_debug_enabled
}
else {
    $false
}
$expectedSharedIngressSunsetReady = (-not $debugEnabledForSunset) -or $sharedBreakGlassRequired
$expectedSharedIngressSunsetReason = if (-not $debugEnabledForSunset) {
    "shared_debug_route_disabled_with_debug_payload_off"
}
elseif ($sharedBreakGlassRequired) {
    "shared_debug_route_break_glass_only"
}
else {
    "shared_debug_route_still_in_compatibility_mode"
}
if ($sharedIngressSunsetReady -ne $expectedSharedIngressSunsetReady) {
    throw "Health check failed: inconsistent shared ingress sunset readiness."
}
if ($sharedIngressSunsetReason -ne $expectedSharedIngressSunsetReason) {
    throw "Health check failed: inconsistent shared ingress sunset reason '$sharedIngressSunsetReason'."
}
if (-not (Has-Property -Object $runtimePolicy -Name "compatibility_sunset_ready")) {
    throw "Health check failed: runtime_policy is missing compatibility_sunset_ready."
}
$compatibilitySunsetReady = [bool]$runtimePolicy.compatibility_sunset_ready
if (-not (Has-Property -Object $runtimePolicy -Name "compatibility_sunset_blockers")) {
    throw "Health check failed: runtime_policy is missing compatibility_sunset_blockers."
}
$compatibilitySunsetBlockers = @($runtimePolicy.compatibility_sunset_blockers)
$expectedCompatibilitySunsetReady = $startupSchemaCompatibilitySunsetReady -and $sharedIngressSunsetReady
$expectedCompatibilitySunsetBlockers = @()
if (-not $startupSchemaCompatibilitySunsetReady) {
    $expectedCompatibilitySunsetBlockers += "startup_schema_compatibility_active"
}
if (-not $sharedIngressSunsetReady) {
    $expectedCompatibilitySunsetBlockers += "shared_debug_ingress_compatibility_mode_active"
}
if ($compatibilitySunsetReady -ne $expectedCompatibilitySunsetReady) {
    throw "Health check failed: inconsistent compatibility_sunset_ready."
}
if (($compatibilitySunsetBlockers -join ",") -ne ($expectedCompatibilitySunsetBlockers -join ",")) {
    throw "Health check failed: inconsistent compatibility_sunset_blockers."
}

$releaseReadiness = $health.release_readiness
$releaseReadinessReady = $true
$releaseReadinessViolations = @()

if ($null -ne $releaseReadiness -and $releaseReadiness.PSObject.Properties.Name -contains "ready") {
    $releaseReadinessReady = [bool]$releaseReadiness.ready
    if ($releaseReadiness.PSObject.Properties.Name -contains "violations" -and $null -ne $releaseReadiness.violations) {
        $releaseReadinessViolations = @($releaseReadiness.violations)
    }
}
else {
    $fallbackViolations = @()
    $policyMismatches = @()
    if (
        $runtimePolicy.PSObject.Properties.Name -contains "production_policy_mismatches" -and
        $null -ne $runtimePolicy.production_policy_mismatches
    ) {
        $policyMismatches = @($runtimePolicy.production_policy_mismatches)
    }
    if ($policyMismatches.Count -gt 0) {
        $fallbackViolations += "runtime_policy.production_policy_mismatches_non_empty"
    }
    if ([bool]$runtimePolicy.strict_startup_blocked) {
        $fallbackViolations += "runtime_policy.strict_startup_blocked=true"
    }
    if ([bool]$runtimePolicy.event_debug_query_compat_enabled) {
        $fallbackViolations += "runtime_policy.event_debug_query_compat_enabled=true"
    }
    $releaseReadinessViolations = $fallbackViolations
    $releaseReadinessReady = $releaseReadinessViolations.Count -eq 0
}

if (-not $releaseReadinessReady) {
    $details = if ($releaseReadinessViolations.Count -gt 0) {
        ($releaseReadinessViolations -join ",")
    }
    else {
        "unspecified"
    }
    throw "Release readiness check failed: $details."
}

$reflection = $health.reflection
if ($null -eq $reflection) {
    throw "Health check failed: response is missing reflection."
}

$reflectionDeploymentReadiness = if (Has-Property -Object $reflection -Name "deployment_readiness") {
    $reflection.deployment_readiness
}
else {
    $null
}
$reflectionExternalDriverPolicy = if (Has-Property -Object $reflection -Name "external_driver_policy") {
    $reflection.external_driver_policy
}
else {
    $null
}
$reflectionSupervision = if (Has-Property -Object $reflection -Name "supervision") {
    $reflection.supervision
}
else {
    $null
}
$reflectionDeploymentReady = $true
$reflectionDeploymentBlockingSignals = @()

if ($null -ne $reflectionDeploymentReadiness -and (Has-Property -Object $reflectionDeploymentReadiness -Name "ready")) {
    $reflectionDeploymentReady = [bool]$reflectionDeploymentReadiness.ready
    if ((Has-Property -Object $reflectionDeploymentReadiness -Name "blocking_signals") -and $null -ne $reflectionDeploymentReadiness.blocking_signals) {
        $reflectionDeploymentBlockingSignals = @($reflectionDeploymentReadiness.blocking_signals)
    }
}
else {
    $runtimeMode = if (Has-Property -Object $reflection -Name "runtime_mode") {
        [string]$reflection.runtime_mode
    }
    else {
        "in_process"
    }
    $workerRunning = if ((Has-Property -Object $reflection -Name "worker") -and $null -ne $reflection.worker -and (Has-Property -Object $reflection.worker -Name "running")) {
        [bool]$reflection.worker.running
    }
    else {
        $false
    }
    $topology = if (Has-Property -Object $reflection -Name "topology") {
        $reflection.topology
    }
    else {
        $null
    }
    $tasks = if (Has-Property -Object $reflection -Name "tasks") {
        $reflection.tasks
    }
    else {
        $null
    }

    $fallbackBlockingSignals = @()

    if ($runtimeMode -eq "deferred") {
        if ($workerRunning) {
            $fallbackBlockingSignals += "deferred_in_process_worker_running"
        }
        if (-not (Has-Property -Object $topology -Name "queue_drain_owner") -or [string]$topology.queue_drain_owner -ne "external_driver") {
            $fallbackBlockingSignals += "deferred_queue_drain_owner_mismatch"
        }
        if (-not (Has-Property -Object $topology -Name "external_driver_expected") -or -not [bool]$topology.external_driver_expected) {
            $fallbackBlockingSignals += "deferred_external_driver_expectation_missing"
        }
        if (-not (Has-Property -Object $topology -Name "scheduler_tick_dispatch") -or -not [bool]$topology.scheduler_tick_dispatch) {
            $fallbackBlockingSignals += "deferred_scheduler_dispatch_flag_mismatch"
        }
    }
    else {
        if (-not $workerRunning) {
            $fallbackBlockingSignals += "in_process_worker_not_running"
        }
        if (-not (Has-Property -Object $topology -Name "queue_drain_owner") -or [string]$topology.queue_drain_owner -ne "in_process_worker") {
            $fallbackBlockingSignals += "in_process_queue_drain_owner_mismatch"
        }
        if ((Has-Property -Object $topology -Name "external_driver_expected") -and [bool]$topology.external_driver_expected) {
            $fallbackBlockingSignals += "in_process_external_driver_flag_mismatch"
        }
        if ((Has-Property -Object $topology -Name "scheduler_tick_dispatch") -and [bool]$topology.scheduler_tick_dispatch) {
            $fallbackBlockingSignals += "in_process_scheduler_dispatch_flag_mismatch"
        }
    }

    $stuckProcessing = if (Has-Property -Object $tasks -Name "stuck_processing") {
        [int]$tasks.stuck_processing
    }
    else {
        0
    }
    $exhaustedFailed = if (Has-Property -Object $tasks -Name "exhausted_failed") {
        [int]$tasks.exhausted_failed
    }
    else {
        0
    }
    if ($stuckProcessing -gt 0) {
        $fallbackBlockingSignals += "reflection_stuck_processing_detected"
    }
    if ($exhaustedFailed -gt 0) {
        $fallbackBlockingSignals += "reflection_exhausted_failures_detected"
    }

    $reflectionDeploymentBlockingSignals = $fallbackBlockingSignals
    $reflectionDeploymentReady = $reflectionDeploymentBlockingSignals.Count -eq 0
}

if (-not $reflectionDeploymentReady) {
    $details = if ($reflectionDeploymentBlockingSignals.Count -gt 0) {
        ($reflectionDeploymentBlockingSignals -join ",")
    }
    else {
        "unspecified"
    }
    throw "Reflection deployment readiness check failed: $details."
}

if ($null -ne $reflectionExternalDriverPolicy) {
    if (-not (Has-Property -Object $reflectionExternalDriverPolicy -Name "policy_owner")) {
        throw "Reflection external-driver policy check failed: policy_owner is missing."
    }
    if ([string]$reflectionExternalDriverPolicy.policy_owner -ne "deferred_reflection_external_worker") {
        throw "Reflection external-driver policy check failed: unexpected policy_owner '$($reflectionExternalDriverPolicy.policy_owner)'."
    }
    if (-not (Has-Property -Object $reflectionExternalDriverPolicy -Name "entrypoint_path")) {
        throw "Reflection external-driver policy check failed: entrypoint_path is missing."
    }
    if (-not [string]$reflectionExternalDriverPolicy.entrypoint_path) {
        throw "Reflection external-driver policy check failed: entrypoint_path is empty."
    }
    if (-not (Has-Property -Object $reflectionExternalDriverPolicy -Name "production_baseline_ready")) {
        throw "Reflection external-driver policy check failed: production_baseline_ready is missing."
    }
}
if ($null -eq $reflectionSupervision) {
    throw "Reflection supervision check failed: supervision is missing."
}
if (-not (Has-Property -Object $reflectionSupervision -Name "policy_owner")) {
    throw "Reflection supervision check failed: policy_owner is missing."
}
if ([string]$reflectionSupervision.policy_owner -ne "deferred_reflection_supervision_policy") {
    throw "Reflection supervision check failed: unexpected policy_owner '$($reflectionSupervision.policy_owner)'."
}
if (-not (Has-Property -Object $reflectionSupervision -Name "queue_health_state")) {
    throw "Reflection supervision check failed: queue_health_state is missing."
}
if (-not (Has-Property -Object $reflectionSupervision -Name "production_supervision_ready")) {
    throw "Reflection supervision check failed: production_supervision_ready is missing."
}
if (-not (Has-Property -Object $reflectionSupervision -Name "production_supervision_state")) {
    throw "Reflection supervision check failed: production_supervision_state is missing."
}
if (-not (Has-Property -Object $reflectionSupervision -Name "blocking_signals")) {
    throw "Reflection supervision check failed: blocking_signals are missing."
}
if (-not (Has-Property -Object $reflectionSupervision -Name "recovery_actions")) {
    throw "Reflection supervision check failed: recovery_actions are missing."
}

$runtimeTopology = $health.runtime_topology
if ($null -eq $runtimeTopology) {
    throw "Health check failed: response is missing runtime_topology."
}
if (-not (Has-Property -Object $runtimeTopology -Name "policy_owner")) {
    throw "Health check failed: runtime_topology is missing policy_owner."
}
if ([string]$runtimeTopology.policy_owner -ne "runtime_topology_finalization") {
    throw "Health check failed: unexpected runtime_topology.policy_owner '$($runtimeTopology.policy_owner)'."
}
$attention = $health.attention
if ($null -eq $attention) {
    throw "Health check failed: response is missing attention."
}
if ([string]$attention.coordination_mode -ne "durable_inbox") {
    throw "Health check failed: unexpected attention.coordination_mode '$($attention.coordination_mode)'."
}
if ([string]$attention.contract_store_mode -ne "repository_backed") {
    throw "Health check failed: unexpected attention.contract_store_mode '$($attention.contract_store_mode)'."
}
if ($null -eq $attention.deployment_readiness) {
    throw "Health check failed: attention is missing deployment_readiness."
}
if ([string]$attention.deployment_readiness.selected_coordination_mode -ne "durable_inbox") {
    throw "Health check failed: unexpected attention.deployment_readiness.selected_coordination_mode '$($attention.deployment_readiness.selected_coordination_mode)'."
}
if ([string]$attention.deployment_readiness.contract_store_state -ne "repository_backed_contract_store_active") {
    throw "Health check failed: unexpected attention.deployment_readiness.contract_store_state '$($attention.deployment_readiness.contract_store_state)'."
}
if (-not [bool]$attention.deployment_readiness.store_available) {
    throw "Health check failed: attention.deployment_readiness.store_available is not true."
}
if (-not (Has-Property -Object $runtimeTopology -Name "attention_switch")) {
    throw "Health check failed: runtime_topology is missing attention_switch."
}
if ([string]$runtimeTopology.attention_switch.selected_mode -ne "durable_inbox") {
    throw "Health check failed: unexpected runtime_topology.attention_switch.selected_mode '$($runtimeTopology.attention_switch.selected_mode)'."
}
if (-not [bool]$runtimeTopology.attention_switch.production_default_change_ready) {
    throw "Health check failed: runtime_topology.attention_switch.production_default_change_ready is not true."
}
$proactive = $health.proactive
if ($null -eq $proactive) {
    throw "Health check failed: response is missing proactive."
}
if ([string]$proactive.policy_owner -ne "proactive_runtime_policy") {
    throw "Health check failed: unexpected proactive policy owner '$($proactive.policy_owner)'."
}
if (-not [bool]$proactive.enabled) {
    throw "Health check failed: proactive is not enabled."
}
if (-not [bool]$proactive.production_baseline_ready) {
    throw "Health check failed: proactive production_baseline_ready is not true."
}
if ([string]$proactive.production_baseline_state -eq "disabled_by_policy") {
    throw "Health check failed: proactive production baseline is still disabled_by_policy."
}
$deployment = $health.deployment
if ($null -eq $deployment) {
    throw "Health check failed: response is missing deployment."
}
if (-not (Has-Property -Object $deployment -Name "hosting_baseline")) {
    throw "Health check failed: deployment is missing hosting_baseline."
}
if (-not (Has-Property -Object $deployment -Name "deployment_trigger_slo")) {
    throw "Health check failed: deployment is missing deployment_trigger_slo."
}
$scheduler = $health.scheduler
if ($null -eq $scheduler) {
    throw "Health check failed: response is missing scheduler."
}
if (-not (Has-Property -Object $scheduler -Name "external_owner_policy")) {
    throw "Health check failed: scheduler is missing external_owner_policy."
}
$externalSchedulerPolicy = $scheduler.external_owner_policy
if (-not (Has-Property -Object $externalSchedulerPolicy -Name "policy_owner")) {
    throw "Health check failed: scheduler.external_owner_policy is missing policy_owner."
}
if ([string]$externalSchedulerPolicy.policy_owner -ne "external_scheduler_cadence_policy") {
    throw "Health check failed: unexpected external scheduler policy owner '$($externalSchedulerPolicy.policy_owner)'."
}
if (-not (Has-Property -Object $externalSchedulerPolicy -Name "maintenance_entrypoint_path")) {
    throw "Health check failed: scheduler.external_owner_policy is missing maintenance_entrypoint_path."
}
if (-not (Has-Property -Object $externalSchedulerPolicy -Name "proactive_entrypoint_path")) {
    throw "Health check failed: scheduler.external_owner_policy is missing proactive_entrypoint_path."
}
if (-not (Has-Property -Object $externalSchedulerPolicy -Name "production_baseline_ready")) {
    throw "Health check failed: scheduler.external_owner_policy is missing production_baseline_ready."
}
if (-not (Has-Property -Object $externalSchedulerPolicy -Name "cutover_proof_owner")) {
    throw "Health check failed: scheduler.external_owner_policy is missing cutover_proof_owner."
}
if (-not (Has-Property -Object $externalSchedulerPolicy -Name "cutover_proof_ready")) {
    throw "Health check failed: scheduler.external_owner_policy is missing cutover_proof_ready."
}
if (-not (Has-Property -Object $externalSchedulerPolicy -Name "maintenance_run_evidence")) {
    throw "Health check failed: scheduler.external_owner_policy is missing maintenance_run_evidence."
}
if (-not (Has-Property -Object $externalSchedulerPolicy -Name "proactive_run_evidence")) {
    throw "Health check failed: scheduler.external_owner_policy is missing proactive_run_evidence."
}
if (-not (Has-Property -Object $externalSchedulerPolicy -Name "duplicate_protection_posture")) {
    throw "Health check failed: scheduler.external_owner_policy is missing duplicate_protection_posture."
}
$validExternalCadenceEvidenceStates = @(
    "missing_external_run_evidence",
    "stale_external_run_evidence",
    "recent_external_run_evidence",
    "recent_external_run_non_success"
)
$validDuplicateProtectionStates = @(
    "single_owner_boundary_clear",
    "app_local_conflict_detected"
)
if ([string]$externalSchedulerPolicy.cutover_proof_owner -ne "external_scheduler_cutover_proof_policy") {
    throw "Health check failed: unexpected scheduler cutover proof owner '$($externalSchedulerPolicy.cutover_proof_owner)'."
}
if ($validExternalCadenceEvidenceStates -notcontains [string]$externalSchedulerPolicy.maintenance_run_evidence.evidence_state) {
    throw "Health check failed: unexpected maintenance_run_evidence state '$($externalSchedulerPolicy.maintenance_run_evidence.evidence_state)'."
}
if ($validExternalCadenceEvidenceStates -notcontains [string]$externalSchedulerPolicy.proactive_run_evidence.evidence_state) {
    throw "Health check failed: unexpected proactive_run_evidence state '$($externalSchedulerPolicy.proactive_run_evidence.evidence_state)'."
}
if ($validDuplicateProtectionStates -notcontains [string]$externalSchedulerPolicy.duplicate_protection_posture.state) {
    throw "Health check failed: unexpected duplicate_protection_posture state '$($externalSchedulerPolicy.duplicate_protection_posture.state)'."
}
$memoryRetrieval = $health.memory_retrieval
if ($null -eq $memoryRetrieval) {
    throw "Health check failed: response is missing memory_retrieval."
}
if (-not (Has-Property -Object $memoryRetrieval -Name "retrieval_lifecycle_policy_owner")) {
    throw "Health check failed: memory_retrieval is missing retrieval_lifecycle_policy_owner."
}
if (-not (Has-Property -Object $memoryRetrieval -Name "retrieval_lifecycle_provider_drift_state")) {
    throw "Health check failed: memory_retrieval is missing retrieval_lifecycle_provider_drift_state."
}
if (-not (Has-Property -Object $memoryRetrieval -Name "retrieval_lifecycle_alignment_state")) {
    throw "Health check failed: memory_retrieval is missing retrieval_lifecycle_alignment_state."
}
if (-not (Has-Property -Object $memoryRetrieval -Name "retrieval_lifecycle_pending_gaps")) {
    throw "Health check failed: memory_retrieval is missing retrieval_lifecycle_pending_gaps."
}
if (-not (Has-Property -Object $memoryRetrieval -Name "semantic_embedding_provider_requested")) {
    throw "Health check failed: memory_retrieval is missing semantic_embedding_provider_requested."
}
if (-not (Has-Property -Object $memoryRetrieval -Name "semantic_embedding_provider_effective")) {
    throw "Health check failed: memory_retrieval is missing semantic_embedding_provider_effective."
}
if (-not (Has-Property -Object $memoryRetrieval -Name "semantic_embedding_model_requested")) {
    throw "Health check failed: memory_retrieval is missing semantic_embedding_model_requested."
}
if (-not (Has-Property -Object $memoryRetrieval -Name "semantic_embedding_model_effective")) {
    throw "Health check failed: memory_retrieval is missing semantic_embedding_model_effective."
}
if (-not (Has-Property -Object $memoryRetrieval -Name "semantic_embedding_execution_class")) {
    throw "Health check failed: memory_retrieval is missing semantic_embedding_execution_class."
}
if (-not (Has-Property -Object $memoryRetrieval -Name "semantic_embedding_production_baseline_state")) {
    throw "Health check failed: memory_retrieval is missing semantic_embedding_production_baseline_state."
}
if (-not (Has-Property -Object $memoryRetrieval -Name "retrieval_lifecycle_relation_source_policy_owner")) {
    throw "Health check failed: memory_retrieval is missing retrieval_lifecycle_relation_source_policy_owner."
}
if (-not (Has-Property -Object $memoryRetrieval -Name "retrieval_lifecycle_relation_source_state")) {
    throw "Health check failed: memory_retrieval is missing retrieval_lifecycle_relation_source_state."
}
if (-not (Has-Property -Object $memoryRetrieval -Name "retrieval_lifecycle_relation_source_enabled")) {
    throw "Health check failed: memory_retrieval is missing retrieval_lifecycle_relation_source_enabled."
}
$retrievalAlignment = Assert-RetrievalAlignmentPosture `
    -MemoryRetrieval $memoryRetrieval `
    -FailurePrefix "Health check failed"
$observability = $health.observability
if ($null -eq $observability) {
    throw "Health check failed: response is missing observability."
}
if (-not (Has-Property -Object $observability -Name "policy_owner")) {
    throw "Health check failed: observability is missing policy_owner."
}
if ([string]$observability.policy_owner -ne "incident_evidence_export_policy") {
    throw "Health check failed: unexpected observability.policy_owner '$($observability.policy_owner)'."
}
if (-not (Has-Property -Object $observability -Name "export_artifact_available")) {
    throw "Health check failed: observability is missing export_artifact_available."
}
if (-not [bool]$observability.export_artifact_available) {
    throw "Health check failed: observability export artifact is not available."
}
if (-not (Has-Property -Object $observability -Name "incident_export_ready")) {
    throw "Health check failed: observability is missing incident_export_ready."
}
if (-not [bool]$observability.incident_export_ready) {
    throw "Health check failed: observability incident export is not ready."
}
$conversationChannels = $health.conversation_channels
if ($null -eq $conversationChannels) {
    throw "Health check failed: response is missing conversation_channels."
}
$telegramConversation = $conversationChannels.telegram
if ($null -eq $telegramConversation) {
    throw "Health check failed: conversation_channels.telegram is missing."
}
if (-not (Has-Property -Object $telegramConversation -Name "policy_owner")) {
    throw "Health check failed: conversation_channels.telegram is missing policy_owner."
}
if ([string]$telegramConversation.policy_owner -ne "telegram_conversation_reliability_telemetry") {
    throw "Health check failed: unexpected conversation_channels.telegram policy_owner '$($telegramConversation.policy_owner)'."
}
if (-not (Has-Property -Object $telegramConversation -Name "round_trip_state")) {
    throw "Health check failed: conversation_channels.telegram is missing round_trip_state."
}
$validTelegramRoundTripStates = @(
    "provider_backed_ready",
    "missing_bot_token"
)
if ($validTelegramRoundTripStates -notcontains [string]$telegramConversation.round_trip_state) {
    throw "Health check failed: unexpected conversation_channels.telegram round_trip_state '$($telegramConversation.round_trip_state)'."
}
if (-not (Has-Property -Object $telegramConversation -Name "bot_token_configured")) {
    throw "Health check failed: conversation_channels.telegram is missing bot_token_configured."
}
if (-not (Has-Property -Object $telegramConversation -Name "delivery_attempts")) {
    throw "Health check failed: conversation_channels.telegram is missing delivery_attempts."
}
if (-not (Has-Property -Object $telegramConversation -Name "delivery_failures")) {
    throw "Health check failed: conversation_channels.telegram is missing delivery_failures."
}
$learnedState = $health.learned_state
if ($null -eq $learnedState) {
    throw "Health check failed: response is missing learned_state."
}
if (-not (Has-Property -Object $learnedState -Name "policy_owner")) {
    throw "Health check failed: learned_state is missing policy_owner."
}
if ([string]$learnedState.policy_owner -ne "learned_state_inspection_policy") {
    throw "Health check failed: unexpected learned_state.policy_owner '$($learnedState.policy_owner)'."
}
if (-not (Has-Property -Object $learnedState -Name "internal_inspection_path")) {
    throw "Health check failed: learned_state is missing internal_inspection_path."
}
if ([string]$learnedState.internal_inspection_path -ne "/internal/state/inspect") {
    throw "Health check failed: unexpected learned_state.internal_inspection_path '$($learnedState.internal_inspection_path)'."
}
$v1Readiness = $health.v1_readiness
if ($null -eq $v1Readiness) {
    throw "Health check failed: response is missing v1_readiness."
}
if ([string]$v1Readiness.policy_owner -ne "v1_release_readiness_policy") {
    throw "Health check failed: unexpected v1_readiness.policy_owner '$($v1Readiness.policy_owner)'."
}
if ([string]$v1Readiness.product_stage -ne "v1_no_ui_life_assistant") {
    throw "Health check failed: unexpected v1_readiness.product_stage '$($v1Readiness.product_stage)'."
}
if ([string]$v1Readiness.conversation_gate_state -ne "conversation_surface_ready") {
    throw "Health check failed: unexpected v1_readiness.conversation_gate_state '$($v1Readiness.conversation_gate_state)'."
}
if ([string]$v1Readiness.learned_state_gate_state -ne "inspection_surface_ready") {
    throw "Health check failed: unexpected v1_readiness.learned_state_gate_state '$($v1Readiness.learned_state_gate_state)'."
}
$requiredV1Scenarios = @("T13.1", "T14.1", "T14.2", "T14.3", "T15.1", "T15.2")
$actualV1Scenarios = @()
if ($v1Readiness.PSObject.Properties.Name -contains "required_behavior_scenarios" -and $null -ne $v1Readiness.required_behavior_scenarios) {
    $actualV1Scenarios = @($v1Readiness.required_behavior_scenarios)
}
foreach ($requiredScenario in $requiredV1Scenarios) {
    if ($actualV1Scenarios -notcontains $requiredScenario) {
        throw "Health check failed: v1_readiness is missing required behavior scenario '$requiredScenario'."
    }
}
$requiredV1ToolSlices = @(
    "knowledge_search.search_web",
    "web_browser.read_page",
    "task_system.clickup_update_task"
)
$actualV1ToolSlices = @()
if ($v1Readiness.PSObject.Properties.Name -contains "approved_tool_slices" -and $null -ne $v1Readiness.approved_tool_slices) {
    $actualV1ToolSlices = @($v1Readiness.approved_tool_slices)
}
foreach ($requiredToolSlice in $requiredV1ToolSlices) {
    if ($actualV1ToolSlices -notcontains $requiredToolSlice) {
        throw "Health check failed: v1_readiness is missing approved tool slice '$requiredToolSlice'."
    }
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

$incidentEvidence = $null
$incidentDebugPosture = $null
$incidentTelegramConversation = $null
$incidentAttention = $null
$incidentTopologyAttention = $null
$incidentProactive = $null
if ($IncludeDebug) {
    if (-not (Has-Property -Object $response -Name "incident_evidence")) {
        throw "Smoke request failed: debug request is missing incident_evidence."
    }
    $incidentEvidence = $response.incident_evidence
    if (-not (Has-Property -Object $incidentEvidence -Name "policy_owner")) {
        throw "Smoke request failed: incident_evidence is missing policy_owner."
    }
    if ([string]$incidentEvidence.policy_owner -ne "incident_evidence_export_policy") {
        throw "Smoke request failed: unexpected incident_evidence.policy_owner '$($incidentEvidence.policy_owner)'."
    }
    if (-not (Has-Property -Object $incidentEvidence -Name "schema_version")) {
        throw "Smoke request failed: incident_evidence is missing schema_version."
    }
    if (-not (Has-Property -Object $incidentEvidence -Name "duration_ms")) {
        throw "Smoke request failed: incident_evidence is missing duration_ms."
    }
    if (-not (Has-Property -Object $incidentEvidence -Name "stage_timings_ms")) {
        throw "Smoke request failed: incident_evidence is missing stage_timings_ms."
    }
    if (-not (Has-Property -Object $incidentEvidence -Name "policy_surface_coverage")) {
        throw "Smoke request failed: incident_evidence is missing policy_surface_coverage."
    }
    $incidentCoverage = $incidentEvidence.policy_surface_coverage
    if (-not (Has-Property -Object $incidentCoverage -Name "complete")) {
        throw "Smoke request failed: incident_evidence.policy_surface_coverage is missing complete."
    }
    if (-not [bool]$incidentCoverage.complete) {
        throw "Smoke request failed: incident_evidence policy surface coverage is incomplete."
    }
    if (-not (Has-Property -Object $incidentEvidence -Name "policy_posture")) {
        throw "Smoke request failed: incident_evidence is missing policy_posture."
    }
    $incidentDebugPosture = Assert-DedicatedAdminDebugPosture `
        -RuntimePolicy $incidentEvidence.policy_posture.runtime_policy `
        -FailurePrefix "Smoke request failed"
    $incidentTelegramConversation = $incidentEvidence.policy_posture."conversation_channels.telegram"
    if ($null -eq $incidentTelegramConversation) {
        throw "Smoke request failed: incident_evidence is missing conversation_channels.telegram posture."
    }
    if ([string]$incidentTelegramConversation.policy_owner -ne "telegram_conversation_reliability_telemetry") {
        throw "Smoke request failed: unexpected incident_evidence conversation_channels.telegram policy_owner '$($incidentTelegramConversation.policy_owner)'."
    }
    if ($validTelegramRoundTripStates -notcontains [string]$incidentTelegramConversation.round_trip_state) {
        throw "Smoke request failed: unexpected incident_evidence conversation_channels.telegram round_trip_state '$($incidentTelegramConversation.round_trip_state)'."
    }
    $incidentAttention = $incidentEvidence.policy_posture.attention
    if ($null -eq $incidentAttention) {
        throw "Smoke request failed: incident_evidence is missing attention posture."
    }
    if ([string]$incidentAttention.attention_policy_owner -ne "durable_attention_inbox_policy") {
        throw "Smoke request failed: unexpected incident_evidence attention policy_owner '$($incidentAttention.attention_policy_owner)'."
    }
    if ([string]$incidentAttention.coordination_mode -ne "durable_inbox") {
        throw "Smoke request failed: unexpected incident_evidence attention coordination_mode '$($incidentAttention.coordination_mode)'."
    }
    if ([string]$incidentAttention.deployment_readiness.selected_coordination_mode -ne "durable_inbox") {
        throw "Smoke request failed: unexpected incident_evidence attention selected_coordination_mode '$($incidentAttention.deployment_readiness.selected_coordination_mode)'."
    }
    if ([string]$incidentAttention.deployment_readiness.contract_store_state -ne "repository_backed_contract_store_active") {
        throw "Smoke request failed: unexpected incident_evidence attention contract_store_state '$($incidentAttention.deployment_readiness.contract_store_state)'."
    }
    if (-not [bool]$incidentAttention.deployment_readiness.store_available) {
        throw "Smoke request failed: incident_evidence attention store_available is not true."
    }
    $incidentTopologyAttention = $incidentEvidence.policy_posture."runtime_topology.attention_switch"
    if ($null -eq $incidentTopologyAttention) {
        throw "Smoke request failed: incident_evidence is missing runtime_topology.attention_switch posture."
    }
    if ([string]$incidentTopologyAttention.policy_owner -ne "runtime_topology_finalization") {
        throw "Smoke request failed: unexpected incident_evidence runtime_topology.attention_switch policy_owner '$($incidentTopologyAttention.policy_owner)'."
    }
    if ([string]$incidentTopologyAttention.selected_mode -ne "durable_inbox") {
        throw "Smoke request failed: unexpected incident_evidence runtime_topology.attention_switch selected_mode '$($incidentTopologyAttention.selected_mode)'."
    }
    if (-not [bool]$incidentTopologyAttention.production_default_change_ready) {
        throw "Smoke request failed: incident_evidence runtime_topology.attention_switch production_default_change_ready is not true."
    }
    $incidentProactive = $incidentEvidence.policy_posture.proactive
    if ($null -eq $incidentProactive) {
        throw "Smoke request failed: incident_evidence is missing proactive posture."
    }
    if ([string]$incidentProactive.policy_owner -ne "proactive_runtime_policy") {
        throw "Smoke request failed: unexpected incident_evidence proactive policy_owner '$($incidentProactive.policy_owner)'."
    }
    if (-not [bool]$incidentProactive.enabled) {
        throw "Smoke request failed: incident_evidence proactive enabled is not true."
    }
    if (-not [bool]$incidentProactive.production_baseline_ready) {
        throw "Smoke request failed: incident_evidence proactive production_baseline_ready is not true."
    }
    if ([string]$incidentProactive.production_baseline_state -eq "disabled_by_policy") {
        throw "Smoke request failed: incident_evidence proactive production baseline is still disabled_by_policy."
    }
    $incidentRetrieval = $incidentEvidence.policy_posture.memory_retrieval
    $incidentRetrievalAlignment = Assert-RetrievalAlignmentPosture `
        -MemoryRetrieval $incidentRetrieval `
        -FailurePrefix "Smoke request failed"
    $incidentLearnedState = $incidentEvidence.policy_posture.learned_state
    if ($null -eq $incidentLearnedState) {
        throw "Smoke request failed: incident_evidence is missing learned_state posture."
    }
    if ([string]$incidentLearnedState.policy_owner -ne "learned_state_inspection_policy") {
        throw "Smoke request failed: unexpected incident_evidence learned_state policy_owner '$($incidentLearnedState.policy_owner)'."
    }
    if ([string]$incidentLearnedState.internal_inspection_path -ne "/internal/state/inspect") {
        throw "Smoke request failed: unexpected incident_evidence learned_state internal_inspection_path '$($incidentLearnedState.internal_inspection_path)'."
    }
    $incidentV1Readiness = $incidentEvidence.policy_posture.v1_readiness
    if ($null -eq $incidentV1Readiness) {
        throw "Smoke request failed: incident_evidence is missing v1_readiness posture."
    }
    if ([string]$incidentV1Readiness.policy_owner -ne "v1_release_readiness_policy") {
        throw "Smoke request failed: unexpected incident_evidence v1_readiness policy_owner '$($incidentV1Readiness.policy_owner)'."
    }
    if ([string]$incidentV1Readiness.product_stage -ne "v1_no_ui_life_assistant") {
        throw "Smoke request failed: unexpected incident_evidence v1_readiness product_stage '$($incidentV1Readiness.product_stage)'."
    }
    if ([string]$incidentV1Readiness.conversation_gate_state -ne "conversation_surface_ready") {
        throw "Smoke request failed: unexpected incident_evidence v1_readiness conversation_gate_state '$($incidentV1Readiness.conversation_gate_state)'."
    }
    if ([string]$incidentV1Readiness.learned_state_gate_state -ne "inspection_surface_ready") {
        throw "Smoke request failed: unexpected incident_evidence v1_readiness learned_state_gate_state '$($incidentV1Readiness.learned_state_gate_state)'."
    }
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
    release_ready        = $releaseReadinessReady
    release_violations   = @($releaseReadinessViolations)
    reflection_deployment_ready      = $reflectionDeploymentReady
    reflection_deployment_violations = @($reflectionDeploymentBlockingSignals)
    reflection_external_driver_policy_owner = if ($null -ne $reflectionExternalDriverPolicy) { [string]$reflectionExternalDriverPolicy.policy_owner } else { $null }
    reflection_external_driver_entrypoint_path = if ($null -ne $reflectionExternalDriverPolicy) { [string]$reflectionExternalDriverPolicy.entrypoint_path } else { $null }
    reflection_external_driver_baseline_ready = if ($null -ne $reflectionExternalDriverPolicy) { [bool]$reflectionExternalDriverPolicy.production_baseline_ready } else { $null }
    reflection_supervision_policy_owner = [string]$reflectionSupervision.policy_owner
    reflection_supervision_queue_health_state = [string]$reflectionSupervision.queue_health_state
    reflection_supervision_ready = [bool]$reflectionSupervision.production_supervision_ready
    reflection_supervision_state = [string]$reflectionSupervision.production_supervision_state
    reflection_supervision_blocking_signals = @($reflectionSupervision.blocking_signals)
    reflection_supervision_recovery_actions = @($reflectionSupervision.recovery_actions)
    debug_internal_ingress_path      = [string]$runtimePolicy.event_debug_internal_ingress_path
    debug_admin_policy_owner         = [string]$runtimePolicy.event_debug_admin_policy_owner
    debug_admin_ingress_target_path  = [string]$runtimePolicy.event_debug_admin_ingress_target_path
    debug_admin_posture_state        = [string]$runtimePolicy.event_debug_admin_posture_state
    debug_shared_ingress_path        = [string]$runtimePolicy.event_debug_shared_ingress_path
    debug_shared_ingress_mode        = $sharedIngressMode
    debug_shared_break_glass_required = $sharedBreakGlassRequired
    debug_shared_ingress_posture     = $sharedIngressPosture
    debug_shared_ingress_retirement_ready = [bool]$runtimePolicy.event_debug_shared_ingress_retirement_ready
    debug_shared_ingress_retirement_blockers = @($debugRetirementBlockers)
    startup_schema_compatibility_posture = $startupSchemaCompatibilityPosture
    startup_schema_compatibility_sunset_ready = $startupSchemaCompatibilitySunsetReady
    startup_schema_compatibility_sunset_reason = $startupSchemaCompatibilitySunsetReason
    debug_shared_ingress_sunset_ready = $sharedIngressSunsetReady
    debug_shared_ingress_sunset_reason = $sharedIngressSunsetReason
    compatibility_sunset_ready = $compatibilitySunsetReady
    compatibility_sunset_blockers = @($compatibilitySunsetBlockers)
    runtime_topology_owner = [string]$runtimeTopology.policy_owner
    topology_release_window = [string]$runtimeTopology.release_window
    attention_coordination_mode = [string]$attention.coordination_mode
    attention_contract_store_mode = [string]$attention.contract_store_mode
    attention_contract_store_state = [string]$attention.deployment_readiness.contract_store_state
    attention_store_available = [bool]$attention.deployment_readiness.store_available
    runtime_topology_attention_selected_mode = [string]$runtimeTopology.attention_switch.selected_mode
    runtime_topology_attention_ready = [bool]$runtimeTopology.attention_switch.production_default_change_ready
    proactive_policy_owner = [string]$proactive.policy_owner
    proactive_enabled = [bool]$proactive.enabled
    proactive_production_baseline_ready = [bool]$proactive.production_baseline_ready
    proactive_production_baseline_state = [string]$proactive.production_baseline_state
    deployment_hosting_baseline = [string]$deployment.hosting_baseline
    deployment_manual_fallback_exception_rate_percent = [double]$deployment.deployment_trigger_slo.manual_redeploy_exception_rate_percent
    scheduler_external_policy_owner = [string]$externalSchedulerPolicy.policy_owner
    scheduler_external_cutover_proof_owner = [string]$externalSchedulerPolicy.cutover_proof_owner
    scheduler_external_maintenance_entrypoint = [string]$externalSchedulerPolicy.maintenance_entrypoint_path
    scheduler_external_proactive_entrypoint = [string]$externalSchedulerPolicy.proactive_entrypoint_path
    scheduler_external_baseline_ready = [bool]$externalSchedulerPolicy.production_baseline_ready
    scheduler_external_baseline_state = [string]$externalSchedulerPolicy.production_baseline_state
    scheduler_external_cutover_proof_ready = [bool]$externalSchedulerPolicy.cutover_proof_ready
    scheduler_external_maintenance_evidence_state = [string]$externalSchedulerPolicy.maintenance_run_evidence.evidence_state
    scheduler_external_proactive_evidence_state = [string]$externalSchedulerPolicy.proactive_run_evidence.evidence_state
    scheduler_external_duplicate_protection_state = [string]$externalSchedulerPolicy.duplicate_protection_posture.state
    retrieval_lifecycle_policy_owner = [string]$memoryRetrieval.retrieval_lifecycle_policy_owner
    retrieval_semantic_embedding_provider_requested = [string]$retrievalAlignment.provider_requested
    retrieval_semantic_embedding_provider_effective = [string]$retrievalAlignment.provider_effective
    retrieval_semantic_embedding_model_requested = [string]$retrievalAlignment.model_requested
    retrieval_semantic_embedding_model_effective = [string]$retrievalAlignment.model_effective
    retrieval_semantic_embedding_execution_class = [string]$retrievalAlignment.execution_class
    retrieval_semantic_embedding_production_baseline_state = [string]$retrievalAlignment.production_baseline_state
    retrieval_lifecycle_provider_drift_state = [string]$memoryRetrieval.retrieval_lifecycle_provider_drift_state
    retrieval_lifecycle_alignment_state = [string]$memoryRetrieval.retrieval_lifecycle_alignment_state
    retrieval_lifecycle_pending_gaps = @($memoryRetrieval.retrieval_lifecycle_pending_gaps)
    retrieval_lifecycle_relation_source_policy_owner = [string]$memoryRetrieval.retrieval_lifecycle_relation_source_policy_owner
    retrieval_lifecycle_relation_source_posture = [string]$memoryRetrieval.retrieval_lifecycle_relation_source_posture
    retrieval_lifecycle_relation_source_state = [string]$memoryRetrieval.retrieval_lifecycle_relation_source_state
    retrieval_lifecycle_relation_source_enabled = [bool]$memoryRetrieval.retrieval_lifecycle_relation_source_enabled
    observability_policy_owner = [string]$observability.policy_owner
    observability_export_artifact_available = [bool]$observability.export_artifact_available
    observability_incident_export_ready = [bool]$observability.incident_export_ready
    telegram_conversation_policy_owner = [string]$telegramConversation.policy_owner
    telegram_conversation_round_trip_state = [string]$telegramConversation.round_trip_state
    telegram_conversation_bot_token_configured = [bool]$telegramConversation.bot_token_configured
    telegram_conversation_delivery_attempts = [int]$telegramConversation.delivery_attempts
    telegram_conversation_delivery_failures = [int]$telegramConversation.delivery_failures
    debug_included       = [bool]$response.debug
    incident_evidence_policy_owner = if ($null -ne $incidentEvidence) { [string]$incidentEvidence.policy_owner } else { $null }
    incident_evidence_schema_version = if ($null -ne $incidentEvidence) { [string]$incidentEvidence.schema_version } else { $null }
    incident_evidence_duration_ms = if ($null -ne $incidentEvidence) { [int]$incidentEvidence.duration_ms } else { $null }
    incident_evidence_stage_count = if ($null -ne $incidentEvidence) { @($incidentEvidence.stage_timings_ms.PSObject.Properties).Count } else { $null }
    incident_evidence_policy_surface_complete = if ($null -ne $incidentEvidence) { [bool]$incidentEvidence.policy_surface_coverage.complete } else { $null }
    incident_evidence_debug_posture_state = if ($null -ne $incidentDebugPosture) { [string]$incidentDebugPosture.debug_posture_state } else { $null }
    incident_evidence_debug_exception_state = if ($null -ne $incidentDebugPosture) { [string]$incidentDebugPosture.debug_exception_state } else { $null }
    incident_evidence_telegram_conversation_policy_owner = if ($null -ne $incidentTelegramConversation) { [string]$incidentTelegramConversation.policy_owner } else { $null }
    incident_evidence_telegram_conversation_round_trip_state = if ($null -ne $incidentTelegramConversation) { [string]$incidentTelegramConversation.round_trip_state } else { $null }
    incident_evidence_attention_policy_owner = if ($null -ne $incidentAttention) { [string]$incidentAttention.attention_policy_owner } else { $null }
    incident_evidence_attention_coordination_mode = if ($null -ne $incidentAttention) { [string]$incidentAttention.coordination_mode } else { $null }
    incident_evidence_attention_contract_store_state = if ($null -ne $incidentAttention) { [string]$incidentAttention.deployment_readiness.contract_store_state } else { $null }
    incident_evidence_attention_runtime_topology_policy_owner = if ($null -ne $incidentTopologyAttention) { [string]$incidentTopologyAttention.policy_owner } else { $null }
    incident_evidence_attention_runtime_topology_selected_mode = if ($null -ne $incidentTopologyAttention) { [string]$incidentTopologyAttention.selected_mode } else { $null }
    incident_evidence_attention_runtime_topology_ready = if ($null -ne $incidentTopologyAttention) { [bool]$incidentTopologyAttention.production_default_change_ready } else { $null }
    incident_evidence_proactive_policy_owner = if ($null -ne $incidentProactive) { [string]$incidentProactive.policy_owner } else { $null }
    incident_evidence_proactive_enabled = if ($null -ne $incidentProactive) { [bool]$incidentProactive.enabled } else { $null }
    incident_evidence_proactive_production_baseline_ready = if ($null -ne $incidentProactive) { [bool]$incidentProactive.production_baseline_ready } else { $null }
    incident_evidence_proactive_production_baseline_state = if ($null -ne $incidentProactive) { [string]$incidentProactive.production_baseline_state } else { $null }
    incident_evidence_retrieval_policy_owner = if ($null -ne $incidentRetrievalAlignment) { [string]$incidentRetrievalAlignment.retrieval_policy_owner } else { $null }
    incident_evidence_retrieval_provider_requested = if ($null -ne $incidentRetrievalAlignment) { [string]$incidentRetrievalAlignment.provider_requested } else { $null }
    incident_evidence_retrieval_provider_effective = if ($null -ne $incidentRetrievalAlignment) { [string]$incidentRetrievalAlignment.provider_effective } else { $null }
    incident_evidence_retrieval_execution_class = if ($null -ne $incidentRetrievalAlignment) { [string]$incidentRetrievalAlignment.execution_class } else { $null }
    incident_evidence_retrieval_baseline_state = if ($null -ne $incidentRetrievalAlignment) { [string]$incidentRetrievalAlignment.production_baseline_state } else { $null }
    incident_evidence_retrieval_provider_drift_state = if ($null -ne $incidentRetrievalAlignment) { [string]$incidentRetrievalAlignment.provider_drift_state } else { $null }
    incident_evidence_retrieval_alignment_state = if ($null -ne $incidentRetrievalAlignment) { [string]$incidentRetrievalAlignment.alignment_state } else { $null }
    incident_bundle_checked = [bool]$incidentEvidenceBundleCheck.checked
    incident_bundle_path = [string]$incidentEvidenceBundleCheck.path
    incident_bundle_manifest_schema_version = $incidentEvidenceBundleCheck.manifest_schema_version
    incident_bundle_capture_mode = $incidentEvidenceBundleCheck.capture_mode
    incident_bundle_trace_id = $incidentEvidenceBundleCheck.trace_id
    incident_bundle_event_id = $incidentEvidenceBundleCheck.event_id
    incident_bundle_behavior_report_attached = $incidentEvidenceBundleCheck.behavior_report_attached
    incident_bundle_policy_surface_complete = $incidentEvidenceBundleCheck.policy_surface_complete
    incident_bundle_health_status = $incidentEvidenceBundleCheck.health_status
    incident_bundle_debug_posture_state = $incidentEvidenceBundleCheck.debug_posture_state
    incident_bundle_debug_exception_state = $incidentEvidenceBundleCheck.debug_exception_state
    incident_bundle_telegram_round_trip_state = $incidentEvidenceBundleCheck.telegram_round_trip_state
    incident_bundle_attention_coordination_mode = $incidentEvidenceBundleCheck.attention_coordination_mode
    incident_bundle_attention_contract_store_state = $incidentEvidenceBundleCheck.attention_contract_store_state
    incident_bundle_attention_runtime_topology_selected_mode = $incidentEvidenceBundleCheck.attention_runtime_topology_selected_mode
    incident_bundle_proactive_policy_owner = $incidentEvidenceBundleCheck.proactive_policy_owner
    incident_bundle_proactive_enabled = $incidentEvidenceBundleCheck.proactive_enabled
    incident_bundle_proactive_production_baseline_state = $incidentEvidenceBundleCheck.proactive_production_baseline_state
    incident_bundle_retrieval_policy_owner = $incidentEvidenceBundleCheck.retrieval_policy_owner
    incident_bundle_retrieval_provider_requested = $incidentEvidenceBundleCheck.retrieval_provider_requested
    incident_bundle_retrieval_provider_effective = $incidentEvidenceBundleCheck.retrieval_provider_effective
    incident_bundle_retrieval_execution_class = $incidentEvidenceBundleCheck.retrieval_execution_class
    incident_bundle_retrieval_baseline_state = $incidentEvidenceBundleCheck.retrieval_baseline_state
    incident_bundle_retrieval_provider_drift_state = $incidentEvidenceBundleCheck.retrieval_provider_drift_state
    incident_bundle_retrieval_alignment_state = $incidentEvidenceBundleCheck.retrieval_alignment_state
    deployment_evidence_checked = [bool]$deploymentEvidenceCheck.checked
    deployment_evidence_path = [string]$deploymentEvidenceCheck.path
    deployment_evidence_age_minutes = $deploymentEvidenceCheck.age_minutes
    deployment_evidence_status_code = $deploymentEvidenceCheck.status_code
}

$summary | ConvertTo-Json -Depth 6
