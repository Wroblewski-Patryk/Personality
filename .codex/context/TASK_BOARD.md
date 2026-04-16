# TASK_BOARD

Last updated: 2026-04-16

## READY

## BACKLOG

## IN_PROGRESS

- [ ] (none)

## BLOCKED

- [ ] (none)

## DONE

- [x] PRJ-000 Establish Personality-specific agent workflow scaffolding
  - Status: DONE
  - Owner: Product Docs
  - Depends on: none
  - Priority: P1
  - Done when:
    - `AGENTS.md`, `.agents/`, `.claude/`, `.codex/`, `.githooks/`, and `.github/` exist in project-specific form
    - workflow rules mention the real stack and docs
    - validation commands match the repo

- [x] PRJ-001 Align runtime-facing docs with current reflection, language, role, and preference behavior
  - Status: DONE
  - Owner: Product Docs
  - Depends on: none
  - Priority: P1
  - Done when:
    - `docs/overview.md`, `docs/planning/open-decisions.md`, and any needed assumptions or basics docs reflect the current implemented runtime
    - current vs planned behavior is explicit
    - follow-up gaps remain captured rather than hidden

- [x] PRJ-002 Add endpoint-level coverage for reflection-related runtime contracts
  - Status: DONE
  - Owner: QA/Test
  - Depends on: none
  - Priority: P1
  - Done when:
    - `GET /health` reflection snapshot or related runtime contract is covered where applicable
    - `/event` reflection-trigger behavior is validated by tests if that contract is exposed
    - any brittle assumptions are documented

- [x] PRJ-003 Decide migration baseline and either document deferral or scaffold the first formal migration path
  - Status: DONE
  - Owner: DB/Migrations
  - Depends on: none
  - Priority: P1
  - Done when:
    - the schema strategy is explicit
    - rollback risk is documented
    - local bootstrap behavior remains understood

- [x] PRJ-004 Revisit the public `/event` response contract
  - Status: DONE
  - Owner: Planner
  - Depends on: PRJ-001
  - Priority: P1
  - Done when:
    - the owner and purpose of the response shape are explicit
    - tests and docs match the chosen contract
    - debug-only fields are intentional rather than accidental

- [x] PRJ-005 Harden release and deployment confidence for the Coolify path
  - Status: DONE
  - Owner: Ops/Release
  - Depends on: none
  - Priority: P2
  - Done when:
    - deployment smoke steps are explicit
    - webhook or manual-release fallback is documented
    - release verification is repeatable
