# Deployment Agent Checklist Template

## Mission

Deploy `Personality / AION` to `<ENV>` using SHA `<SHA>` and return only after
health plus smoke validation.

## Inputs

1. Repo path
2. SHA or branch
3. Environment (`stage` or `production`)
4. Web or API URL
5. Telegram webhook URL, if relevant
6. Service map or deployment topology

## Required Execution Order

1. Verify SHA and repo state.
2. Verify env variables and service routing.
3. Verify database connectivity assumptions.
4. Deploy app containers or services.
5. Restart workers if reflection is split out later.
6. Run health checks.
7. Run one `/event` smoke.
8. Run Telegram webhook smoke if relevant.
9. Report outcome.

## Health And Smoke Commands

1. `GET /health` -> expected `200`
2. `POST /event` with a minimal payload -> expected successful runtime response
3. Telegram webhook setup or delivery smoke if integration config changed

## Stop Conditions

1. startup or migration failure
2. health endpoint not green
3. `/event` smoke fails
4. Telegram delivery or webhook validation fails when it is in scope

## Output Contract

1. Final status (`success`, `blocked`, `rolled_back`)
2. Deployed SHA
3. Passed or failed checks
4. Exact failing endpoint or error if blocked
5. Recommended next action

## Deployment Gate Evidence

- [ ] `DEPLOYMENT_GATE.md` has no hard blocks.
- [ ] Build passes without errors.
- [ ] Runtime startup logs have no blocking errors.
- [ ] API contracts match deployed clients.
- [ ] Required migrations are applied.
- [ ] Environment variables and secrets are configured.
- [ ] Rollback path is prepared and appropriate for the risk level.
