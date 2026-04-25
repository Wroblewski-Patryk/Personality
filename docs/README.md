# Docs Index

This repository uses a two-layer documentation model:

- `docs/architecture/` holds the canonical AION architecture and intended system design
- the other `docs/` folders hold implementation reality, operations, engineering, planning, and governance truth

## Start Here

- `overview.md` - short current-state summary of what the runtime actually does today
- `implementation/runtime-reality.md` - current implementation details and transitional runtime notes
- `architecture/02_architecture.md` - canonical cognitive architecture
- `architecture/15_runtime_flow.md` - canonical runtime order
- `architecture/16_agent_contracts.md` - canonical stage contracts
- `../backend/README.md` - backend workspace entrypoint for runtime commands

If an older numbered architecture doc ever reads differently from `02`, `15`,
and `16`, treat `02/15/16` as canonical and update the older file instead of
carrying two competing architecture narratives.

## Canonical Architecture

These files describe the intended long-term shape of the system:

- `architecture/00_quickstart.md`
- `architecture/01_project_overview.md`
- `architecture/02_architecture.md`
- `architecture/03_identity_roles_skills.md`
- `architecture/04_memory_system.md`
- `architecture/05_conscious_subconscious.md`
- `architecture/06_motivation_engine.md`
- `architecture/07_agent_system.md`
- `architecture/08_stack.md`
- `architecture/09_mvp_scope.md`
- `architecture/10_future_vision.md`
- `architecture/11_event_contact.md`
- `architecture/12_data_model.md`
- `architecture/13_repository_structure.md`
- `architecture/14_build_roadmap.md`
- `architecture/15_runtime_flow.md`
- `architecture/16_agent_contracts.md`
- `architecture/17_logging_and_debugging.md`
- `architecture/18_theta_dynamics.md`
- `architecture/19_expression_system.md`
- `architecture/20_action_system.md`
- `architecture/21_goal_task_system.md`
- `architecture/22_relation_system.md`
- `architecture/23_proactive_system.md`
- `architecture/24_system_guardrails.md`
- `architecture/25_first_iteration_plan.md`
- `architecture/26_env_and_config.md`
- `architecture/27_codex_instructions.md`
- `architecture/28_local_windows_and_coolify_deploy.md`
- `architecture/29_runtime_behavior_testing.md`

## Implementation Reality

These files describe what is implemented today, including transitional runtime details:

- `implementation/runtime-reality.md`
- `implementation/dual-loop-coordination.md`
- `overview.md`

They also carry supplemental non-canonical notes when the repo needs to record
near-term coordination direction without rewriting the canonical architecture.

## Governance

- `governance/working-agreements.md`
- `governance/repository-structure-policy.md`

## Engineering

- `engineering/local-development.md`
- `engineering/testing.md`

## Planning

- `planning/open-decisions.md`
- `planning/next-iteration-plan.md`
- `planning/v2-product-entry-plan.md`

## Product Workspaces

- `../backend/` - current production runtime
- `../web/` - browser client workspace
- `../mobile/` - future mobile client placeholder

Use these files for explicit follow-up on dual-loop coordination, attention
gating, batched conversation handling, and future external productivity
connector boundaries before those decisions become live runtime behavior.

## Operations

- `operations/runtime-ops-runbook.md`

## Update Rule

If implementation and canonical architecture diverge:

- update `docs/architecture/` only when the intended architecture itself changed
- record live implementation details in `docs/implementation/` and `docs/overview.md`
- keep `docs/operations/`, `docs/planning/`, and `.codex/context/` honest about what is already live
