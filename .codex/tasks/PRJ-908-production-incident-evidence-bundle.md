# Task

## Header
- ID: PRJ-908
- Title: Production Incident Evidence Bundle
- Task Type: release
- Current Stage: verification
- Status: BLOCKED
- Owner: Ops/Release
- Depends on: PRJ-907
- Priority: P0
- Coverage Ledger Rows: not applicable
- Iteration: 908
- Operation Mode: BUILDER

## Process Self-Audit
- [x] All seven autonomous loop steps are planned.
- [x] No loop step is being skipped.
- [x] Exactly one priority task is selected.
- [x] Operation mode matches the iteration number.
- [x] The task is aligned with repository source-of-truth documents.

## Context
PRJ-907 proved production deploy parity for the current release candidate.
PRJ-908 was intended to export the canonical production incident-evidence
bundle and verify it through release smoke.

## Goal
Export and verify a production incident-evidence bundle for the v1 candidate.

## Scope
- production Coolify application: `Aviary / production / aviary`
- `backend/scripts/export_incident_evidence_bundle.py`
- `backend/scripts/run_release_smoke.ps1`
- `docs/planning/v1-production-incident-evidence-bundle.md`
- `.codex/context/TASK_BOARD.md`
- `.codex/context/PROJECT_STATE.md`
- `.codex/tasks/PRJ-908-production-incident-evidence-bundle.md`

## Success Signal
- User or operator problem: release owner needs a production incident-evidence
  bundle that can be reviewed offline and accepted by release smoke.
- Expected product or reliability outcome: current production evidence can be
  exported without weakening production safety.
- How success will be observed: bundle export succeeds and release smoke
  accepts `-IncidentEvidenceBundlePath`.
- Post-launch learning needed: yes

## Deliverable For This Stage
Blocked evidence record with restoration proof and next safe implementation
options.

## Constraints
- do not leave production debug payload exposure enabled
- do not commit tokens or generated secret artifacts
- do not bypass production strict policy
- keep production healthy before stopping

## Implementation Plan
1. Attempt canonical production bundle export.
2. If blocked by debug policy, use the user-approved temporary Coolify debug
   window.
3. Restore production if strict policy rejects the temporary window.
4. Run release smoke after restoration.
5. Record the blocker and next safe path.

## Acceptance Criteria
- Production is not left in a degraded state.
- No debug token is committed.
- The blocker is documented precisely.
- Next safe fix options are explicit.

## Definition of Done
- [x] Initial export attempt was run.
- [x] Temporary debug window was attempted with user approval.
- [x] Production was restored to `event_debug_enabled=false`.
- [x] Release smoke passed after restoration.
- [x] Blocker was recorded.

## Stage Exit Criteria
- [x] The output matches the declared `Current Stage`.
- [x] Work from later stages was not mixed in without explicit approval.
- [x] Risks and assumptions for this stage are stated clearly.

## Forbidden
- new systems without approval
- duplicated logic or parallel implementations of the same contract
- temporary bypasses, hacks, or workaround-only paths
- architecture changes without explicit approval
- implicit stage skipping

## Validation Evidence
- Tests:
  - `.\backend\scripts\run_release_smoke.ps1 -BaseUrl "https://aviary.luckysparrow.ch" -WaitForDeployParity -DeployParityMaxWaitSeconds 300 -DeployParityPollSeconds 15 -HealthRetryMaxAttempts 10 -HealthRetryDelaySeconds 10`
  - result: passed after restoration
- Manual checks:
  - production `/health` returned to `event_debug_enabled=false`
  - production `/health` returned to `release_readiness.ready=true`
- Screenshots/logs:
  - Coolify deployment screenshots are local `.codex/artifacts` evidence only
- High-risk checks:
  - temporary local debug-token file was deleted
  - user reported Coolify-side token cleanup complete
- Coverage ledger updated: not applicable
- Coverage rows closed or changed: none

## Architecture Evidence
- Architecture source reviewed:
  - `docs/architecture/17_logging_and_debugging.md`
  - `docs/architecture/26_env_and_config.md`
  - `docs/operations/runtime-ops-runbook.md`
- Fits approved architecture: yes
- Mismatch discovered: yes
- Decision required from user: yes, before implementing a production-safe
  incident-evidence export path
- Approval reference if architecture changed: not applicable
- Follow-up architecture doc updates: required if the bundle contract changes

## Deployment / Ops Evidence
- Deploy impact: medium
- Env or secret changes:
  - temporary debug variables were added during the attempt
  - debug flag was restored to disabled
  - Coolify-side token cleanup was reported complete by the user
- Health-check impact:
  - temporary debug window caused production 503 under strict policy
  - restoration redeploy returned health to green
- Smoke steps updated: no
- Rollback note:
  - keep `EVENT_DEBUG_ENABLED=false` in production strict mode
  - do not repeat the temporary debug-window approach without an approved
    policy-window runbook
- Observability or alerting impact: none
- Staged rollout or feature flag: debug exposure remains disabled

## Review Checklist
- [x] Process self-audit completed before implementation.
- [x] Autonomous loop evidence covers all seven steps.
- [x] Exactly one priority task was completed in this iteration.
- [x] Operation mode was selected according to iteration rotation.
- [x] Current stage is declared and respected.
- [x] Deliverable for the current stage is complete.
- [x] Architecture alignment confirmed.
- [x] Existing systems were reused where applicable.
- [x] No workaround paths were introduced.
- [x] No logic duplication was introduced.
- [x] Definition of Done evidence is attached.
- [x] Relevant validations were run.
- [x] Docs or context were updated if repository truth changed.
- [x] Learning journal was updated if a recurring pitfall was confirmed.

## Result Report

- Task summary: PRJ-908 is blocked because the canonical bundle helper depends
  on full debug payload access, while production strict policy rejects that
  posture.
- Files changed:
  - `docs/planning/v1-production-incident-evidence-bundle.md`
  - `.codex/context/TASK_BOARD.md`
  - `.codex/context/PROJECT_STATE.md`
  - `.codex/tasks/PRJ-908-production-incident-evidence-bundle.md`
- How tested: production release smoke passed after restoration.
- What is incomplete: no production incident-evidence bundle was exported.
- Next steps: choose a production-safe incident-evidence export route or carry
  this as a known blocked evidence gap into PRJ-910.
- Decisions made: do not repeat `EVENT_DEBUG_ENABLED=true` under current
  production strict policy.

## Autonomous Loop Evidence

### 1. Analyze Current State
- Issues: canonical export needs `/internal/event/debug`; production debug
  payload access is disabled.
- Gaps: no production-safe bundle export path exists.
- Inconsistencies: release bundle contract expects incident evidence, but
  production strict policy blocks the current producer path.
- Architecture constraints: do not expose debug payloads casually in
  production.

### 2. Select One Priority Task
- Selected task: PRJ-908 Production Incident Evidence Bundle.
- Priority rationale: it is the next P0 release evidence task.
- Why other candidates were deferred: acceptance bundle depends on knowing
  whether incident evidence is available.

### 3. Plan Implementation
- Files or surfaces to modify: production Coolify config and release docs.
- Logic: attempt export, restore production, document blocker.
- Edge cases: do not leave debug enabled or commit token artifacts.

### 4. Execute Implementation
- Implementation notes: attempted export, attempted temporary debug window,
  restored debug disabled, reran release smoke.

### 5. Verify and Test
- Validation performed: production health and release smoke.
- Result: production restored and smoke passed; bundle export remains blocked.

### 6. Self-Review
- Simpler option considered: accept a health-only bundle, rejected because it
  would silently change the architecture contract.
- Technical debt introduced: no
- Scalability assessment: recommended fix is a dedicated production-safe export
  path.
- Refinements made: strict-policy blocker is explicit.

### 7. Update Documentation and Knowledge
- Docs updated: yes
- Context updated: yes
- Learning journal updated: not applicable.
