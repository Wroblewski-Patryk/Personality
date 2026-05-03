# V1 Core Acceptance Bundle

Last updated: 2026-05-02

## Status

Core no-UI `v1` is GO for the current production revision:

- `0984440a8a2a283942e4aa2c190e3964d0dadc9c`

This is a core runtime acceptance result, not a claim that every product,
provider, security, AI, or web-polish follow-up is complete.

## Acceptance Summary

| Gate | Health Surface | Production State | Evidence | Residual Risk |
| --- | --- | --- | --- | --- |
| Conversation reliability | `/health.conversation_channels.telegram` | `provider_backed_ready` | Release smoke passed; bot token and webhook secret configured; Telegram delivery posture exposes segmentation and formatting support | Live user/chat round-trip smoke remains `PRJ-909` before a Telegram-led launch claim |
| Learned-state inspection | `/health.learned_state` | `inspection_surface_ready` | Strict-mode incident bundle includes learned-state policy owner, inspection path, inspection sections, growth sections, and tool-grounded learning contract | No core blocker |
| Website reading | `/health.connectors.web_knowledge_tools.website_reading_workflow` | `ready_for_direct_and_search_first_review` | Health and incident bundle expose direct URL and search-first page review readiness with no blockers | No core blocker |
| Tool-grounded learning | `/health.learned_state.tool_grounded_learning` | `tool_grounded_learning_surface_ready` | Health and incident bundle expose action-owned external read summaries only, semantic memory layer, and no raw payload storage | Privacy/security hardening remains a separate `PRJ-912/PRJ-933` check |
| Time-aware planned work | `/health.v1_readiness` | `foreground_due_delivery_and_recurring_reevaluation_ready` | Behavior validation and health expose planned-work policy owner, delivery path, and recurrence owner; scheduler external evidence is recent and aligned | No core blocker |
| Deploy parity | `/health.deployment` and release smoke | runtime/web/local SHA match | Release smoke passed with deploy parity for `0984440a8a2a283942e4aa2c190e3964d0dadc9c` | Every later commit requires fresh deploy parity smoke |

## Evidence Set

Local candidate validation:

- PRJ-905 backend tests: `1019 passed`
- PRJ-905 web production build: passed
- PRJ-905 behavior validation: `19 passed, 209 deselected`
- PRJ-922 backend validation: `1021 passed`

Production validation:

- release smoke after PRJ-929 queue cleanup passed with deploy parity for:
  `0984440a8a2a283942e4aa2c190e3964d0dadc9c`
- strict-mode incident evidence bundle export passed with:
  `incident_evidence_source=health_snapshot_strict_mode`
- release smoke with the strict-mode incident bundle passed

Current production incident bundle:

- `.codex/artifacts/prj923-final-v1-acceptance/20260502T220616Z_prj923-final-v1-acceptance-0984440`

The bundle is local evidence output and is not committed by default.

## Behavior Scenario Coverage

The current `v1_readiness.required_behavior_scenarios` list is:

- `T13.1`
- `T14.1`
- `T14.2`
- `T14.3`
- `T15.1`
- `T15.2`
- `T16.1`
- `T16.2`
- `T16.3`
- `T17.1`
- `T17.2`
- `T18.1`
- `T18.2`
- `T19.1`
- `T19.2`

PRJ-905 behavior validation passed with `19 passed, 209 deselected` and is
attached to the strict-mode incident bundle.

## Extension And Hardening Gates

The following are not core no-UI `v1` blockers, but remain required before a
broader public or web-led release claim:

- `PRJ-909` production Telegram live-mode smoke: BLOCKED until an operator
  provides `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, and a known
  `REQUIRED_CHAT_ID`; production health currently reports
  `provider_backed_ready`
- `PRJ-911` rollback and recovery drill
- `PRJ-912` data privacy and debug posture check
- `PRJ-913` web-v1 route smoke: DONE locally with desktop/mobile route
  evidence and `/tools` mobile overflow fix
- `PRJ-914` static Personality metrics replacement: DONE locally with
  desktop/mobile focused evidence
- `PRJ-915` backend-backed dashboard summary surface: DONE locally with
  desktop/mobile focused evidence
- `PRJ-916` web empty/error state audit: DONE locally with authenticated route
  and backend-down dashboard evidence
- `PRJ-917` organizer provider credential activation runbook: DONE locally
- `PRJ-918` organizer provider activation smoke: BLOCKED until provider
  credentials are configured
- `PRJ-919` tool authorization UX tightening
- `PRJ-920` minimal external health monitor: DONE with active hourly
  `aion-production-health-monitor`
- `PRJ-921` release-evidence archive: DONE with
  `docs/planning/v1-release-evidence-archive-standard.md`
- `PRJ-930` deployment trigger SLO evidence: DONE with
  `docs/planning/v1-deployment-trigger-slo-evidence.md`; direct Coolify
  deployment-history proof remains operator-owned for the final release
  declaration
- `PRJ-931` AI red-team scenario pack: DONE with
  `docs/security/v1-ai-red-team-scenario-pack.md`; execution results remain a
  separate release-hardening evidence item
- `PRJ-932` cross-user/session isolation audit: DONE with
  `docs/security/v1-cross-user-session-isolation-audit.md`; follow-up two-user
  regression gaps remain
- `PRJ-933` provider payload leakage audit: DONE with
  `docs/security/v1-provider-payload-leakage-audit.md`; follow-up live
  provider, red-team execution, strict-mode incident sentinel, and frontend
  fixture smoke gaps remain
- `PRJ-934` final go/no-go review: DONE with
  `docs/planning/v1-final-go-no-go-review.md`; release marker is `NO-GO / HOLD`
  because production is not serving the current local candidate SHA
- `PRJ-935..PRJ-936` handoff and release marker remain open; PRJ-936 is blocked
  until the chosen release SHA has green production evidence

## Go / No-Go

- Core no-UI v1 behavior: GO
- Production deploy parity: GO
- Production incident-evidence bundle: GO
- Core no-UI v1 declaration: GO
- Current local candidate release marker: NO-GO / HOLD
- Public/web-led v1 launch marker: HOLD until the remaining launch-channel,
  rollback, privacy/debug, and AI/security hardening gates are complete or
  explicitly waived by a documented release decision.

## Recommended Next Step

Rerun `PRJ-909` when Telegram operator preconditions are available. Until then,
continue with locally actionable public-launch hardening, starting with
`PRJ-935` release notes and operator handoff, or deploy the selected release
candidate and rerun production release smoke if the marker should target the
current local `HEAD`.
