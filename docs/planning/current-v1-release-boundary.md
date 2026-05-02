# Current V1 Release Boundary

Last updated: 2026-05-02

## Purpose

This document freezes what the next `v1` release candidate means for this
repository. It exists so release work can package, validate, publish, and smoke
one explicit scope instead of silently expanding `v1` with every useful
follow-up feature.

## Frozen Core V1

The core `v1` release remains the no-UI life-assistant bundle already described
by the architecture and release-readiness docs:

1. stable Telegram or API conversation
2. learned-state inspection and later reuse
3. bounded website reading
4. tool-grounded learning
5. time-aware planned work
6. deployment parity in live production

These six gates are the P0 release blockers. A candidate is not `v1` until the
current commit is validated locally, published, and proven in production with
release-smoke evidence tied to the deployed revision.

## Included Candidate Surface

The current web shell and canonical route work are included in the release
candidate as a product-facing companion surface, but they do not redefine the
core no-UI `v1` architecture gate.

For this candidate, the web shell must satisfy:

- committed and pushed source scope
- successful `npm run build`
- route smoke evidence for the authenticated shell and primary routes
- deployed revision parity in release smoke

Remaining static decorative values or polish gaps are tracked as web-v1 follow
ups unless they block route rendering, authenticated use, or revision parity.

## Extension Gates

The following are extension gates, not core `v1` blockers:

- organizer provider activation for ClickUp, Google Calendar, and Google Drive
- richer daily-use organizer workflows
- multimodal Telegram input and output
- mobile/Expo client restart
- external observability beyond the existing health, smoke, and incident
  evidence mechanisms

Each extension may become a release blocker only through an explicit scope
decision that updates this document and the relevant architecture or planning
source of truth.

## Hardening Gates

The following hardening work is required for a world-class public claim, but it
must stay separate from core feature invention:

- production release smoke with deployed revision parity
- incident evidence bundle for the current candidate
- rollback and recovery drill notes
- data privacy and debug posture check
- AI red-team scenario evidence for prompt injection, data leakage, and
  unauthorized access risks

## Non-Goals For The Current Candidate

- no new runtime architecture
- no new provider integration system
- no new parallel web shell
- no temporary bypass for failing production parity
- no release claim based only on local tests

## Next Execution Order

1. `PRJ-904` V1 Commit Scope Audit
2. `PRJ-905` V1 Candidate Validation Gate
3. `PRJ-906` Publish V1 Candidate
4. `PRJ-907` Production Release Smoke With Deploy Parity
5. `PRJ-908` Production Incident Evidence Bundle
6. `PRJ-910` Core V1 Acceptance Bundle

`PRJ-909`, `PRJ-911`, `PRJ-912`, and the P1/P2 hardening tasks remain queued
behind the candidate package unless the release smoke exposes a higher-risk
gap.
