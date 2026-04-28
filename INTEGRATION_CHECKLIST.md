# Integration Checklist

Use this checklist before marking any integrated feature complete.

## Required Checks

- [ ] Frontend or client uses the real API, SDK, storage layer, or service path.
- [ ] No mocks, fixture-only paths, placeholders, or hardcoded production-like
  data remain in the delivered behavior.
- [ ] Endpoints exist and match the client usage exactly.
- [ ] Request and response shapes match documented contracts.
- [ ] Database schema matches the code that reads and writes it.
- [ ] Required migrations exist, run cleanly, and are applied in the target
  environment.
- [ ] Validation exists at the boundary that owns the data.
- [ ] Loading states are handled.
- [ ] Empty states are handled.
- [ ] Error states are handled.
- [ ] Retry, idempotency, or fail-closed behavior is covered where relevant.
- [ ] Feature works after refresh, restart, or reload.
- [ ] No regression is introduced in adjacent flows.
- [ ] Logs and errors do not leak secrets or private data.

## Vertical Slice Rule

Feature work must be delivered as a vertical slice:

`UI -> logic -> API -> DB -> validation -> error handling -> test`

Partial implementations are forbidden unless the task is explicitly scoped as
analysis, design, or an approved non-runtime documentation change.

## Stop Conditions

Stop and report instead of continuing when:

- the real endpoint, schema, or service contract does not exist
- the correct implementation requires an architecture decision
- validation cannot be made reproducible
- a mock or placeholder would be needed to make the feature appear complete
