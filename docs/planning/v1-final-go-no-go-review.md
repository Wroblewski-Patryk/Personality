# V1 Final Go/No-Go Review

Date: 2026-05-03
Task: `PRJ-934`
Decision: NO-GO / HOLD for final release marker

## Summary

The current repository has strong core `v1` evidence, but the final release
marker must not be created yet. Production is not serving the current local
candidate commit, and several launch-channel or evidence gaps remain explicit.

This review closes PRJ-934 as a decision record. It does not close PRJ-935
release notes/operator handoff or PRJ-936 release marker.

## Revision Check

| Check | Value | Result |
| --- | --- | --- |
| Local `HEAD` | `92f7bf3af16502a1a3f661aa16bf6a9ead92e0cd` | Candidate is newer than production |
| Production `/health.deployment.runtime_build_revision` | `ed1c4d981314787d76252985b53c14ea1d7886ed` | Does not match local `HEAD` |
| Production web shell meta `aion-web-build-revision` | `ed1c4d981314787d76252985b53c14ea1d7886ed` | Matches production backend, not local `HEAD` |
| Production trigger posture | `source_automation` / `primary_automation` | Policy surface is healthy |
| Production final acceptance gate states | all inspected core states green | Core production posture is still green for deployed SHA |

Commands used:

```powershell
git rev-parse HEAD
Invoke-RestMethod -Uri "https://aviary.luckysparrow.ch/health" -TimeoutSec 20
Invoke-RestMethod -Uri "https://aviary.luckysparrow.ch/settings" -TimeoutSec 20
```

## Go / No-Go

| Scope | Decision | Reason |
| --- | --- | --- |
| Core no-UI v1 already deployed at `ed1c4d9...` | GO | Existing acceptance bundle and production health remain green for that deployed revision. |
| Current local repository candidate `92f7bf3...` | NO-GO / HOLD | Production is not serving this SHA; release smoke with deploy parity would fail until deployment catches up or a release SHA is intentionally frozen. |
| Public/web-led v1 launch marker | NO-GO / HOLD | PRJ-935 handoff and PRJ-936 marker are not complete; launch-channel and evidence gaps remain explicit. |
| Release tag/marker | BLOCKED | Tags must come after green production smoke and acceptance evidence, not before. |

## P0 Review

| Item | Status |
| --- | --- |
| PRJ-903 release boundary | Closed in release plan |
| PRJ-904 commit scope audit | Closed in release plan |
| PRJ-905 candidate validation | Closed in release plan |
| PRJ-906 publish candidate | Closed for earlier candidate only |
| PRJ-907 production release smoke with deploy parity | Closed for deployed SHA; must be rerun for current local HEAD |
| PRJ-908 production incident evidence bundle | Superseded by strict-mode safe export path and closed |
| PRJ-910 / PRJ-923 acceptance bundle | Closed for current documented core-v1 acceptance |
| PRJ-911 rollback and recovery drill | Closed |
| PRJ-912 data privacy/debug posture | Closed; PRJ-933 added provider-payload follow-up hardening |

## P1 / Launch-Channel Review

| Item | Status | Release effect |
| --- | --- | --- |
| PRJ-909 production Telegram live-mode smoke | BLOCKED by missing operator token, webhook secret, and known chat id | Telegram-led launch claim blocked |
| PRJ-918 organizer provider activation smoke | BLOCKED by provider credentials | Organizer daily-use claim blocked |
| PRJ-931 AI red-team scenario pack | DONE as scenario pack only | Execution results still needed or explicitly waived |
| PRJ-932 cross-user/session isolation audit | DONE with follow-up test gaps | Not a current release marker blocker if accepted as follow-up |
| PRJ-933 provider payload leakage audit | DONE with follow-up evidence gaps | Not a current release marker blocker if accepted as follow-up |
| PRJ-930 deployment-trigger SLO evidence | DONE locally | Direct Coolify deployment-history proof remains operator-owned |

## Deferred P2 Items

- `PRJ-919` tool authorization UX tightening
- multimodal Telegram plan and implementation
- mobile Expo restart from approved stack baseline

These should stay deferred unless the release claim is expanded beyond the
current core/web-supported v1 posture.

## Required Actions Before PRJ-936

1. Decide whether the release target is the deployed SHA
   `ed1c4d981314787d76252985b53c14ea1d7886ed` or the current local candidate
   `92f7bf3af16502a1a3f661aa16bf6a9ead92e0cd`.
2. If the target is current local `HEAD`, deploy it and wait for production
   `/health.deployment.runtime_build_revision` and web meta revision to match.
3. Run production release smoke with deploy parity.
4. Complete PRJ-935 release notes and operator handoff.
5. Keep PRJ-936 blocked until the chosen release SHA has green production
   evidence.

## Final Decision

Do not create a release marker now.

The correct next task is PRJ-935 release notes and operator handoff, written
with this HOLD posture, or a deploy-and-smoke task if the user/operator wants
the current local `HEAD` to become the release candidate.
