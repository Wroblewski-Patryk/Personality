param(
    [Parameter(Mandatory = $true)][string]$BaseUrl,
    [string]$Text = "AION manual smoke test",
    [string]$UserId = "manual-smoke",
    [switch]$IncludeDebug,
    [string]$DeploymentEvidencePath = "",
    [int]$DeploymentEvidenceMaxAgeMinutes = 60,
    [string]$IncidentEvidenceBundlePath = "",
    [switch]$WaitForDeployParity,
    [int]$DeployParityMaxWaitSeconds = 300,
    [int]$DeployParityPollSeconds = 15,
    [int]$HealthRetryMaxAttempts = 3,
    [int]$HealthRetryDelaySeconds = 5
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

function Invoke-TextUtf8 {
    param(
        [Parameter(Mandatory = $true)][string]$Uri
    )

    $handler = [System.Net.Http.HttpClientHandler]::new()
    $client = [System.Net.Http.HttpClient]::new($handler)
    try {
        $response = $client.GetAsync($Uri).GetAwaiter().GetResult()
        $response.EnsureSuccessStatusCode() | Out-Null
        $bytes = $response.Content.ReadAsByteArrayAsync().GetAwaiter().GetResult()
        return [System.Text.Encoding]::UTF8.GetString($bytes)
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

function Assert-WebShellRouteBuildRevision {
    param(
        [Parameter(Mandatory = $true)][string]$BaseUrl,
        [Parameter(Mandatory = $true)][string]$RoutePath,
        [Parameter(Mandatory = $true)][string]$ExpectedRevision
    )

    $normalizedRoute = if ([string]::IsNullOrWhiteSpace($RoutePath)) { "/" } else { $RoutePath }
    $routeUri = if ($normalizedRoute -eq "/") { "$BaseUrl/" } else { "$BaseUrl$normalizedRoute" }
    $routeHtml = Invoke-TextUtf8 -Uri $routeUri
    $routeRevisionMatch = [regex]::Match(
        $routeHtml,
        '<meta\s+name="aion-web-build-revision"\s+content="(?<revision>[^"]*)"\s*/?>',
        [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
    )
    if (-not $routeRevisionMatch.Success) {
        throw "Health check failed: web shell build revision meta tag is missing from '$normalizedRoute'."
    }

    $routeRevision = [string]$routeRevisionMatch.Groups["revision"].Value
    if (-not $routeRevision) {
        throw "Health check failed: web shell build revision is empty on '$normalizedRoute'."
    }
    if ($routeRevision -ne $ExpectedRevision) {
        throw "Health check failed: web shell build revision '$routeRevision' on '$normalizedRoute' does not match deployment runtime_build_revision '$ExpectedRevision'."
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
        policy_owner = $null
        trigger_mode = $null
        trigger_class = $null
        canonical_application_id = $null
        after_sha = $null
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
    if ([string]$evidence.policy_owner -ne "coolify_repo_deploy_automation") {
        throw "Deployment evidence verification failed: unexpected policy_owner '$($evidence.policy_owner)'."
    }

    $validTriggerModes = @(
        "source_automation",
        "webhook_manual_fallback",
        "ui_manual_fallback"
    )
    $triggerMode = [string]$evidence.trigger_mode
    if ($validTriggerModes -notcontains $triggerMode) {
        throw "Deployment evidence verification failed: unexpected trigger_mode '$triggerMode'."
    }

    $validTriggerClasses = @(
        "primary_automation",
        "manual_fallback"
    )
    $triggerClass = [string]$evidence.trigger_class
    if ($validTriggerClasses -notcontains $triggerClass) {
        throw "Deployment evidence verification failed: unexpected trigger_class '$triggerClass'."
    }

    if ($null -eq $evidence.canonical_coolify_app) {
        throw "Deployment evidence verification failed: canonical_coolify_app is missing."
    }
    $canonicalApplicationId = [string]$evidence.canonical_coolify_app.application_id
    if (-not $canonicalApplicationId) {
        throw "Deployment evidence verification failed: canonical_coolify_app.application_id is missing."
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
        policy_owner = [string]$evidence.policy_owner
        trigger_mode = $triggerMode
        trigger_class = $triggerClass
        canonical_application_id = $canonicalApplicationId
        after_sha = [string]$evidence.after_sha
    }
}

function Resolve-LocalRepoHeadSha {
    $command = Get-Command git -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        return ""
    }

    try {
        $head = (& git rev-parse HEAD 2>$null)
        if ($LASTEXITCODE -ne 0) {
            return ""
        }
        return [string]($head | Select-Object -First 1)
    }
    catch {
        return ""
    }
}

function Get-DeploymentRuntimeBuildRevision {
    param(
        [Parameter(Mandatory = $true)][object]$Health
    )

    if ($null -eq $Health) {
        throw "Health check failed: response is empty."
    }
    if ($null -eq $Health.deployment) {
        throw "Health check failed: response is missing deployment."
    }
    if (-not (Has-Property -Object $Health.deployment -Name "runtime_build_revision")) {
        throw "Health check failed: deployment is missing runtime_build_revision."
    }
    return [string]$Health.deployment.runtime_build_revision
}

function Wait-ForDeploymentParity {
    param(
        [Parameter(Mandatory = $true)][string]$BaseUrl,
        [Parameter(Mandatory = $true)][string]$ExpectedRevision,
        [Parameter(Mandatory = $true)][int]$TimeoutSeconds,
        [Parameter(Mandatory = $true)][int]$PollSeconds
    )

    $deadline = [datetimeoffset]::UtcNow.AddSeconds($TimeoutSeconds)

    while ($true) {
        $health = Invoke-HealthJsonWithRetry `
            -Uri "$BaseUrl/health" `
            -MaxAttempts $HealthRetryMaxAttempts `
            -DelaySeconds $HealthRetryDelaySeconds
        $observedRevision = Get-DeploymentRuntimeBuildRevision -Health $health
        if ($observedRevision -eq $ExpectedRevision) {
            return $health
        }

        if ([datetimeoffset]::UtcNow -ge $deadline) {
            throw "Health check failed: deployment runtime_build_revision '$observedRevision' did not match local repo HEAD '$ExpectedRevision' within $TimeoutSeconds seconds."
        }

        Start-Sleep -Seconds $PollSeconds
    }
}

function Invoke-HealthJsonWithRetry {
    param(
        [Parameter(Mandatory = $true)][string]$Uri,
        [Parameter(Mandatory = $true)][int]$MaxAttempts,
        [Parameter(Mandatory = $true)][int]$DelaySeconds
    )

    $attempt = 0
    $lastErrorMessage = ""

    while ($attempt -lt $MaxAttempts) {
        $attempt += 1
        try {
            return Invoke-JsonUtf8 -Method GET -Uri $Uri
        }
        catch {
            $lastErrorMessage = $_.Exception.Message
            if ($attempt -ge $MaxAttempts) {
                throw "Health check failed after $MaxAttempts attempts: $lastErrorMessage"
            }
            Start-Sleep -Seconds $DelaySeconds
        }
    }

    throw "Health check failed after $MaxAttempts attempts: $lastErrorMessage"
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
        deployment_automation_policy_owner = $null
        deployment_primary_trigger_mode = $null
        deployment_runtime_trigger_mode = $null
        deployment_runtime_trigger_class = $null
        deployment_runtime_build_revision = $null
        deployment_runtime_build_revision_state = $null
        deployment_runtime_provenance_state = $null
        organizer_tool_stack_policy_owner = $null
        organizer_tool_stack_readiness_state = $null
        organizer_tool_stack_ready_operations = @()
        organizer_tool_stack_credential_gap_operations = @()
        organizer_tool_activation_state = $null
        organizer_tool_activation_next_actions = @()
        retrieval_policy_owner = $null
        retrieval_provider_requested = $null
        retrieval_provider_effective = $null
        retrieval_execution_class = $null
        retrieval_baseline_state = $null
        retrieval_provider_drift_state = $null
        retrieval_alignment_state = $null
        learned_state_tool_grounded_policy_owner = $null
        learned_state_tool_grounded_allowed_read_operations = @()
        capability_catalog_policy_owner = $null
        capability_catalog_approved_tool_families = @()
        capability_catalog_skill_execution_boundary = $null
        capability_catalog_catalog_count = $null
        capability_catalog_organizer_stack_state = $null
        capability_catalog_organizer_activation_state = $null
        capability_catalog_execution_baseline_owner = $null
        capability_catalog_tool_grounded_learning_policy_owner = $null
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
    if ([string]$telegramConversation.delivery_adaptation_policy_owner -ne "telegram_delivery_channel_adaptation") {
        throw "Incident evidence bundle verification failed: unexpected conversation_channels.telegram delivery_adaptation_policy_owner '$($telegramConversation.delivery_adaptation_policy_owner)'."
    }
    if ([string]$telegramConversation.delivery_segmentation_state -ne "bounded_transport_segmentation") {
        throw "Incident evidence bundle verification failed: unexpected conversation_channels.telegram delivery_segmentation_state '$($telegramConversation.delivery_segmentation_state)'."
    }
    if ([string]$telegramConversation.delivery_formatting_state -ne "supported_markdown_to_html_with_plain_text_fallback") {
        throw "Incident evidence bundle verification failed: unexpected conversation_channels.telegram delivery_formatting_state '$($telegramConversation.delivery_formatting_state)'."
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
    $learnedStateContract = Assert-LearnedStateContract `
        -LearnedState $learnedState `
        -FailurePrefix "Incident evidence bundle verification failed"
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
    $incidentDeployment = $incidentEvidence.policy_posture.deployment
    if ($null -eq $incidentDeployment) {
        throw "Incident evidence bundle verification failed: deployment posture is missing."
    }
    if ([string]$incidentDeployment.deployment_automation_policy_owner -ne "coolify_repo_deploy_automation") {
        throw "Incident evidence bundle verification failed: unexpected deployment_automation_policy_owner '$($incidentDeployment.deployment_automation_policy_owner)'."
    }
    if ([string]$incidentDeployment.deployment_automation_baseline.primary_trigger_mode -ne "source_automation") {
        throw "Incident evidence bundle verification failed: unexpected deployment primary_trigger_mode '$($incidentDeployment.deployment_automation_baseline.primary_trigger_mode)'."
    }
    $incidentDeploymentFallbackModes = @($incidentDeployment.deployment_automation_baseline.fallback_trigger_modes)
    foreach ($requiredFallbackMode in @("webhook_manual_fallback", "ui_manual_fallback")) {
        if ($incidentDeploymentFallbackModes -notcontains $requiredFallbackMode) {
            throw "Incident evidence bundle verification failed: deployment posture is missing fallback trigger mode '$requiredFallbackMode'."
        }
    }
    if (-not (Has-Property -Object $incidentDeployment -Name "runtime_trigger_mode")) {
        throw "Incident evidence bundle verification failed: deployment runtime_trigger_mode is missing."
    }
    if (-not (Has-Property -Object $incidentDeployment -Name "runtime_trigger_class")) {
        throw "Incident evidence bundle verification failed: deployment runtime_trigger_class is missing."
    }
    if (-not (Has-Property -Object $incidentDeployment -Name "runtime_build_revision")) {
        throw "Incident evidence bundle verification failed: deployment runtime_build_revision is missing."
    }
    if (-not (Has-Property -Object $incidentDeployment -Name "runtime_build_revision_state")) {
        throw "Incident evidence bundle verification failed: deployment runtime_build_revision_state is missing."
    }
    if (-not (Has-Property -Object $incidentDeployment -Name "runtime_provenance_state")) {
        throw "Incident evidence bundle verification failed: deployment runtime_provenance_state is missing."
    }
    $validRuntimeTriggerModes = @("source_automation", "webhook_manual_fallback", "ui_manual_fallback")
    if ($validRuntimeTriggerModes -notcontains [string]$incidentDeployment.runtime_trigger_mode) {
        throw "Incident evidence bundle verification failed: unexpected deployment runtime_trigger_mode '$($incidentDeployment.runtime_trigger_mode)'."
    }
    $validRuntimeTriggerClasses = @("primary_automation", "manual_fallback")
    if ($validRuntimeTriggerClasses -notcontains [string]$incidentDeployment.runtime_trigger_class) {
        throw "Incident evidence bundle verification failed: unexpected deployment runtime_trigger_class '$($incidentDeployment.runtime_trigger_class)'."
    }
    if ([string]$incidentDeployment.runtime_build_revision_state -eq "runtime_build_revision_missing") {
        throw "Incident evidence bundle verification failed: deployment runtime_build_revision is still missing."
    }
    if (-not [string]$incidentDeployment.runtime_build_revision) {
        throw "Incident evidence bundle verification failed: deployment runtime_build_revision is empty."
    }
    $healthConnectors = $healthSnapshot.connectors
    if ($null -eq $healthConnectors) {
        throw "Incident evidence bundle verification failed: health snapshot connectors surface is missing."
    }
    $healthOrganizerToolStack = $healthConnectors.organizer_tool_stack
    $organizerToolStackContract = Assert-OrganizerToolStackContract `
        -OrganizerToolStack $healthOrganizerToolStack `
        -FailurePrefix "Incident evidence bundle verification failed"
    $healthWebKnowledgeTools = $healthConnectors.web_knowledge_tools
    $webKnowledgeWorkflowContract = Assert-WebKnowledgeWorkflowContract `
        -WebKnowledgeTools $healthWebKnowledgeTools `
        -FailurePrefix "Incident evidence bundle verification failed"
    $healthCapabilityCatalog = $healthSnapshot.capability_catalog
    $capabilityCatalogContract = Assert-CapabilityCatalogContract `
        -CapabilityCatalog $healthCapabilityCatalog `
        -FailurePrefix "Incident evidence bundle verification failed"
    $incidentOrganizerToolStack = $incidentEvidence.policy_posture."connectors.organizer_tool_stack"
    $incidentOrganizerToolStackContract = Assert-OrganizerToolStackContract `
        -OrganizerToolStack $incidentOrganizerToolStack `
        -FailurePrefix "Incident evidence bundle verification failed"
    $incidentWebKnowledgeTools = $incidentEvidence.policy_posture."connectors.web_knowledge_tools"
    $incidentWebKnowledgeWorkflowContract = Assert-WebKnowledgeWorkflowContract `
        -WebKnowledgeTools $incidentWebKnowledgeTools `
        -FailurePrefix "Incident evidence bundle verification failed"

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
        telegram_delivery_adaptation_policy_owner = [string]$telegramConversation.delivery_adaptation_policy_owner
        telegram_delivery_segmentation_state = [string]$telegramConversation.delivery_segmentation_state
        telegram_delivery_formatting_state = [string]$telegramConversation.delivery_formatting_state
        attention_coordination_mode = [string]$attention.coordination_mode
        attention_contract_store_state = [string]$attention.deployment_readiness.contract_store_state
        attention_runtime_topology_selected_mode = [string]$runtimeTopologyAttention.selected_mode
        proactive_policy_owner = [string]$proactive.policy_owner
        proactive_enabled = [bool]$proactive.enabled
        proactive_production_baseline_state = [string]$proactive.production_baseline_state
        deployment_automation_policy_owner = [string]$incidentDeployment.deployment_automation_policy_owner
        deployment_primary_trigger_mode = [string]$incidentDeployment.deployment_automation_baseline.primary_trigger_mode
        deployment_runtime_trigger_mode = [string]$incidentDeployment.runtime_trigger_mode
        deployment_runtime_trigger_class = [string]$incidentDeployment.runtime_trigger_class
        deployment_runtime_build_revision = [string]$incidentDeployment.runtime_build_revision
        deployment_runtime_build_revision_state = [string]$incidentDeployment.runtime_build_revision_state
        deployment_runtime_provenance_state = [string]$incidentDeployment.runtime_provenance_state
        organizer_tool_stack_policy_owner = [string]$organizerToolStackContract.policy_owner
        organizer_tool_stack_readiness_state = [string]$organizerToolStackContract.readiness_state
        organizer_tool_stack_ready_operations = @($organizerToolStackContract.ready_operations)
        organizer_tool_stack_credential_gap_operations = @($organizerToolStackContract.credential_gap_operations)
        organizer_tool_stack_daily_use_state = [string]$organizerToolStackContract.daily_use_state
        organizer_tool_stack_daily_use_ready_workflow_count = [int]$organizerToolStackContract.daily_use_ready_workflow_count
        organizer_tool_activation_state = [string]$organizerToolStackContract.activation_state
        organizer_tool_activation_next_actions = @($organizerToolStackContract.activation_next_actions)
        web_knowledge_policy_owner = [string]$webKnowledgeWorkflowContract.policy_owner
        website_reading_workflow_policy_owner = [string]$webKnowledgeWorkflowContract.workflow_policy_owner
        website_reading_workflow_state = [string]$webKnowledgeWorkflowContract.workflow_state
        website_reading_direct_url_review_available = [bool]$webKnowledgeWorkflowContract.direct_url_review_available
        website_reading_search_then_page_review_available = [bool]$webKnowledgeWorkflowContract.search_then_page_review_available
        website_reading_allowed_entry_modes = @($webKnowledgeWorkflowContract.allowed_entry_modes)
        website_reading_search_provider_hint = [string]$webKnowledgeWorkflowContract.search_provider_hint
        website_reading_page_read_provider_hint = [string]$webKnowledgeWorkflowContract.page_read_provider_hint
        website_reading_memory_capture_boundary = [string]$webKnowledgeWorkflowContract.memory_capture_boundary
        incident_web_knowledge_policy_owner = [string]$incidentWebKnowledgeWorkflowContract.policy_owner
        incident_website_reading_workflow_state = [string]$incidentWebKnowledgeWorkflowContract.workflow_state
        retrieval_policy_owner = [string]$retrievalAlignment.retrieval_policy_owner
        retrieval_provider_requested = [string]$retrievalAlignment.provider_requested
        retrieval_provider_effective = [string]$retrievalAlignment.provider_effective
        retrieval_execution_class = [string]$retrievalAlignment.execution_class
        retrieval_baseline_state = [string]$retrievalAlignment.production_baseline_state
        retrieval_provider_drift_state = [string]$retrievalAlignment.provider_drift_state
        retrieval_alignment_state = [string]$retrievalAlignment.alignment_state
        learned_state_policy_owner = [string]$learnedStateContract.policy_owner
        learned_state_internal_inspection_path = [string]$learnedStateContract.internal_inspection_path
        learned_state_inspection_sections = @($learnedStateContract.inspection_sections)
        learned_state_growth_summary_sections = @($learnedStateContract.growth_summary_sections)
        learned_state_tool_grounded_policy_owner = [string]$learnedStateContract.tool_grounded_policy_owner
        learned_state_tool_grounded_allowed_read_operations = @($learnedStateContract.tool_grounded_allowed_read_operations)
        capability_catalog_policy_owner = [string]$capabilityCatalogContract.policy_owner
        capability_catalog_approved_tool_families = @($capabilityCatalogContract.approved_tool_families)
        capability_catalog_skill_execution_boundary = [string]$capabilityCatalogContract.skill_execution_boundary
        capability_catalog_catalog_count = [int]$capabilityCatalogContract.catalog_count
        capability_catalog_organizer_stack_state = [string]$capabilityCatalogContract.organizer_stack_state
        capability_catalog_organizer_activation_state = [string]$capabilityCatalogContract.organizer_activation_state
        capability_catalog_execution_baseline_owner = [string]$capabilityCatalogContract.execution_baseline_owner
        capability_catalog_tool_grounded_learning_policy_owner = [string]$capabilityCatalogContract.tool_grounded_learning_policy_owner
        incident_organizer_tool_stack_policy_owner = [string]$incidentOrganizerToolStackContract.policy_owner
        incident_organizer_tool_stack_readiness_state = [string]$incidentOrganizerToolStackContract.readiness_state
        incident_organizer_tool_stack_daily_use_state = [string]$incidentOrganizerToolStackContract.daily_use_state
        incident_organizer_tool_stack_daily_use_ready_workflow_count = [int]$incidentOrganizerToolStackContract.daily_use_ready_workflow_count
        incident_organizer_tool_activation_state = [string]$incidentOrganizerToolStackContract.activation_state
        incident_organizer_tool_activation_next_actions = @($incidentOrganizerToolStackContract.activation_next_actions)
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

function Assert-LearnedStateContract {
    param(
        [object]$LearnedState,
        [Parameter(Mandatory = $true)][string]$FailurePrefix
    )

    $expectedInspectionSections = @(
        "identity_state",
        "learned_knowledge",
        "role_skill_state",
        "planning_state"
    )
    $expectedGrowthSummarySections = @(
        "preference_summary",
        "knowledge_summary",
        "reflection_growth_summary",
        "planning_continuity_summary"
    )
    $expectedRoleSkillMetadataSections = @(
        "role_skill_policy",
        "skill_registry",
        "selection_visibility_summary"
    )
    $expectedPlanningContinuitySections = @(
        "active_goals",
        "active_tasks",
        "active_goal_milestones",
        "pending_proposals",
        "continuity_summary"
    )
    $expectedReflectionGrowthSignalKinds = @(
        "semantic_conclusions",
        "affective_conclusions",
        "tool_grounded_conclusions",
        "adaptive_outputs",
        "relations"
    )
    $expectedToolGroundedReadOperations = @(
        "knowledge_search.search_web",
        "web_browser.read_page",
        "task_system.list_tasks",
        "calendar.read_availability",
        "cloud_drive.list_files"
    )

    if ($null -eq $LearnedState) {
        throw "${FailurePrefix}: learned_state posture is missing."
    }
    if ([string]$LearnedState.policy_owner -ne "learned_state_inspection_policy") {
        throw "${FailurePrefix}: unexpected learned_state policy_owner '$($LearnedState.policy_owner)'."
    }
    if ([string]$LearnedState.internal_inspection_path -ne "/internal/state/inspect") {
        throw "${FailurePrefix}: unexpected learned_state internal_inspection_path '$($LearnedState.internal_inspection_path)'."
    }
    if (-not (Has-Property -Object $LearnedState -Name "inspection_sections")) {
        throw "${FailurePrefix}: learned_state is missing inspection_sections."
    }
    if (-not (Has-Property -Object $LearnedState -Name "growth_summary_sections")) {
        throw "${FailurePrefix}: learned_state is missing growth_summary_sections."
    }
    if (-not (Has-Property -Object $LearnedState -Name "role_skill_metadata_sections")) {
        throw "${FailurePrefix}: learned_state is missing role_skill_metadata_sections."
    }
    if (-not (Has-Property -Object $LearnedState -Name "planning_continuity_sections")) {
        throw "${FailurePrefix}: learned_state is missing planning_continuity_sections."
    }
    if (-not (Has-Property -Object $LearnedState -Name "reflection_growth_signal_kinds")) {
        throw "${FailurePrefix}: learned_state is missing reflection_growth_signal_kinds."
    }
    if (-not (Has-Property -Object $LearnedState -Name "tool_grounded_learning")) {
        throw "${FailurePrefix}: learned_state is missing tool_grounded_learning."
    }

    $inspectionSections = @($LearnedState.inspection_sections)
    $growthSummarySections = @($LearnedState.growth_summary_sections)
    $roleSkillMetadataSections = @($LearnedState.role_skill_metadata_sections)
    $planningContinuitySections = @($LearnedState.planning_continuity_sections)
    $reflectionGrowthSignalKinds = @($LearnedState.reflection_growth_signal_kinds)
    $toolGroundedLearning = $LearnedState.tool_grounded_learning

    if (@(Compare-Object -ReferenceObject $expectedInspectionSections -DifferenceObject $inspectionSections).Count -ne 0) {
        throw "${FailurePrefix}: learned_state inspection_sections do not match the bounded contract."
    }
    if (@(Compare-Object -ReferenceObject $expectedGrowthSummarySections -DifferenceObject $growthSummarySections).Count -ne 0) {
        throw "${FailurePrefix}: learned_state growth_summary_sections do not match the bounded contract."
    }
    if (@(Compare-Object -ReferenceObject $expectedRoleSkillMetadataSections -DifferenceObject $roleSkillMetadataSections).Count -ne 0) {
        throw "${FailurePrefix}: learned_state role_skill_metadata_sections do not match the bounded contract."
    }
    if (@(Compare-Object -ReferenceObject $expectedPlanningContinuitySections -DifferenceObject $planningContinuitySections).Count -ne 0) {
        throw "${FailurePrefix}: learned_state planning_continuity_sections do not match the bounded contract."
    }
    if (@(Compare-Object -ReferenceObject $expectedReflectionGrowthSignalKinds -DifferenceObject $reflectionGrowthSignalKinds).Count -ne 0) {
        throw "${FailurePrefix}: learned_state reflection_growth_signal_kinds do not match the bounded contract."
    }
    if ($null -eq $toolGroundedLearning) {
        throw "${FailurePrefix}: learned_state tool_grounded_learning contract is missing."
    }
    if ([string]$toolGroundedLearning.policy_owner -ne "tool_grounded_learning_policy") {
        throw "${FailurePrefix}: unexpected learned_state tool_grounded_learning policy_owner '$($toolGroundedLearning.policy_owner)'."
    }
    if ([string]$toolGroundedLearning.capture_owner -ne "action_owned_external_read_summaries_only") {
        throw "${FailurePrefix}: unexpected learned_state tool_grounded_learning capture_owner '$($toolGroundedLearning.capture_owner)'."
    }
    if ([string]$toolGroundedLearning.persistence_owner -ne "memory_conclusion_write_after_action") {
        throw "${FailurePrefix}: unexpected learned_state tool_grounded_learning persistence_owner '$($toolGroundedLearning.persistence_owner)'."
    }
    if ([bool]$toolGroundedLearning.raw_payload_storage_allowed) {
        throw "${FailurePrefix}: learned_state tool_grounded_learning must keep raw_payload_storage_allowed false."
    }
    if ([bool]$toolGroundedLearning.execution_bypass_allowed) {
        throw "${FailurePrefix}: learned_state tool_grounded_learning must keep execution_bypass_allowed false."
    }
    if ([bool]$toolGroundedLearning.self_modifying_skill_learning_allowed) {
        throw "${FailurePrefix}: learned_state tool_grounded_learning must keep self_modifying_skill_learning_allowed false."
    }
    $toolGroundedReadOperations = @($toolGroundedLearning.allowed_read_operations)
    if (@(Compare-Object -ReferenceObject $expectedToolGroundedReadOperations -DifferenceObject $toolGroundedReadOperations).Count -ne 0) {
        throw "${FailurePrefix}: learned_state tool_grounded_learning allowed_read_operations do not match the bounded contract."
    }

    return @{
        policy_owner = [string]$LearnedState.policy_owner
        internal_inspection_path = [string]$LearnedState.internal_inspection_path
        inspection_sections = $inspectionSections
        growth_summary_sections = $growthSummarySections
        role_skill_metadata_sections = $roleSkillMetadataSections
        planning_continuity_sections = $planningContinuitySections
        reflection_growth_signal_kinds = $reflectionGrowthSignalKinds
        tool_grounded_policy_owner = [string]$toolGroundedLearning.policy_owner
        tool_grounded_allowed_read_operations = $toolGroundedReadOperations
    }
}

function Assert-CapabilityCatalogContract {
    param(
        [object]$CapabilityCatalog,
        [Parameter(Mandatory = $true)][string]$FailurePrefix
    )

    $expectedApprovedToolFamilies = @(
        "calendar",
        "cloud_drive",
        "knowledge_search",
        "task_system",
        "web_browser"
    )

    if ($null -eq $CapabilityCatalog) {
        throw "${FailurePrefix}: capability_catalog posture is missing."
    }
    if ([string]$CapabilityCatalog.policy_owner -ne "backend_capability_catalog_policy") {
        throw "${FailurePrefix}: unexpected capability_catalog policy_owner '$($CapabilityCatalog.policy_owner)'."
    }
    if ([string]$CapabilityCatalog.catalog_posture -ne "aggregated_backend_truth_surface") {
        throw "${FailurePrefix}: unexpected capability_catalog catalog_posture '$($CapabilityCatalog.catalog_posture)'."
    }
    if ([string]$CapabilityCatalog.execution_authority -ne "unchanged_action_boundary") {
        throw "${FailurePrefix}: unexpected capability_catalog execution_authority '$($CapabilityCatalog.execution_authority)'."
    }
    if ([string]$CapabilityCatalog.authorization_authority -ne "unchanged_connector_permission_gates") {
        throw "${FailurePrefix}: unexpected capability_catalog authorization_authority '$($CapabilityCatalog.authorization_authority)'."
    }
    if ($null -eq $CapabilityCatalog.capability_record_truth_model) {
        throw "${FailurePrefix}: capability_catalog capability_record_truth_model is missing."
    }
    if ([string]$CapabilityCatalog.capability_record_truth_model.description_boundary -ne "durable_role_and_skill_metadata_plus_tool_authorization_records") {
        throw "${FailurePrefix}: capability_catalog description boundary is unexpected."
    }
    if ([string]$CapabilityCatalog.capability_record_truth_model.selection_boundary -ne "runtime_turn_selection_and_selected_skill_metadata") {
        throw "${FailurePrefix}: capability_catalog selection boundary is unexpected."
    }
    if ([string]$CapabilityCatalog.capability_record_truth_model.authorization_boundary -ne "connector_permission_gates_plus_provider_readiness") {
        throw "${FailurePrefix}: capability_catalog authorization boundary is unexpected."
    }
    if ($null -eq $CapabilityCatalog.source_surfaces) {
        throw "${FailurePrefix}: capability_catalog source_surfaces are missing."
    }
    $requiredSourceSurfaces = @{
        api_readiness = "/health.api_readiness"
        learned_state = "/health.learned_state"
        role_skill = "/health.role_skill"
        connectors = "/health.connectors"
        internal_inspection = "/internal/state/inspect"
        current_turn_role = "system_debug.role"
        current_turn_selected_skills = "system_debug.adaptive_state.selected_skills"
        current_turn_plan = "system_debug.plan"
    }
    foreach ($sourceSurface in $requiredSourceSurfaces.GetEnumerator()) {
        if ([string]$CapabilityCatalog.source_surfaces.($sourceSurface.Key) -ne $sourceSurface.Value) {
            throw "${FailurePrefix}: capability_catalog source_surfaces.$($sourceSurface.Key) is unexpected."
        }
    }
    if ($null -eq $CapabilityCatalog.role_posture) {
        throw "${FailurePrefix}: capability_catalog role_posture is missing."
    }
    if ([string]$CapabilityCatalog.role_posture.role_selection_owner -ne "role_selection_policy") {
        throw "${FailurePrefix}: capability_catalog role_posture.role_selection_owner is unexpected."
    }
    if (-not [bool]$CapabilityCatalog.role_posture.work_partner_role_available) {
        throw "${FailurePrefix}: capability_catalog role_posture.work_partner_role_available is not true."
    }
    $describedRoleNames = @($CapabilityCatalog.role_posture.described_role_names)
    foreach ($requiredRole in @("friend", "advisor", "analyst", "executor", "mentor", "work_partner")) {
        if ($describedRoleNames -notcontains $requiredRole) {
            throw "${FailurePrefix}: capability_catalog role_posture is missing described role '$requiredRole'."
        }
    }
    if ($describedRoleNames.Count -ne @($CapabilityCatalog.role_posture.selectable_role_names).Count) {
        throw "${FailurePrefix}: capability_catalog role_posture described and selectable role counts drift."
    }
    if ($null -eq $CapabilityCatalog.skill_catalog_posture) {
        throw "${FailurePrefix}: capability_catalog skill_catalog_posture is missing."
    }
    if ([string]$CapabilityCatalog.skill_catalog_posture.skill_selection_owner -ne "skill_registry") {
        throw "${FailurePrefix}: capability_catalog skill_catalog_posture.skill_selection_owner is unexpected."
    }
    if ([string]$CapabilityCatalog.skill_catalog_posture.skill_execution_boundary -ne "metadata_only_capability_hints") {
        throw "${FailurePrefix}: capability_catalog skill_catalog_posture.skill_execution_boundary is unexpected."
    }
    if ([bool]$CapabilityCatalog.skill_catalog_posture.action_skill_execution_allowed) {
        throw "${FailurePrefix}: capability_catalog skill_catalog_posture.action_skill_execution_allowed must be false."
    }
    if ([int]$CapabilityCatalog.skill_catalog_posture.catalog_count -lt 1) {
        throw "${FailurePrefix}: capability_catalog skill_catalog_posture.catalog_count must be positive."
    }
    $describedSkillIds = @($CapabilityCatalog.skill_catalog_posture.described_skill_ids)
    foreach ($requiredSkillId in @("emotional_support", "structured_reasoning", "execution_planning", "memory_recall", "connector_boundary_review")) {
        if ($describedSkillIds -notcontains $requiredSkillId) {
            throw "${FailurePrefix}: capability_catalog skill_catalog_posture is missing described skill '$requiredSkillId'."
        }
    }
    if ($null -eq $CapabilityCatalog.tool_and_connector_posture) {
        throw "${FailurePrefix}: capability_catalog tool_and_connector_posture is missing."
    }
    if ([string]$CapabilityCatalog.tool_and_connector_posture.authorization_record_owner -ne "connector_execution_policy") {
        throw "${FailurePrefix}: capability_catalog tool_and_connector_posture.authorization_record_owner is unexpected."
    }
    $actualApprovedToolFamilies = @($CapabilityCatalog.tool_and_connector_posture.approved_tool_families)
    foreach ($requiredToolFamily in $expectedApprovedToolFamilies) {
        if ($actualApprovedToolFamilies -notcontains $requiredToolFamily) {
            throw "${FailurePrefix}: capability_catalog tool_and_connector_posture is missing approved tool family '$requiredToolFamily'."
        }
    }
    $actualSelectableToolFamilies = @($CapabilityCatalog.tool_and_connector_posture.selectable_tool_families)
    foreach ($requiredSelectableToolFamily in $expectedApprovedToolFamilies) {
        if ($actualSelectableToolFamilies -notcontains $requiredSelectableToolFamily) {
            throw "${FailurePrefix}: capability_catalog tool_and_connector_posture is missing selectable tool family '$requiredSelectableToolFamily'."
        }
    }
    $authorizedWithoutOptInOperations = @($CapabilityCatalog.tool_and_connector_posture.authorized_without_opt_in_operations)
    foreach ($requiredAuthorizedRead in @("knowledge_search.search_web", "web_browser.read_page")) {
        if ($authorizedWithoutOptInOperations -notcontains $requiredAuthorizedRead) {
            throw "${FailurePrefix}: capability_catalog tool_and_connector_posture is missing authorized public read '$requiredAuthorizedRead'."
        }
    }
    $authorizedWithConfirmationOperations = @($CapabilityCatalog.tool_and_connector_posture.authorized_with_confirmation_operations)
    foreach ($requiredConfirmedOperation in @("task_system.create_task", "task_system.update_task")) {
        if ($authorizedWithConfirmationOperations -notcontains $requiredConfirmedOperation) {
            throw "${FailurePrefix}: capability_catalog tool_and_connector_posture is missing confirmation-gated operation '$requiredConfirmedOperation'."
        }
    }
    if ([string]$CapabilityCatalog.tool_and_connector_posture.execution_baseline_owner -ne "connector_execution_registry") {
        throw "${FailurePrefix}: capability_catalog tool_and_connector_posture.execution_baseline_owner is unexpected."
    }
    if (-not [string]$CapabilityCatalog.tool_and_connector_posture.organizer_stack_state) {
        throw "${FailurePrefix}: capability_catalog tool_and_connector_posture.organizer_stack_state is missing."
    }
    if (-not [string]$CapabilityCatalog.tool_and_connector_posture.organizer_activation_state) {
        throw "${FailurePrefix}: capability_catalog tool_and_connector_posture.organizer_activation_state is missing."
    }
    if ($null -eq $CapabilityCatalog.tool_and_connector_posture.web_knowledge_tools) {
        throw "${FailurePrefix}: capability_catalog tool_and_connector_posture.web_knowledge_tools is missing."
    }
    if ([string]$CapabilityCatalog.tool_and_connector_posture.web_knowledge_tools.policy_owner -ne "web_knowledge_tooling_policy") {
        throw "${FailurePrefix}: capability_catalog tool_and_connector_posture.web_knowledge_tools.policy_owner is unexpected."
    }
    if ($null -eq $CapabilityCatalog.learned_state_linkage) {
        throw "${FailurePrefix}: capability_catalog learned_state_linkage is missing."
    }
    if ([string]$CapabilityCatalog.learned_state_linkage.learned_state_policy_owner -ne "learned_state_inspection_policy") {
        throw "${FailurePrefix}: capability_catalog learned_state_linkage.learned_state_policy_owner is unexpected."
    }
    if ([string]$CapabilityCatalog.learned_state_linkage.tool_grounded_learning_policy_owner -ne "tool_grounded_learning_policy") {
        throw "${FailurePrefix}: capability_catalog learned_state_linkage.tool_grounded_learning_policy_owner is unexpected."
    }
    if ([string]$CapabilityCatalog.learned_state_linkage.skill_learning_posture -ne "selected_skill_metadata_only") {
        throw "${FailurePrefix}: capability_catalog learned_state_linkage.skill_learning_posture is unexpected."
    }
    if ([string]$CapabilityCatalog.learned_state_linkage.internal_inspection_path -ne "/internal/state/inspect") {
        throw "${FailurePrefix}: capability_catalog learned_state_linkage.internal_inspection_path is unexpected."
    }

    return @{
        policy_owner = [string]$CapabilityCatalog.policy_owner
        approved_tool_families = $actualApprovedToolFamilies
        described_role_names = $describedRoleNames
        described_skill_ids = $describedSkillIds
        skill_execution_boundary = [string]$CapabilityCatalog.skill_catalog_posture.skill_execution_boundary
        catalog_count = [int]$CapabilityCatalog.skill_catalog_posture.catalog_count
        authorization_record_owner = [string]$CapabilityCatalog.tool_and_connector_posture.authorization_record_owner
        authorized_without_opt_in_operations = $authorizedWithoutOptInOperations
        authorized_with_confirmation_operations = $authorizedWithConfirmationOperations
        organizer_stack_state = [string]$CapabilityCatalog.tool_and_connector_posture.organizer_stack_state
        organizer_activation_state = [string]$CapabilityCatalog.tool_and_connector_posture.organizer_activation_state
        execution_baseline_owner = [string]$CapabilityCatalog.tool_and_connector_posture.execution_baseline_owner
        tool_grounded_learning_policy_owner = [string]$CapabilityCatalog.learned_state_linkage.tool_grounded_learning_policy_owner
    }
}

function Assert-WebKnowledgeWorkflowContract {
    param(
        [object]$WebKnowledgeTools,
        [Parameter(Mandatory = $true)][string]$FailurePrefix
    )

    if ($null -eq $WebKnowledgeTools) {
        throw "${FailurePrefix}: web_knowledge_tools posture is missing."
    }
    if ([string]$WebKnowledgeTools.policy_owner -ne "web_knowledge_tooling_policy") {
        throw "${FailurePrefix}: unexpected web_knowledge_tools policy_owner '$($WebKnowledgeTools.policy_owner)'."
    }
    if ([string]$WebKnowledgeTools.tool_boundary -ne "action_owned_external_capability") {
        throw "${FailurePrefix}: unexpected web_knowledge_tools tool_boundary '$($WebKnowledgeTools.tool_boundary)'."
    }
    if ([string]$WebKnowledgeTools.provider_execution_posture -ne "first_bounded_provider_slices_selected") {
        throw "${FailurePrefix}: unexpected web_knowledge_tools provider_execution_posture '$($WebKnowledgeTools.provider_execution_posture)'."
    }
    if ($null -eq $WebKnowledgeTools.knowledge_search) {
        throw "${FailurePrefix}: web_knowledge_tools knowledge_search posture is missing."
    }
    if ($null -eq $WebKnowledgeTools.web_browser) {
        throw "${FailurePrefix}: web_knowledge_tools web_browser posture is missing."
    }
    if ([string]$WebKnowledgeTools.knowledge_search.selected_provider_hint -ne "duckduckgo_html") {
        throw "${FailurePrefix}: unexpected web_knowledge_tools knowledge_search.selected_provider_hint '$($WebKnowledgeTools.knowledge_search.selected_provider_hint)'."
    }
    if ([string]$WebKnowledgeTools.web_browser.selected_provider_hint -ne "generic_http") {
        throw "${FailurePrefix}: unexpected web_knowledge_tools web_browser.selected_provider_hint '$($WebKnowledgeTools.web_browser.selected_provider_hint)'."
    }
    if ($null -eq $WebKnowledgeTools.website_reading_workflow) {
        throw "${FailurePrefix}: web_knowledge_tools website_reading_workflow is missing."
    }

    $workflow = $WebKnowledgeTools.website_reading_workflow
    if ([string]$workflow.policy_owner -ne "website_reading_workflow_policy") {
        throw "${FailurePrefix}: unexpected website_reading_workflow policy_owner '$($workflow.policy_owner)'."
    }

    $validWorkflowStates = @(
        "ready_for_direct_and_search_first_review",
        "ready_for_direct_url_review_only",
        "search_available_but_page_review_blocked",
        "website_reading_blocked"
    )
    if ($validWorkflowStates -notcontains [string]$workflow.workflow_state) {
        throw "${FailurePrefix}: unexpected website_reading_workflow workflow_state '$($workflow.workflow_state)'."
    }

    if (-not (Has-Property -Object $workflow -Name "direct_url_review_available")) {
        throw "${FailurePrefix}: website_reading_workflow is missing direct_url_review_available."
    }
    if (-not (Has-Property -Object $workflow -Name "search_then_page_review_available")) {
        throw "${FailurePrefix}: website_reading_workflow is missing search_then_page_review_available."
    }

    $allowedEntryModes = @($workflow.allowed_entry_modes)
    $boundedReadSemantics = @($workflow.bounded_read_semantics)
    $boundedOutputContract = @($workflow.bounded_output_contract)
    $selectedProviderPath = $workflow.selected_provider_path

    if ($null -eq $selectedProviderPath) {
        throw "${FailurePrefix}: website_reading_workflow selected_provider_path is missing."
    }
    if ([string]$selectedProviderPath.search_provider_hint -ne "duckduckgo_html") {
        throw "${FailurePrefix}: unexpected website_reading_workflow search_provider_hint '$($selectedProviderPath.search_provider_hint)'."
    }
    if ([string]$selectedProviderPath.page_read_provider_hint -ne "generic_http") {
        throw "${FailurePrefix}: unexpected website_reading_workflow page_read_provider_hint '$($selectedProviderPath.page_read_provider_hint)'."
    }
    if ([string]$workflow.memory_capture_boundary -ne "tool_grounded_summary_only_via_action_then_memory") {
        throw "${FailurePrefix}: unexpected website_reading_workflow memory_capture_boundary '$($workflow.memory_capture_boundary)'."
    }
    foreach ($requiredSemantic in @("single_page_read_only", "search_optional_before_page_read", "no_login_or_form_submission", "no_raw_full_page_dump")) {
        if ($boundedReadSemantics -notcontains $requiredSemantic) {
            throw "${FailurePrefix}: website_reading_workflow is missing bounded_read_semantics '$requiredSemantic'."
        }
    }
    foreach ($requiredOutput in @("final_page_url", "bounded_summary", "source_note", "explicit_uncertainty_or_blocker_note")) {
        if ($boundedOutputContract -notcontains $requiredOutput) {
            throw "${FailurePrefix}: website_reading_workflow is missing bounded_output_contract '$requiredOutput'."
        }
    }

    return @{
        policy_owner = [string]$WebKnowledgeTools.policy_owner
        workflow_policy_owner = [string]$workflow.policy_owner
        workflow_state = [string]$workflow.workflow_state
        direct_url_review_available = [bool]$workflow.direct_url_review_available
        search_then_page_review_available = [bool]$workflow.search_then_page_review_available
        allowed_entry_modes = @($allowedEntryModes)
        search_provider_hint = [string]$selectedProviderPath.search_provider_hint
        page_read_provider_hint = [string]$selectedProviderPath.page_read_provider_hint
        memory_capture_boundary = [string]$workflow.memory_capture_boundary
        blockers = @($workflow.blockers)
        next_actions = @($workflow.next_actions)
    }
}

function Assert-OrganizerToolStackContract {
    param(
        [object]$OrganizerToolStack,
        [Parameter(Mandatory = $true)][string]$FailurePrefix
    )

    $expectedConnectorKinds = @("task_system", "calendar", "cloud_drive")
    $expectedApprovedOperations = @(
        "task_system.clickup_create_task",
        "task_system.clickup_list_tasks",
        "task_system.clickup_update_task",
        "calendar.google_calendar_read_availability",
        "cloud_drive.google_drive_list_files"
    )
    $expectedReadOnlyOperations = @(
        "task_system.clickup_list_tasks",
        "calendar.google_calendar_read_availability",
        "cloud_drive.google_drive_list_files"
    )
    $expectedConfirmationRequiredOperations = @(
        "task_system.clickup_create_task",
        "task_system.clickup_update_task"
    )
    $expectedDailyUseWorkflowIds = @(
        "clickup_task_review_and_mutation",
        "google_calendar_availability_inspection",
        "google_drive_file_space_inspection"
    )

    if ($null -eq $OrganizerToolStack) {
        throw "${FailurePrefix}: organizer_tool_stack posture is missing."
    }
    if ([string]$OrganizerToolStack.policy_owner -ne "production_organizer_tool_stack") {
        throw "${FailurePrefix}: unexpected organizer_tool_stack policy_owner '$($OrganizerToolStack.policy_owner)'."
    }
    if ([string]$OrganizerToolStack.stack_name -ne "clickup_calendar_drive_first_stack") {
        throw "${FailurePrefix}: unexpected organizer_tool_stack stack_name '$($OrganizerToolStack.stack_name)'."
    }
    foreach ($propertyName in @(
        "approved_connector_kinds",
        "approved_operations",
        "read_only_operations",
        "confirmation_required_operations",
        "user_opt_in_required_operations",
        "ready_operations",
        "credential_gap_operations",
        "readiness_state",
        "daily_use_workflows",
        "daily_use_ready_workflow_count",
        "daily_use_total_workflow_count",
        "daily_use_ready_workflows",
        "daily_use_blocked_workflows",
        "daily_use_state",
        "daily_use_hint",
        "activation_snapshot"
    )) {
        if (-not (Has-Property -Object $OrganizerToolStack -Name $propertyName)) {
            throw "${FailurePrefix}: organizer_tool_stack is missing $propertyName."
        }
    }

    $actualConnectorKinds = @($OrganizerToolStack.approved_connector_kinds)
    if (@(Compare-Object -ReferenceObject $expectedConnectorKinds -DifferenceObject $actualConnectorKinds -SyncWindow 0).Count -gt 0) {
        throw "${FailurePrefix}: organizer_tool_stack approved_connector_kinds drifted."
    }
    $actualApprovedOperations = @($OrganizerToolStack.approved_operations)
    if (@(Compare-Object -ReferenceObject $expectedApprovedOperations -DifferenceObject $actualApprovedOperations -SyncWindow 0).Count -gt 0) {
        throw "${FailurePrefix}: organizer_tool_stack approved_operations drifted."
    }
    $actualReadOnlyOperations = @($OrganizerToolStack.read_only_operations)
    if (@(Compare-Object -ReferenceObject $expectedReadOnlyOperations -DifferenceObject $actualReadOnlyOperations -SyncWindow 0).Count -gt 0) {
        throw "${FailurePrefix}: organizer_tool_stack read_only_operations drifted."
    }
    $actualConfirmationRequiredOperations = @($OrganizerToolStack.confirmation_required_operations)
    if (@(Compare-Object -ReferenceObject $expectedConfirmationRequiredOperations -DifferenceObject $actualConfirmationRequiredOperations -SyncWindow 0).Count -gt 0) {
        throw "${FailurePrefix}: organizer_tool_stack confirmation_required_operations drifted."
    }
    $actualOptInRequiredOperations = @($OrganizerToolStack.user_opt_in_required_operations)
    if (@(Compare-Object -ReferenceObject $expectedApprovedOperations -DifferenceObject $actualOptInRequiredOperations -SyncWindow 0).Count -gt 0) {
        throw "${FailurePrefix}: organizer_tool_stack user_opt_in_required_operations drifted."
    }

    $validReadinessStates = @("provider_stack_ready", "provider_credentials_missing")
    $readinessState = [string]$OrganizerToolStack.readiness_state
    if ($validReadinessStates -notcontains $readinessState) {
        throw "${FailurePrefix}: unexpected organizer_tool_stack readiness_state '$readinessState'."
    }

    $readyOperations = @($OrganizerToolStack.ready_operations)
    $credentialGapOperations = @($OrganizerToolStack.credential_gap_operations)
    if ($readinessState -eq "provider_stack_ready" -and $credentialGapOperations.Count -ne 0) {
        throw "${FailurePrefix}: organizer_tool_stack readiness_state is provider_stack_ready but credential_gap_operations is not empty."
    }
    if ($readinessState -eq "provider_credentials_missing" -and $credentialGapOperations.Count -eq 0) {
        throw "${FailurePrefix}: organizer_tool_stack readiness_state is provider_credentials_missing but credential_gap_operations is empty."
    }
    $dailyUseWorkflows = $OrganizerToolStack.daily_use_workflows
    if ($null -eq $dailyUseWorkflows) {
        throw "${FailurePrefix}: organizer_tool_stack daily_use_workflows is missing."
    }
    $actualDailyUseWorkflowIds = @()
    if ($dailyUseWorkflows.PSObject -and $dailyUseWorkflows.PSObject.Properties) {
        $actualDailyUseWorkflowIds = @($dailyUseWorkflows.PSObject.Properties.Name)
    }
    if (@(Compare-Object -ReferenceObject $expectedDailyUseWorkflowIds -DifferenceObject $actualDailyUseWorkflowIds -SyncWindow 0).Count -gt 0) {
        throw "${FailurePrefix}: organizer_tool_stack daily_use_workflows drifted."
    }
    $dailyUseReadyWorkflows = @($OrganizerToolStack.daily_use_ready_workflows)
    $dailyUseBlockedWorkflows = @($OrganizerToolStack.daily_use_blocked_workflows)
    $dailyUseReadyWorkflowCount = [int]$OrganizerToolStack.daily_use_ready_workflow_count
    $dailyUseTotalWorkflowCount = [int]$OrganizerToolStack.daily_use_total_workflow_count
    if ($dailyUseTotalWorkflowCount -ne $expectedDailyUseWorkflowIds.Count) {
        throw "${FailurePrefix}: organizer_tool_stack daily_use_total_workflow_count drifted."
    }
    if ($dailyUseReadyWorkflowCount -ne $dailyUseReadyWorkflows.Count) {
        throw "${FailurePrefix}: organizer_tool_stack daily_use_ready_workflow_count does not match daily_use_ready_workflows."
    }
    $validDailyUseStates = @("all_daily_use_workflows_ready", "daily_use_workflows_blocked_by_provider_activation")
    $dailyUseState = [string]$OrganizerToolStack.daily_use_state
    if ($validDailyUseStates -notcontains $dailyUseState) {
        throw "${FailurePrefix}: unexpected organizer_tool_stack daily_use_state '$($dailyUseState)'."
    }
    if ($dailyUseState -eq "all_daily_use_workflows_ready" -and $dailyUseBlockedWorkflows.Count -ne 0) {
        throw "${FailurePrefix}: organizer_tool_stack daily_use_state is all_daily_use_workflows_ready but daily_use_blocked_workflows is not empty."
    }
    if ($dailyUseState -eq "daily_use_workflows_blocked_by_provider_activation" -and $dailyUseBlockedWorkflows.Count -eq 0) {
        throw "${FailurePrefix}: organizer_tool_stack daily_use_state is daily_use_workflows_blocked_by_provider_activation but daily_use_blocked_workflows is empty."
    }

    $activationSnapshot = $OrganizerToolStack.activation_snapshot
    if ($null -eq $activationSnapshot) {
        throw "${FailurePrefix}: organizer_tool_stack activation_snapshot is missing."
    }
    if ([string]$activationSnapshot.policy_owner -ne "production_organizer_tool_activation") {
        throw "${FailurePrefix}: unexpected organizer_tool_stack activation_snapshot policy_owner '$($activationSnapshot.policy_owner)'."
    }
    $validActivationStates = @("provider_activation_incomplete", "all_providers_ready_for_operator_acceptance")
    $activationState = [string]$activationSnapshot.provider_activation_state
    if ($validActivationStates -notcontains $activationState) {
        throw "${FailurePrefix}: unexpected organizer_tool_stack activation state '$activationState'."
    }
    if (-not [bool]$activationSnapshot.user_opt_in_required) {
        throw "${FailurePrefix}: organizer_tool_stack activation_snapshot.user_opt_in_required must stay true."
    }
    if (-not [bool]$activationSnapshot.mutation_confirmation_required) {
        throw "${FailurePrefix}: organizer_tool_stack activation_snapshot.mutation_confirmation_required must stay true."
    }
    $providerRequirements = $activationSnapshot.provider_requirements
    if ($null -eq $providerRequirements) {
        throw "${FailurePrefix}: organizer_tool_stack activation_snapshot.provider_requirements is missing."
    }
    foreach ($providerName in @("clickup", "google_calendar", "google_drive")) {
        $providerEntry = $providerRequirements.$providerName
        if ($null -eq $providerEntry) {
            throw "${FailurePrefix}: organizer_tool_stack activation_snapshot.provider_requirements.$providerName is missing."
        }
        foreach ($propertyName in @(
            "provider",
            "required_settings",
            "activation_scope",
            "ready",
            "missing_settings",
            "user_opt_in_required",
            "confirmation_required_operations",
            "next_action"
        )) {
            if (-not (Has-Property -Object $providerEntry -Name $propertyName)) {
                throw "${FailurePrefix}: organizer_tool_stack activation_snapshot.provider_requirements.$providerName is missing $propertyName."
            }
        }
    }

    return @{
        policy_owner = [string]$OrganizerToolStack.policy_owner
        stack_name = [string]$OrganizerToolStack.stack_name
        readiness_state = $readinessState
        ready_operations = $readyOperations
        credential_gap_operations = $credentialGapOperations
        daily_use_ready_workflow_count = $dailyUseReadyWorkflowCount
        daily_use_total_workflow_count = $dailyUseTotalWorkflowCount
        daily_use_ready_workflows = $dailyUseReadyWorkflows
        daily_use_blocked_workflows = $dailyUseBlockedWorkflows
        daily_use_state = $dailyUseState
        daily_use_hint = [string]$OrganizerToolStack.daily_use_hint
        activation_state = $activationState
        activation_next_actions = @($activationSnapshot.next_actions)
    }
}

function Assert-V1ReadinessTruthContract {
    param(
        [object]$V1Readiness,
        [object]$TelegramConversation,
        [object]$LearnedState,
        [hashtable]$WebKnowledgeWorkflowContract,
        [hashtable]$OrganizerToolStackContract,
        [object]$Deployment,
        [Parameter(Mandatory = $true)][string]$FailurePrefix
    )

    if ($null -eq $V1Readiness) {
        throw "${FailurePrefix}: v1_readiness posture is missing."
    }
    foreach ($propertyName in @(
        "policy_owner",
        "product_stage",
        "conversation_gate_state",
        "learned_state_gate_state",
        "website_reading_workflow_state",
        "tool_grounded_learning_state",
        "time_aware_planned_work_policy_owner",
        "time_aware_planned_work_delivery_path",
        "time_aware_planned_work_recurrence_owner",
        "time_aware_planned_work_gate_state",
        "deploy_parity_state",
        "organizer_daily_use_state",
        "organizer_daily_use_classification",
        "final_acceptance_state",
        "final_acceptance_gate_states",
        "final_acceptance_surfaces",
        "extension_gate_states",
        "extension_gate_surfaces"
    )) {
        if (-not (Has-Property -Object $V1Readiness -Name $propertyName)) {
            throw "${FailurePrefix}: v1_readiness is missing $propertyName."
        }
    }

    if ([string]$V1Readiness.policy_owner -ne "v1_release_readiness_policy") {
        throw "${FailurePrefix}: unexpected v1_readiness policy_owner '$($V1Readiness.policy_owner)'."
    }
    if ([string]$V1Readiness.product_stage -ne "v1_no_ui_life_assistant") {
        throw "${FailurePrefix}: unexpected v1_readiness product_stage '$($V1Readiness.product_stage)'."
    }
    if ([string]$V1Readiness.organizer_daily_use_classification -ne "extension_readiness_non_blocking_for_core_v1") {
        throw "${FailurePrefix}: unexpected v1_readiness organizer_daily_use_classification '$($V1Readiness.organizer_daily_use_classification)'."
    }
    if ([string]$V1Readiness.time_aware_planned_work_policy_owner -ne "internal_time_aware_planned_work_policy") {
        throw "${FailurePrefix}: unexpected v1_readiness time_aware_planned_work_policy_owner '$($V1Readiness.time_aware_planned_work_policy_owner)'."
    }
    if ([string]$V1Readiness.time_aware_planned_work_delivery_path -ne "attention_to_planning_to_expression_to_action") {
        throw "${FailurePrefix}: unexpected v1_readiness time_aware_planned_work_delivery_path '$($V1Readiness.time_aware_planned_work_delivery_path)'."
    }
    if ([string]$V1Readiness.time_aware_planned_work_recurrence_owner -ne "scheduler_reevaluation_with_foreground_handoff") {
        throw "${FailurePrefix}: unexpected v1_readiness time_aware_planned_work_recurrence_owner '$($V1Readiness.time_aware_planned_work_recurrence_owner)'."
    }
    if ([string]$V1Readiness.time_aware_planned_work_gate_state -ne "foreground_due_delivery_and_recurring_reevaluation_ready") {
        throw "${FailurePrefix}: unexpected v1_readiness time_aware_planned_work_gate_state '$($V1Readiness.time_aware_planned_work_gate_state)'."
    }

    $telegramRoundTripState = [string]$TelegramConversation.round_trip_state
    $expectedConversationGateState = if ([bool]$TelegramConversation.round_trip_ready -and $telegramRoundTripState -eq "provider_backed_ready") {
        "conversation_surface_ready"
    }
    elseif ($telegramRoundTripState -eq "missing_bot_token") {
        "conversation_surface_provider_missing"
    }
    else {
        "conversation_surface_invalid"
    }
    if ([string]$V1Readiness.conversation_gate_state -ne $expectedConversationGateState) {
        throw "${FailurePrefix}: v1_readiness conversation_gate_state drifted from conversation_channels.telegram."
    }

    $expectedLearnedStateGateState = if ([string]$LearnedState.internal_inspection_path -eq "/internal/state/inspect") {
        "inspection_surface_ready"
    }
    else {
        "inspection_surface_invalid"
    }
    if ([string]$V1Readiness.learned_state_gate_state -ne $expectedLearnedStateGateState) {
        throw "${FailurePrefix}: v1_readiness learned_state_gate_state drifted from learned_state."
    }

    $toolGroundedLearning = $LearnedState.tool_grounded_learning
    $expectedToolGroundedLearningState = if (
        $null -ne $toolGroundedLearning `
        -and [string]$toolGroundedLearning.policy_owner -eq "tool_grounded_learning_policy" `
        -and [string]$toolGroundedLearning.capture_owner -eq "action_owned_external_read_summaries_only" `
        -and [string]$toolGroundedLearning.persistence_owner -eq "memory_conclusion_write_after_action" `
        -and -not [bool]$toolGroundedLearning.execution_bypass_allowed `
        -and -not [bool]$toolGroundedLearning.self_modifying_skill_learning_allowed
    ) {
        "tool_grounded_learning_surface_ready"
    }
    else {
        "tool_grounded_learning_surface_invalid"
    }
    if ([string]$V1Readiness.tool_grounded_learning_state -ne $expectedToolGroundedLearningState) {
        throw "${FailurePrefix}: v1_readiness tool_grounded_learning_state drifted from learned_state.tool_grounded_learning."
    }

    $expectedWebsiteReadingState = [string]$WebKnowledgeWorkflowContract.workflow_state
    if ([string]$V1Readiness.website_reading_workflow_state -ne $expectedWebsiteReadingState) {
        throw "${FailurePrefix}: v1_readiness website_reading_workflow_state drifted from connectors.web_knowledge_tools."
    }

    $expectedDeployParityState = if (
        [string]$Deployment.deployment_automation_policy_owner -eq "coolify_repo_deploy_automation" `
        -and [string]$Deployment.runtime_build_revision_state -eq "runtime_build_revision_declared" `
        -and [string]$Deployment.runtime_trigger_class -eq "primary_automation" `
        -and [string]$Deployment.runtime_provenance_state -eq "primary_runtime_provenance_declared"
    ) {
        "deploy_parity_surface_ready"
    }
    elseif (
        [string]$Deployment.deployment_automation_policy_owner -eq "coolify_repo_deploy_automation" `
        -and [string]$Deployment.runtime_build_revision_state -eq "runtime_build_revision_declared" `
        -and [string]$Deployment.runtime_trigger_mode -in @("webhook_manual_fallback", "ui_manual_fallback") `
        -and [string]$Deployment.runtime_provenance_state -eq "fallback_runtime_provenance_declared"
    ) {
        "deploy_parity_surface_manual_fallback"
    }
    else {
        "deploy_parity_surface_invalid"
    }
    if ([string]$V1Readiness.deploy_parity_state -ne $expectedDeployParityState) {
        throw "${FailurePrefix}: v1_readiness deploy_parity_state drifted from deployment."
    }

    if ([string]$V1Readiness.organizer_daily_use_state -ne [string]$OrganizerToolStackContract.daily_use_state) {
        throw "${FailurePrefix}: v1_readiness organizer_daily_use_state drifted from connectors.organizer_tool_stack."
    }

    $finalAcceptanceGateStates = $V1Readiness.final_acceptance_gate_states
    if ($null -eq $finalAcceptanceGateStates) {
        throw "${FailurePrefix}: v1_readiness final_acceptance_gate_states is missing."
    }
    if ($finalAcceptanceGateStates.PSObject.Properties.Name -contains "organizer_daily_use") {
        throw "${FailurePrefix}: v1_readiness final_acceptance_gate_states must not include organizer_daily_use."
    }
    $expectedFinalGateKeys = @(
        "conversation_reliability",
        "learned_state_inspection",
        "website_reading",
        "tool_grounded_learning",
        "time_aware_planned_work",
        "deploy_parity"
    )
    $actualFinalGateKeys = @($finalAcceptanceGateStates.PSObject.Properties.Name)
    if (@(Compare-Object -ReferenceObject $expectedFinalGateKeys -DifferenceObject $actualFinalGateKeys -SyncWindow 0).Count -gt 0) {
        throw "${FailurePrefix}: v1_readiness final_acceptance_gate_states drifted from the approved core-v1 boundary."
    }
    $expectedFinalGateStates = @{
        conversation_reliability = $expectedConversationGateState
        learned_state_inspection = $expectedLearnedStateGateState
        website_reading = $expectedWebsiteReadingState
        tool_grounded_learning = $expectedToolGroundedLearningState
        time_aware_planned_work = "foreground_due_delivery_and_recurring_reevaluation_ready"
        deploy_parity = $expectedDeployParityState
    }
    foreach ($gateName in $expectedFinalGateKeys) {
        if ([string]$finalAcceptanceGateStates.$gateName -ne [string]$expectedFinalGateStates[$gateName]) {
            throw "${FailurePrefix}: v1_readiness final_acceptance_gate_states.$gateName drifted from its owner surface."
        }
    }

    $expectedFinalAcceptanceState = if (
        $expectedConversationGateState -eq "conversation_surface_ready" `
        -and $expectedLearnedStateGateState -eq "inspection_surface_ready" `
        -and $expectedWebsiteReadingState -eq "ready_for_direct_and_search_first_review" `
        -and $expectedToolGroundedLearningState -eq "tool_grounded_learning_surface_ready" `
        -and $expectedDeployParityState -eq "deploy_parity_surface_ready"
    ) {
        "core_v1_bundle_ready"
    }
    else {
        "core_v1_bundle_incomplete"
    }
    if ([string]$V1Readiness.final_acceptance_state -ne $expectedFinalAcceptanceState) {
        throw "${FailurePrefix}: v1_readiness final_acceptance_state drifted from the approved core gate bundle."
    }

    $finalAcceptanceSurfaces = $V1Readiness.final_acceptance_surfaces
    $expectedFinalAcceptanceSurfaces = @{
        conversation_reliability = "/health.conversation_channels.telegram"
        learned_state_inspection = "/health.learned_state"
        website_reading = "/health.connectors.web_knowledge_tools.website_reading_workflow"
        tool_grounded_learning = "/health.learned_state.tool_grounded_learning"
        time_aware_planned_work = "/health.v1_readiness"
        deploy_parity = "/health.deployment"
    }
    $actualFinalSurfaceKeys = @($finalAcceptanceSurfaces.PSObject.Properties.Name)
    if (@(Compare-Object -ReferenceObject $expectedFinalGateKeys -DifferenceObject $actualFinalSurfaceKeys -SyncWindow 0).Count -gt 0) {
        throw "${FailurePrefix}: v1_readiness final_acceptance_surfaces drifted from the approved core-v1 boundary."
    }
    foreach ($surfaceName in $expectedFinalGateKeys) {
        if ([string]$finalAcceptanceSurfaces.$surfaceName -ne [string]$expectedFinalAcceptanceSurfaces[$surfaceName]) {
            throw "${FailurePrefix}: v1_readiness final_acceptance_surfaces.$surfaceName drifted."
        }
    }

    $extensionGateStates = $V1Readiness.extension_gate_states
    $extensionGateSurfaces = $V1Readiness.extension_gate_surfaces
    if ($null -eq $extensionGateStates -or $null -eq $extensionGateSurfaces) {
        throw "${FailurePrefix}: v1_readiness extension gate posture is missing."
    }
    if (@($extensionGateStates.PSObject.Properties.Name) -notcontains "organizer_daily_use") {
        throw "${FailurePrefix}: v1_readiness extension_gate_states is missing organizer_daily_use."
    }
    if ([string]$extensionGateStates.organizer_daily_use -ne [string]$OrganizerToolStackContract.daily_use_state) {
        throw "${FailurePrefix}: v1_readiness extension_gate_states.organizer_daily_use drifted from organizer_tool_stack."
    }
    if ([string]$extensionGateSurfaces.organizer_daily_use -ne "/health.connectors.organizer_tool_stack") {
        throw "${FailurePrefix}: v1_readiness extension_gate_surfaces.organizer_daily_use drifted."
    }

    return @{
        conversation_gate_state = $expectedConversationGateState
        learned_state_gate_state = $expectedLearnedStateGateState
        website_reading_workflow_state = $expectedWebsiteReadingState
        tool_grounded_learning_state = $expectedToolGroundedLearningState
        deploy_parity_state = $expectedDeployParityState
        final_acceptance_state = $expectedFinalAcceptanceState
        organizer_daily_use_state = [string]$OrganizerToolStackContract.daily_use_state
    }
}

$trimmedBaseUrl = $BaseUrl.TrimEnd("/")
$localRepoHeadSha = Resolve-LocalRepoHeadSha
if (-not $localRepoHeadSha) {
    throw "Health check failed: local repo HEAD could not be resolved for deploy parity."
}
if ($DeployParityMaxWaitSeconds -lt 1) {
    throw "Health check failed: DeployParityMaxWaitSeconds must be at least 1."
}
if ($DeployParityPollSeconds -lt 1) {
    throw "Health check failed: DeployParityPollSeconds must be at least 1."
}
if ($HealthRetryMaxAttempts -lt 1) {
    throw "Health check failed: HealthRetryMaxAttempts must be at least 1."
}
if ($HealthRetryDelaySeconds -lt 0) {
    throw "Health check failed: HealthRetryDelaySeconds must be greater than or equal to 0."
}
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

$health = if ($WaitForDeployParity) {
    Wait-ForDeploymentParity `
        -BaseUrl $trimmedBaseUrl `
        -ExpectedRevision $localRepoHeadSha `
        -TimeoutSeconds $DeployParityMaxWaitSeconds `
        -PollSeconds $DeployParityPollSeconds
}
else {
    Invoke-HealthJsonWithRetry `
        -Uri "$trimmedBaseUrl/health" `
        -MaxAttempts $HealthRetryMaxAttempts `
        -DelaySeconds $HealthRetryDelaySeconds
}
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
if (-not (Has-Property -Object $deployment -Name "deployment_automation_policy_owner")) {
    throw "Health check failed: deployment is missing deployment_automation_policy_owner."
}
if (-not (Has-Property -Object $deployment -Name "canonical_coolify_app")) {
    throw "Health check failed: deployment is missing canonical_coolify_app."
}
if (-not (Has-Property -Object $deployment -Name "deployment_automation_baseline")) {
    throw "Health check failed: deployment is missing deployment_automation_baseline."
}
if (-not (Has-Property -Object $deployment -Name "runtime_build_revision")) {
    throw "Health check failed: deployment is missing runtime_build_revision."
}
if (-not (Has-Property -Object $deployment -Name "runtime_build_revision_state")) {
    throw "Health check failed: deployment is missing runtime_build_revision_state."
}
if (-not (Has-Property -Object $deployment -Name "runtime_trigger_mode")) {
    throw "Health check failed: deployment is missing runtime_trigger_mode."
}
if (-not (Has-Property -Object $deployment -Name "runtime_trigger_class")) {
    throw "Health check failed: deployment is missing runtime_trigger_class."
}
if (-not (Has-Property -Object $deployment -Name "runtime_provenance_state")) {
    throw "Health check failed: deployment is missing runtime_provenance_state."
}
if ([string]$deployment.deployment_automation_policy_owner -ne "coolify_repo_deploy_automation") {
    throw "Health check failed: unexpected deployment_automation_policy_owner '$($deployment.deployment_automation_policy_owner)'."
}
if (-not (Has-Property -Object $deployment.canonical_coolify_app -Name "application_id")) {
    throw "Health check failed: deployment canonical_coolify_app is missing application_id."
}
if ([string]$deployment.deployment_automation_baseline.primary_trigger_mode -ne "source_automation") {
    throw "Health check failed: unexpected deployment_automation_baseline.primary_trigger_mode '$($deployment.deployment_automation_baseline.primary_trigger_mode)'."
}
$validDeploymentFallbackModes = @("webhook_manual_fallback", "ui_manual_fallback")
$fallbackModes = @($deployment.deployment_automation_baseline.fallback_trigger_modes)
foreach ($requiredFallbackMode in $validDeploymentFallbackModes) {
    if ($fallbackModes -notcontains $requiredFallbackMode) {
        throw "Health check failed: deployment_automation_baseline is missing fallback trigger mode '$requiredFallbackMode'."
    }
}
$validRuntimeTriggerModes = @("source_automation", "webhook_manual_fallback", "ui_manual_fallback")
if ($validRuntimeTriggerModes -notcontains [string]$deployment.runtime_trigger_mode) {
    throw "Health check failed: unexpected deployment runtime_trigger_mode '$($deployment.runtime_trigger_mode)'."
}
$validRuntimeTriggerClasses = @("primary_automation", "manual_fallback")
if ($validRuntimeTriggerClasses -notcontains [string]$deployment.runtime_trigger_class) {
    throw "Health check failed: unexpected deployment runtime_trigger_class '$($deployment.runtime_trigger_class)'."
}
if ([string]$deployment.runtime_build_revision_state -eq "runtime_build_revision_missing") {
    throw "Health check failed: deployment runtime_build_revision is still missing."
}
if (-not [string]$deployment.runtime_build_revision) {
    throw "Health check failed: deployment runtime_build_revision is empty."
}
if ([string]$deployment.runtime_build_revision -ne $localRepoHeadSha) {
    throw "Health check failed: deployment runtime_build_revision '$($deployment.runtime_build_revision)' does not match local repo HEAD '$localRepoHeadSha'."
}
if ([bool]$deploymentEvidenceCheck.checked) {
    if (-not [string]$deploymentEvidenceCheck.after_sha) {
        throw "Health check failed: deployment evidence is missing after_sha for parity comparison."
    }
    if ([string]$deployment.runtime_build_revision -ne [string]$deploymentEvidenceCheck.after_sha) {
        throw "Health check failed: deployment runtime_build_revision '$($deployment.runtime_build_revision)' does not match deployment evidence after_sha '$($deploymentEvidenceCheck.after_sha)'."
    }
}
$webShellRoutes = @("/", "/chat", "/settings", "/tools", "/personality")
foreach ($webShellRoute in $webShellRoutes) {
    Assert-WebShellRouteBuildRevision `
        -BaseUrl $trimmedBaseUrl `
        -RoutePath $webShellRoute `
        -ExpectedRevision ([string]$deployment.runtime_build_revision)
}
$webBuildRevision = [string]$deployment.runtime_build_revision
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
if (-not (Has-Property -Object $telegramConversation -Name "delivery_adaptation_policy_owner")) {
    throw "Health check failed: conversation_channels.telegram is missing delivery_adaptation_policy_owner."
}
if ([string]$telegramConversation.delivery_adaptation_policy_owner -ne "telegram_delivery_channel_adaptation") {
    throw "Health check failed: unexpected conversation_channels.telegram delivery_adaptation_policy_owner '$($telegramConversation.delivery_adaptation_policy_owner)'."
}
if (-not (Has-Property -Object $telegramConversation -Name "delivery_segmentation_state")) {
    throw "Health check failed: conversation_channels.telegram is missing delivery_segmentation_state."
}
if ([string]$telegramConversation.delivery_segmentation_state -ne "bounded_transport_segmentation") {
    throw "Health check failed: unexpected conversation_channels.telegram delivery_segmentation_state '$($telegramConversation.delivery_segmentation_state)'."
}
if (-not (Has-Property -Object $telegramConversation -Name "delivery_formatting_state")) {
    throw "Health check failed: conversation_channels.telegram is missing delivery_formatting_state."
}
if ([string]$telegramConversation.delivery_formatting_state -ne "supported_markdown_to_html_with_plain_text_fallback") {
    throw "Health check failed: unexpected conversation_channels.telegram delivery_formatting_state '$($telegramConversation.delivery_formatting_state)'."
}
if (-not (Has-Property -Object $telegramConversation -Name "delivery_attempts")) {
    throw "Health check failed: conversation_channels.telegram is missing delivery_attempts."
}
if (-not (Has-Property -Object $telegramConversation -Name "delivery_failures")) {
    throw "Health check failed: conversation_channels.telegram is missing delivery_failures."
}
$learnedState = $health.learned_state
$learnedStateContract = Assert-LearnedStateContract `
    -LearnedState $learnedState `
    -FailurePrefix "Health check failed"
$capabilityCatalog = $health.capability_catalog
$capabilityCatalogContract = Assert-CapabilityCatalogContract `
    -CapabilityCatalog $capabilityCatalog `
    -FailurePrefix "Health check failed"
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
$validV1OrganizerDailyUseStates = @("all_daily_use_workflows_ready", "daily_use_workflows_blocked_by_provider_activation")
if ($validV1OrganizerDailyUseStates -notcontains [string]$v1Readiness.organizer_daily_use_state) {
    throw "Health check failed: unexpected v1_readiness.organizer_daily_use_state '$($v1Readiness.organizer_daily_use_state)'."
}
if ([int]$v1Readiness.organizer_daily_use_total_workflow_count -ne 3) {
    throw "Health check failed: unexpected v1_readiness.organizer_daily_use_total_workflow_count '$($v1Readiness.organizer_daily_use_total_workflow_count)'."
}
$actualOrganizerReadyWorkflows = @()
if ($v1Readiness.PSObject.Properties.Name -contains "organizer_daily_use_ready_workflows" -and $null -ne $v1Readiness.organizer_daily_use_ready_workflows) {
    $actualOrganizerReadyWorkflows = @($v1Readiness.organizer_daily_use_ready_workflows)
}
$actualOrganizerBlockedWorkflows = @()
if ($v1Readiness.PSObject.Properties.Name -contains "organizer_daily_use_blocked_workflows" -and $null -ne $v1Readiness.organizer_daily_use_blocked_workflows) {
    $actualOrganizerBlockedWorkflows = @($v1Readiness.organizer_daily_use_blocked_workflows)
}
if ([string]$v1Readiness.organizer_daily_use_state -eq "all_daily_use_workflows_ready" -and $actualOrganizerBlockedWorkflows.Count -ne 0) {
    throw "Health check failed: v1_readiness organizer_daily_use_state is all_daily_use_workflows_ready but organizer_daily_use_blocked_workflows is not empty."
}
if ([string]$v1Readiness.organizer_daily_use_state -eq "daily_use_workflows_blocked_by_provider_activation" -and $actualOrganizerBlockedWorkflows.Count -eq 0) {
    throw "Health check failed: v1_readiness organizer_daily_use_state is daily_use_workflows_blocked_by_provider_activation but organizer_daily_use_blocked_workflows is empty."
}
$requiredV1Scenarios = @("T13.1", "T14.1", "T14.2", "T14.3", "T15.1", "T15.2", "T16.1", "T16.2", "T16.3", "T17.1", "T17.2", "T18.1", "T18.2", "T19.1", "T19.2")
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
    "task_system.clickup_list_tasks",
    "task_system.clickup_update_task",
    "calendar.google_calendar_read_availability",
    "cloud_drive.google_drive_list_files"
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
$connectors = $health.connectors
if ($null -eq $connectors) {
    throw "Health check failed: response is missing connectors."
}
$organizerToolStackContract = Assert-OrganizerToolStackContract `
    -OrganizerToolStack $connectors.organizer_tool_stack `
    -FailurePrefix "Health check failed"
$webKnowledgeWorkflowContract = Assert-WebKnowledgeWorkflowContract `
    -WebKnowledgeTools $connectors.web_knowledge_tools `
    -FailurePrefix "Health check failed"
$v1ReadinessTruthContract = Assert-V1ReadinessTruthContract `
    -V1Readiness $v1Readiness `
    -TelegramConversation $telegramConversation `
    -LearnedState $learnedState `
    -WebKnowledgeWorkflowContract $webKnowledgeWorkflowContract `
    -OrganizerToolStackContract $organizerToolStackContract `
    -Deployment $deployment `
    -FailurePrefix "Health check failed"

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
    if ([string]$incidentTelegramConversation.delivery_adaptation_policy_owner -ne "telegram_delivery_channel_adaptation") {
        throw "Smoke request failed: unexpected incident_evidence conversation_channels.telegram delivery_adaptation_policy_owner '$($incidentTelegramConversation.delivery_adaptation_policy_owner)'."
    }
    if ([string]$incidentTelegramConversation.delivery_segmentation_state -ne "bounded_transport_segmentation") {
        throw "Smoke request failed: unexpected incident_evidence conversation_channels.telegram delivery_segmentation_state '$($incidentTelegramConversation.delivery_segmentation_state)'."
    }
    if ([string]$incidentTelegramConversation.delivery_formatting_state -ne "supported_markdown_to_html_with_plain_text_fallback") {
        throw "Smoke request failed: unexpected incident_evidence conversation_channels.telegram delivery_formatting_state '$($incidentTelegramConversation.delivery_formatting_state)'."
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
    $incidentLearnedStateContract = Assert-LearnedStateContract `
        -LearnedState $incidentLearnedState `
        -FailurePrefix "Smoke request failed"
    $incidentOrganizerToolStack = $incidentEvidence.policy_posture."connectors.organizer_tool_stack"
    $incidentOrganizerToolStackContract = Assert-OrganizerToolStackContract `
        -OrganizerToolStack $incidentOrganizerToolStack `
        -FailurePrefix "Smoke request failed"
    $incidentWebKnowledgeTools = $incidentEvidence.policy_posture."connectors.web_knowledge_tools"
    $incidentWebKnowledgeWorkflowContract = Assert-WebKnowledgeWorkflowContract `
        -WebKnowledgeTools $incidentWebKnowledgeTools `
        -FailurePrefix "Smoke request failed"
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
    if ($validV1OrganizerDailyUseStates -notcontains [string]$incidentV1Readiness.organizer_daily_use_state) {
        throw "Smoke request failed: unexpected incident_evidence v1_readiness organizer_daily_use_state '$($incidentV1Readiness.organizer_daily_use_state)'."
    }
    if ([int]$incidentV1Readiness.organizer_daily_use_total_workflow_count -ne 3) {
        throw "Smoke request failed: unexpected incident_evidence v1_readiness organizer_daily_use_total_workflow_count '$($incidentV1Readiness.organizer_daily_use_total_workflow_count)'."
    }
    $incidentDeployment = $incidentEvidence.policy_posture.deployment
    if ($null -eq $incidentDeployment) {
        throw "Smoke request failed: incident_evidence is missing deployment posture."
    }
    if ([string]$incidentDeployment.deployment_automation_policy_owner -ne "coolify_repo_deploy_automation") {
        throw "Smoke request failed: unexpected incident_evidence deployment_automation_policy_owner '$($incidentDeployment.deployment_automation_policy_owner)'."
    }
    if ([string]$incidentDeployment.deployment_automation_baseline.primary_trigger_mode -ne "source_automation") {
        throw "Smoke request failed: unexpected incident_evidence deployment primary_trigger_mode '$($incidentDeployment.deployment_automation_baseline.primary_trigger_mode)'."
    }
    $incidentDeploymentFallbackModes = @($incidentDeployment.deployment_automation_baseline.fallback_trigger_modes)
    foreach ($requiredFallbackMode in @("webhook_manual_fallback", "ui_manual_fallback")) {
        if ($incidentDeploymentFallbackModes -notcontains $requiredFallbackMode) {
            throw "Smoke request failed: incident_evidence deployment is missing fallback trigger mode '$requiredFallbackMode'."
        }
    }
    $incidentV1ReadinessTruthContract = Assert-V1ReadinessTruthContract `
        -V1Readiness $incidentV1Readiness `
        -TelegramConversation $incidentTelegramConversation `
        -LearnedState $incidentLearnedState `
        -WebKnowledgeWorkflowContract $incidentWebKnowledgeWorkflowContract `
        -OrganizerToolStackContract $incidentOrganizerToolStackContract `
        -Deployment $incidentDeployment `
        -FailurePrefix "Smoke request failed"
    $incidentRequiredV1Scenarios = @("T13.1", "T14.1", "T14.2", "T14.3", "T15.1", "T15.2", "T16.1", "T16.2", "T16.3", "T17.1", "T17.2", "T18.1", "T18.2", "T19.1", "T19.2")
    $incidentActualV1Scenarios = @()
    if ($incidentV1Readiness.PSObject.Properties.Name -contains "required_behavior_scenarios" -and $null -ne $incidentV1Readiness.required_behavior_scenarios) {
        $incidentActualV1Scenarios = @($incidentV1Readiness.required_behavior_scenarios)
    }
    foreach ($requiredScenario in $incidentRequiredV1Scenarios) {
        if ($incidentActualV1Scenarios -notcontains $requiredScenario) {
            throw "Smoke request failed: incident_evidence v1_readiness is missing required behavior scenario '$requiredScenario'."
        }
    }
    $incidentRequiredV1ToolSlices = @(
        "knowledge_search.search_web",
        "web_browser.read_page",
        "task_system.clickup_list_tasks",
        "task_system.clickup_update_task",
        "calendar.google_calendar_read_availability",
        "cloud_drive.google_drive_list_files"
    )
    $incidentActualV1ToolSlices = @()
    if ($incidentV1Readiness.PSObject.Properties.Name -contains "approved_tool_slices" -and $null -ne $incidentV1Readiness.approved_tool_slices) {
        $incidentActualV1ToolSlices = @($incidentV1Readiness.approved_tool_slices)
    }
    foreach ($requiredToolSlice in $incidentRequiredV1ToolSlices) {
        if ($incidentActualV1ToolSlices -notcontains $requiredToolSlice) {
            throw "Smoke request failed: incident_evidence v1_readiness is missing approved tool slice '$requiredToolSlice'."
        }
    }
    $incidentOrganizerToolStackContract = Assert-OrganizerToolStackContract `
        -OrganizerToolStack $incidentEvidence.policy_posture."connectors.organizer_tool_stack" `
        -FailurePrefix "Smoke request failed"
    $incidentWebKnowledgeWorkflowContract = Assert-WebKnowledgeWorkflowContract `
        -WebKnowledgeTools $incidentEvidence.policy_posture."connectors.web_knowledge_tools" `
        -FailurePrefix "Smoke request failed"
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
    deployment_automation_policy_owner = [string]$deployment.deployment_automation_policy_owner
    deployment_primary_trigger_mode = [string]$deployment.deployment_automation_baseline.primary_trigger_mode
    deployment_runtime_trigger_mode = [string]$deployment.runtime_trigger_mode
    deployment_runtime_trigger_class = [string]$deployment.runtime_trigger_class
    deployment_runtime_build_revision = [string]$deployment.runtime_build_revision
    deployment_runtime_build_revision_state = [string]$deployment.runtime_build_revision_state
    deployment_runtime_provenance_state = [string]$deployment.runtime_provenance_state
    web_shell_build_revision = [string]$webBuildRevision
    deployment_local_repo_head_sha = [string]$localRepoHeadSha
    deployment_fallback_trigger_modes = @($deployment.deployment_automation_baseline.fallback_trigger_modes)
    deployment_canonical_application_id = [string]$deployment.canonical_coolify_app.application_id
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
    telegram_conversation_delivery_adaptation_policy_owner = [string]$telegramConversation.delivery_adaptation_policy_owner
    telegram_conversation_delivery_segmentation_state = [string]$telegramConversation.delivery_segmentation_state
    telegram_conversation_delivery_formatting_state = [string]$telegramConversation.delivery_formatting_state
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
    incident_evidence_telegram_conversation_delivery_adaptation_policy_owner = if ($null -ne $incidentTelegramConversation) { [string]$incidentTelegramConversation.delivery_adaptation_policy_owner } else { $null }
    incident_evidence_telegram_conversation_delivery_segmentation_state = if ($null -ne $incidentTelegramConversation) { [string]$incidentTelegramConversation.delivery_segmentation_state } else { $null }
    incident_evidence_telegram_conversation_delivery_formatting_state = if ($null -ne $incidentTelegramConversation) { [string]$incidentTelegramConversation.delivery_formatting_state } else { $null }
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
    incident_evidence_learned_state_policy_owner = if ($null -ne $incidentLearnedStateContract) { [string]$incidentLearnedStateContract.policy_owner } else { $null }
    incident_evidence_learned_state_internal_inspection_path = if ($null -ne $incidentLearnedStateContract) { [string]$incidentLearnedStateContract.internal_inspection_path } else { $null }
    incident_evidence_learned_state_inspection_sections = if ($null -ne $incidentLearnedStateContract) { @($incidentLearnedStateContract.inspection_sections) } else { @() }
    incident_evidence_learned_state_growth_summary_sections = if ($null -ne $incidentLearnedStateContract) { @($incidentLearnedStateContract.growth_summary_sections) } else { @() }
    capability_catalog_policy_owner = [string]$capabilityCatalogContract.policy_owner
    capability_catalog_approved_tool_families = @($capabilityCatalogContract.approved_tool_families)
    capability_catalog_skill_execution_boundary = [string]$capabilityCatalogContract.skill_execution_boundary
    capability_catalog_catalog_count = [int]$capabilityCatalogContract.catalog_count
    capability_catalog_organizer_stack_state = [string]$capabilityCatalogContract.organizer_stack_state
    capability_catalog_organizer_activation_state = [string]$capabilityCatalogContract.organizer_activation_state
    capability_catalog_execution_baseline_owner = [string]$capabilityCatalogContract.execution_baseline_owner
    capability_catalog_tool_grounded_learning_policy_owner = [string]$capabilityCatalogContract.tool_grounded_learning_policy_owner
    incident_evidence_deployment_automation_policy_owner = if ($null -ne $incidentDeployment) { [string]$incidentDeployment.deployment_automation_policy_owner } else { $null }
    incident_evidence_deployment_primary_trigger_mode = if ($null -ne $incidentDeployment) { [string]$incidentDeployment.deployment_automation_baseline.primary_trigger_mode } else { $null }
    organizer_tool_stack_policy_owner = [string]$organizerToolStackContract.policy_owner
    organizer_tool_stack_readiness_state = [string]$organizerToolStackContract.readiness_state
    organizer_tool_stack_ready_operations = @($organizerToolStackContract.ready_operations)
    organizer_tool_stack_credential_gap_operations = @($organizerToolStackContract.credential_gap_operations)
    organizer_tool_stack_daily_use_state = [string]$organizerToolStackContract.daily_use_state
    organizer_tool_stack_daily_use_ready_workflow_count = [int]$organizerToolStackContract.daily_use_ready_workflow_count
    organizer_tool_stack_daily_use_ready_workflows = @($organizerToolStackContract.daily_use_ready_workflows)
    organizer_tool_stack_daily_use_blocked_workflows = @($organizerToolStackContract.daily_use_blocked_workflows)
    organizer_tool_activation_state = [string]$organizerToolStackContract.activation_state
    organizer_tool_activation_next_actions = @($organizerToolStackContract.activation_next_actions)
    v1_organizer_daily_use_state = [string]$v1Readiness.organizer_daily_use_state
    v1_organizer_daily_use_ready_workflow_count = [int]$v1Readiness.organizer_daily_use_ready_workflow_count
    v1_organizer_daily_use_ready_workflows = @($actualOrganizerReadyWorkflows)
    v1_organizer_daily_use_blocked_workflows = @($actualOrganizerBlockedWorkflows)
    web_knowledge_policy_owner = [string]$webKnowledgeWorkflowContract.policy_owner
    website_reading_workflow_policy_owner = [string]$webKnowledgeWorkflowContract.workflow_policy_owner
    website_reading_workflow_state = [string]$webKnowledgeWorkflowContract.workflow_state
    website_reading_direct_url_review_available = [bool]$webKnowledgeWorkflowContract.direct_url_review_available
    website_reading_search_then_page_review_available = [bool]$webKnowledgeWorkflowContract.search_then_page_review_available
    website_reading_allowed_entry_modes = @($webKnowledgeWorkflowContract.allowed_entry_modes)
    website_reading_search_provider_hint = [string]$webKnowledgeWorkflowContract.search_provider_hint
    website_reading_page_read_provider_hint = [string]$webKnowledgeWorkflowContract.page_read_provider_hint
    website_reading_memory_capture_boundary = [string]$webKnowledgeWorkflowContract.memory_capture_boundary
    website_reading_blockers = @($webKnowledgeWorkflowContract.blockers)
    website_reading_next_actions = @($webKnowledgeWorkflowContract.next_actions)
    incident_evidence_organizer_tool_stack_policy_owner = if ($null -ne $incidentOrganizerToolStackContract) { [string]$incidentOrganizerToolStackContract.policy_owner } else { $null }
    incident_evidence_organizer_tool_stack_readiness_state = if ($null -ne $incidentOrganizerToolStackContract) { [string]$incidentOrganizerToolStackContract.readiness_state } else { $null }
    incident_evidence_organizer_tool_stack_daily_use_state = if ($null -ne $incidentOrganizerToolStackContract) { [string]$incidentOrganizerToolStackContract.daily_use_state } else { $null }
    incident_evidence_organizer_tool_stack_daily_use_ready_workflow_count = if ($null -ne $incidentOrganizerToolStackContract) { [int]$incidentOrganizerToolStackContract.daily_use_ready_workflow_count } else { $null }
    incident_evidence_organizer_tool_activation_state = if ($null -ne $incidentOrganizerToolStackContract) { [string]$incidentOrganizerToolStackContract.activation_state } else { $null }
    incident_evidence_organizer_tool_activation_next_actions = if ($null -ne $incidentOrganizerToolStackContract) { @($incidentOrganizerToolStackContract.activation_next_actions) } else { @() }
    incident_evidence_v1_organizer_daily_use_state = if ($null -ne $incidentV1Readiness) { [string]$incidentV1Readiness.organizer_daily_use_state } else { $null }
    incident_evidence_web_knowledge_policy_owner = if ($null -ne $incidentWebKnowledgeWorkflowContract) { [string]$incidentWebKnowledgeWorkflowContract.policy_owner } else { $null }
    incident_evidence_website_reading_workflow_state = if ($null -ne $incidentWebKnowledgeWorkflowContract) { [string]$incidentWebKnowledgeWorkflowContract.workflow_state } else { $null }
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
    incident_bundle_telegram_delivery_adaptation_policy_owner = $incidentEvidenceBundleCheck.telegram_delivery_adaptation_policy_owner
    incident_bundle_telegram_delivery_segmentation_state = $incidentEvidenceBundleCheck.telegram_delivery_segmentation_state
    incident_bundle_telegram_delivery_formatting_state = $incidentEvidenceBundleCheck.telegram_delivery_formatting_state
    incident_bundle_attention_coordination_mode = $incidentEvidenceBundleCheck.attention_coordination_mode
    incident_bundle_attention_contract_store_state = $incidentEvidenceBundleCheck.attention_contract_store_state
    incident_bundle_attention_runtime_topology_selected_mode = $incidentEvidenceBundleCheck.attention_runtime_topology_selected_mode
    incident_bundle_proactive_policy_owner = $incidentEvidenceBundleCheck.proactive_policy_owner
    incident_bundle_proactive_enabled = $incidentEvidenceBundleCheck.proactive_enabled
    incident_bundle_proactive_production_baseline_state = $incidentEvidenceBundleCheck.proactive_production_baseline_state
    incident_bundle_deployment_automation_policy_owner = $incidentEvidenceBundleCheck.deployment_automation_policy_owner
    incident_bundle_deployment_primary_trigger_mode = $incidentEvidenceBundleCheck.deployment_primary_trigger_mode
    incident_bundle_deployment_runtime_trigger_mode = $incidentEvidenceBundleCheck.deployment_runtime_trigger_mode
    incident_bundle_deployment_runtime_trigger_class = $incidentEvidenceBundleCheck.deployment_runtime_trigger_class
    incident_bundle_deployment_runtime_build_revision = $incidentEvidenceBundleCheck.deployment_runtime_build_revision
    incident_bundle_deployment_runtime_build_revision_state = $incidentEvidenceBundleCheck.deployment_runtime_build_revision_state
    incident_bundle_deployment_runtime_provenance_state = $incidentEvidenceBundleCheck.deployment_runtime_provenance_state
    incident_bundle_organizer_tool_stack_policy_owner = $incidentEvidenceBundleCheck.organizer_tool_stack_policy_owner
    incident_bundle_organizer_tool_stack_readiness_state = $incidentEvidenceBundleCheck.organizer_tool_stack_readiness_state
    incident_bundle_organizer_tool_stack_ready_operations = $incidentEvidenceBundleCheck.organizer_tool_stack_ready_operations
    incident_bundle_organizer_tool_stack_credential_gap_operations = $incidentEvidenceBundleCheck.organizer_tool_stack_credential_gap_operations
    incident_bundle_organizer_tool_stack_daily_use_state = $incidentEvidenceBundleCheck.organizer_tool_stack_daily_use_state
    incident_bundle_organizer_tool_stack_daily_use_ready_workflow_count = $incidentEvidenceBundleCheck.organizer_tool_stack_daily_use_ready_workflow_count
    incident_bundle_organizer_tool_activation_state = $incidentEvidenceBundleCheck.organizer_tool_activation_state
    incident_bundle_organizer_tool_activation_next_actions = $incidentEvidenceBundleCheck.organizer_tool_activation_next_actions
    incident_bundle_web_knowledge_policy_owner = $incidentEvidenceBundleCheck.web_knowledge_policy_owner
    incident_bundle_website_reading_workflow_policy_owner = $incidentEvidenceBundleCheck.website_reading_workflow_policy_owner
    incident_bundle_website_reading_workflow_state = $incidentEvidenceBundleCheck.website_reading_workflow_state
    incident_bundle_website_reading_direct_url_review_available = $incidentEvidenceBundleCheck.website_reading_direct_url_review_available
    incident_bundle_website_reading_search_then_page_review_available = $incidentEvidenceBundleCheck.website_reading_search_then_page_review_available
    incident_bundle_website_reading_allowed_entry_modes = $incidentEvidenceBundleCheck.website_reading_allowed_entry_modes
    incident_bundle_website_reading_search_provider_hint = $incidentEvidenceBundleCheck.website_reading_search_provider_hint
    incident_bundle_website_reading_page_read_provider_hint = $incidentEvidenceBundleCheck.website_reading_page_read_provider_hint
    incident_bundle_website_reading_memory_capture_boundary = $incidentEvidenceBundleCheck.website_reading_memory_capture_boundary
    incident_bundle_learned_state_policy_owner = $incidentEvidenceBundleCheck.learned_state_policy_owner
    incident_bundle_learned_state_internal_inspection_path = $incidentEvidenceBundleCheck.learned_state_internal_inspection_path
    incident_bundle_learned_state_inspection_sections = $incidentEvidenceBundleCheck.learned_state_inspection_sections
    incident_bundle_learned_state_growth_summary_sections = $incidentEvidenceBundleCheck.learned_state_growth_summary_sections
    incident_bundle_capability_catalog_policy_owner = $incidentEvidenceBundleCheck.capability_catalog_policy_owner
    incident_bundle_capability_catalog_approved_tool_families = $incidentEvidenceBundleCheck.capability_catalog_approved_tool_families
    incident_bundle_capability_catalog_skill_execution_boundary = $incidentEvidenceBundleCheck.capability_catalog_skill_execution_boundary
    incident_bundle_capability_catalog_catalog_count = $incidentEvidenceBundleCheck.capability_catalog_catalog_count
    incident_bundle_capability_catalog_organizer_stack_state = $incidentEvidenceBundleCheck.capability_catalog_organizer_stack_state
    incident_bundle_capability_catalog_organizer_activation_state = $incidentEvidenceBundleCheck.capability_catalog_organizer_activation_state
    incident_bundle_capability_catalog_execution_baseline_owner = $incidentEvidenceBundleCheck.capability_catalog_execution_baseline_owner
    incident_bundle_capability_catalog_tool_grounded_learning_policy_owner = $incidentEvidenceBundleCheck.capability_catalog_tool_grounded_learning_policy_owner
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
    deployment_evidence_policy_owner = [string]$deploymentEvidenceCheck.policy_owner
    deployment_evidence_trigger_mode = [string]$deploymentEvidenceCheck.trigger_mode
    deployment_evidence_trigger_class = [string]$deploymentEvidenceCheck.trigger_class
    deployment_evidence_canonical_application_id = [string]$deploymentEvidenceCheck.canonical_application_id
    deployment_evidence_after_sha = [string]$deploymentEvidenceCheck.after_sha
}

$summary | ConvertTo-Json -Depth 6
