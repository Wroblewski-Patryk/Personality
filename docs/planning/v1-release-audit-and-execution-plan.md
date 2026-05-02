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
  - Identify intended release files across backend, web, `.codex`, docs, and
    generated artifacts.
  - Decide whether untracked historical task records are part of this release.
  - Exclude generated `artifacts/` unless explicitly needed as committed
    evidence.

- `PRJ-905` V1 Candidate Validation Gate
  - Run:
    - backend full test suite
    - web build
    - behavior validation with artifact
    - targeted release-smoke script tests
  - Close only if all gates pass.

- `PRJ-906` Publish V1 Candidate
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
  - Export current production incident-evidence bundle.
  - Attach the latest behavior-validation report.
  - Verify release smoke accepts the bundle path.

- `PRJ-909` Production Telegram Mode Smoke
  - Run webhook/listen smoke with real bot token, webhook secret, and known
    chat id.
  - Restore webhook after listen probe.
  - Record whether Telegram is launch-ready or blocked by operator
    preconditions.

### Phase 3 - Close Core V1 Gaps

Goal: ensure every core gate has fresh release evidence.

Tasks:

- `PRJ-910` Core V1 Acceptance Bundle
  - Produce one concise acceptance bundle mapping every final gate to:
    - health field
    - behavior scenario
    - release smoke proof
    - incident evidence field
    - residual risk

- `PRJ-911` V1 Rollback And Recovery Drill
  - Record rollback target, previous known good revision, database migration
    posture, and recovery steps.
  - Confirm rollback does not require undocumented operator memory.

- `PRJ-912` V1 Data Privacy And Debug Posture Check
  - Verify shared debug ingress posture, debug token policy, auth boundaries,
    and app reset behavior.
  - Confirm no raw provider payloads or memory payloads leak through app
    overview, health, or incident evidence.

### Phase 4 - Make The Web Product Claim Honest

Goal: if the web shell is part of v1, remove misleading static/demo behavior
from primary surfaces.

Tasks:

- `PRJ-913` Web V1 Route Smoke After Release Candidate
  - Cover login, dashboard, chat, personality, settings, tools, memory,
    reflections, plans, goals, insights, automations, and integrations.
  - Check desktop/mobile, empty/loading/success/error where practical.

- `PRJ-914` Replace Remaining Static Personality Metrics
  - Convert clarity, energy, load, intuition, and similar values to backend
    truth or explicitly decorative copy.

- `PRJ-915` Backend-Backed Dashboard Summary Surface
  - Replace route-local dashboard summary cards that imply live operational
    truth with values from `/health`, `/app/personality/overview`, and
    `/app/tools/overview`.

- `PRJ-916` Web Empty And Error State Audit
  - Confirm all first-party routes handle unauthenticated, loading, empty,
    backend error, and success states without raw technical leakage.

### Phase 5 - Extension Readiness

Goal: make post-core daily-use value visible and honest.

Tasks:

- `PRJ-917` Organizer Provider Credential Activation Runbook
  - Turn provider missing settings into a step-by-step operator checklist.
  - Include ClickUp, Google Calendar, and Google Drive.

- `PRJ-918` Organizer Provider Activation Smoke
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
  - Add or document uptime check, alert destination, check cadence, and owner.

- `PRJ-921` Release Evidence Archive Standard
  - Define where latest release smoke, behavior report, incident bundle, and
    rollback notes live.
  - Avoid committing generated machine-local artifacts unless intentionally
    selected.

- `PRJ-922` Deployment Trigger SLO Evidence
  - Prove Coolify source automation triggers reliably enough or document manual
    redeploy as an exception-only fallback.

### Phase 7 - AI And Security Hardening

Goal: make AI behavior safe enough for a real user-facing launch.

Tasks:

- `PRJ-923` V1 AI Red-Team Scenario Pack
  - Cover prompt injection, tool boundary bypass attempts, data exfiltration,
    unauthorized memory access, and connector misuse.

- `PRJ-924` Cross-User And Session Isolation Audit
  - Verify app auth, Telegram linked identity, reset behavior, chat history,
    overview data, and internal inspection authorization boundaries.

- `PRJ-925` Provider Payload Leakage Audit
  - Confirm raw web page, task, calendar, drive, Telegram, and memory payloads
    do not leak through durable memory, health, app overview, or UI routes.

### Phase 8 - Final V1 Declaration

Goal: make the statement "v1 is real" defensible.

Tasks:

- `PRJ-926` V1 Final Go/No-Go Review
  - Review all P0/P1 findings.
  - Confirm which P2 extension gaps remain intentionally deferred.
  - Verify production is serving the intended SHA.

- `PRJ-927` V1 Release Notes And Operator Handoff
  - Record capabilities, known limits, rollback, smoke commands, and support
    triage.

- `PRJ-928` V1 Tag And Release Marker
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
8. `PRJ-911` V1 Rollback And Recovery Drill
9. `PRJ-912` V1 Data Privacy And Debug Posture Check

### P1 Product And Operations

1. `PRJ-909` Production Telegram Mode Smoke
2. `PRJ-913` Web V1 Route Smoke After Release Candidate
3. `PRJ-914` Replace Remaining Static Personality Metrics
4. `PRJ-915` Backend-Backed Dashboard Summary Surface
5. `PRJ-916` Web Empty And Error State Audit
6. `PRJ-917` Organizer Provider Credential Activation Runbook
7. `PRJ-918` Organizer Provider Activation Smoke
8. `PRJ-920` Minimal External Health Monitor
9. `PRJ-921` Release Evidence Archive Standard
10. `PRJ-923` V1 AI Red-Team Scenario Pack
11. `PRJ-924` Cross-User And Session Isolation Audit
12. `PRJ-925` Provider Payload Leakage Audit

### P2 Extensions

1. `PRJ-919` Tool Authorization UX Tightening
2. `PRJ-922` Deployment Trigger SLO Evidence
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
