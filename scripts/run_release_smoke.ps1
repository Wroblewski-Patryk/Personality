param(
    [Parameter(Mandatory = $true)][string]$BaseUrl,
    [string]$Text = "AION manual smoke test",
    [string]$UserId = "manual-smoke",
    [switch]$IncludeDebug,
    [string]$DeploymentEvidencePath = "",
    [int]$DeploymentEvidenceMaxAgeMinutes = 60
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
    deployment_hosting_baseline = [string]$deployment.hosting_baseline
    deployment_manual_fallback_exception_rate_percent = [double]$deployment.deployment_trigger_slo.manual_redeploy_exception_rate_percent
    scheduler_external_policy_owner = [string]$externalSchedulerPolicy.policy_owner
    scheduler_external_maintenance_entrypoint = [string]$externalSchedulerPolicy.maintenance_entrypoint_path
    scheduler_external_proactive_entrypoint = [string]$externalSchedulerPolicy.proactive_entrypoint_path
    scheduler_external_baseline_ready = [bool]$externalSchedulerPolicy.production_baseline_ready
    scheduler_external_baseline_state = [string]$externalSchedulerPolicy.production_baseline_state
    retrieval_lifecycle_policy_owner = [string]$memoryRetrieval.retrieval_lifecycle_policy_owner
    retrieval_lifecycle_provider_drift_state = [string]$memoryRetrieval.retrieval_lifecycle_provider_drift_state
    retrieval_lifecycle_alignment_state = [string]$memoryRetrieval.retrieval_lifecycle_alignment_state
    retrieval_lifecycle_pending_gaps = @($memoryRetrieval.retrieval_lifecycle_pending_gaps)
    observability_policy_owner = [string]$observability.policy_owner
    observability_export_artifact_available = [bool]$observability.export_artifact_available
    observability_incident_export_ready = [bool]$observability.incident_export_ready
    debug_included       = [bool]$response.debug
    incident_evidence_policy_owner = if ($null -ne $incidentEvidence) { [string]$incidentEvidence.policy_owner } else { $null }
    incident_evidence_schema_version = if ($null -ne $incidentEvidence) { [string]$incidentEvidence.schema_version } else { $null }
    incident_evidence_duration_ms = if ($null -ne $incidentEvidence) { [int]$incidentEvidence.duration_ms } else { $null }
    incident_evidence_stage_count = if ($null -ne $incidentEvidence) { @($incidentEvidence.stage_timings_ms.PSObject.Properties).Count } else { $null }
    incident_evidence_policy_surface_complete = if ($null -ne $incidentEvidence) { [bool]$incidentEvidence.policy_surface_coverage.complete } else { $null }
    deployment_evidence_checked = [bool]$deploymentEvidenceCheck.checked
    deployment_evidence_path = [string]$deploymentEvidenceCheck.path
    deployment_evidence_age_minutes = $deploymentEvidenceCheck.age_minutes
    deployment_evidence_status_code = $deploymentEvidenceCheck.status_code
}

$summary | ConvertTo-Json -Depth 6
