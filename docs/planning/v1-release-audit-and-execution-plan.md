# V1 Release Audit And Execution Plan

Last updated: 2026-05-02

Current release boundary:
`docs/planning/current-v1-release-boundary.md`.

## Purpose

This document turns the current repository state into a concrete path for
making `v1` a release fact, not only a locally proven architecture baseline.

The current approved core `v1` is the no-UI life-assistant bundle:

1. stable Telegram or API conversation
2. learned-state inspection and later reuse
3. bounded website reading
4. tool-grounded learning
5. time-aware planned work
6. deployment parity in live production

Organizer daily-use tooling, richer web UI, mobile, multimodal Telegram, and
full provider activation are valuable extensions. They should be planned and
tracked, but they must not silently redefine the core `v1` blocker set.

## Current Evidence

- Local `HEAD`: `5372d33a4fd132bc6280bb781642eb3ce55fbfdc`
- `origin/main`: `5372d33a4fd132bc6280bb781642eb3ce55fbfdc`
- Fresh behavior validation:
  - command:
    `Push-Location .\backend; ..\.venv\Scripts\python .\scripts\run_behavior_validation.py --gate-mode operator --artifact-path ..\.codex\artifacts\prj902-v1-audit\behavior-validation-report.json; Pop-Location`
  - result: `19 passed, 209 deselected`
  - artifact:
    `.codex/artifacts/prj902-v1-audit/behavior-validation-report.json`
- Recent full backend gate:
  - `PRJ-901` recorded `1019 passed`
- Recent web build:
  - `PRJ-901` recorded `npm run build` passed
- Previous production smoke evidence exists, but it is not current for the
  dirty working tree and later local UI/backend changes.

## Audit Findings

### A. Release-State Findings

1. **Current local tree is not release-clean.**
   - `git status --short` shows modified tracked files and many untracked task
     records.
   - Impact: `v1` cannot be declared as a current production fact from this
     tree until the intended release scope is selected, validated, committed,
     pushed, and smoke-tested.
   - Severity: P0 release blocker.

2. **Production parity evidence is stale for the current local product state.**
   - Earlier production smoke proved earlier commits, but the canonical web and
     product-usability work after that is local/unpublished.
   - Impact: live production may be behind the current intended product shell.
   - Severity: P0 release blocker.

3. **The final v1 target explicitly requires live production green gates.**
   - `v1_readiness.final_acceptance_target` is
     `all_final_gates_green_in_live_production`.
   - Impact: local unit/behavior evidence is necessary but insufficient.
   - Severity: P0 release blocker until release smoke passes after publish.

4. **Deploy provenance and build revision must be proven after every release
   commit.**
   - The release smoke already checks runtime/web build revision parity.
   - Impact: a docs-only commit after smoke would itself create a new unsmoked
     production candidate.
   - Severity: P0 process constraint.

### B. Core V1 Runtime Findings

5. **Core behavior scenario coverage is strong locally.**
   - Behavior validation passed with 19 scenario-level checks.
   - Covered anchors include the core `T13.1..T19.2` family plus newer
     behavior/proactivity checks.
   - Impact: no immediate core behavior implementation blocker was found in
     local evidence.
   - Severity: evidence strength, not a blocker.

6. **`v1_readiness` gate structure is aligned with architecture.**
   - Final gates remain limited to conversation reliability, learned-state
     inspection, website reading, tool-grounded learning, planned work, and
     deploy parity.
   - Organizer daily use remains extension posture.
   - Impact: no architecture mismatch found.
   - Severity: none.

7. **Affective fallback is still explicitly deterministic when AI classifier
   support is unavailable.**
   - Code and health diagnostics still expose `deterministic_placeholder`.
   - This is documented fallback behavior, not a core `v1` blocker.
   - Impact: premium empathy quality will depend on configuring and proving the
     AI-backed assessor in target environments.
   - Severity: P2 quality feature.

8. **Tool-grounded learning and bounded external reads are release-sensitive.**
   - Existing behavior evidence proves the local path.
   - A final release must attach health, incident-evidence, and behavior
     artifacts so the proof is reproducible against the release candidate.
   - Severity: P0 evidence blocker for release, not implementation blocker.

### C. Product/Web Findings

9. **The authenticated web shell is becoming product-grade, but it is beyond
   the original no-UI core `v1` gate.**
   - Canonical dashboard/chat/personality/module work is substantial and useful.
   - Impact: it should be included in a product-facing v1.1 or web-v1 lane, but
     core no-UI v1 should not be blocked on every web polish item.
   - Severity: P1 product scope decision.

10. **Some web surfaces still carry static or decorative values.**
    - PRJ-901 replaced shared recent activity with real backend data.
    - Remaining examples include display-only values such as clarity, energy,
      intuition, and some route-local guidance cards.
    - Impact: this does not break core no-UI v1, but it weakens the product UI
      claim if the web shell is included in the release promise.
    - Severity: P1 for web-v1, P3 for core no-UI v1.

11. **The web app needs one fresh post-change route smoke before release.**
    - Recent route screenshots were generated before the latest backend-backed
      activity slice and local dirty changes.
    - Impact: a release candidate should prove login shell, dashboard, chat,
      settings, tools, and module routes are nonblank, non-overflowing, and
      revision-aligned.
    - Severity: P1 product release blocker if web is part of the claim.

### D. Provider And Extension Findings

12. **Organizer provider credentials remain an extension readiness gap.**
    - Prior release smoke reported missing settings for ClickUp, Google
      Calendar, and Google Drive.
    - Impact: core no-UI v1 can be green, but daily-use organizer extension is
      incomplete until credentials and user opt-in are configured and smoked.
    - Severity: P1 extension blocker.

13. **Telegram production truth requires an operator smoke with real bot and
    chat preconditions.**
    - Health/release smoke can prove runtime paths, but Telegram end-to-end
      confidence still needs webhook/listen smoke using real production
      configuration.
    - Impact: without this, conversation reliability is inferred rather than
      directly observed through the provider channel.
    - Severity: P0/P1 depending on whether Telegram is the launch channel.

14. **Multimodal Telegram remains explicitly open and out of core v1.**
    - Photo, voice, and media reply handling are not frozen as core.
    - Impact: do not block v1; plan as post-v1 feature.
    - Severity: P2 feature.

### E. Operations, Security, And AI Risk Findings

15. **External observability is still limited.**
    - The repo has strong health and incident-evidence export, but the runbook
      still records no external observability stack with dashboards or
      centralized trace storage.
    - Impact: acceptable for a small launch only if release ownership and
      manual triage are explicit; stronger v1 operations need at least a simple
      uptime/health monitor and alert route.
    - Severity: P1 ops hardening.

16. **AI red-team evidence is not part of the latest v1 release bundle.**
    - Behavior validation is strong, but production hardening standards require
      AI testing for prompt injection, data leakage, and unauthorized access
      when AI/user data are involved.
    - Impact: a world-class v1 claim should include a reproducible AI safety
      checklist and scenario results.
    - Severity: P1 hardening blocker.

17. **Release bundle evidence exists as mechanisms, but not as one latest
    signed-off bundle for the current candidate.**
    - Required pieces: backend tests, web build, behavior report, health
      snapshot, incident evidence bundle, production release smoke, rollback
      note.
    - Impact: without one current bundle, handoff and deploy confidence depend
      on scattered task history.
    - Severity: P0 release evidence blocker.

## V1 Acceptance Matrix

| Gate | Current Status | Release Need | Priority |
| --- | --- | --- | --- |
| Conversation reliability | Implemented and health-backed | Run production release smoke plus Telegram provider smoke | P0 |
| Learned-state inspection | Implemented and health-backed | Attach health and incident evidence for current candidate | P0 |
| Website reading | Implemented and behavior-proven locally | Attach behavior report and release smoke | P0 |
| Tool-grounded learning | Implemented and behavior-proven locally | Attach behavior report and incident evidence | P0 |
| Time-aware planned work | Implemented and behavior-proven locally | Attach `T19.1..T19.2` evidence and health parity | P0 |
| Deploy parity | Previously proven for older commits | Publish current scope and rerun production release smoke | P0 |
| Web product shell | Strong but locally dirty | Commit scope audit, route smoke, release smoke revision parity | P1 |
| Organizer extension | Contract exists, credentials likely missing | Configure providers or keep explicit extension-blocked posture | P1 |
| External observability | Health/export exists, no external stack | Add minimal uptime/alert posture | P1 |
| AI safety hardening | Partially covered by behavior tests | Add red-team/prompt-injection/data-leakage evidence | P1 |
| Multimodal Telegram | Open decision | Post-v1 feature plan | P2 |

## Execution Plan

### Phase 0 - Freeze The Current Release Boundary

Goal: decide what `v1` means for the next actual release.

1. Keep core `v1` as no-UI backend life assistant.
2. Treat current web shell as included product surface only if its local dirty
   changes are committed, built, smoked, and deployed.
3. Keep organizer daily-use and multimodal Telegram as extension gates unless
   the user explicitly revises the architecture.

Tasks:

- `PRJ-903` Freeze Current V1 Release Boundary
  - Type: planning
  - Status: DONE
  - Output: `docs/planning/current-v1-release-boundary.md` separates core
    release blockers, included web-product checks, extension gates, and
    hardening gates.

### Phase 1 - Clean And Package The Candidate

Goal: make the repo releasable again.

Tasks:

- `PRJ-904` V1 Commit Scope Audit
  - Status: DONE
  - Output: `docs/planning/v1-commit-scope-audit.md` records the candidate
    base, head, local commits, included scope, excluded local artifacts, and
    PRJ-905 validation gate.
  - Identify intended release files across backend, web, `.codex`, docs, and
    generated artifacts.
  - Decide whether untracked historical task records are part of this release.
  - Exclude generated `artifacts/` unless explicitly needed as committed
    evidence.

- `PRJ-905` V1 Candidate Validation Gate
  - Status: DONE
  - Output: `docs/planning/v1-candidate-validation-gate.md` records the local
    candidate validation gate for head
    `463ad04bc147c1284d0f1e12b4d5ff0cabec6fa1`.
  - Run:
    - backend full test suite
    - web build
    - behavior validation with artifact
    - targeted release-smoke script tests
  - Close only if all gates pass.

- `PRJ-906` Publish V1 Candidate
  - Status: DONE
  - Output: `docs/planning/v1-publish-candidate.md` records the successful
    push of validated candidate `582b146cdd89a488acc6bcebee4c00a7c418d108` to
    `origin/main`.
  - Commit the selected scope.
  - Push to `origin/main`.
  - Do not call the release complete until production smoke passes.

### Phase 2 - Prove Production Parity

Goal: make live production match the candidate.

Tasks:

- `PRJ-907` Production Release Smoke With Deploy Parity
  - Run:
    `.\backend\scripts\run_release_smoke.ps1 -BaseUrl "https://aviary.luckysparrow.ch" -WaitForDeployParity -DeployParityMaxWaitSeconds 900 -DeployParityPollSeconds 30 -HealthRetryMaxAttempts 10 -HealthRetryDelaySeconds 10`
  - Required pass signals:
    - `health_status=ok`
    - `release_ready=true`
    - `release_violations=[]`
    - runtime build revision equals local release SHA
    - web shell build revision equals local release SHA
    - runtime action smoke succeeds

- `PRJ-908` Production Incident Evidence Bundle
  - Status: DONE by `PRJ-922` and refreshed by `PRJ-923`
  - Output: `docs/planning/v1-production-incident-evidence-bundle.md` records
    the original strict-policy blocker and the passing strict-mode
    health-derived bundle path added by `PRJ-922`.
  - Current production incident-evidence bundle was exported.
  - Latest behavior-validation evidence was attached through the final
    acceptance bundle.
  - Release smoke accepted the bundle path.

- `PRJ-922` Production-Safe Incident Evidence Export
  - Status: DONE
  - Output: `backend/scripts/export_incident_evidence_bundle.py` now falls
    back to `/health` policy surfaces when production debug payload access is
    intentionally disabled.
  - Production bundle export succeeded with
    `incident_evidence_source=health_snapshot_strict_mode`.
  - Release smoke accepted the bundle path.

- `PRJ-909` Production Telegram Mode Smoke
  - Status: BLOCKED
  - Output: `docs/planning/v1-production-telegram-mode-smoke.md` records that
    production health reports Telegram as `provider_backed_ready`, but the live
    provider listen probe was not run because this local operator session lacks
    `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, and a known
    `REQUIRED_CHAT_ID`.
  - Run webhook/listen smoke with real bot token, webhook secret, and known
    chat id.
  - Restore webhook after listen probe.
  - Record whether Telegram is launch-ready or blocked by operator
    preconditions.

### Phase 3 - Close Core V1 Gaps

Goal: ensure every core gate has fresh release evidence.

Tasks:

- `PRJ-910` Core V1 Acceptance Bundle
  - Status: REFRESHED by `PRJ-923`
  - Output: `docs/planning/v1-core-acceptance-bundle.md` records core v1
    behavior as GO, deploy parity as GO, incident evidence as GO, and core
    no-UI v1 declaration as GO for
    `0984440a8a2a283942e4aa2c190e3964d0dadc9c`.
  - Produce one concise acceptance bundle mapping every final gate to:
    - health field
    - behavior scenario
    - release smoke proof
    - incident evidence field
    - residual risk

- `PRJ-923` Final V1 Acceptance Refresh
  - Status: DONE
  - Output: refreshed `docs/planning/v1-core-acceptance-bundle.md` against the
    latest production SHA and strict-mode incident evidence bundle.
  - Bundle:
    `.codex/artifacts/prj923-final-v1-acceptance/20260502T220616Z_prj923-final-v1-acceptance-0984440`
  - Release smoke with `-IncidentEvidenceBundlePath` passed.

- `PRJ-911` V1 Rollback And Recovery Drill
  - Status: DONE
  - Output: `docs/planning/v1-rollback-and-recovery-drill.md` records the
    current production SHA, previous known-good SHA, Alembic head, Coolify
    rollback procedure, strict incident-evidence triage path, and recovery
    smoke steps.
  - Record rollback target, previous known good revision, database migration
    posture, and recovery steps.
  - Confirm rollback does not require undocumented operator memory.

- `PRJ-912` V1 Data Privacy And Debug Posture Check
  - Status: DONE
  - Output: `docs/planning/v1-data-privacy-and-debug-posture-check.md`
    records debug-disabled production posture, auth/reset boundary regression
    evidence, and payload exposure boundaries.
  - Verify shared debug ingress posture, debug token policy, auth boundaries,
    and app reset behavior.
  - Confirm no raw provider payloads or memory payloads leak through app
    overview, health, or incident evidence.

### Phase 4 - Make The Web Product Claim Honest

Goal: if the web shell is part of v1, remove misleading static/demo behavior
from primary surfaces.

Tasks:

- `PRJ-913` Web V1 Route Smoke After Release Candidate
  - Status: DONE
  - Output: `docs/planning/v1-web-route-smoke-after-release-candidate.md`
    records a passing local route smoke across `/login` plus 12 authenticated
    routes on desktop/mobile, and `web/src/index.css` fixes the concrete
    `/tools` mobile overflow found during the smoke.
  - Cover login, dashboard, chat, personality, settings, tools, memory,
    reflections, plans, goals, insights, automations, and integrations.
  - Check desktop/mobile, empty/loading/success/error where practical.

- `PRJ-914` Replace Remaining Static Personality Metrics
  - Status: DONE
  - Output: `docs/planning/v1-replace-static-personality-metrics.md` records
    the replacement of fixed Personality clarity, intuition, and skill-count
    claims with values derived from the existing overview contract.
  - Converted clarity, energy, load, focus, intuition, role, and skills values
    to backend truth or explicit empty runtime state.

- `PRJ-915` Backend-Backed Dashboard Summary Surface
  - Status: DONE
  - Output:
    `docs/planning/v1-backend-backed-dashboard-summary-surface.md` records the
    dashboard summary replacement and focused desktop/mobile smoke evidence.
  - Replaced route-local dashboard summary cards that implied live operational
    truth with values from `/app/personality/overview` and
    `/app/tools/overview`.

- `PRJ-916` Web Empty And Error State Audit
  - Status: DONE
  - Output: `docs/planning/v1-web-empty-and-error-state-audit.md` records
    authenticated route smoke and backend-down dashboard smoke evidence.
  - Confirmed first-party routes handle unauthenticated, empty/success, and
    backend-error postures without route failures or raw technical leakage in
    the checked local states.

### Phase 5 - Extension Readiness

Goal: make post-core daily-use value visible and honest.

Tasks:

- `PRJ-917` Organizer Provider Credential Activation Runbook
  - Status: DONE
  - Output:
    `docs/planning/v1-organizer-provider-credential-activation-runbook.md`
    records the production organizer health snapshot and runbook link.
  - Turned provider missing settings into a step-by-step operator checklist
    for ClickUp, Google Calendar, and Google Drive.

- `PRJ-918` Organizer Provider Activation Smoke
  - Status: BLOCKED
  - Output: `docs/planning/v1-organizer-provider-activation-smoke.md` records
    that production still reports `provider_credentials_missing`.
  - After credentials are configured, run production release smoke and provider
    read-only smoke.
  - Confirm `organizer_daily_use_state` and provider-specific readiness are
    accurate.

- `PRJ-919` Tool Authorization UX Tightening
  - Ensure the web tools screen clearly distinguishes always-on, configured,
    user-enabled, linked, and confirmation-required states.

### Phase 6 - Operational Hardening

Goal: make v1 operable beyond one manual deploy.

Tasks:

- `PRJ-920` Minimal External Health Monitor
  - Status: DONE
  - Output: `docs/planning/v1-minimal-external-health-monitor.md` records the
    active hourly `aion-production-health-monitor` automation and runbook.
  - Added and documented an hourly read-only production `/health` check,
    alert criteria, check cadence, and operator response path.

- `PRJ-921` Release Evidence Archive Standard
  - Status: DONE
  - Output: `docs/planning/v1-release-evidence-archive-standard.md` defines
    where latest release smoke, behavior report, incident bundle, rollback
    notes, local generated artifacts, and committed decision summaries live.
  - Generated machine-local artifacts remain local by default unless an
    operator explicitly selects a sanitized artifact for repository history.

- `PRJ-930` Deployment Trigger SLO Evidence
  - Status: DONE
  - Output: `docs/planning/v1-deployment-trigger-slo-evidence.md` records the
    Coolify deployment-trigger SLO, primary source-automation proof path,
    webhook/UI exception-only fallback path, release-smoke validation, and the
    operator-owned Coolify history proof gap.
  - Manual redeploy remains recovery evidence only; it does not replace
    source-automation reliability proof.

### Phase 7 - AI And Security Hardening

Goal: make AI behavior safe enough for a real user-facing launch.

Tasks:

- `PRJ-931` V1 AI Red-Team Scenario Pack
  - Status: DONE
  - Output: `docs/security/v1-ai-red-team-scenario-pack.md` and
    `docs/security/v1-ai-red-team-scenarios.json` cover prompt injection, tool
    boundary bypass attempts, data exfiltration, unauthorized memory access,
    connector misuse, malicious web content, memory corruption, and malformed
    inputs.
  - This closes the reproducible scenario-pack gap only; executed pass/fail
    red-team evidence still requires a separate run or waiver.

- `PRJ-932` Cross-User And Session Isolation Audit
  - Status: DONE
  - Output: `docs/security/v1-cross-user-session-isolation-audit.md` verifies
    app auth, Telegram linked identity, reset behavior, chat history, overview
    data, tools overview, and internal inspection boundaries.
  - Focused validation passed: `24 passed, 95 deselected`.
  - Follow-up evidence gaps remain for explicit two-user transcript, reset,
    session-cookie-switching, and Telegram relink/conflict regressions.

- `PRJ-933` Provider Payload Leakage Audit
  - Status: DONE
  - Output: `docs/security/v1-provider-payload-leakage-audit.md` records the
    inspected app overview, tools overview, chat history, health, incident
    evidence, durable memory, and frontend usage boundaries.
  - Fixed the only confirmed projection leak candidate: raw subconscious
    proposal `payload` is no longer returned through learned-state planning
    snapshots; callers receive proposal metadata, `payload_present`, and
    `payload_keys` only.
  - Follow-up evidence gaps remain for live provider credential smoke, executed
    AI red-team exfiltration scenarios, strict-mode incident-bundle sentinel
    regression, and frontend fixture-based payload sentinel smoke.

### Phase 8 - Final V1 Declaration

Goal: make the statement "v1 is real" defensible.

Tasks:

- `PRJ-934` V1 Final Go/No-Go Review
  - Status: DONE
  - Output: `docs/planning/v1-final-go-no-go-review.md` records the final
    decision as `NO-GO / HOLD` for the release marker.
  - Production currently serves
    `ed1c4d981314787d76252985b53c14ea1d7886ed`, while local `HEAD` is
    `92f7bf3af16502a1a3f661aa16bf6a9ead92e0cd`.
  - Core deployed production gates remain green for the deployed SHA, but the
    current local candidate is not yet deployed and must not be tagged as
    released.

- `PRJ-935` V1 Release Notes And Operator Handoff
  - Record capabilities, known limits, rollback, smoke commands, and support
    triage.

- `PRJ-936` V1 Tag And Release Marker
  - Create a release tag only after production smoke and acceptance bundle are
    green.

## Priority Queue

### P0 Blockers

1. `PRJ-903` Freeze Current V1 Release Boundary
2. `PRJ-904` V1 Commit Scope Audit
3. `PRJ-905` V1 Candidate Validation Gate
4. `PRJ-906` Publish V1 Candidate
5. `PRJ-907` Production Release Smoke With Deploy Parity
6. `PRJ-908` Production Incident Evidence Bundle
7. `PRJ-910` Core V1 Acceptance Bundle
8. `PRJ-923` Final V1 Acceptance Refresh
9. `PRJ-911` V1 Rollback And Recovery Drill
10. `PRJ-912` V1 Data Privacy And Debug Posture Check

### P1 Product And Operations

1. `PRJ-909` Production Telegram Mode Smoke - BLOCKED by operator
   preconditions
2. `PRJ-913` Web V1 Route Smoke After Release Candidate - DONE locally
3. `PRJ-914` Replace Remaining Static Personality Metrics - DONE locally
4. `PRJ-915` Backend-Backed Dashboard Summary Surface - DONE locally
5. `PRJ-916` Web Empty And Error State Audit - DONE locally
6. `PRJ-917` Organizer Provider Credential Activation Runbook - DONE locally
7. `PRJ-918` Organizer Provider Activation Smoke - BLOCKED by provider
   credentials
8. `PRJ-920` Minimal External Health Monitor - DONE locally
9. `PRJ-921` Release Evidence Archive Standard - DONE locally
10. `PRJ-931` V1 AI Red-Team Scenario Pack - DONE locally
11. `PRJ-932` Cross-User And Session Isolation Audit - DONE locally with
    follow-up test gaps
12. `PRJ-933` Provider Payload Leakage Audit - DONE locally with follow-up
    provider/red-team evidence gaps
13. `PRJ-934` V1 Final Go/No-Go Review - DONE with `NO-GO / HOLD`
    release-marker decision

### P2 Extensions

1. `PRJ-919` Tool Authorization UX Tightening
2. `PRJ-930` Deployment Trigger SLO Evidence - DONE locally with
   operator-owned Coolify history proof gap
3. multimodal Telegram plan and implementation after v1
4. mobile Expo restart from the approved stack baseline after web/backend v1

## Done Definition For V1

`v1` can be declared real only when:

1. the release boundary is frozen
2. the repo has no ambiguous release-scope dirt
3. the candidate is committed and pushed
4. full backend tests pass
5. web build passes if the web shell is included
6. behavior validation passes and artifact is captured
7. production release smoke passes with deploy parity
8. production incident-evidence bundle is exported and validated
9. Telegram provider smoke is either passed or explicitly marked as blocked by
   operator preconditions
10. every core `v1_readiness.final_acceptance_gate_states` value is green in
    live production
11. debug, privacy, and raw-payload leakage checks are documented
12. rollback/recovery is recorded
13. release notes and operator handoff are written
14. a release marker/tag is created after, not before, the evidence is green

## Residual Risks

- Provider credentials are an operational dependency and cannot be solved by
  code alone.
- Web product polish can keep expanding indefinitely; it needs a boundary so it
  improves v1 without preventing core release.
- AI quality and empathy can be improved after v1, but safety and data-boundary
  evidence should be captured before a serious launch claim.
- Production smoke after a docs-only evidence commit creates a new SHA and must
  be repeated; record smoke evidence carefully to avoid infinite deploy loops.
