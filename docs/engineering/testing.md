# Testing Strategy

## Current Automated Coverage

The repository currently contains lightweight backend-focused tests for:

- event normalization
- expression behavior
- end-to-end runtime pipeline composition with fake dependencies

Primary command:

```powershell
.\.venv\Scripts\python -m pytest -q
```

## Testing Layers For This Repo

- Unit tests:
  - heuristic agent logic
  - config validation
  - event normalization
  - repository helpers that can be exercised without a live service
- Integration tests:
  - FastAPI endpoints
  - database-backed memory persistence
  - Telegram/OpenAI adapter boundaries using mocks or fakes
- Manual smoke checks:
  - Docker startup
  - health endpoint
  - API roundtrip through `POST /event`
  - Telegram webhook flow in a non-production environment

## Required Checks By Change Type

- Runtime stage changes:
  - update or add tests around changed stage outputs
  - run the full pytest suite
- API contract changes:
  - add endpoint-level coverage
  - confirm the returned serialized shape still matches expectations
- Memory or database changes:
  - add repository or integration coverage
  - verify startup table creation or migration behavior
  - when migration files change, validate the Alembic path explicitly
- Integration changes:
  - mock external providers
  - verify fallback behavior when providers are unavailable

## Risk Areas To Keep Honest

- placeholder values presented as real runtime facts
- hidden side effects outside `ActionExecutor`
- changes that break Telegram-specific payload handling
- changes that silently disable memory persistence
- changes that rely on live OpenAI responses in automated tests

## Evidence Preference

For meaningful repo changes, leave behind:

- the exact test command used
- pass/fail result
- a short note if coverage is still missing for a known edge case

Useful migration verification command:

```powershell
.\.venv\Scripts\python -m alembic upgrade head --sql
```
