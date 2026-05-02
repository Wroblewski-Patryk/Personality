# V1 Production Incident Evidence Bundle

Last updated: 2026-05-02

## Status

`PRJ-908` is blocked for the current production configuration.

Production is healthy again and release smoke is green, but the canonical
incident-evidence bundle cannot be exported through the current helper without
opening full debug payload access. Opening that window is blocked by the
production strict-policy baseline.

## Attempted Flow

The intended PRJ-908 flow was:

1. export a production incident-evidence bundle with
   `backend/scripts/export_incident_evidence_bundle.py`
2. attach the latest behavior-validation report from PRJ-905
3. verify the bundle with `backend/scripts/run_release_smoke.ps1`

The first export attempt failed with:

```text
HTTP 403 while calling https://aviary.luckysparrow.ch/internal/event/debug:
{"detail":"Debug payload is disabled for this environment."}
```

An operator-approved temporary debug window was then attempted by adding
temporary Coolify environment variables for the `Aviary / production / aviary`
application. The redeploy did not produce an exportable debug window. Instead,
production strict policy kept the runtime from becoming healthy while debug
payload exposure was enabled.

## Restoration Evidence

The temporary debug flag was reverted to disabled in Coolify and the
application was redeployed.

Restoration checks:

- `/health` returned to `health_status=ok`
- `runtime_policy.event_debug_enabled=false`
- `release_readiness.ready=true`
- runtime build revision:
  `948e7f6245c9dd4c5e767e0c8b840223b141cfa4`
- web shell build revision:
  `948e7f6245c9dd4c5e767e0c8b840223b141cfa4`
- release smoke passed after restoration

The temporary local debug-token artifact was deleted. The user reported the
Coolify-side token cleanup complete.

## Decision

Do not attempt PRJ-908 again by enabling `EVENT_DEBUG_ENABLED=true` in the
current production strict-policy posture.

## Required Fix Before PRJ-908 Can Close

Choose and implement one approved evidence path:

1. Add a dedicated token-gated production-safe incident-evidence export route
   that does not expose the full debug payload.
2. Add a Coolify/operator runbook for a temporary policy window that changes
   both debug access and production policy posture, with explicit rollback.
3. Redefine the release bundle contract to accept a health-only evidence bundle
   for production strict mode, with architecture approval.

Option 1 is the recommended path because it preserves the production strict
baseline while still allowing release evidence to be exported.

## Next Task

`PRJ-910` may produce the core v1 acceptance bundle with PRJ-908 marked as a
known blocked evidence gap, or a new narrow implementation task can be created
first to add the production-safe incident-evidence export route.
