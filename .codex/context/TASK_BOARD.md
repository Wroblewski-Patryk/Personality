# TASK_BOARD

Last updated: 2026-05-03

## Fresh PRJ-800G Public Home Production Parity Closure (2026-05-03)

- `PRJ-800G` is DONE:
  - `.codex/tasks/PRJ-800G-public-home-production-parity-slice.md`
- result:
  - the public-home production parity slice is no longer a stale `IN_PROGRESS`
    item
  - historical first-viewport improvements are preserved:
    - calmer hero headline block
    - lighter micro-proof row
    - compressed feature bridge
    - preserved public auth route contract
  - current public landing source keeps `LANDING_HERO_ART_SRC`,
    `aion-public-hero`, `aion-public-feature-bridge`, and
    `aion-public-trust-band`
  - current public landing truth is chrome-free per `PRJ-782`:
    - use content/composition from canonical landing references
    - ignore browser mockup frames from generated previews
  - later proof owners:
    - `PRJ-869` public home landing `99%` canonical pass
    - `PRJ-875` canonical UI final route sweep
- validation:
  - reviewed PRJ-800G task history, current public landing source, design
    memory, PRJ-782 user clarification, and later board/project proof
  - `Select-String -Path web\src\App.tsx,web\src\index.css -Pattern
    "aion-public-browser|WindowChrome|aion-window-chrome"`
  - result: no matches
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - review `PRJ-816` chat canonical parity closure lane

## Fresh PRJ-800F Dashboard Editorial Parity Closure (2026-05-03)

- `PRJ-800F` is DONE:
  - `.codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md`
- result:
  - the dashboard editorial parity lane is no longer a stale `IN_PROGRESS`
    item
  - historical dashboard micro-passes are preserved:
    - hero hierarchy and right rail calming
    - CTA hierarchy correction
    - figure-caption removal
    - unified and route-corrected dashboard hero artwork
    - proportions, crop/spacing, callout scale, and flow/closure rhythm
  - current source uses `DASHBOARD_HERO_ART_SRC` with
    `aviary-dashboard-hero-canonical-reference-v4.png`
  - active dashboard truth now points to:
    - `docs/ux/dashboard-proof-matrix.md`
    - `docs/ux/design-memory.md`
    - `docs/ux/flagship-baseline-transfer.md`
    - `PRJ-870` dashboard `99%` canonical evidence pass
    - `PRJ-875` canonical UI final route sweep
- validation:
  - reviewed PRJ-800F task history, current dashboard source, dashboard proof
    matrix, design memory, flagship baseline transfer, and later board/project
    proof
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - review `PRJ-800G` public home production parity slice for stale status

## Fresh PRJ-795 Shared Persona Freeze Closure (2026-05-03)

- `PRJ-795` is DONE:
  - `.codex/tasks/PRJ-795-freeze-shared-canonical-persona-figure-and-dashboard-pass.md`
- result:
  - the shared canonical persona figure task is no longer a stale
    `IN_PROGRESS` item
  - design memory keeps the durable rule:
    - reuse one approved Aviary persona family across flagship routes
    - adapt crop, callouts, and supporting objects to the route context
  - current source keeps `CANONICAL_PERSONA_FIGURE_SRC` for shared persona
    identity surfaces
  - approved route-specific hero assets such as `LANDING_HERO_ART_SRC` and
    `DASHBOARD_HERO_ART_SRC` are treated as later route adaptation, not as a
    new character system
  - later proof owners remain active history:
    - `PRJ-796` chat shared-persona adaptation
    - `PRJ-800F` dashboard route-corrected hero artwork
    - `PRJ-870` dashboard `99%` evidence pass
    - `PRJ-871` personality `99%` canonical pass
    - `PRJ-875` final canonical UI route sweep
- validation:
  - reviewed PRJ-795 task history, design memory, flagship baseline transfer,
    current source constants, and later board/project-state proof
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - review `PRJ-800F` dashboard editorial parity lane

## Fresh PRJ-785 Backend Architecture Audit Closure (2026-05-03)

- `PRJ-785` is DONE:
  - `.codex/tasks/PRJ-785-backend-architecture-quality-audit-and-improvement-plan.md`
- result:
  - the backend architecture quality audit task is no longer a stale `READY`
    item
  - original audit findings are preserved as history
  - later backend follow-up history and documentation repair lanes now carry
    the active engineering map:
    - generated OpenAPI reference
    - ERD and column model reference
    - test feature/pipeline ownership ledger
    - frontend route/component map
    - provider-specific integration docs
    - architecture codebase map and traceability matrix
- validation:
  - reviewed PRJ-785 task history, project state, task board, codebase map,
    traceability matrix, API docs, data docs, and documentation drift report
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - select the next active `IN_PROGRESS` task after excluding stale visual and
    audit tasks already superseded by later proof

## Fresh PRJ-784 Public Home First Viewport Closure (2026-05-03)

- `PRJ-784` is DONE:
  - `.codex/tasks/PRJ-784-public-home-first-viewport-canonical-pass.md`
- result:
  - the historical public-home first-viewport task is no longer a stale
    `IN_PROGRESS` item
  - current public landing keeps the embodied/scenic hero stage, integrated
    motif notes, CTA path, and feature bridge while staying on the
    chrome-free landing shell
  - later landing proof tasks remain useful:
    - `PRJ-866` landing canonical first viewport
    - `PRJ-869` public home landing `99%` canonical pass
    - `PRJ-875` canonical UI final route sweep
  - browser-window/frame wording in older landing proof notes is superseded by
    the `PRJ-782` decision resolution:
    - browser mockups in canonical images are preview context
    - browser chrome must not be implemented as product UI
- validation:
  - reviewed PRJ-784 task history, current public landing source, design
    memory, user clarification, and later board evidence
  - `Select-String -Path web\src\App.tsx,web\src\index.css -Pattern
    "aion-public-browser|WindowChrome|aion-window-chrome"`
  - result: no matches
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - review `PRJ-800A` and landing follow-up drift entries for stale
    browser-frame wording before reopening route-local visual work

## Fresh PRJ-782 Shell Frame Decision Resolution (2026-05-03)

- `PRJ-782` is DONE:
  - `.codex/tasks/PRJ-782-remove-window-chrome-and-audit-layout-frame-drift.md`
- result:
  - user clarified that browser chrome in canonical images is generated
    browser/mockup preview context and must be ignored in implementation
  - removed later public-home browser-like chrome under
    `aion-public-browser-*`
  - durable UX truth remains in `docs/ux/design-memory.md`:
    - do not simulate browser controls, title bars, or fake window chrome
    - ignore browser mockup frames in canonical reference images
  - later proof tasks carry the active frame/sidebar/shell trail:
    - `PRJ-800A` authenticated shell frame exactness
    - `PRJ-800B` sidebar pixel-close refinement
    - `PRJ-868` canonical layout foundation
    - `PRJ-875` canonical UI final route sweep
- validation:
  - reviewed PRJ-782 task history, current shell source, design memory, user
    clarification, and later board evidence
  - `Select-String -Path web\src\App.tsx,web\src\index.css -Pattern
    "aion-public-browser|WindowChrome|aion-window-chrome"`
  - result: no matches
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - review `PRJ-784` for public-home first-viewport canonical status on the
    chrome-free landing shell

## Fresh PRJ-781 Sidebar Desktop Spine Closure (2026-05-03)

- `PRJ-781` is DONE:
  - `.codex/tasks/PRJ-781-implement-canonical-sidebar-desktop-spine-pass.md`
- result:
  - the historical sidebar desktop spine task is no longer a stale
    `IN_PROGRESS` item
  - current source contains `SidebarGlyph`, `SidebarBrandBlock`, icon-led nav,
    the health/identity/quote support stack, and `.aion-sidebar-*` CSS
  - later implementation and proof tasks carry the active sidebar/shell trail:
    - `PRJ-800B` sidebar pixel-close refinement
    - `PRJ-868` canonical layout foundation
    - `PRJ-875` canonical UI final route sweep
  - the route-inventory mismatch remains explicit and no route was silently
    invented
- validation:
  - reviewed PRJ-781 task history, current sidebar source, design memory,
    flagship baseline transfer, and later board evidence
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - review `PRJ-782` for WindowChrome removal and layout-frame drift status

## Fresh PRJ-780 Canonical Sidebar Planning Closure (2026-05-03)

- `PRJ-780` is DONE:
  - `.codex/tasks/PRJ-780-freeze-canonical-sidebar-layout-and-plan-shell-convergence.md`
- result:
  - the canonical sidebar planning task is no longer a stale `READY` item
  - later implementation and proof tasks carry the active sidebar/shell trail:
    - `PRJ-781` canonical sidebar desktop spine
    - `PRJ-800B` sidebar pixel-close refinement
    - `PRJ-868` canonical layout foundation
    - `PRJ-875` canonical UI final route sweep
  - current reusable shell/sidebar truth points to:
    - `docs/ux/design-memory.md`
    - `docs/ux/flagship-baseline-transfer.md`
    - `web/src/App.tsx`
    - `web/src/index.css`
  - the route-inventory mismatch remains explicit and must not be solved by
    silently inventing routes
- validation:
  - reviewed PRJ-780 task history, current sidebar code, design memory,
    flagship baseline transfer, and later board evidence
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - review `PRJ-781` for canonical sidebar desktop spine implementation status

## Fresh PRJ-779 Dashboard Structural Closure (2026-05-03)

- `PRJ-779` is DONE:
  - `.codex/tasks/PRJ-779-dashboard-structural-canonical-convergence-pass.md`
- result:
  - the historical dashboard structural convergence task is no longer a stale
    `IN_PROGRESS` item
  - later dashboard work supersedes it as active proof:
    - `PRJ-800D` dashboard canonical convergence
    - `PRJ-864` dashboard canonical density pass
    - `PRJ-870` dashboard `99%` canonical evidence pass
    - `PRJ-875` canonical UI final route sweep
  - current dashboard truth points to:
    - `docs/ux/dashboard-proof-matrix.md`
    - `docs/ux/flagship-baseline-transfer.md`
    - `docs/ux/design-memory.md`
- validation:
  - reviewed PRJ-779 task history, dashboard convergence loop plan, dashboard
    proof matrix, design memory, and later board evidence
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - review `PRJ-780` for canonical sidebar/shell convergence planning status

## Fresh PRJ-776 Public Home And Shell Frame Closure (2026-05-03)

- `PRJ-776` is DONE:
  - `.codex/tasks/PRJ-776-implement-public-home-and-authenticated-shell-frame-pass.md`
- result:
  - the historical public-home/authenticated-shell frame task is no longer a
    stale `IN_PROGRESS` item
  - its original implementation is preserved as history, while the later
    `PRJ-782` correction remains active source of truth:
    - `WindowChrome` must not be revived
    - public and authenticated shells should remain premium and framed without
      fake browser controls
  - current shell-frame truth points to:
    - `docs/ux/design-memory.md`
    - `docs/ux/flagship-baseline-transfer.md`
    - `web/src/App.tsx`
    - `web/src/index.css`
- validation:
  - reviewed PRJ-776 task history, PRJ-782 board evidence, current shell code,
    design memory, and flagship baseline transfer
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - review `PRJ-779` for dashboard structural convergence status

## Fresh PRJ-743 Flagship Polish Lane Closure (2026-05-03)

- `PRJ-743` is DONE:
  - `.codex/tasks/PRJ-743-dashboard-chat-personality-canonical-polish-and-proof.md`
- result:
  - the historical dashboard/chat/personality canonical polish lane is no
    longer a stale `IN_PROGRESS` item
  - later proof and baseline owners now carry the active source of truth:
    - `docs/ux/flagship-baseline-transfer.md`
    - `docs/ux/dashboard-proof-matrix.md`
    - `docs/ux/personality-module-map.md`
    - `docs/ux/design-memory.md`
  - PRJ-875 remains the current final route-sweep proof anchor for the canonical
    UI package
  - remaining proof gaps stay explicit instead of being hidden in an old active
    task:
    - dashboard-specific tablet proof
    - personality tablet proof
    - consistently named keyboard traversal evidence
    - consistently named touch-target evidence
    - contrast/reduced-motion evidence for future changed routes
- validation:
  - reviewed PRJ-743 task history, design memory, dashboard proof matrix,
    personality module map, flagship baseline transfer, and PRJ-875 board proof
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - select the next READY task after excluding stale visual tasks already
    superseded by later canonical proof work

## Fresh Flagship Baseline Transfer Sync (2026-05-03)

- `PRJ-731` is DONE:
  - `.codex/tasks/PRJ-731-cross-module-proof-design-memory-update-and-future-app-baseline-sync.md`
- created:
  - `docs/ux/flagship-baseline-transfer.md`
- updated:
  - `docs/index.md`
  - `docs/README.md`
- result:
  - cross-module proof scope, design-memory sync rules, and future-app transfer
    expectations now live in one durable baseline note
  - current transferable UX sources are explicitly linked:
    - `docs/ux/design-memory.md`
    - `docs/ux/dashboard-proof-matrix.md`
    - `docs/ux/personality-module-map.md`
    - `docs/ux/canonical-web-screen-reference-set.md`
  - known proof gaps remain explicit instead of blocking the whole baseline
- validation:
  - reviewed design memory, dashboard proof matrix, personality module map, and
    PRJ-875/final route-sweep evidence in the task board
  - `git diff --check`
  - result: passed
- result:
  - PRJ-724 through PRJ-731 visual-system lane task-file drift is now closed or
    repaired with durable docs
- next smallest useful task:
  - return to the task board and select the next READY item outside the stale
    PRJ-724..PRJ-731 visual-system lane

## Fresh Personality Implementation Status Sync (2026-05-03)

- `PRJ-730` is DONE:
  - `.codex/tasks/PRJ-730-personality-module-implementation-on-shared-visual-foundations.md`
- result:
  - the stale `READY` implementation-planning task was closed against current
    route implementation reality
  - `web/src/App.tsx` already contains the `/personality` canvas,
    `PersonalityLayerCard`, `PersonalityTimelineRow`, callout pins, conscious
    and subconscious signal panels, timeline rows, and recent activity section
  - `web/src/index.css` already contains the `aion-personality-*` implementation
    and responsive styling
  - `docs/ux/personality-module-map.md` now records the reuse contract and
    known proof gaps
- validation:
  - reviewed personality module map, route code, CSS implementation, and later
    PRJ-865/PRJ-871 build/screenshot evidence
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - review `PRJ-731` for cross-module proof/design-memory/future-app baseline
    sync status

## Fresh Personality Module Map Repair (2026-05-03)

- `PRJ-729` is DONE:
  - `.codex/tasks/PRJ-729-freeze-personality-module-information-architecture-and-motif-mapping.md`
- created:
  - `docs/ux/personality-module-map.md`
- updated:
  - `docs/index.md`
  - `docs/README.md`
- result:
  - `/personality` IA, architecture-to-visual mapping, and shared-component
    reuse are now recorded in one durable map
  - the route remains tied to `GET /app/personality/overview`,
    `web/src/App.tsx`, `web/src/index.css`, and the shared dashboard/motif
    component language
  - known gaps are explicit: tablet-specific personality proof and future
    component extraction remain follow-up concerns, not hidden blockers
- validation:
  - reviewed personality planning direction, task-board history, current
    route code, and later PRJ-865/PRJ-871 canonical screenshot evidence
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - review `PRJ-730` for implementation status on shared visual foundations

## Fresh Dashboard Proof Matrix Repair (2026-05-03)

- `PRJ-728` is DONE:
  - `.codex/tasks/PRJ-728-dashboard-proof-across-states-accessibility-and-breakpoints.md`
- created:
  - `docs/ux/dashboard-proof-matrix.md`
- updated:
  - `docs/index.md`
  - `docs/README.md`
- result:
  - dashboard proof is now a durable matrix rather than scattered task-board
    notes
  - verified evidence is separated from `PARTIAL` and `GAP` rows
  - current dashboard local desktop/mobile proof is recorded, while
    dashboard-specific tablet, empty-state, keyboard traversal, touch-target,
    contrast, and reduced-motion gaps remain explicit
- validation:
  - reviewed screen-quality checklist, dashboard planning contract, task-board
    proof history, and local artifact paths
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - review `PRJ-729` for personality IA/motif mapping status before selecting
    the next implementation or sync slice

## Fresh Dashboard Continuity Sections Queue Sync (2026-05-03)

- `PRJ-727` is DONE:
  - `.codex/tasks/PRJ-727-dashboard-continuity-flow-and-module-entry-sections.md`
- result:
  - the stale `READY` task was closed against the existing dashboard continuity,
    cognitive-flow, and module-entry sections instead of adding duplicates
  - `web/src/App.tsx` already contains:
    - `ModuleEntryCard`
    - dashboard signal and guidance cards
    - dashboard cognitive-flow steps
    - dashboard goal, memory, reflection, and continuity sections
  - `docs/planning/dashboard-foundation-and-personality-visual-system-plan.md`
    already maps dashboard sections to shared component families
- validation:
  - verified continuity preview, cognitive-flow summary, and module-entry
    expectations in the planning contract
  - verified dashboard section ownership in `web/src/App.tsx`
  - verified historical board evidence that `PRJ-724..PRJ-727` were complete
    locally and that later dashboard proof exists
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - review `PRJ-728`, the next proof-oriented task after the completed
    PRJ-724..PRJ-727 implementation lane

## Fresh Authenticated Dashboard Shell Queue Sync (2026-05-03)

- `PRJ-726` is DONE:
  - `.codex/tasks/PRJ-726-authenticated-dashboard-shell-and-responsive-layout-foundation.md`
- result:
  - the stale `READY` task was closed against the existing authenticated shell
    and dashboard route instead of creating a parallel shell path
  - `web/src/App.tsx` already contains:
    - authenticated shell frame
    - shell navigation and utility bar
    - `/dashboard` route normalization
    - dashboard canvas with continuity and module-entry sections
  - `web/src/index.css` already carries the authenticated shell/dashboard
    responsive styling used by later canonical route passes
- validation:
  - verified dashboard section-order and responsive expectations in the
    planning contract
  - verified shell/dashboard ownership in `web/src/App.tsx` and
    `web/src/index.css`
  - verified historical board evidence that `PRJ-724..PRJ-727` were complete
    locally and that later dashboard/shell proof exists
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - review `PRJ-727` for the same stale READY/task-board drift before
    selecting new implementation work

## Fresh Shared Token Infrastructure Queue Sync (2026-05-03)

- `PRJ-725` is DONE:
  - `.codex/tasks/PRJ-725-shared-tokens-surfaces-and-motif-infrastructure.md`
- result:
  - the stale `READY` task was closed against existing shared token and motif
    infrastructure instead of creating a duplicate CSS primitive layer
  - `web/src/index.css` already contains the `--aion-*` token family and
    shared `.aion-panel*` surface primitives
  - `web/src/App.tsx` already reuses shared surface classes and route-level
    primitives such as `RouteHeroPanel`, `InsightPanel`, and `MotifFigurePanel`
  - `docs/planning/dashboard-foundation-and-personality-visual-system-plan.md`
    already excludes route-specific composition until after shared tokens and
    primitives
- validation:
  - verified token and primitive intent in the planning contract
  - verified shared motif-aware surfaces in CSS and web route components
  - verified historical board evidence that `PRJ-724..PRJ-727` were complete
    locally
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - review `PRJ-726` for the same stale READY/task-board drift before
    selecting new implementation work

## Fresh Dashboard Visual Contract Queue Sync (2026-05-03)

- `PRJ-724` is DONE:
  - `.codex/tasks/PRJ-724-freeze-dashboard-first-visual-system-and-component-contract.md`
- result:
  - the stale `READY` task was closed against the existing source-of-truth
    contract instead of creating a duplicate visual-system plan
  - the dashboard-first contract already lives in:
    - `docs/planning/dashboard-foundation-and-personality-visual-system-plan.md`
  - durable follow-on visual decisions are already recorded in:
    - `docs/ux/design-memory.md`
  - historical board evidence already stated `PRJ-724..PRJ-727` were complete
    locally
  - recurring stale-task selection guidance was recorded in:
    - `.codex/context/LEARNING_JOURNAL.md`
- validation:
  - verified first-motif priority, shared component families, and dashboard IA
    in the planning contract
  - verified later dashboard/shell patterns in design memory
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - review `PRJ-725` for the same stale READY/task-board drift before
    selecting new implementation work

## Fresh Mobile Foundation Scaffold (2026-05-03)

- `PRJ-668` is DONE:
  - `.codex/tasks/PRJ-668-build-initial-mobile-foundation-using-shared-client-contracts.md`
- created:
  - `mobile/package.json`
  - `mobile/app.json`
  - `mobile/tsconfig.json`
  - `mobile/expo-env.d.ts`
  - `mobile/app/_layout.tsx`
  - `mobile/app/index.tsx`
  - `mobile/src/api/shared-client-contract.ts`
  - `mobile/src/theme.ts`
- updated:
  - `mobile/README.md`
  - `docs/planning/mobile-client-baseline.md`
  - `docs/architecture/codebase-map.md`
  - `docs/README.md`
- validation:
  - package JSON parse passed
  - app JSON parse passed
  - shared endpoint coverage smoke passed
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - review current READY visual-system tasks before selecting the next slice

## Fresh Provider Specific Integration Docs (2026-05-03)

- `PRJ-950` is DONE:
  - `.codex/tasks/PRJ-950-provider-specific-integration-docs.md`
- created:
  - `docs/integrations/index.md`
- updated:
  - `docs/pipelines/tools.md`
  - `docs/index.md`
  - `docs/architecture/codebase-map.md`
  - `docs/architecture/traceability-matrix.md`
  - `docs/analysis/documentation-drift.md`
  - `docs/analysis/documentation-inventory.md`
  - `docs/planning/documentation-system-gap-repair-plan.md`
- validation:
  - connector policy operation coverage check passed
  - provider section coverage check passed
  - local markdown link check passed
  - `git diff --check`
  - result: passed
- result:
  - PRJ-945 documentation-system gap repair queue is complete at foundation
    level
- next smallest useful task:
  - commit PRJ-946 through PRJ-950 documentation repair lane after review

## Fresh Frontend Route And Component Map (2026-05-03)

- `PRJ-949` is DONE:
  - `.codex/tasks/PRJ-949-frontend-route-and-component-map.md`
- created:
  - `docs/frontend/route-component-map.md`
- updated:
  - `docs/architecture/codebase-map.md`
  - `docs/architecture/traceability-matrix.md`
  - `docs/index.md`
  - `docs/analysis/documentation-drift.md`
  - `docs/analysis/documentation-inventory.md`
  - `docs/planning/documentation-system-gap-repair-plan.md`
- validation:
  - route coverage check passed against `RoutePath` union and `ROUTES`
  - API client method coverage check passed
  - local markdown link check passed
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - `PRJ-950` Provider Specific Integration Docs

## Fresh Test Feature Pipeline Ownership Ledger (2026-05-03)

- `PRJ-948` is DONE:
  - `.codex/tasks/PRJ-948-test-feature-pipeline-ownership-ledger.md`
- created:
  - `docs/engineering/test-ownership-ledger.md`
- updated:
  - `docs/engineering/testing.md`
  - `docs/architecture/traceability-matrix.md`
  - `docs/index.md`
  - `docs/analysis/documentation-drift.md`
  - `docs/analysis/documentation-inventory.md`
  - `docs/planning/documentation-system-gap-repair-plan.md`
- validation:
  - traceability referenced-test coverage check passed
  - backend test file ledger coverage check passed
  - local markdown link check passed
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - `PRJ-949` Frontend Route And Component Map

## Fresh ERD And Column Model Reference (2026-05-03)

- `PRJ-947` is DONE:
  - `.codex/tasks/PRJ-947-erd-and-column-model-reference.md`
- created:
  - `backend/scripts/export_data_model_reference.py`
  - `docs/data/columns.md`
  - `docs/data/erd.mmd`
- updated:
  - `docs/data/index.md`
  - `docs/index.md`
  - `docs/analysis/documentation-drift.md`
  - `docs/analysis/documentation-inventory.md`
  - `docs/planning/documentation-system-gap-repair-plan.md`
- validation:
  - data model export command passed
  - generated artifact coverage check passed for `18` tables
  - local markdown link check passed
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - `PRJ-948` Test Feature Pipeline Ownership Ledger

## Fresh Generated OpenAPI Reference (2026-05-03)

- `PRJ-946` is DONE:
  - `.codex/tasks/PRJ-946-generated-openapi-reference.md`
- created:
  - `backend/scripts/export_openapi_schema.py`
  - `docs/api/openapi.json`
- updated:
  - `docs/api/index.md`
  - `docs/index.md`
  - `docs/analysis/documentation-drift.md`
  - `docs/analysis/documentation-inventory.md`
  - `docs/planning/documentation-system-gap-repair-plan.md`
- validation:
  - OpenAPI export command passed
  - OpenAPI schema shape check passed: `openapi=3.1.0`, `paths=18`,
    `info.title=AION MVP`
  - local markdown link check passed
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - `PRJ-947` ERD And Column Model Reference

## Fresh Documentation Gap Repair Queue (2026-05-03)

- `PRJ-945` is DONE:
  - `.codex/tasks/PRJ-945-documentation-gap-repair-queue.md`
  - `docs/planning/documentation-system-gap-repair-plan.md`
- queued:
  - `PRJ-946` Generated OpenAPI Reference - DONE
  - `PRJ-947` ERD And Column Model Reference - DONE
  - `PRJ-948` Test Feature Pipeline Ownership Ledger - DONE
  - `PRJ-949` Frontend Route And Component Map - DONE
  - `PRJ-950` Provider Specific Integration Docs - DONE
- validation:
  - local markdown link check passed
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - `PRJ-946` Generated OpenAPI Reference

## Fresh Tools Pipeline Reference (2026-05-03)

- `PRJ-944` is DONE:
  - `.codex/tasks/PRJ-944-tools-pipeline-reference.md`
- created:
  - `docs/pipelines/tools.md`
- updated:
  - `docs/index.md`
  - `docs/pipelines/index.md`
  - `docs/analysis/documentation-drift.md`
  - `docs/architecture/traceability-matrix.md`
- validation:
  - tools pipeline coverage check passed
  - local markdown link check passed
  - `git diff --check -- docs .codex/context/PROJECT_STATE.md .codex/context/TASK_BOARD.md .codex/tasks/PRJ-944-tools-pipeline-reference.md`
  - result: passed
- next smallest useful task:
  - add stable feature/pipeline IDs to tests or create a test ownership ledger

## Fresh Scheduler Proactive Pipeline Reference (2026-05-03)

- `PRJ-943` is DONE:
  - `.codex/tasks/PRJ-943-scheduler-proactive-pipeline-reference.md`
- created:
  - `docs/pipelines/scheduler-proactive.md`
- updated:
  - `docs/index.md`
  - `docs/pipelines/index.md`
  - `docs/analysis/documentation-drift.md`
  - `docs/architecture/traceability-matrix.md`
- validation:
  - scheduler/proactive coverage check passed
  - local markdown link check passed
  - `git diff --check -- docs .codex/context/PROJECT_STATE.md .codex/context/TASK_BOARD.md .codex/tasks/PRJ-943-scheduler-proactive-pipeline-reference.md`
  - result: passed
- next smallest useful task:
  - create a dedicated tools pipeline doc

## Fresh Organizer Provider Activation Smoke (2026-05-03)

- `PRJ-918` is BLOCKED:
  - `.codex/tasks/PRJ-918-organizer-provider-activation-smoke.md`
  - `docs/planning/v1-organizer-provider-activation-smoke.md`
- result:
  - live organizer provider smoke was not run because production still reports
    `provider_credentials_missing`
  - production currently reports `provider_ready_operation_count=0/5` and
    `daily_use_ready_workflow_count=0/3`
  - no provider secrets were changed or stored
- validation:
  - production `/health` organizer snapshot reviewed
  - `git diff --check`
- next smallest useful task:
  - `PRJ-920` Minimal External Health Monitor

## Fresh Deferred Reflection Pipeline Reference (2026-05-03)

- `PRJ-942` is DONE:
  - `.codex/tasks/PRJ-942-deferred-reflection-pipeline-reference.md`
- purpose:
  - split the background reflection queue and signal writer path into a
    dedicated pipeline doc
- created:
  - `docs/pipelines/deferred-reflection.md`
- updated:
  - `docs/index.md`
  - `docs/pipelines/index.md`
  - `docs/analysis/documentation-drift.md`
  - `docs/architecture/traceability-matrix.md`
- validation:
  - deferred reflection reference coverage check passed
  - local markdown link check passed
  - `git diff --check -- docs .codex/context/PROJECT_STATE.md .codex/context/TASK_BOARD.md .codex/tasks/PRJ-942-deferred-reflection-pipeline-reference.md`
  - result: passed
- next smallest useful task:
  - create a dedicated scheduler/proactive pipeline doc

## Fresh Organizer Provider Credential Activation Runbook (2026-05-03)

- `PRJ-917` is DONE:
  - `.codex/tasks/PRJ-917-organizer-provider-credential-activation-runbook.md`
  - `docs/planning/v1-organizer-provider-credential-activation-runbook.md`
  - `docs/operations/organizer-provider-activation-runbook.md`
- result:
  - production organizer health currently reports
    `provider_credentials_missing`, `provider_ready_operation_count=0`, and
    `daily_use_workflows_blocked_by_provider_activation`
  - ClickUp, Google Calendar, and Google Drive required settings, expected
    health transitions, smoke expectations, and rollback are documented
  - no provider secrets were changed or stored
- validation:
  - production `/health` organizer snapshot reviewed
  - `git diff --check`
- next smallest useful task:
  - `PRJ-918` Organizer Provider Activation Smoke, blocked until provider
    credentials are configured

## Fresh App Chat Pipeline Reference (2026-05-03)

- `PRJ-941` is DONE:
  - `.codex/tasks/PRJ-941-app-chat-pipeline-reference.md`
- purpose:
  - split the product-critical browser chat flow into a dedicated pipeline doc
    covering optimistic local UI state, backend runtime handoff, durable
    transcript projection, reconciliation, failure points, and tests
- created:
  - `docs/pipelines/app-chat.md`
- updated:
  - `docs/index.md`
  - `docs/pipelines/index.md`
  - `docs/analysis/documentation-drift.md`
  - `docs/architecture/traceability-matrix.md`
- validation:
  - app chat reference coverage check passed for frontend/API/runtime/repository
    terms
  - local markdown link check passed
  - `git diff --check -- docs .codex/context/PROJECT_STATE.md .codex/context/TASK_BOARD.md .codex/tasks/PRJ-941-app-chat-pipeline-reference.md`
  - result: passed
- remaining gaps:
  - dedicated frontend e2e tests for chat send/history UI
  - app chat sequence diagram
  - dedicated docs for long-message/markdown rendering behavior
- next smallest useful task:
  - create a dedicated deferred reflection pipeline doc

## Fresh Web Empty And Error State Audit (2026-05-03)

- `PRJ-916` is DONE:
  - `.codex/tasks/PRJ-916-web-empty-and-error-state-audit.md`
  - `docs/planning/v1-web-empty-and-error-state-audit.md`
- result:
  - authenticated route smoke passed for `/login` plus 12 authenticated routes
    on desktop and mobile
  - backend-down `/dashboard` mobile smoke passed without raw technical
    leakage or horizontal overflow
  - no runtime fix was required in this slice
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - bundled Node + Playwright authenticated route smoke
  - bundled Node + Playwright backend-down dashboard smoke
  - `git diff --check`
- next smallest useful task:
  - `PRJ-917` Organizer Provider Credential Activation Runbook

## Fresh Foreground Runtime Pipeline Reference (2026-05-03)

- `PRJ-940` is DONE:
  - `.codex/tasks/PRJ-940-foreground-runtime-pipeline-reference.md`
- purpose:
  - split the highest-risk pipeline registry entry into a dedicated foreground
    runtime reference grounded in `runtime.py`, `runtime_graph.py`, contracts,
    and runtime graph tests
- created:
  - `docs/pipelines/foreground-runtime.md`
- updated:
  - `docs/index.md`
  - `docs/pipelines/index.md`
  - `docs/analysis/documentation-drift.md`
  - `docs/architecture/traceability-matrix.md`
- validation:
  - stage-order coverage check passed for:
    `perception -> affective_assessment -> context -> motivation -> role -> planning -> expression -> action`
  - local markdown link check passed
  - `git diff --check -- docs .codex/context/PROJECT_STATE.md .codex/context/TASK_BOARD.md .codex/tasks/PRJ-940-foreground-runtime-pipeline-reference.md`
  - result: passed
- remaining gaps:
  - rendered sequence diagram
  - generated stage contract table from `backend/app/core/contracts.py`
  - dedicated app chat, reflection, scheduler/proactive, and tools pipeline docs
  - stable feature or pipeline IDs in tests
- next smallest useful task:
  - create a dedicated app chat pipeline doc

## Fresh Data Model Reference Foundation (2026-05-03)

- `PRJ-939` is DONE:
  - `.codex/tasks/PRJ-939-data-model-reference-foundation.md`
- purpose:
  - close the persistence-side documentation gap by mapping real ORM models,
    tables, migrations, repository capability groups, feature usage, tests, and
    data-change rules
- created:
  - `docs/data/index.md`
- updated:
  - `docs/index.md`
  - `docs/README.md`
  - `docs/analysis/documentation-inventory.md`
  - `docs/analysis/documentation-drift.md`
  - `docs/architecture/codebase-map.md`
  - `docs/architecture/traceability-matrix.md`
- validation:
  - model coverage check passed for 18 models
  - table coverage check passed for 18 tables
  - migration coverage check passed for 12 migrations
  - local markdown link check passed
  - `git diff --check -- docs .codex/context/PROJECT_STATE.md .codex/context/TASK_BOARD.md .codex/tasks/PRJ-939-data-model-reference-foundation.md`
  - result: passed
- remaining gaps:
  - generated ERD
  - column-by-column model reference
  - exhaustive migration-to-column mapping
  - one-by-one repository method reference
- next smallest useful task:
  - split the highest-risk pipeline registry entries into dedicated pipeline
    docs, starting with foreground runtime

## Fresh Backend-Backed Dashboard Summary Surface (2026-05-03)

- `PRJ-915` is DONE:
  - `.codex/tasks/PRJ-915-backend-backed-dashboard-summary-surface.md`
  - `docs/planning/v1-backend-backed-dashboard-summary-surface.md`
- result:
  - dashboard goal rows, memory bars, reflection rows, and current phase now
    derive from existing runtime overview/tool data instead of fixed demo
    values
  - removed fixed `72%`, `58%`, `41%`, `33%`, and weekday fake memory history
    claims from `/dashboard`
  - focused `/dashboard` desktop/mobile smoke passed with no failures and no
    unexpected console issues
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - bundled Node + Playwright focused dashboard summary smoke
  - `git diff --check`
- next smallest useful task:
  - `PRJ-916` Web Empty And Error State Audit

## Fresh API Reference Foundation (2026-05-03)

- `PRJ-938` is DONE:
  - `.codex/tasks/PRJ-938-api-reference-foundation.md`
- purpose:
  - close the first PRJ-937 follow-up by creating a dedicated API reference
    from real FastAPI routes, Pydantic schemas, and the web API client
- created:
  - `docs/api/index.md`
- updated:
  - `docs/index.md`
  - `docs/README.md`
  - `docs/analysis/documentation-inventory.md`
  - `docs/analysis/documentation-drift.md`
  - `docs/architecture/codebase-map.md`
  - `docs/architecture/traceability-matrix.md`
- validation:
  - all 18 verified backend routes from `backend/app/api/routes.py`, including
    dynamic route constants, are present in `docs/api/index.md`
  - local markdown link check passed
  - `git diff --check -- docs .codex/context/PROJECT_STATE.md .codex/context/TASK_BOARD.md .codex/tasks/PRJ-938-api-reference-foundation.md`
  - result: passed
- remaining gaps:
  - generated OpenAPI artifact or richer per-endpoint examples
  - deeper shape docs for flexible `extra="allow"` overview responses
  - dedicated event/debug payload contract reference
  - test endpoint IDs or ownership metadata
- next smallest useful task:
  - create `docs/data/index.md` with model/table/migration/repository mapping

## Fresh Replace Static Personality Metrics (2026-05-03)

- `PRJ-914` is DONE:
  - `.codex/tasks/PRJ-914-replace-static-personality-metrics.md`
  - `docs/planning/v1-replace-static-personality-metrics.md`
- result:
  - Personality clarity, energy, load, focus, intuition, role, and skills
    values now derive from existing `/app/personality/overview` data where
    they imply runtime truth
  - removed fixed `87%`, `Strong`, and fallback `18` skills claims
  - the focused `/personality` desktop/mobile smoke passed with no failures
    and no unexpected console issues
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - bundled Node + Playwright focused Personality metrics smoke
  - `git diff --check`
- next smallest useful task:
  - `PRJ-915` Backend-Backed Dashboard Summary Surface

## Fresh Documentation System Map Foundation (2026-05-03)

- `PRJ-937` is DONE:
  - `.codex/tasks/PRJ-937-documentation-system-map-foundation.md`
- purpose:
  - convert the existing human-readable documentation into the first
    engineering traceability foundation without rewriting canonical
    architecture
- created:
  - `docs/index.md`
  - `docs/analysis/documentation-inventory.md`
  - `docs/analysis/documentation-drift.md`
  - `docs/architecture/codebase-map.md`
  - `docs/architecture/traceability-matrix.md`
  - `docs/pipelines/index.md`
  - `docs/modules/index.md`
  - `docs/CONTRIBUTING-DOCS.md`
- updated:
  - `docs/README.md`
- validation:
  - documentation file existence check passed
  - local markdown link check passed
  - `git diff --check -- docs .codex/tasks/PRJ-937-documentation-system-map-foundation.md`
  - result: passed
- remaining gaps:
  - dedicated API reference
  - dedicated data/model and migration reference
  - deeper per-pipeline docs for foreground runtime, app chat, reflection,
    scheduler/proactive, and tools
  - stable feature or pipeline IDs in tests
- next smallest useful task:
  - create `docs/api/index.md` from `backend/app/api/routes.py`,
    `backend/app/api/schemas.py`, and `web/src/lib/api.ts`

## Fresh Web V1 Route Smoke After Release Candidate (2026-05-03)

- `PRJ-913` is DONE:
  - `.codex/tasks/PRJ-913-web-v1-route-smoke-after-release-candidate.md`
  - `docs/planning/v1-web-route-smoke-after-release-candidate.md`
- result:
  - web build passed
  - local backend `/health` was green during the smoke
  - route smoke passed for `/login` plus 12 authenticated routes on desktop
    and mobile:
    - `routeChecks=24`
    - `failures=0`
    - `unexpectedConsoleIssueCount=0`
    - `benignConsoleIssueCount=2`
    - `screenshots=8`
  - `/tools` mobile overflow was fixed in `web/src/index.css`
  - in-app browser plugin was blocked by local Node version; bundled Node +
    Playwright fallback was used
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - bundled Node + Playwright route smoke
  - `git diff --check`
- next smallest useful task:
  - `PRJ-914` Replace Remaining Static Personality Metrics

## Fresh Production Telegram Mode Smoke (2026-05-03)

- `PRJ-909` is BLOCKED:
  - `.codex/tasks/PRJ-909-production-telegram-mode-smoke.md`
  - `docs/planning/v1-production-telegram-mode-smoke.md`
- result:
  - production Telegram health is green:
    - `round_trip_state=provider_backed_ready`
    - `bot_token_configured=true`
    - `webhook_secret_configured=true`
    - `delivery_failures=0`
  - live Telegram listen probe was not run because the local operator session
    does not have `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, or a known
    `REQUIRED_CHAT_ID`
  - no Telegram API mutation was performed and the production webhook was not
    changed from this session
- validation:
  - production `/health` reviewed on 2026-05-03
  - `git diff --check` passed
- next smallest useful task:
  - continue with `PRJ-931` AI red-team pack or web-v1 route smoke unless the
    Telegram operator preconditions are supplied

## Fresh V1 Data Privacy And Debug Posture Check (2026-05-02)

- `PRJ-912` is DONE:
  - `.codex/tasks/PRJ-912-v1-data-privacy-and-debug-posture-check.md`
  - `docs/planning/v1-data-privacy-and-debug-posture-check.md`
- result:
  - core no-UI v1 privacy/debug posture is GO
  - production reports `event_debug_enabled=false`
  - query debug compatibility is disabled
  - auth/reset/transcript boundary regressions passed
  - public-launch AI/security hardening remains HOLD until `PRJ-931..PRJ-933`
- validation:
  - focused backend tests passed with `23 passed, 96 deselected`
  - production health snapshot captured locally at
    `.codex/artifacts/prj912-health-snapshot.json`
  - health snapshot scan found setting names and policy hints, not secret
    values
- next smallest useful task:
  - run `PRJ-909` production Telegram mode smoke if Telegram is the primary
    launch channel, otherwise continue to `PRJ-931` AI red-team pack

## Fresh V1 Rollback And Recovery Drill (2026-05-02)

- `PRJ-911` is DONE:
  - `.codex/tasks/PRJ-911-v1-rollback-and-recovery-drill.md`
  - `docs/planning/v1-rollback-and-recovery-drill.md`
- result:
  - rollback target and previous known-good SHA are recorded
  - migration posture is explicit:
    - Alembic head `20260426_0012`
  - Coolify rollback and recovery smoke steps are documented
  - strict-mode incident-evidence export is the rollback triage path; full
    debug payload exposure is not required
- validation:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m alembic -c alembic.ini heads; Pop-Location`
  - result: `20260426_0012 (head)`
  - `git diff --check` passed
- next smallest useful task:
  - run `PRJ-912` data privacy and debug posture check

## Fresh Final V1 Acceptance Refresh (2026-05-02)

- `PRJ-923` is DONE:
  - `.codex/tasks/PRJ-923-final-v1-acceptance-refresh.md`
- result:
  - core no-UI v1 is GO for production revision
    `0984440a8a2a283942e4aa2c190e3964d0dadc9c`
  - production deploy parity is GO
  - strict-mode incident evidence is GO
  - public/web-led launch marker remains on HOLD until launch-channel,
    rollback, privacy/debug, and AI/security hardening gates are complete or
    explicitly waived
- production evidence:
  - strict-mode bundle:
    `.codex/artifacts/prj923-final-v1-acceptance/20260502T220616Z_prj923-final-v1-acceptance-0984440`
  - release smoke with `-IncidentEvidenceBundlePath` passed
- next smallest useful task:
  - run `PRJ-909` production Telegram mode smoke if Telegram is the primary
    launch channel, otherwise run `PRJ-911` rollback/recovery

## Fresh V1 Queue Renumbering Cleanup (2026-05-02)

- `PRJ-929` is DONE:
  - `.codex/tasks/PRJ-929-v1-queue-renumbering-cleanup.md`
- result:
  - completed `PRJ-922` remains the production-safe incident-evidence export
    task
  - the older future Deployment Trigger SLO Evidence slot was moved to
    `PRJ-930`
  - AI/security/final-release future tasks were shifted to `PRJ-931..PRJ-936`
    so task IDs are unique before final v1 execution continues
- validation:
  - searched planning/context files for `PRJ-922`
  - `git diff --check` passed
- next smallest useful task:
  - run final v1 acceptance refresh against the latest production SHA and
    strict-mode incident bundle

## Fresh Production-Safe Incident Evidence Export (2026-05-02)

- `PRJ-922` is DONE:
  - `.codex/tasks/PRJ-922-production-safe-incident-evidence-export.md`
- result:
  - incident bundle export no longer requires enabling full debug payload
    access in strict production
  - `backend/scripts/export_incident_evidence_bundle.py` falls back to
    `/health` policy surfaces only when `/internal/event/debug` returns the
    expected disabled-debug `403`
  - invalid-token and unrelated HTTP failures still fail closed
- production evidence:
  - bundle export succeeded with
    `incident_evidence_source=health_snapshot_strict_mode`
  - bundle path:
    `.codex/artifacts/prj922-production-safe-incident-evidence/20260502T213839Z_prj922-strict-production-evidence-08dda30`
  - release smoke with `-IncidentEvidenceBundlePath` passed
  - deployed revision:
    `08dda306b554d55183d7cd675bc0f9aaf95480a5`
- validation:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_observability_policy.py tests/test_incident_evidence_bundle_script.py tests/test_deployment_trigger_scripts.py; Pop-Location`
  - result: `60 passed`
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q; Pop-Location`
  - result: `1021 passed`
- next smallest useful task:
  - refresh the final v1 acceptance/declaration now that the PRJ-908 evidence
    blocker has a passing strict-mode production bundle

## Fresh Core V1 Acceptance Bundle (2026-05-02)

- `PRJ-910` is DONE:
  - `.codex/tasks/PRJ-910-core-v1-acceptance-bundle.md`
  - `docs/planning/v1-core-acceptance-bundle.md`
- result:
  - core no-UI v1 behavior is GO
  - production deploy parity is GO
  - final v1 release declaration remains NO-GO until PRJ-908 is resolved or
    explicitly waived by a documented release decision
- current evaluated production revision:
  - `0e0929670fb669a94dd52498129147ef11281d66`
- evidence:
  - PRJ-905 backend tests passed with `1019 passed`
  - PRJ-905 web build passed
  - PRJ-905 behavior validation passed with `19 passed, 209 deselected`
  - production release smoke passed with deploy parity
  - production health snapshot was captured locally at
    `.codex/artifacts/prj910-health-snapshot.json`
- next smallest useful task:
  - implement or approve a production-safe incident-evidence export path, then
    rerun final acceptance; otherwise continue to PRJ-911/PRJ-912 with the
    PRJ-908 blocker explicit

## Fresh Production Incident Evidence Bundle Blocker (2026-05-02)

- `PRJ-908` is BLOCKED:
  - `.codex/tasks/PRJ-908-production-incident-evidence-bundle.md`
  - `docs/planning/v1-production-incident-evidence-bundle.md`
- result:
  - canonical production bundle export failed because `/internal/event/debug`
    returns `403` when production debug payload access is disabled
  - a user-approved temporary Coolify debug window was attempted
  - production strict policy rejected `EVENT_DEBUG_ENABLED=true` by leaving the
    runtime unhealthy during the redeploy
  - `EVENT_DEBUG_ENABLED=false` was restored
  - the user reported Coolify-side token cleanup complete
  - the local debug-token artifact was deleted
- restoration validation:
  - production `/health` returned to `event_debug_enabled=false`
  - production `/health` returned to `release_readiness.ready=true`
  - release smoke passed with deploy parity for
    `948e7f6245c9dd4c5e767e0c8b840223b141cfa4`
- next smallest useful task:
  - either create a production-safe incident-evidence export route, or continue
    to `PRJ-910` with PRJ-908 recorded as a blocked evidence gap

## Fresh V1 Candidate Publish (2026-05-02)

- `PRJ-906` is DONE:
  - `.codex/tasks/PRJ-906-publish-v1-candidate.md`
  - `docs/planning/v1-publish-candidate.md`
- publish result:
  - validated candidate `582b146cdd89a488acc6bcebee4c00a7c418d108` was pushed
    to `origin/main`
  - push output: `5372d33..582b146 main -> main`
- release posture:
  - published to remote, but not production-green until PRJ-907 release smoke
    passes with deploy parity
- next smallest useful task:
  - start `PRJ-907` Production Release Smoke With Deploy Parity

## Fresh V1 Candidate Validation Gate (2026-05-02)

- `PRJ-905` is DONE:
  - `.codex/tasks/PRJ-905-v1-candidate-validation-gate.md`
  - `docs/planning/v1-candidate-validation-gate.md`
- candidate head:
  - `463ad04bc147c1284d0f1e12b4d5ff0cabec6fa1`
- validation:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q; Pop-Location`
  - result: passed, `1019 passed`
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `Push-Location .\backend; ..\.venv\Scripts\python .\scripts\run_behavior_validation.py --gate-mode operator --artifact-path ..\.codex\artifacts\prj905-v1-candidate-validation\behavior-validation-report.json; Pop-Location`
  - result: passed, `19 passed, 209 deselected`
  - `git diff --check`
  - result: passed
- artifact:
  - `.codex/artifacts/prj905-v1-candidate-validation/behavior-validation-report.json`
- remaining local-only output:
  - `artifacts/behavior_validation/prj843-report.json`
- next smallest useful task:
  - `PRJ-906` is complete; continue with `PRJ-907` Production Release Smoke
    With Deploy Parity

## Fresh V1 Commit Scope Audit (2026-05-02)

- `PRJ-904` is DONE:
  - `.codex/tasks/PRJ-904-v1-commit-scope-audit.md`
  - `docs/planning/v1-commit-scope-audit.md`
- candidate scope:
  - base: `origin/main` at `5372d33a4fd132bc6280bb781642eb3ce55fbfdc`
  - head: `350250fa7ee737863f72cdeb6c876d7fc39e17e1`
  - local branch posture before PRJ-904 commit: `main` was ahead of
    `origin/main` by 2 commits
  - included: canonical UI/localization baseline, backend-backed recent
    activity, v1 audit, release boundary, task/context records
  - excluded: `artifacts/behavior_validation/prj843-report.json` and generated
    local evidence artifacts
- validation:
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - `PRJ-905` is complete; continue with `PRJ-906` Publish V1 Candidate

## Fresh Current V1 Release Boundary (2026-05-02)

- `PRJ-903` is DONE:
  - `.codex/tasks/PRJ-903-freeze-current-v1-release-boundary.md`
  - `docs/planning/current-v1-release-boundary.md`
- release boundary:
  - core `v1` remains the no-UI life-assistant bundle:
    conversation reliability, learned-state inspection, bounded website
    reading, tool-grounded learning, time-aware planned work, and production
    deploy parity
  - current web shell and canonical route work are included in the candidate as
    a product-facing surface, but only with build, route-smoke, and deployed
    revision-parity evidence
  - organizer providers, richer daily-use workflows, multimodal Telegram,
    mobile/Expo restart, and external observability are extension gates unless
    explicitly promoted by a future scope decision
  - production smoke, incident evidence, rollback/recovery, privacy/debug
    posture, and AI red-team evidence remain queued hardening/release gates
- validation:
  - `git diff --check`
  - result: passed
- next smallest useful task:
  - `PRJ-904` is complete; continue with `PRJ-905` V1 Candidate Validation Gate

## Fresh V1 Release Audit And Execution Plan (2026-05-02)

- `PRJ-902` is DONE as a detailed v1 audit and execution plan:
  - `.codex/tasks/PRJ-902-v1-release-audit-and-execution-plan.md`
  - `docs/planning/v1-release-audit-and-execution-plan.md`
- purpose:
  - identify everything blocking `v1` from being a release fact and translate
    it into a sequenced P0/P1/P2 queue
- current audit result:
  - core no-UI v1 behavior is locally strong
  - fresh behavior validation passed with `19 passed, 209 deselected`
  - current local tree is not release-clean and cannot be declared production
    v1 until scope is selected, validated, committed, pushed, and smoked
  - production parity evidence is stale for the current local product state
  - organizer provider activation, external observability, AI red-team
    evidence, and remaining web static/decorative values are planned as
    explicit follow-up lanes instead of hidden blockers
- validation:
  - `Push-Location .\backend; ..\.venv\Scripts\python .\scripts\run_behavior_validation.py --gate-mode operator --artifact-path ..\.codex\artifacts\prj902-v1-audit\behavior-validation-report.json; Pop-Location`
  - result: passed, `19 passed, 209 deselected`
  - evidence:
    - `.codex/artifacts/prj902-v1-audit/behavior-validation-report.json`
- new priority queue:
  - `PRJ-903` Freeze Current V1 Release Boundary
  - `PRJ-904` V1 Commit Scope Audit
  - `PRJ-905` V1 Candidate Validation Gate
  - `PRJ-906` Publish V1 Candidate
  - `PRJ-907` Production Release Smoke With Deploy Parity
  - `PRJ-908` Production Incident Evidence Bundle
  - `PRJ-909` Production Telegram Mode Smoke
  - `PRJ-910` Core V1 Acceptance Bundle
  - `PRJ-911` V1 Rollback And Recovery Drill
  - `PRJ-912` V1 Data Privacy And Debug Posture Check
- next smallest useful task:
  - `PRJ-903` is complete; continue with `PRJ-904` V1 Commit Scope Audit

## Fresh Real Recent Activity Surface (2026-05-02)

- `PRJ-901` is DONE as a small product-usability vertical slice:
  - `.codex/tasks/PRJ-901-real-recent-activity-surface.md`
- purpose:
  - replace static/demo recent activity with real persisted activity wherever
    the existing Personality overview contract can safely provide it
- implemented:
  - `/app/personality/overview` now includes a user-scoped `recent_activity`
    list built from existing episodic memory records
  - overview activity is sanitized to `event_id`, `title`, `timestamp`,
    `source`, and bounded `importance`; raw memory payloads are not exposed
  - Dashboard, Memory, Reflections, and Personality recent-activity panels now
    prefer backend activity and fall back to localized static rows when needed
- validation:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py -k personality_overview; Pop-Location`
  - result: passed, `1 passed, 118 deselected`
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q; Pop-Location`
  - result: passed, `1019 passed`
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
- deployment impact:
  - low; authenticated app overview response gains an additive extra field and
    the web shell consumes it defensively
- next smallest useful task:
  - continue replacing route-local static summaries with backend-backed state
    where approved contracts already exist

## Fresh Localized Module Copy Final Reaudit (2026-05-02)

- `PRJ-899` is DONE as a final localized module-copy reaudit:
  - `.codex/tasks/PRJ-899-localized-module-copy-final-reaudit.md`
- purpose:
  - verify targeted route-owned English copy after PRJ-891 through PRJ-898
- validation:
  - Chrome CDP Polish module-copy reaudit across `/memory`, `/reflections`,
    `/plans`, `/goals`, `/insights`, `/automations`, `/integrations`, and
    `/tools`
  - result: passed after PRJ-900 fixed the remaining Memory zero-count form
  - no checked route had horizontal overflow at 390px mobile width
  - evidence:
    - `.codex/artifacts/prj899-localized-module-copy-final-reaudit/localized-module-copy-final-reaudit.json`
    - `.codex/artifacts/prj899-localized-module-copy-final-reaudit/pl-final-reaudit-last-route.png`
- findings:
  - targeted route-owned localization gaps are closed for the checked module
    routes
  - provider/API-owned English values may remain by design
- deployment impact:
  - none; audit and documentation only
- next smallest useful task:
  - move from localization closure to the next product-usability slice, likely
    replacing static/demo activity with real persisted activity where the
    backend contract already supports it

## Fresh Memory Zero Count Polish Forms (2026-05-02)

- `PRJ-900` is DONE as a TESTER grammar fix:
  - `.codex/tasks/PRJ-900-memory-zero-count-polish-forms.md`
- purpose:
  - fix the remaining `/memory` zero-count Polish form found by PRJ-899
- implemented:
  - Memory pattern, insight, and cue unit labels now have zero-count suffixes
    in `UI_COPY.memory`
  - Polish Memory now renders `0 wzorców`, `0 wniosków`, and `0 sygnałów`
    instead of rough plural forms
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - PRJ-899 final localized module-copy reaudit
  - result: passed
- deployment impact:
  - low; frontend-only copy/grammar fix

## Fresh Tools Route-Owned Copy Localization (2026-05-02)

- `PRJ-898` is DONE as a focused Tools route-owned localization fix:
  - `.codex/tasks/PRJ-898-tools-route-owned-copy-localization.md`
- purpose:
  - localize `/tools` UI-owned copy while preserving provider/API-owned values
- implemented:
  - Tools summary notes, directory title, item count labels, status labels,
    provider readiness labels, link-state labels, Telegram linking helper copy,
    expiry copy, and Tools toast/error fallbacks now read from `UI_COPY.tools`
  - provider/API-owned fields such as group titles, item labels, descriptions,
    status reasons, capabilities, and source-of-truth strings remain unchanged
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - Chrome CDP Polish `/tools` route-owned copy smoke with a mocked app API
    snapshot
  - result: passed; no horizontal overflow at 390px mobile width
  - evidence:
    - `.codex/artifacts/prj898-tools-route-owned-copy-localization/pl-tools-route-owned-copy-smoke.json`
    - `.codex/artifacts/prj898-tools-route-owned-copy-localization/pl-tools-route-owned-copy-mobile.png`
- deployment impact:
  - low; frontend-only route-owned copy refactor, no backend, DB, auth,
    scheduler, provider, or action-layer changes
- next smallest useful task:
  - run a fresh localized module-copy reaudit to confirm whether route-owned
    localization gaps remain

## Fresh Shared Recent Activity Localization (2026-05-02)

- `PRJ-897` is DONE as an ARCHITECT shared-copy cleanup:
  - `.codex/tasks/PRJ-897-shared-recent-activity-localization.md`
- purpose:
  - remove the shared English recent-activity rows from localized module
    surfaces
- implemented:
  - shared recent-activity rows now live in `UI_COPY.common.recentActivity`
    for English, Polish, and German
  - Dashboard, Memory, Reflections, and Personality now consume the localized
    shared activity list
  - the shared Personality activity action label now uses `UI_COPY.common.view`
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - Chrome CDP Polish shared activity smoke across `/dashboard`, `/memory`,
    `/reflections`, and `/personality`
  - result: passed; no horizontal overflow at 390px mobile width
  - evidence:
    - `.codex/artifacts/prj897-shared-recent-activity-localization/pl-shared-recent-activity-smoke.json`
    - `.codex/artifacts/prj897-shared-recent-activity-localization/pl-memory-shared-activity-scrolled.png`
- deployment impact:
  - low; frontend-only shared-copy refactor, no backend, DB, auth, scheduler,
    provider, or action-layer changes
- next smallest useful task:
  - run a narrow `/tools` ownership pass to separate route-owned copy from
    provider/data-owned English values

## Fresh Reflections Body Copy Localization (2026-05-02)

- `PRJ-896` is DONE as a focused localized Reflections body-copy fix:
  - `.codex/tasks/PRJ-896-reflections-body-copy-localization.md`
- purpose:
  - remove route-owned English body copy from the Polish Reflections surface
- implemented:
  - Reflections stat details, status labels, flow labels, prompt cards, and
    recent-movement header now read from `UI_COPY.reflections`
  - visible Reflections insight counts now handle the Polish zero form
    (`0 wniosków`) instead of the rough plural fallback
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - Chrome CDP Polish Reflections copy smoke with a mocked app API snapshot
  - result: passed; no horizontal overflow at 390px mobile width
  - evidence:
    - `.codex/artifacts/prj896-reflections-body-copy-localization/pl-reflections-copy-smoke.json`
    - `.codex/artifacts/prj896-reflections-body-copy-localization/pl-reflections-mobile.png`
- deployment impact:
  - low; frontend-only localization refactor, no backend, DB, auth, scheduler,
    provider, or action-layer changes
- next smallest useful task:
  - localize shared recent-activity entries used by Memory and Reflections, or
    run a narrow `/tools` ownership pass to separate route-owned copy from
    provider/data-owned English values

## Fresh Localized Module Copy Reaudit (2026-05-02)

- `PRJ-895` is DONE as a TESTER reaudit:
  - `.codex/tasks/PRJ-895-localized-module-copy-reaudit.md`
- purpose:
  - confirm remaining localized module-copy gaps after PRJ-891 through PRJ-894
- validation:
  - Chrome CDP Polish module copy reaudit across `/memory`, `/reflections`,
    `/plans`, `/goals`, `/insights`, `/automations`, `/integrations`, and
    `/tools`
  - result: passed; no checked route had horizontal overflow
  - evidence:
    - `.codex/artifacts/prj895-localized-module-copy-reaudit/localized-module-copy-reaudit.json`
- findings:
  - `/reflections` is now the highest-impact remaining route-owned body-copy
    localization task
  - `/plans`, `/goals`, `/insights`, `/automations`, and `/integrations` are
    clean for the targeted route-owned English signals
  - `/memory` still shows shared recent-activity English entries
  - `/tools` still has mixed route-owned and provider/data-owned English values
- deployment impact:
  - none; audit and documentation only
- next smallest useful task:
  - localize `/reflections` route-owned body copy

## Fresh Goals Body Copy Localization (2026-05-02)

- `PRJ-894` is DONE as a focused localized Goals body-copy fix:
  - `.codex/tasks/PRJ-894-goals-body-copy-localization.md`
- purpose:
  - remove route-owned English body copy from the Polish Goals surface
- implemented:
  - Goals stat details, horizon labels, goal rows, signal cards, and guidance
    rows now read from `UI_COPY.goals`
  - visible Goals count units and direction text now handle `1 cel` correctly
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - Chrome CDP Polish Goals copy smoke
  - result: passed
  - evidence:
    - `.codex/artifacts/prj894-goals-body-copy-localization/pl-goals-copy-smoke.json`
    - `.codex/artifacts/prj894-goals-body-copy-localization/pl-goals-mobile.png`
- deployment impact:
  - low; frontend-only localization refactor, no backend, DB, auth, scheduler,
    provider, or action-layer changes
- next smallest useful task:
  - localize `/reflections` route-owned body copy or rerun a fresh localized
    route audit to confirm remaining gaps

## Fresh Plans Body Copy Localization (2026-05-02)

- `PRJ-893` is DONE as a focused localized Plans body-copy fix:
  - `.codex/tasks/PRJ-893-plans-body-copy-localization.md`
- purpose:
  - remove route-owned English body copy from the Polish Plans surface
- implemented:
  - Plans stat details, planning path labels, flow rows, next-step cards, and
    context cards now read from `UI_COPY.plans`
  - visible Plans count units now use localized singular/plural labels
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - Chrome CDP Polish Plans copy smoke
  - result: passed
  - evidence:
    - `.codex/artifacts/prj893-plans-body-copy-localization/pl-plans-copy-smoke.json`
    - `.codex/artifacts/prj893-plans-body-copy-localization/pl-plans-mobile.png`
- deployment impact:
  - low; frontend-only localization refactor, no backend, DB, auth, scheduler,
    provider, or action-layer changes
- next smallest useful task:
  - localize `/goals` route-owned body copy

## Fresh Memory Body Copy Localization (2026-05-02)

- `PRJ-892` is DONE as a focused localized Memory body-copy fix:
  - `.codex/tasks/PRJ-892-memory-body-copy-localization.md`
- purpose:
  - remove route-owned English body copy from the Polish Memory surface
- implemented:
  - Memory stat details, map labels, continuity rows, and signal cards now read
    from `UI_COPY.memory`
  - visible Memory count units now use localized singular/plural labels
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - Chrome CDP Polish Memory copy smoke
  - result: passed
  - evidence:
    - `.codex/artifacts/prj892-memory-body-copy-localization/pl-memory-copy-smoke-v2.json`
    - `.codex/artifacts/prj892-memory-body-copy-localization/pl-memory-mobile-v2.png`
- findings:
  - shared recent-activity entries remain English and need a separate shared
    localization slice
- deployment impact:
  - low; frontend-only localization refactor, no backend, DB, auth, scheduler,
    provider, or action-layer changes
- next smallest useful task:
  - localize `/plans` and `/goals` route-owned body copy

## Fresh Insights Body Copy Localization (2026-05-02)

- `PRJ-891` is DONE as a focused localized Insights body-copy fix:
  - `.codex/tasks/PRJ-891-insights-body-copy-localization.md`
- purpose:
  - remove the highest-impact route-owned English body copy identified by
    PRJ-890 from the Polish Insights surface
- implemented:
  - Insights stat details, map labels, signal rows, clarity notes, and guidance
    candidates now read from `UI_COPY.insights`
  - visible Insights count units now avoid the `1 cele` grammar issue
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - Chrome CDP Polish Insights copy smoke
  - result: passed
  - evidence:
    - `.codex/artifacts/prj891-insights-body-copy-localization/pl-insights-copy-smoke-v2.json`
    - `.codex/artifacts/prj891-insights-body-copy-localization/pl-insights-mobile-v2.png`
- deployment impact:
  - low; frontend-only localization refactor, no backend, DB, auth, scheduler,
    provider, or action-layer changes
- next smallest useful task:
  - localize `/memory`, `/plans`, and `/goals` route-owned body copy

## Fresh Localized Module Copy Audit (2026-05-02)

- `PRJ-890` is DONE as a TESTER audit:
  - `.codex/tasks/PRJ-890-localized-module-copy-audit.md`
- purpose:
  - rank remaining localized module routes that still show route-owned English
    body copy in Polish UI mode
- validation:
  - Chrome CDP Polish module copy audit across `/memory`, `/reflections`,
    `/plans`, `/goals`, `/insights`, and `/tools`
  - result: passed; no checked route had horizontal overflow
  - evidence:
    - `.codex/artifacts/prj890-localized-module-copy-audit/localized-module-copy-audit.json`
- findings:
  - `/insights` has the highest observed route-owned English copy debt
  - `/memory`, `/plans`, and `/goals` also need copy-localization slices
  - `/tools` still shows English details, but some are provider or data-owned
    and need separate ownership decisions
- deployment impact:
  - none; audit and documentation only
- next smallest useful task:
  - localize `/insights` route-owned body copy

## Fresh Automations Body Copy Localization (2026-05-02)

- `PRJ-889` is DONE as a focused localized Automations body-copy fix:
  - `.codex/tasks/PRJ-889-automations-body-copy-localization.md`
- purpose:
  - remove route-owned English body copy from the Polish Automations surface
    without introducing a new localization system
  - keep backend health status and error strings data-owned and out of scope
- implemented:
  - Automations stat details, flow headers, flow rows, boundary cards, and
    health detail labels now read from `UI_COPY.automations`
  - English, Polish, and German copy keys were added to the existing UI copy
    structure
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - Chrome CDP Polish Automations copy smoke
  - result: passed
  - evidence:
    - `.codex/artifacts/prj889-automations-body-copy-localization/pl-automations-copy-smoke.json`
    - `.codex/artifacts/prj889-automations-body-copy-localization/pl-automations-mobile.png`
- deployment impact:
  - low; frontend-only localization refactor, no backend, DB, auth, scheduler,
    provider, or action-layer changes
- next smallest useful task:
  - localize the next module route with route-owned English body copy

## Fresh Integrations Body Copy Localization (2026-05-02)

- `PRJ-888` is DONE as a focused localized Integrations body-copy fix:
  - `.codex/tasks/PRJ-888-integrations-body-copy-localization.md`
- purpose:
  - remove route-owned English body copy from the Polish Integrations surface
    without introducing a new localization system
  - keep provider-owned `status_reason` values data-owned and out of scope
- implemented:
  - Integrations stat details, provider-map labels, boundary cards, and
    readiness detail labels now read from `UI_COPY.integrations`
  - English, Polish, and German copy keys were added to the existing UI copy
    structure
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - Chrome CDP Polish Integrations copy smoke
  - result: passed
  - evidence:
    - `.codex/artifacts/prj888-integrations-body-copy-localization/pl-integrations-copy-smoke-v3.json`
    - `.codex/artifacts/prj888-integrations-body-copy-localization/pl-integrations-mobile-v3.png`
- deployment impact:
  - low; frontend-only localization refactor, no backend, DB, auth, provider,
    scheduler, or action-layer changes
- next smallest useful task:
  - localize the next highest-visibility module body copy surfaced by the
    localized route smoke

## Fresh Localized Shell Route Smoke (2026-05-02)

- `PRJ-887` is DONE as a localized shell route smoke:
  - `.codex/tasks/PRJ-887-localized-shell-route-smoke.md`
- purpose:
  - verify Polish authenticated shell behavior after PRJ-886 changed module
    labels to use `routeLabel`
  - confirm representative desktop/mobile routes remain nonblank,
    non-overflowing, and exception-free
- scoped routes:
  - `/dashboard`
  - `/chat`
  - `/integrations`
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - Chrome CDP localized shell smoke
  - result: passed, 6 checks
  - evidence:
    - `.codex/artifacts/prj887-localized-shell-route-smoke/localized-shell-smoke-results-v2.json`
    - `.codex/artifacts/prj887-localized-shell-route-smoke/dashboard-desktop-v2.png`
    - `.codex/artifacts/prj887-localized-shell-route-smoke/chat-mobile-v2.png`
    - `.codex/artifacts/prj887-localized-shell-route-smoke/integrations-mobile-v2.png`
- findings:
  - mobile `/chat` intentionally does not render the mobile tabbar, so the
    localized tabbar label assertion is not applied to that route/viewport
  - some newly added module body copy remains English in localized views and
    should be handled as a separate copy-localization slice
- deployment impact:
  - none; verification and documentation only
- next smallest useful task:
  - localize newly added module body copy where it remains English

## Fresh Sidebar Localized Module Labels (2026-05-02)

- `PRJ-886` is DONE as a canonical shell localization fix:
  - `.codex/tasks/PRJ-886-sidebar-localized-module-labels.md`
- purpose:
  - make newly enabled module labels use existing `UI_COPY.routes`
    localization instead of English literals
  - keep desktop sidebar and mobile tabbar consistent with selected UI language
- implemented:
  - Memory, Reflections, Plans, Goals, Insights, Automations, and Integrations
    now use `routeLabel(route, resolvedUiLanguage)` in `shellNavItems`
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - Chrome CDP Polish sidebar smoke
  - result: passed
  - `git diff --check -- web/src/App.tsx .codex/tasks/PRJ-886-sidebar-localized-module-labels.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
  - result: passed with line-ending warnings only
  - evidence:
    - `.codex/artifacts/prj886-sidebar-localized-module-labels/pl-sidebar-smoke-v2.json`
    - `.codex/artifacts/prj886-sidebar-localized-module-labels/pl-dashboard-sidebar-desktop-v2.png`
- deployment impact:
  - low; frontend-only localization consistency fix, no backend, DB, auth,
    provider, scheduler, or action-layer changes
- next smallest useful task:
  - rerun final route smoke only if more shell navigation changes are made

## Fresh Canonical UI Commit Scope Audit (2026-05-02)

- `PRJ-885` is DONE as the refreshed canonical UI commit scope audit:
  - `.codex/tasks/PRJ-885-canonical-ui-commit-scope-audit.md`
- purpose:
  - classify the working tree after the canonical route rollout and final sweep
  - prevent unrelated untracked artifacts from entering the UI commit
- tracked changed files:
  - `.codex/context/PROJECT_STATE.md`
  - `.codex/context/TASK_BOARD.md`
  - `web/src/App.tsx`
  - `web/src/index.css`
- canonical UI task records to include:
  - `.codex/tasks/PRJ-864-dashboard-canonical-density-pass.md` through
    `.codex/tasks/PRJ-885-canonical-ui-commit-scope-audit.md`
- separate inclusion decision:
  - `.codex/tasks/PRJ-851-publish-and-smoke-release-smoke-summary.md`
  - `.codex/tasks/PRJ-852-chat-canonical-97-parity-closure.md`
- exclude unless explicitly requested:
  - `artifacts/behavior_validation/prj843-report.json`
- validation:
  - `git diff --name-only`
  - `git ls-files --others --exclude-standard`
  - `git diff --stat -- web/src/App.tsx web/src/index.css .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- deployment impact:
  - none; release-scope audit only
- next smallest useful task:
  - stage, commit, and push the canonical UI package only if explicitly
    requested

## Fresh Canonical Route Final Sweep (2026-05-02)

- `PRJ-884` is DONE as the canonical route final sweep:
  - `.codex/tasks/PRJ-884-canonical-route-final-sweep.md`
- purpose:
  - verify the authenticated route set after the canonical module rollout
  - catch blank routes, authenticated redirects, mobile overflow, or JavaScript
    exceptions before commit-scope preparation
- scoped routes:
  - `/dashboard`, `/chat`, `/personality`, `/memory`, `/reflections`, `/plans`,
    `/goals`, `/insights`, `/automations`, `/integrations`, `/tools`,
    `/settings`
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - Chrome CDP final route smoke
  - result: passed, 24 route/viewport checks
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-884-canonical-route-final-sweep.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
  - result: passed with line-ending warnings only
  - evidence:
    - `.codex/artifacts/prj884-canonical-route-final-sweep/route-smoke-results.json`
    - `.codex/artifacts/prj884-canonical-route-final-sweep/dashboard-desktop.png`
    - `.codex/artifacts/prj884-canonical-route-final-sweep/chat-mobile.png`
    - `.codex/artifacts/prj884-canonical-route-final-sweep/integrations-mobile.png`
- deployment impact:
  - none; verification and documentation only
- next smallest useful task:
  - prepare a commit scope audit for the canonical UI package

## Fresh Integrations Canonical Route (2026-05-02)

- `PRJ-883` is DONE as the Integrations canonical route slice:
  - `.codex/tasks/PRJ-883-integrations-canonical-route.md`
- purpose:
  - promote `Integrations` from a disabled authenticated sidebar entry to a
    first-class canonical route
  - reuse existing `/app/tools/overview` provider readiness and link state data
    instead of adding provider calls, backend, or fake data paths
  - keep Integrations read-only and preserve Tools as the place for toggles and
    link flows
- implemented:
  - `/integrations` is now part of `RoutePath`, route normalization, desktop
    sidebar, and mobile tabbar navigation
  - Integrations participates in the existing tools overview fetch path
  - the route renders a canonical overview bar, stat cards, provider map,
    provider rows, connection rules, and readiness details
  - CSS is route-scoped with responsive desktop/mobile behavior
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-883-integrations-canonical-route.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
  - result: passed with line-ending warnings only
  - Chrome CDP screenshot evidence:
    - `.codex/artifacts/prj883-integrations-canonical-route/integrations-desktop-1568x1003-v2.png`
    - `.codex/artifacts/prj883-integrations-canonical-route/integrations-mobile-390x844-v2.png`
- deployment impact:
  - low; frontend-only route enablement and layout, no backend, DB, auth, env,
    provider, link-flow, or action-layer changes
- next smallest useful task:
  - run a final canonical route sweep and prepare the commit scope

## Fresh Automations Canonical Route (2026-05-02)

- `PRJ-882` is DONE as the Automations canonical route slice:
  - `.codex/tasks/PRJ-882-automations-canonical-route.md`
- purpose:
  - promote `Automations` from a disabled authenticated sidebar entry to a
    first-class canonical route
  - reuse existing `/app/me` proactive settings and `/health` attention /
    scheduler data instead of adding scheduler APIs, backend, or fake data paths
  - keep Automations read-only and preserve action boundaries
- implemented:
  - `/automations` is now part of `RoutePath`, route normalization, desktop
    sidebar, and mobile tabbar navigation
  - Automations participates in the existing health fetch path
  - the route renders a canonical overview bar, stat cards, switchboard, flow
    rows, guardrail notes, and health details
  - CSS is route-scoped with responsive desktop/mobile behavior
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-882-automations-canonical-route.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
  - result: passed with line-ending warnings only
  - Chrome CDP screenshot evidence:
    - `.codex/artifacts/prj882-automations-canonical-route/automations-desktop-1568x1003-v1.png`
    - `.codex/artifacts/prj882-automations-canonical-route/automations-mobile-390x844-v1.png`
- deployment impact:
  - low; frontend-only route enablement and layout, no backend, DB, auth, env,
    scheduler, or action-layer changes
- next smallest useful task:
  - implement Integrations as the next separate canonical module slice

## Fresh Insights Canonical Route (2026-05-02)

- `PRJ-881` is DONE as the Insights canonical route slice:
  - `.codex/tasks/PRJ-881-insights-canonical-route.md`
- purpose:
  - promote `Insights` from a disabled authenticated sidebar entry to a
    first-class canonical route
  - reuse existing `/app/personality/overview` knowledge, planning, and
    dashboard guidance data instead of adding analytics, backend, or fake data
    paths
  - keep Insights as read-only sensemaking, separate from Reflections and
    action surfaces
- implemented:
  - `/insights` is now part of `RoutePath`, route normalization, desktop
    sidebar, and mobile tabbar navigation
  - Insights participates in the existing overview fetch path
  - the route renders a canonical overview bar, stat cards, insight map,
    signal rows, clarity notes, and guidance candidates
  - CSS is route-scoped with responsive desktop/mobile behavior
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-881-insights-canonical-route.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
  - result: passed with line-ending warnings only
  - Chrome CDP screenshot evidence:
    - `.codex/artifacts/prj881-insights-canonical-route/insights-desktop-1568x1003-v2.png`
    - `.codex/artifacts/prj881-insights-canonical-route/insights-mobile-390x844-v2.png`
- deployment impact:
  - low; frontend-only route enablement and layout, no backend, DB, auth, env,
    action-layer, analytics, or runtime insight contract changes
- next smallest useful task:
  - implement Automations as the next separate canonical module slice

## Fresh Goals Canonical Route (2026-05-02)

- `PRJ-880` is DONE as the Goals canonical route slice:
  - `.codex/tasks/PRJ-880-goals-canonical-route.md`
- purpose:
  - promote `Goals` from a disabled authenticated sidebar entry to a
    first-class canonical route
  - reuse existing `/app/personality/overview` planning summary and dashboard
    goal rows instead of adding a backend, editor, action layer, or fake data
    path
  - keep Goals as a direction/progress surface, separate from Plans/action
- implemented:
  - `/goals` is now part of `RoutePath`, route normalization, desktop sidebar,
    and mobile tabbar navigation
  - Goals participates in the existing overview fetch path
  - the route renders a canonical overview bar, stat cards, goal horizon rings,
    progress list, signal cards, and guidance list
  - CSS is route-scoped with responsive desktop/mobile behavior
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-880-goals-canonical-route.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
  - result: passed with line-ending warnings only
  - Chrome CDP screenshot evidence:
    - `.codex/artifacts/prj880-goals-canonical-route/goals-desktop-1568x1003-v1.png`
    - `.codex/artifacts/prj880-goals-canonical-route/goals-mobile-390x844-v1.png`
- deployment impact:
  - low; frontend-only route enablement and layout, no backend, DB, auth, env,
    action-layer, or runtime goal contract changes
- next smallest useful task:
  - implement Insights as the next separate canonical module slice

## Fresh Plans Canonical Route (2026-05-02)

- `PRJ-879` is DONE as the Plans canonical route slice:
  - `.codex/tasks/PRJ-879-plans-canonical-route.md`
- purpose:
  - promote `Plans` from a disabled authenticated sidebar entry to a
    first-class canonical route
  - reuse existing `/app/personality/overview` planning summary data instead of
    adding a backend, editor, action layer, or fake data path
  - preserve the action boundary by keeping Plans as a read/guidance surface
- implemented:
  - `/plans` is now part of `RoutePath`, route normalization, desktop sidebar,
    and mobile tabbar navigation
  - Plans now participates in the existing overview fetch path
  - the route renders a canonical overview bar, summary stat cards, planning
    board, flow rows, next-step suggestions, and context list
  - CSS is route-scoped with responsive desktop/mobile behavior
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-879-plans-canonical-route.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
  - result: passed with line-ending warnings only
  - Chrome CDP screenshot evidence:
    - `.codex/artifacts/prj879-plans-canonical-route/plans-desktop-1568x1003-v1.png`
    - `.codex/artifacts/prj879-plans-canonical-route/plans-mobile-390x844-v1.png`
- deployment impact:
  - low; frontend-only route enablement and layout, no backend, DB, auth, env,
    action-layer, or runtime planning contract changes
- next smallest useful task:
  - implement Goals as the next separate canonical module slice

## Fresh Reflections Canonical Route (2026-05-02)

- `PRJ-878` is DONE as the Reflections canonical route slice:
  - `.codex/tasks/PRJ-878-reflections-canonical-route.md`
- purpose:
  - promote `Reflections` from a disabled authenticated sidebar entry to a
    first-class canonical route
  - reuse existing `/app/personality/overview` display data instead of adding a
    backend, worker, or fake data path
  - continue the canonical module rollout one route at a time
- implemented:
  - `/reflections` is now part of `RoutePath`, route normalization, desktop
    sidebar, and mobile tabbar navigation
  - Reflections now participates in the existing overview fetch path
  - the route renders a canonical overview bar, summary stat cards, process
    flow, prompt cards, and recent movement list
  - CSS is route-scoped with responsive desktop/mobile behavior
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-878-reflections-canonical-route.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
  - result: passed with line-ending warnings only
  - Chrome CDP screenshot evidence:
    - `.codex/artifacts/prj878-reflections-canonical-route/reflections-desktop-1568x1003-v1.png`
    - `.codex/artifacts/prj878-reflections-canonical-route/reflections-mobile-390x844-v1.png`
- deployment impact:
  - low; frontend-only route enablement and layout, no backend, DB, auth, env,
    reflection worker, or runtime contract changes
- next smallest useful task:
  - implement the next disabled module route as a separate canonical slice,
    likely Plans

## Fresh Memory Canonical Route (2026-05-02)

- `PRJ-877` is DONE as the Memory canonical route slice:
  - `.codex/tasks/PRJ-877-memory-canonical-route.md`
- purpose:
  - promote `Memory` from a disabled authenticated sidebar entry to a
    first-class canonical route
  - reuse existing `/app/personality/overview` display data instead of adding a
    backend or fake data path
  - continue the canonical route rollout one module at a time
- implemented:
  - `/memory` is now part of `RoutePath`, route normalization, desktop sidebar,
    and mobile tabbar navigation
  - Memory now participates in the existing overview fetch path
  - the route renders a canonical overview bar, summary stat cards, a continuity
    map, signal cards, and recent movement list
  - CSS is route-scoped with responsive desktop/mobile behavior
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-877-memory-canonical-route.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
  - result: passed with line-ending warnings only
  - Chrome CDP screenshot evidence:
    - `.codex/artifacts/prj877-memory-canonical-route/memory-desktop-1568x1003-v2.png`
    - `.codex/artifacts/prj877-memory-canonical-route/memory-mobile-390x844-v2.png`
- deployment impact:
  - low; frontend-only route enablement and layout, no backend, DB, auth, env,
    or runtime memory contract changes
- next smallest useful task:
  - implement the next disabled module route as a separate canonical slice,
    likely Reflections

## Fresh Canonical UI Commit Scope Audit (2026-05-02)

- `PRJ-876` is DONE as the canonical UI commit scope audit:
  - `.codex/tasks/PRJ-876-canonical-ui-commit-scope-audit.md`
- purpose:
  - record the exact canonical UI commit candidate after PRJ-875
  - avoid accidentally staging unrelated artifacts during the next commit
  - complete an ARCHITECT-mode release-scope slice for iteration `876`
- findings:
  - tracked changed files are:
    - `.codex/context/PROJECT_STATE.md`
    - `.codex/context/TASK_BOARD.md`
    - `web/src/App.tsx`
    - `web/src/index.css`
  - untracked canonical UI task files are PRJ-864 through PRJ-876
  - `.codex/artifacts/` screenshot evidence is intentionally ignored by
    `.gitignore`
  - `artifacts/behavior_validation/prj843-report.json` is untracked and should
    stay out of the canonical UI commit unless explicitly requested
  - `.codex/tasks/PRJ-851-publish-and-smoke-release-smoke-summary.md` and
    `.codex/tasks/PRJ-852-chat-canonical-97-parity-closure.md` predate this
    canonical UI package and should not be included without a separate decision
- validation:
  - `git diff --name-only`
  - `git ls-files --others --exclude-standard`
  - `git diff --stat -- web/src/App.tsx web/src/index.css .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- deployment impact:
  - none; release-scope documentation only
- next smallest useful task:
  - create a selective commit for the canonical UI package when requested

## Fresh Canonical UI Final Route Sweep (2026-05-02)

- `PRJ-875` is DONE as the canonical UI final route sweep:
  - `.codex/tasks/PRJ-875-canonical-ui-final-route-sweep.md`
- purpose:
  - verify the refreshed public/private canonical route package as one coherent
    commit candidate
  - check `/`, `/dashboard`, `/chat`, `/personality`, `/settings`, and `/tools`
    after the PRJ-869 through PRJ-874 UI slices
  - keep the iteration in TESTER mode for route evidence and regression focus
- implemented:
  - captured Chrome CDP screenshot evidence for the primary route set on
    desktop and mobile
  - corrected the mobile chat composer so the text input receives a full row
    and compact controls move beneath it
  - no backend, DB, env, auth, API, or runtime behavior changed
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-875-canonical-ui-final-route-sweep.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
  - result: passed with line-ending warnings only
  - Chrome CDP screenshot evidence:
    - `.codex/artifacts/prj875-canonical-ui-final-route-sweep/public-home-unauth-desktop-1568x1003-v2.png`
    - `.codex/artifacts/prj875-canonical-ui-final-route-sweep/public-home-unauth-mobile-390x844-v2.png`
    - `.codex/artifacts/prj875-canonical-ui-final-route-sweep/dashboard-desktop-1568x1003.png`
    - `.codex/artifacts/prj875-canonical-ui-final-route-sweep/dashboard-mobile-390x844.png`
    - `.codex/artifacts/prj875-canonical-ui-final-route-sweep/chat-desktop-1568x1003.png`
    - `.codex/artifacts/prj875-canonical-ui-final-route-sweep/chat-mobile-full-390x844-v3.png`
    - `.codex/artifacts/prj875-canonical-ui-final-route-sweep/personality-desktop-1568x1003.png`
    - `.codex/artifacts/prj875-canonical-ui-final-route-sweep/personality-mobile-390x844.png`
    - `.codex/artifacts/prj875-canonical-ui-final-route-sweep/settings-desktop-1568x1003.png`
    - `.codex/artifacts/prj875-canonical-ui-final-route-sweep/settings-mobile-390x844.png`
    - `.codex/artifacts/prj875-canonical-ui-final-route-sweep/tools-desktop-1568x1003.png`
    - `.codex/artifacts/prj875-canonical-ui-final-route-sweep/tools-mobile-390x844.png`
- deployment impact:
  - low; frontend-only verification and route-scoped mobile chat composer CSS
    refinement
- next smallest useful task:
  - create a selective commit for the canonical UI package when requested

## Fresh Tools Canonical Directory Polish (2026-05-02)

- `PRJ-874` is DONE as the tools canonical directory polish pass:
  - `.codex/tasks/PRJ-874-tools-canonical-directory-polish.md`
- purpose:
  - finish the main private route set before commit readiness
  - align `/tools` with the current AION canonical shell/material language
    after the settings polish pass
  - preserve existing tool overview data, toggles, Telegram linking, next
    steps, and technical details
- implemented:
  - tool groups and item cards now use route-scoped canonical classes instead
    of generic heavy card blocks
  - item facts compress into a four-column desktop row and a one-column mobile
    stack
  - current status, next step, and technical details are quieter while staying
    visible
  - the mobile tools route header is compressed like settings and personality
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-874-tools-canonical-directory-polish.md`
  - result: passed with line-ending warnings only
  - Chrome CDP screenshot evidence:
    - `.codex/artifacts/prj874-tools-canonical-directory-polish/tools-desktop-before-1568x1003.png`
    - `.codex/artifacts/prj874-tools-canonical-directory-polish/tools-mobile-before-390x844.png`
    - `.codex/artifacts/prj874-tools-canonical-directory-polish/tools-desktop-after-1568x1003-v1.png`
    - `.codex/artifacts/prj874-tools-canonical-directory-polish/tools-mobile-after-390x844-v1.png`
- deployment impact:
  - low; frontend-only tools layout refinement, no backend, DB, env, auth,
    tool execution, or runtime behavior changed
- next smallest useful task:
  - run a final route sweep and prepare a clean commit candidate

## Fresh Settings Canonical Shell Polish (2026-05-02)

- `PRJ-873` is DONE as the settings canonical shell polish pass:
  - `.codex/tasks/PRJ-873-settings-canonical-shell-polish.md`
- purpose:
  - bring `/settings` into the same canonical AION material language as the
    refreshed home, dashboard, chat, and personality surfaces
  - reduce generic form-grid feel while preserving existing save/reset
    behavior and API contracts
  - complete an ARCHITECT-mode utility-route consistency slice for iteration
    `873`
- implemented:
  - the route hero was replaced with a compact settings overview bar using the
    established canonical route rhythm
  - profile, interface language, UTC offset, and conversation language now live
    in one cohesive preferences panel
  - proactive follow-ups, ready-to-save, and reset runtime data now live in a
    supporting side stack
  - the reset panel is still explicit but less visually dominant, with the
    existing exact confirmation phrase preserved
  - mobile settings header is compressed like personality, reducing first
    viewport height
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-873-settings-canonical-shell-polish.md`
  - result: passed with line-ending warnings only
  - Chrome CDP screenshot evidence:
    - `.codex/artifacts/prj873-settings-canonical-shell-polish/settings-desktop-before-1568x1003.png`
    - `.codex/artifacts/prj873-settings-canonical-shell-polish/settings-mobile-before-390x844.png`
    - `.codex/artifacts/prj873-settings-canonical-shell-polish/settings-desktop-after-1568x1003-v2.png`
    - `.codex/artifacts/prj873-settings-canonical-shell-polish/settings-mobile-after-390x844-v2.png`
- deployment impact:
  - low; frontend-only settings layout refinement, no backend, DB, env, auth,
    reset contract, or runtime behavior changed
- next smallest useful task:
  - prepare a commit candidate or continue lower-priority route polish if the
    product review calls for it

## Fresh Chat 99 Canonical Evidence Pass (2026-05-02)

- `PRJ-872` is DONE as the chat `99%` canonical evidence pass:
  - `.codex/tasks/PRJ-872-chat-99-canonical-evidence-pass.md`
- purpose:
  - refresh `/chat` evidence after the shared shell, home, dashboard, and
    personality 99% passes
  - align the route against
    `docs/ux/assets/aion-chat-canonical-reference-v5.png`
  - preserve the existing two-column conversation/persona model, code-native
    controls, and real route data flow
- implemented:
  - the persona column now carries desktop canonical support notes for memory
    continuity, expression, and channel context
  - note anchors were repositioned to match the right-side annotated portrait
    rhythm of the v5 reference
  - mobile remains intentionally simpler because the portrait notes stay hidden
    below desktop widths
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-872-chat-99-canonical-evidence-pass.md`
  - result: passed with line-ending warnings only
  - Chrome CDP screenshot evidence:
    - `.codex/artifacts/prj872-chat-99-canonical-evidence-pass/chat-desktop-before-1568x1003.png`
    - `.codex/artifacts/prj872-chat-99-canonical-evidence-pass/chat-mobile-before-390x844.png`
    - `.codex/artifacts/prj872-chat-99-canonical-evidence-pass/chat-desktop-after-1568x1003-v1.png`
    - `.codex/artifacts/prj872-chat-99-canonical-evidence-pass/chat-mobile-after-390x844-v1.png`
- deployment impact:
  - low; frontend-only chat visual refinement, no backend, DB, env, auth, or
    runtime behavior changed
- next smallest useful task:
  - prepare a clean commit candidate after reviewing the accumulated local
    canonical UI stack, or continue lower-priority route polish if requested

## Fresh Personality 99 Canonical Pass (2026-05-02)

- `PRJ-871` is DONE as the personality `99%` canonical pass:
  - `.codex/tasks/PRJ-871-personality-99-canonical-pass.md`
- purpose:
  - continue the renewed `99%` canonical lane after public home and dashboard
  - align `/personality` against
    `docs/ux/assets/aion-personality-canonical-reference-v1.png`
  - preserve the current AION canonical shell/sidebar, route data flow, and
    existing personality raster asset
- implemented:
  - the personality overview bar is lighter and less visually dominant
  - the hero stage, callouts, role card, timeline, and side panels are denser
    and closer to the reference first-viewport rhythm
  - mobile personality presentation now uses a route-specific compressed header
    and shorter stage so the embodied scene ends at the fixed tabbar boundary
  - the skills callout now reads the real nested
    `role_skill_state.skill_summary.skill_count` value before falling back
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-871-personality-99-canonical-pass.md`
  - result: passed with line-ending warnings only
  - Chrome CDP screenshot evidence:
    - `.codex/artifacts/prj871-personality-99-canonical-pass/personality-desktop-before-1568x1003.png`
    - `.codex/artifacts/prj871-personality-99-canonical-pass/personality-mobile-before-390x844.png`
    - `.codex/artifacts/prj871-personality-99-canonical-pass/personality-desktop-after-1568x1003-v2.png`
    - `.codex/artifacts/prj871-personality-99-canonical-pass/personality-mobile-after-390x844-v3.png`
- deployment impact:
  - low; frontend-only personality visual/data-read refinement, no backend,
    DB, env, auth, or runtime behavior changed
- next smallest useful task:
  - continue the `99%` canonical lane with the next dependent route or prepare
    a commit/push when the user asks

## Fresh Dashboard 99 Canonical Evidence Pass (2026-05-02)

- `PRJ-870` is DONE as the dashboard `99%` canonical evidence pass:
  - `.codex/tasks/PRJ-870-dashboard-99-canonical-evidence-pass.md`
- purpose:
  - close the dashboard surface after public home, using TESTER-mode screenshot
    evidence for iteration `870`
  - compare `/dashboard` against
    `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`
  - apply only evidence-backed polish needed for first-viewport parity
- implemented:
  - dashboard hero/stage density was tightened so flow and lower modules begin
    earlier in the viewport
  - cognitive-flow panel, phase card, step typography, and step controls were
    compacted toward the canonical rhythm
  - summary balance rows now use a stable label/value grid without visible
    overlap or vertical word splitting
  - no private shell toolbar regression was introduced
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-870-dashboard-99-canonical-evidence-pass.md`
  - result: passed with line-ending warnings only
  - Chrome CDP screenshot evidence:
    - `.codex/artifacts/prj870-dashboard-99-canonical-evidence-pass/dashboard-desktop-viewport-before-1568x1003.png`
    - `.codex/artifacts/prj870-dashboard-99-canonical-evidence-pass/dashboard-desktop-before-1568x1003.png`
    - `.codex/artifacts/prj870-dashboard-99-canonical-evidence-pass/dashboard-mobile-before-390x844.png`
    - `.codex/artifacts/prj870-dashboard-99-canonical-evidence-pass/dashboard-desktop-viewport-after-1568x1003-v3.png`
    - `.codex/artifacts/prj870-dashboard-99-canonical-evidence-pass/dashboard-desktop-after-1568x1003-v3.png`
    - `.codex/artifacts/prj870-dashboard-99-canonical-evidence-pass/dashboard-mobile-after-390x844-v2.png`
- deployment impact:
  - low; frontend dashboard CSS-only visual change
- next smallest useful task:
  - start the personality `99%` canonical route pass

## Fresh Public Home Landing 99 Canonical Pass (2026-05-02)

- `PRJ-869` is DONE as the focused public home/landing `99%` canonical pass:
  - `.codex/tasks/PRJ-869-public-home-landing-99-pass.md`
- purpose:
  - close the public home surface after `PRJ-868` established the shared shell
    foundation
  - align desktop landing with
    `docs/ux/assets/aion-landing-canonical-reference-v1.png`
  - preserve mobile readability and public auth behavior
- implemented:
  - historical note: this slice originally rendered desktop public home inside
    a browser-window frame with chrome, address bar, rounded border, shadow,
    and top `Landing Page` tag
  - 2026-05-03 supersession:
    - browser/mockup chrome in canonical images is preview context and must be
      ignored in implementation
    - current public home uses the chrome-free landing shell from `PRJ-782`
  - first-viewport hero, feature bridge, proof bridge, and trust band now sit
    in one framed composition closer to the approved reference
  - mobile keeps the native full-width flow for readability
  - public auth modal no longer starts with a technical `/app/me` bootstrap
    error before user action
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-869-public-home-landing-99-pass.md`
  - result: passed with line-ending warnings only
  - Chrome CDP screenshot evidence:
    - `.codex/artifacts/prj869-public-home-landing-99-pass/landing-desktop-before-1568x1003.png`
    - `.codex/artifacts/prj869-public-home-landing-99-pass/landing-mobile-before-390x844.png`
    - `.codex/artifacts/prj869-public-home-landing-99-pass/landing-desktop-after-1568x1003-v3.png`
    - `.codex/artifacts/prj869-public-home-landing-99-pass/landing-mobile-after-390x844-v2.png`
    - `.codex/artifacts/prj869-public-home-landing-99-pass/landing-auth-modal-mobile-390x844-v2.png`
- deployment impact:
  - low; frontend public landing visual and public bootstrap-error presentation
    only
- next smallest useful task:
  - start the dashboard `99%` canonical route pass

## Fresh Canonical 99 Layout Foundation (2026-05-02)

- `PRJ-868` is DONE as the shared public/private shell foundation for the
  renewed `99%` canonical program:
  - `.codex/tasks/PRJ-868-canonical-99-layout-foundation.md`
- purpose:
  - restart the canonical sequence from shared layout before route-specific
    work on public home, dashboard, and personality
  - remove remaining authenticated toolbar drift from non-canonicalized routes
  - make mobile private navigation readable without duplicated route rows
- implemented:
  - the authenticated desktop route toolbar is hidden globally
  - mobile private-shell bottom spacing now accounts for the fixed tabbar
  - the duplicated phone header route row is hidden below `md`
  - the phone bottom tabbar is compact enough to show Dashboard, Chat,
    Personality, Tools, and Settings without clipped labels
  - the active mobile tab has deterministic centering support when overflow is
    present
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-868-canonical-99-layout-foundation.md`
  - result: passed with line-ending warnings only
  - Chrome CDP screenshot evidence:
    - `.codex/artifacts/prj868-canonical-99-layout-foundation/settings-mobile-390x844-viewport-v7.png`
    - `.codex/artifacts/prj868-canonical-99-layout-foundation/settings-mobile-390x844-v7.png`
    - `.codex/artifacts/prj868-canonical-99-layout-foundation/settings-desktop-1568x1003-v4.png`
    - `.codex/artifacts/prj868-canonical-99-layout-foundation/dashboard-desktop-1568x1003-v4.png`
    - `.codex/artifacts/prj868-canonical-99-layout-foundation/landing-mobile-390x844.png`
  - latest mobile metrics:
    - `bodyWidth=390`, `viewportWidth=390`, `visibleToolbar=0`,
      `headerRouteRowDisplay=none`, `scrollWidth=366`, `clientWidth=366`
- deployment impact:
  - low; frontend shell/layout change only
- next smallest useful task:
  - start the public home/landing `99%` canonical route pass on this foundation

## Fresh Tools Canonical Shell Consistency Pass (2026-05-02)

- `PRJ-867` is DONE as the focused Tools shell-consistency slice:
  - `.codex/tasks/PRJ-867-tools-canonical-shell-consistency-pass.md`
- purpose:
  - align `/tools` with the canonical shell language even though Tools is not
    frozen by a dedicated canonical screenshot
  - remove repeated large heading/summary layers from the first viewport
  - preserve the existing tool catalog, controls, details, and Telegram linking
- implemented:
  - Tools now hides the extra desktop route toolbar like other canonicalized
    shell routes
  - duplicate route hero and summary panels were replaced with one compact
    operational overview bar
  - the detailed route section is now presented as a tool directory
  - summary cards reuse the AION material language without changing API data
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-867-tools-canonical-shell-consistency-pass.md`
  - result: passed with line-ending warnings only
  - Playwright Chromium screenshot evidence:
    - `.codex/artifacts/prj867-tools-canonical-shell-pass/desktop-1568x1003-v2.png`
    - `.codex/artifacts/prj867-tools-canonical-shell-pass/mobile-390x844-v2.png`
    - `.codex/artifacts/prj867-tools-canonical-shell-pass/settings-smoke-1568x1003.png`
- deployment impact:
  - low; frontend visual composition change only
- next smallest useful task:
  - polish Settings under the same canonical material language

## Fresh Landing Canonical First Viewport Pass (2026-05-02)

- `PRJ-866` is DONE as the focused public Landing first-viewport slice:
  - `.codex/tasks/PRJ-866-landing-canonical-first-viewport-pass.md`
- purpose:
  - bring the public Landing route closer to
    `docs/ux/assets/aion-landing-canonical-reference-v1.png`
  - improve first-viewport framing without changing public auth behavior,
    current copy, or the existing landing hero art asset
- implemented:
  - hero copy now sits inward from the left viewport edge and higher in the
    first viewport
  - hero title/body and CTA rhythm were tuned for a stronger public-entry read
  - feature/proof bridge now begins earlier on desktop
  - mobile proof bridge overlap was reduced so it no longer covers the final
    hero note
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check -- web/src/index.css .codex/tasks/PRJ-866-landing-canonical-first-viewport-pass.md`
  - result: passed with line-ending warnings only
  - Playwright Chromium screenshot evidence:
    - `.codex/artifacts/prj866-landing-canonical-pass/desktop-1568x1003-v3.png`
    - `.codex/artifacts/prj866-landing-canonical-pass/mobile-390x844-v3.png`
    - `.codex/artifacts/prj866-landing-canonical-pass/auth-modal-390x844-v3.png`
- deployment impact:
  - low; frontend CSS-only visual framing change
- next smallest useful task:
  - continue with non-frozen route polish or pause to resolve the local commit
    stack before pushing

## Fresh Personality Canonical First Viewport Pass (2026-05-02)

- `PRJ-865` is DONE as the focused Personality canonical first-viewport slice:
  - `.codex/tasks/PRJ-865-personality-canonical-first-viewport-pass.md`
- purpose:
  - bring `/personality` closer to
    `docs/ux/assets/aion-personality-canonical-reference-v1.png`
  - stop the extra route toolbar and separate large intro card from pushing the
    embodied personality map too far down the first viewport
  - preserve existing route data and the canonical persona figure asset
- implemented:
  - Personality now hides the extra desktop route toolbar like Chat and
    Dashboard
  - the separate route intro card was replaced with a compact overview bar
  - hero/map, callout, timeline, side-panel, signal-row, and activity-row
    spacing were tightened
  - first desktop viewport now shows the embodied map and timeline start
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-865-personality-canonical-first-viewport-pass.md`
  - result: passed with line-ending warnings only
  - Playwright Chromium screenshot evidence:
    - `.codex/artifacts/prj865-personality-canonical-pass/desktop-1568x1003-v2.png`
    - `.codex/artifacts/prj865-personality-canonical-pass/mobile-390x844-v2.png`
    - `.codex/artifacts/prj865-personality-canonical-pass/dashboard-smoke-1568x1003.png`
- deployment impact:
  - low; frontend visual composition change only
- next smallest useful task:
  - decide whether to polish mobile fixed-navigation spacing/capture behavior or
    continue to another non-frozen shell route such as Tools

## Fresh Passive/Active Final Backend Gate (2026-05-02)

- `PRJ-860` is DONE as the final passive/active verification slice:
  - `.codex/tasks/PRJ-860-final-passive-active-backend-gate.md`
- purpose:
  - close the planned passive/active trigger queue with full backend evidence
  - prove the observer, scheduler, evidence, behavior-doc, and release-smoke
    changes did not regress the wider backend suite
- validation:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q; Pop-Location`
  - result: `1019 passed`
- deployment impact:
  - none; verification/context-only closure
- next smallest useful task:
  - select a new independent product/runtime slice from the board

## Fresh Ops Release Smoke Observer Evidence (2026-05-02)

- `PRJ-859` is DONE as the release-evidence sync slice:
  - `.codex/tasks/PRJ-859-sync-ops-release-smoke-and-learning-journal.md`
- purpose:
  - make planned-action observer posture release-visible after passive/active
    scheduler changes
  - fail smoke when proactive evidence loses the observer boundary
  - keep observer evidence counts-only rather than exposing raw planned-work
    payloads
- implemented:
  - `backend/scripts/run_release_smoke.ps1` validates
    `/health.proactive.planned_action_observer`
  - debug `incident_evidence.policy_posture.proactive` and incident-evidence
    bundle validation now require `planned_action_observer_policy`
  - smoke summaries include live, debug, and bundle observer policy/state
    fields
  - ops/runtime docs and the learning journal now describe the observer release
    gate
- validation:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py -k "release_smoke and (proactive_observer or optional_deployment_evidence or incident_evidence or incident_bundle)"; Pop-Location`
  - result: `13 passed, 39 deselected`
- deployment impact:
  - low; release-smoke validation and docs only, no DB/env/API shape change
    beyond already-exported observer posture
- next smallest useful task:
  - `PRJ-860` run the final backend gate and close docs/context

## Fresh Observer-Gated Proactivity Behavior Scenarios (2026-05-02)

- `PRJ-858` is DONE as the observer-gated behavior scenario slice:
  - `.codex/tasks/PRJ-858-observer-gated-proactivity-behavior-scenarios.md`
- purpose:
  - make the passive/active proactive behavior provable as canonical scenario
    truth, not only as module-level output
  - document silent no-op, due outreach, relation-care handoff, and failure
    evidence learning anchors
- implemented:
  - `docs/architecture/29_runtime_behavior_testing.md` now defines
    `T22.1..T22.4`
  - `docs/engineering/testing.md` now requires proactive-runtime slices to pin
    the observer-gated scenario family
  - no runtime behavior changed in this slice
- validation:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_memory_repository.py -k "proactive or passive_active or scheduler_cadence_evidence"; Pop-Location`
  - result: `9 passed, 76 deselected`
  - `git diff --check`
  - result: passed
- deployment impact:
  - docs/testing/context only; no runtime, API, DB, env, or deployment behavior
    change
- next smallest useful task:
  - `PRJ-859` sync ops, release smoke, and learning journal

## Fresh Dashboard Canonical Density Pass (2026-05-02)

- `PRJ-864` is DONE as the focused dashboard canonical density slice:
  - `.codex/tasks/PRJ-864-dashboard-canonical-density-pass.md`
- purpose:
  - bring the Dashboard first viewport closer to the approved canonical
    dashboard reference after the shell/sidebar pass
  - stop the right guidance rail from forcing the hero-stage to exceed the
    first viewport
  - preserve the existing runtime data flow and route-local cards
- implemented:
  - dashboard now uses a top composition with a primary content column and a
    separate guidance rail
  - the hero-stage no longer contains the guidance rail, so flow and lower
    dashboard cards begin in the first desktop viewport
  - dashboard uses the same hidden canonical route toolbar behavior as Chat
  - hero, flow, guidance, and lower-card spacing were tightened
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-864-dashboard-canonical-density-pass.md`
  - result: passed with line-ending warnings only
  - Playwright Chromium screenshot evidence:
    - `.codex/artifacts/prj864-dashboard-canonical-pass/dashboard-desktop-1568x1003-v2.png`
    - `.codex/artifacts/prj864-dashboard-canonical-pass/dashboard-mobile-390x844-v2.png`
    - `.codex/artifacts/prj864-dashboard-canonical-pass/chat-desktop-smoke-1568x1003-v2.png`
- deployment impact:
  - low; frontend visual composition change only
- next smallest useful task:
  - continue with the next canonical route surface after deciding how to handle
    the already-unpushed local `main` commits

## Fresh Passive/Active Skipped And Failed Evidence (2026-05-02)

- `PRJ-857` is DONE as the passive/active evidence persistence slice:
  - `.codex/tasks/PRJ-857-persist-skipped-and-failed-passive-active-evidence.md`
- purpose:
  - preserve skipped, delayed, blocked, and failed observer-admitted work for
    later reflection/scenario learning
  - keep failure evidence internal instead of forcing user-visible expression
  - reuse existing scheduler cadence evidence rather than adding a new store
- implemented:
  - proactive cadence summaries now include bounded `passive_active_evidence`
    and `passive_active_evidence_count`
  - evidence records source, work id, user id, work kind, delivery channel,
    outcome, reason, and `expression_visible`
  - runtime unavailable, foreground-not-required, quiet-hours delay/skip,
    action noop/partial, action failure, and runtime exception paths can leave
    metadata-only evidence
  - repository persistence coverage proves passive-active evidence survives in
    scheduler cadence evidence
- validation:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_memory_repository.py -k "passive_active or scheduler_cadence_evidence or proactive"; Pop-Location`
  - result: `9 passed, 76 deselected`
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_reflection_worker.py tests/test_memory_repository.py tests/test_scheduler_worker.py; Pop-Location`
  - result: `182 passed`
- deployment impact:
  - low; metadata-only evidence in existing cadence store, no env, DB schema,
    API, or user-visible expression behavior change
- next smallest useful task:
  - `PRJ-858` add behavior scenarios for observer-gated proactivity

## Fresh Proactive Cadence Observer Admission (2026-05-02)

- `PRJ-856` is DONE as the behavior-changing passive/active trigger slice:
  - `.codex/tasks/PRJ-856-route-proactive-cadence-through-observer-admission.md`
- purpose:
  - stop generic proactive candidate selection from starting full foreground
    runtime just because cadence fired
  - keep due planned work eligible for conscious planning through the existing
    `planned_work_due` handoff
  - make empty proactive cadence a cheap observer no-op with zero foreground
    events
- implemented:
  - `backend/app/workers/scheduler.py` now routes in-process and external
    proactive ticks through observer-admitted due planned work
  - proactive summaries include `observer_state`, `observer_reason`, due
    counts, proposal handoff counts, and nested planned-action observer
    posture
  - generic `get_proactive_scheduler_candidates(...)` output no longer emits
    foreground runtime events on its own
  - scheduler snapshot proactive policy now receives the latest observer
    summary evidence
- validation:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py -k "proactive"; Pop-Location`
  - result: `4 passed, 15 deselected`
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py; Pop-Location`
  - result: `19 passed`
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py; Pop-Location`
  - result: `109 passed`
- deployment impact:
  - medium; proactive cadence behavior changes, but no env, DB, schema, API,
    or user-authored turn behavior changes
- next smallest useful task:
  - `PRJ-857` persist skipped and failed passive/active evidence for
    reflection learning

## Fresh Chat Shell Sidebar Canonical Layout (2026-05-02)

- `PRJ-863` is DONE as the focused shell/sidebar polish slice:
  - `.codex/tasks/PRJ-863-chat-shell-sidebar-canonical-layout.md`
- purpose:
  - remove the visible nested browser/mockup frame from the authenticated Chat
    shell
  - make desktop read as one canonical sidebar surface plus one main content
    surface
  - improve sidebar parity against
    `docs/ux/assets/aviary-sidebar-layout-canonical-reference-v1.png`
- implemented:
  - kept shell wrapper elements for functional layout/popover behavior while
    making the outer shell visually transparent
  - retuned desktop shell spacing so sidebar and main sit together without an
    extra surrounding card
  - replaced the sidebar brand image with a code-native AION sunburst mark
  - tightened sidebar nav rhythm and active-pill treatment
  - tuned sidebar system health, identity, and quote cards toward the canonical
    reference
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check`
  - result: passed with line-ending warnings only
  - Playwright Chromium screenshot evidence:
    - `.codex/artifacts/prj863-shell-sidebar-layout/desktop-1568x1003-v2.png`
    - `.codex/artifacts/prj863-shell-sidebar-layout/mobile-390x844-v2.png`
  - browser metrics verified:
    - no horizontal overflow on desktop or mobile
    - `.aion-shell-window` has transparent background and `0px` border
    - sidebar brand is `AION` and uses `.aion-sidebar-sunmark`
- deployment impact:
  - low; frontend visual shell/sidebar change only
- next smallest useful task:
  - commit and push this shell/sidebar polish slice after review

## Fresh Chat Canonical V5 Implementation (2026-05-02)

- `PRJ-862` is DONE as the focused `/chat` parity implementation:
  - `.codex/tasks/PRJ-862-implement-chat-canonical-v5-two-column-view.md`
- purpose:
  - implement the user-approved Chat v5 canonical composition in the existing
    web app
  - remove the old third context rail from the rendered Chat screen
  - move context into the top belt and persona-stage support layer
- implemented:
  - `/chat` now uses a top cognitive belt for current intent, motivation,
    active goal, memory, suggested action, and next check-in
  - desktop body now uses equal-height `60/40` conversation/persona columns
  - the composer lives inside the left conversation column below the transcript
  - the right persona column uses `aion-chat-persona-stage-v5.png`, extracted
    from the approved v5 reference with the head facing toward the chat
  - the authenticated rail now shows AION branding and the full canonical module
    list, with unavailable future modules shown as inactive visual entries
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
  - `git diff --check`
  - result: passed with line-ending warnings only
  - Playwright Chromium screenshot evidence:
    - `.codex/artifacts/prj862-chat-v5-parity/desktop-1568x1003-verified-v2.png`
    - `.codex/artifacts/prj862-chat-v5-parity/tablet-1024x900-verified.png`
    - `.codex/artifacts/prj862-chat-v5-parity/mobile-390x844-verified-v3.png`
  - browser metrics verified:
    - no `.aion-chat-context-rail` rendered
    - no horizontal overflow on desktop, tablet, or mobile
    - desktop columns are equal-height and split `710.719px / 473.812px`
- deployment impact:
  - low; frontend visual change only, no env, DB, API, backend, or runtime
    behavior changed
- next smallest useful task:
  - optional pixel-polish pass for the mobile composer and persona crop if the
    user wants stricter visual matching beyond the current v5 structural parity

## Fresh Planned-Action Observer Policy And Diagnostics (2026-05-02)

- `PRJ-855` is DONE as the first implementation slice for the passive/active
  trigger boundary:
  - `.codex/tasks/PRJ-855-planned-action-observer-policy-and-diagnostics.md`
- purpose:
  - make the planned-action observer machine-visible before changing proactive
    cadence behavior
  - distinguish empty passive scans from due planned work, actionable
    proposals, policy blockage, and missing observer evidence
  - expose counts-only diagnostics without leaking raw planned-work payloads
- implemented:
  - added `backend/app/core/planned_action_observer.py`
  - proactive runtime policy now advertises observer-admitted due/actionable
    candidate selection
  - `/health.proactive.planned_action_observer` exposes owner, state, reason,
    counts, no-op behavior, foreground trigger policy, and raw-payload posture
  - incident evidence proactive posture receives the same observer snapshot
  - runtime cadence behavior is intentionally unchanged in this slice
- validation:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_planned_action_observer.py tests/test_api_routes.py -k "planned_action_observer or health_endpoint_returns_ok"; Pop-Location`
  - result: `7 passed, 117 deselected`
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py -k "snapshot_exposes_live_proactive_policy"; Pop-Location`
  - result: `1 passed, 18 deselected`
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_planned_action_observer.py tests/test_api_routes.py tests/test_scheduler_worker.py; Pop-Location`
  - result: `143 passed`
  - `git diff --check`
  - result: passed
- deployment impact:
  - low; health/debug posture only, no env, DB, schema, or cadence behavior
    change
- next smallest useful task:
  - `PRJ-856` route proactive cadence through observer-backed due
    work/proposals

## Fresh Chat Canonical Reference V5 Freeze (2026-05-02)

- `PRJ-861` is DONE as the Chat v5 canonical asset freeze:
  - `.codex/tasks/PRJ-861-freeze-chat-canonical-reference-v5.md`
- purpose:
  - save the user-approved generated Chat concept as the active canonical
    reference before future implementation parity work
- implemented:
  - copied the generated image into:
    - `docs/ux/assets/aion-chat-canonical-reference-v5.png`
  - updated `docs/ux/canonical-web-screen-reference-set.md` so Chat now points
    at v5 instead of v4
  - recorded the approved v5 layout contract:
    - top cognitive belt for intent, motivation, active goal, memory,
      suggested action, and next check-in
    - two equal-height main columns below the belt
    - `60%` conversation transcript/composer column
    - `40%` route-adapted persona stage column
    - no separate third context column below the belt
    - persona faces left toward the chat thread
  - updated `docs/ux/design-memory.md` with the new Chat v5 canonical
    composition rule
- validation:
  - saved asset opened with `view_image`
  - `git diff --check`
  - result: passed
- deployment impact:
  - docs/asset freeze only; no runtime, API, backend, DB, env, or deployment
    behavior changed
- next smallest useful task:
  - implement a focused `/chat` parity pass against v5

## Fresh Passive/Active Trigger Implementation Plan (2026-05-02)

- `PRJ-854` is DONE as the detailed implementation-planning slice:
  - `.codex/tasks/PRJ-854-passive-active-trigger-implementation-plan.md`
- purpose:
  - turn the `PRJ-853` passive/active architecture contract into a concrete,
    file-scoped implementation queue
  - keep planning external contact/care/outreach separate from the internal
    foreground execution loop
- implemented:
  - added `docs/planning/passive-active-trigger-implementation-plan.md`
  - detailed implementation tasks `PRJ-855..PRJ-860` now cover:
    - planned-action observer policy and health/debug posture
    - proactive cadence routing through observer admission
    - skipped/failed evidence persistence for reflection
    - behavior scenarios for no-op, due outreach, relational care, and failure
      learning
    - ops, release smoke, and final backend gate closure
  - no runtime behavior changed
- validation:
  - `git diff --check`
  - result: passed
- deployment impact:
  - docs/context only; no runtime, API, DB, env, or deployment behavior change
- next smallest useful task:
  - `PRJ-855` add planned-action observer policy and diagnostics

## Fresh Passive/Active Runtime Trigger Boundary (2026-05-02)

- `PRJ-853` is DONE as the architecture contract slice for passive external
  planning versus active conscious execution:
  - `.codex/tasks/PRJ-853-passive-active-runtime-trigger-boundary.md`
- purpose:
  - stop treating scheduler time passing as a generic reason to wake conscious
    outreach
  - preserve relationship-based care/check-ins as inferred planned work or
    proposals rather than hard-coded contact duties
  - keep the internal foreground execution loop unchanged once a real stimulus
    is admitted
- implemented:
  - canonical architecture now states that external contact/care/outreach
    planning belongs to planned work or subconscious proposals
  - `docs/architecture/16_agent_contracts.md` now defines the passive/active
    runtime trigger boundary
  - the planned-action observer is now the target bridge: cheap scan first,
    full foreground run only when due/actionable work exists
  - runtime reality records that current proactive cadence still needs a
    follow-up implementation alignment
- validation:
  - `git diff --check`
  - result: passed
- deployment impact:
  - docs/context only; no runtime, API, DB, env, or deployment behavior change
- next smallest useful task:
  - `PRJ-854` add planned-action observer policy and health/debug posture

## Fresh Chat Canonical 97 Percent Parity Closure (2026-05-01)

- `PRJ-852` is DONE as the focused local `/chat` canonical parity slice:
  - `.codex/tasks/PRJ-852-chat-canonical-97-parity-closure.md`
- purpose:
  - converge the web app chat module toward
    `docs/ux/assets/aion-chat-canonical-reference-v4.png` with a 97% local
    parity target
- implemented:
  - `/chat` now uses a compact canonical conversation topbar instead of the
    route-scale heading and shared utility toolbar
  - desktop chat now composes transcript, embodied stage, right cognitive
    context, and composer tray as one workspace
  - the composer spans the transcript plus portrait stage, with mode tabs,
    attachment, voice, and send affordances integrated into one tray
  - the right cognitive context now includes four motivation signals, active
    goal, related memory, three suggested actions, and a separate proactive
    check-in panel
  - tablet and mobile now stack safely below wide desktop, with no horizontal
    clipping in the verified screenshots
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
- screenshot evidence:
  - `.codex/artifacts/prj852-chat-canonical-parity/closure-desktop.png`
  - `.codex/artifacts/prj852-chat-canonical-parity/closure-tablet-v2.png`
  - `.codex/artifacts/prj852-chat-canonical-parity/closure-mobile.png`
  - `.codex/artifacts/prj852-chat-canonical-parity/final-mobile-v2.png`
- deployment impact:
  - local web-only UI change; no env, backend, API, DB, or runtime contract
    change
- next smallest useful task:
  - run production screenshot proof after deploy, or perform a route copy/icon
    fidelity pass if the next closure target is literal screenshot parity

## Fresh Release Smoke Missing Settings Publish And Smoke (2026-05-01)

- `PRJ-851` is DONE as the publish and smoke closure for `PRJ-850`:
  - `.codex/tasks/PRJ-851-publish-and-smoke-release-smoke-summary.md`
- publication:
  - committed `2e9031a` with message
    `chore: surface organizer missing settings in smoke`
  - pushed `2e9031a` to `origin/main`
- validation:
  - `PRJ-850` full backend gate passed with `1010 passed`
  - production release smoke passed with deploy parity wait
- production evidence:
  - `health_status=ok`
  - `release_ready=true`
  - `release_violations=[]`
  - `runtime_action=success`
  - `deployment_runtime_build_revision=2e9031a1efe80a0ef2267f8de793564eaaa0ed72`
  - `web_shell_build_revision=2e9031a1efe80a0ef2267f8de793564eaaa0ed72`
  - `organizer_tool_activation_missing_settings_by_provider` includes missing
    setting-name lists for `clickup`, `google_calendar`, and `google_drive`
- local evidence note:
  - `PRJ-851` is intentionally local and unpushed to avoid a docs-only deploy
    cycle after the successful smoke
- next smallest useful task:
  - provider credentials remain the next operational blocker for organizer
    daily-use readiness

## Fresh Release Smoke Provider Missing Settings Summary (2026-05-01)

- `PRJ-850` is DONE as a release-smoke evidence improvement:
  - `.codex/tasks/PRJ-850-release-smoke-provider-missing-settings-summary.md`
- purpose:
  - make release smoke directly report organizer provider missing settings per
    provider, instead of requiring a separate full `/health` inspection after
    smoke
- implemented:
  - `Assert-OrganizerToolStackContract` now returns
    `activation_missing_settings_by_provider`
  - top-level health smoke summary, debug incident-evidence summary, and
    incident-bundle summary expose the same provider -> missing settings shape
  - only setting names already present in `/health` are surfaced; secret values
    are not exposed
- validation:
  - focused debug/bundle smoke tests:
    `2 passed, 49 deselected`
  - focused organizer/release smoke tests:
    `40 passed, 11 deselected`
  - full deployment-trigger script tests:
    `51 passed`
  - full backend gate:
    `1010 passed in 105.03s`
- next smallest useful task:
  - run normal backend/release validation and publish this operator-smoke
    improvement if it should go live

## Fresh Organizer Guidance Fix Publish And Smoke (2026-05-01)

- `PRJ-849` is DONE as the publish and production-smoke closure for `PRJ-848`:
  - `.codex/tasks/PRJ-849-publish-and-smoke-organizer-guidance-fix.md`
- publication:
  - committed `bdd3dcf` with message
    `fix: refine organizer activation guidance`
  - pushed `bdd3dcf` to `origin/main`
- validation:
  - `PRJ-848` full backend gate passed with `1010 passed`
  - production release smoke passed with deploy parity wait
- production evidence:
  - `health_status=ok`
  - `release_ready=true`
  - `release_violations=[]`
  - `runtime_action=success`
  - `deployment_runtime_build_revision=bdd3dcfa01aad3c737fa46ef610d2e787976f3a3`
  - `web_shell_build_revision=bdd3dcfa01aad3c737fa46ef610d2e787976f3a3`
  - `organizer_tool_activation_next_actions` now includes
    `configure_google_calendar_access_token_and_calendar_id`
- local evidence note:
  - `PRJ-849` is intentionally local and unpushed to avoid a docs-only deploy
    cycle after the successful smoke
- next smallest useful task:
  - provider credentials remain the next operational blocker if organizer
    workflows should become daily-use ready

## Fresh Organizer Activation Next-Action Precision (2026-05-01)

- `PRJ-848` is DONE as a production-readiness quality fix:
  - `.codex/tasks/PRJ-848-precise-organizer-activation-next-actions.md`
- purpose:
  - make organizer provider activation `next_action` values match the actual
    missing settings while preserving existing broad slugs for fully missing
    states
- implemented:
  - added `_configure_next_action()` in
    `backend/app/core/connector_execution.py`
  - reused existing `missing_settings` lists for provider activation and
    daily-use next actions
  - preserved the established all-missing Google Calendar slug:
    `configure_google_calendar_access_token_calendar_id_and_timezone`
  - added regression coverage for the production-like partial Google Calendar
    state where timezone exists but token and calendar id are missing
- validation:
  - focused organizer API test:
    `3 passed, 115 deselected`
  - full API route suite:
    `118 passed`
  - focused release-smoke organizer/parser tests:
    `40 passed, 11 deselected`
  - full backend gate:
    `1010 passed in 103.38s`
- next smallest useful task:
  - prepare/publish this low-risk operator-readiness fix if desired, then run
    the normal deploy validation cycle

## Fresh Post-Deploy Stability Snapshot (2026-05-01)

- `PRJ-847` is DONE as a non-invasive post-deploy stability check:
  - `.codex/tasks/PRJ-847-post-deploy-stability-snapshot.md`
- purpose:
  - confirm production remains healthy after the v1 deploy smoke without
    posting another synthetic runtime event
- validation:
  - `GET https://aviary.luckysparrow.ch/health`
  - `GET https://aviary.luckysparrow.ch/`
  - `git rev-parse HEAD`
- production evidence:
  - `status=ok`
  - `release_ready=true`
  - `release_violations=[]`
  - `runtime_build_revision=1a04b242b54acd5c09f9e67e009b6d86562ba5e6`
  - `web_shell_build_revision=1a04b242b54acd5c09f9e67e009b6d86562ba5e6`
  - local `HEAD=1a04b242b54acd5c09f9e67e009b6d86562ba5e6`
- follow-up signal:
  - core v1 deployment is stable
  - organizer daily-use workflows remain blocked by provider activation:
    ClickUp, Google Calendar, and Google Drive
- next smallest useful task:
  - start a separate provider activation readiness lane if organizer workflows
    should become part of the next release increment

## Fresh Production Release Smoke (2026-05-01)

- `PRJ-846` is DONE as the production smoke and v1 deployment verification:
  - `.codex/tasks/PRJ-846-production-release-smoke.md`
- purpose:
  - confirm production deployed the latest pushed revision and passes the
    release-readiness smoke contract
- validation:
  - first attempt hit transient deploy-time `503 Service Unavailable`
  - retry command:
    `.\backend\scripts\run_release_smoke.ps1 -BaseUrl "https://aviary.luckysparrow.ch" -WaitForDeployParity -DeployParityMaxWaitSeconds 900 -DeployParityPollSeconds 30 -HealthRetryMaxAttempts 10 -HealthRetryDelaySeconds 10`
  - result: pass
- production evidence:
  - `health_status=ok`
  - `release_ready=true`
  - `release_violations=[]`
  - `runtime_action=success`
  - `deployment_runtime_build_revision=1a04b242b54acd5c09f9e67e009b6d86562ba5e6`
  - `web_shell_build_revision=1a04b242b54acd5c09f9e67e009b6d86562ba5e6`
- deployment posture:
  - v1 is deployed on `https://aviary.luckysparrow.ch`
  - local generated `artifacts/behavior_validation/prj843-report.json` remains
    uncommitted
  - this smoke/context evidence is intentionally local and unpushed to avoid a
    new docs-only production deploy cycle
- next smallest useful task:
  - monitor production behavior and handle provider credential activation
    blockers as a separate non-core-v1 lane

## Fresh V1 Deploy Candidate Publish (2026-05-01)

- `PRJ-845` is DONE as the current release publication slice:
  - `.codex/tasks/PRJ-845-publish-v1-deploy-candidate.md`
- purpose:
  - commit and push the validated v1 deploy candidate to `origin/main`
- preconditions:
  - `PRJ-843` behavior-validation gate passed
  - `PRJ-844` full backend gate passed with `1009 passed`
  - local `main` matched `origin/main` before publication work started
- result:
  - committed `e03fb08` with message
    `release: behavior feedback v1 candidate`
  - pushed `e03fb08` to `origin/main`
- scope note:
  - source, tests, docs, and task/context updates are in scope
  - local generated `artifacts/behavior_validation/prj843-report.json` is
    excluded from commit scope
- next smallest useful task:
  - start `PRJ-846` by running production release smoke against
    `https://aviary.luckysparrow.ch`

## Fresh Deploy Readiness Primary Backend Gate (2026-05-01)

- `PRJ-844` is DONE as the current deploy-readiness verification slice:
  - `.codex/tasks/PRJ-844-deploy-readiness-primary-backend-gate.md`
- purpose:
  - prove the current backend working tree against the repository primary gate
    before commit, push, or production deployment movement
- validation:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q; Pop-Location`
  - result: `1009 passed in 107.61s`
  - note: the first attempt was interrupted by a 120s tool timeout before pytest
    produced a result; the same gate was rerun with a longer timeout and passed
- deployment posture:
  - backend primary gate is green
  - production deploy and post-deploy smoke are still pending
- next smallest useful task:
  - start `PRJ-845` by preparing the deploy candidate commit/push and then
    running release smoke against `https://aviary.luckysparrow.ch`

## Fresh Release Evidence Gate (2026-05-01)

- `PRJ-843` is DONE as the current release-evidence gate:
  - `.codex/tasks/PRJ-843-run-current-release-evidence-gate.md`
- purpose:
  - produce fresh behavior-validation evidence before moving to deploy smoke
- implemented:
  - fixed `backend/scripts/run_behavior_validation.ps1` so it resolves the
    repo-root `.venv` when launched from the repository root
  - fixed `backend/scripts/run_behavior_validation.py` so pytest targets
    backend tests with stable paths and runs with `cwd=backend`
  - added a PowerShell wrapper regression in
    `backend/tests/test_deployment_trigger_scripts.py`
  - generated `artifacts/behavior_validation/prj843-report.json`
- validation:
  - `.\backend\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/prj843-report.json`
  - result: `19 passed, 207 deselected`, `gate_status=pass`
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_behavior_validation_script.py tests/test_deployment_trigger_scripts.py -k "behavior_validation"; Pop-Location`
  - result: `23 passed, 49 deselected`
- next smallest useful task:
  - start `PRJ-844` by running release smoke against the chosen target, or by
    preparing commit/deploy first if production cannot contain the current
    working-tree changes yet

## Fresh Release Operator Script Path Alignment (2026-05-01)

- `PRJ-842` is DONE as a release-readiness cleanup:
  - `.codex/tasks/PRJ-842-align-release-operator-script-paths.md`
- purpose:
  - prevent deploy, smoke, behavior-validation, and incident-evidence commands
    from pointing at a missing root `scripts/` directory
- implemented:
  - aligned active deployment, testing, ops, and planning docs to the real
    `backend/scripts/` layout for commands run from the repository root
  - preserved `.\scripts\...` only for examples that first enter
    `.\backend`
  - recorded the path-drift guardrail in the learning journal
  - selected docs-path alignment as the next v1 blocker because it directly
    affects release execution reliability
- validation:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py -k "backend_operator_scripts_expose_help"; Pop-Location`
  - result: `8 passed, 42 deselected`
  - `git diff --check`
  - result: pass
- next smallest useful task:
  - start `PRJ-843` by running or preparing the current release evidence
    bundle against the chosen deployment target

## Fresh Behavior Feedback Learning Lane Closure (2026-05-01)

- `PRJ-841` is DONE as the docs/context closure slice for the
  behavior-feedback learning lane:
  - `.codex/tasks/PRJ-841-sync-runtime-docs-ops-notes-and-learning-journal.md`
- purpose:
  - make the implemented behavior-feedback loop reproducible for release
    review, operator triage, and the next agent
- implemented:
  - synced runtime reality with the implemented perception -> planning ->
    action -> memory/reflection -> expression ownership chain
  - added ops triage notes for `system_debug.behavior_feedback`, relation
    updates, reflection consolidation, and expression self-review notes
  - added testing guidance for behavior-feedback and communication-boundary
    learning changes
  - updated the existing learning-journal communication-boundary entry instead
    of creating a duplicate pitfall
  - marked the behavior-feedback learning plan closure complete
- validation:
  - `git diff --check`
  - result: pass
- next smallest useful task:
  - start `PRJ-842` by selecting the next v1 blocker from the board or
    coverage-ledger evidence

## Fresh End-To-End Behavior Learning Scenarios (2026-05-01)

- `PRJ-840` is DONE as the verification slice of the behavior-feedback
  learning lane:
  - `.codex/tasks/PRJ-840-end-to-end-behavior-learning-scenarios.md`
- purpose:
  - prove behavior learning across time rather than only module output
- implemented:
  - added scenario `T21.1` for repeated-greeting feedback becoming relation
    truth and later expression removing a generated repeated greeting
  - added scenario `T21.2` for repeated weaker feedback consolidating through
    reflection
  - added scenario `T21.3` for unclear feedback staying descriptive-only
  - updated runtime behavior-testing docs with the new scenario anchors
- focused validation:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py -k "behavior_learning_feedback_scenarios"; Pop-Location`
  - result: `1 passed, 108 deselected`
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_communication_boundary.py tests/test_reflection_worker.py; Pop-Location`
  - result: `174 passed`
- closure:
  - `PRJ-841` completed the runtime docs, ops notes, context, and learning
    journal sync for this scenario proof

## Fresh Expression Self-Review For Communication Preferences (2026-05-01)

- `PRJ-839` is DONE as the fifth implementation slice of the behavior-feedback
  learning lane:
  - `.codex/tasks/PRJ-839-expression-self-review-for-known-communication-preferences.md`
- purpose:
  - make expression honor known communication preferences even when generated
    wording drifts, without giving expression durable write authority
- implemented:
  - added `ExpressionOutput.self_review_notes`
  - expression now records side-effect-free adjustment notes
  - repeated greetings are removed when relation truth says to avoid them
  - overly formal openings are removed when concise/direct style is known
  - scheduler replies remove unsolicited future contact promises when contact
    cadence relations discourage them
  - OpenAI reply prompting now explicitly discourages unsolicited future pings
    when contact-cadence boundaries apply
- focused validation:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_expression_agent.py tests/test_openai_prompting.py; Pop-Location`
  - result: `23 passed`
- next smallest useful task:
  - start `PRJ-840` with end-to-end behavior learning scenarios

## Fresh Behavior Feedback Reflection Accumulation (2026-05-01)

- `PRJ-838` is DONE as the fourth implementation slice of the behavior-feedback
  learning lane:
  - `.codex/tasks/PRJ-838-behavior-feedback-evidence-accumulation-and-reflection.md`
- purpose:
  - let repeated weaker behavior feedback accumulate through episodic memory
    and reflection instead of overfitting a single ambiguous turn
- implemented:
  - action preserves `perception.behavior_feedback` in episodic payloads
  - episodic extraction exposes relation-backed behavior-feedback candidates
  - reflection consolidates repeated weak relation-backed candidates into
    relation updates
  - one weak candidate remains descriptive-only
- focused validation:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_memory_repository.py tests/test_communication_boundary.py tests/test_action_executor.py -k "behavior_feedback or relation"; Pop-Location`
  - result: `26 passed, 150 deselected`
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_memory_repository.py tests/test_communication_boundary.py; Pop-Location`
  - result: `129 passed`
- next smallest useful task:
  - start `PRJ-839` by adding side-effect-free expression self-review for known
    communication preferences

## Fresh Behavior Feedback Planning And Action Route (2026-05-01)

- `PRJ-837` is DONE as the third implementation slice of the behavior-feedback
  learning lane:
  - `.codex/tasks/PRJ-837-route-feedback-evidence-through-planning-and-action.md`
- purpose:
  - make durable behavior-feedback learning flow through structured planning
    intents and existing action persistence instead of any raw-text action
    parsing
- implemented:
  - planning now accepts structured `behavior_feedback`
  - graph adapters pass `perception.behavior_feedback` into planning
  - high-confidence relation-backed corrections/observations become typed
    `maintain_relation` intents
  - low-confidence or unclear feedback remains descriptive-only
  - action continues to persist relation updates only from typed domain intents
- focused validation:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py; Pop-Location`
  - result: `236 passed`
- next smallest useful task:
  - start `PRJ-838` by preserving feedback evidence for reflection
    accumulation and consolidation

## Fresh Behavior Feedback Assessor (2026-05-01)

- `PRJ-836` is DONE as the second implementation slice of the behavior-feedback
  learning lane:
  - `.codex/tasks/PRJ-836-implement-behavior-feedback-assessor.md`
- purpose:
  - widen behavior-feedback interpretation beyond the first contract while
    keeping the output descriptive until planning/action explicitly route it
- implemented:
  - added `BehaviorFeedbackAssessor` under `backend/app/communication/`
  - reused existing communication-boundary extraction as the deterministic
    baseline for repeated greetings and contact cadence
  - added descriptive recognition for context-continuity complaints, overly
    formal tone feedback, direct-style approval, hands-on collaboration
    approval, and low-confidence ambiguous behavior feedback
  - wired perception to consume the assessor for `behavior_feedback`
  - proved unclear behavior feedback does not become a durable relation intent
- focused validation:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_communication_boundary.py tests/test_planning_agent.py; Pop-Location`
  - result: `92 passed`
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py -k "behavior_feedback"; Pop-Location`
  - result: `1 passed, 107 deselected`
- next smallest useful task:
  - start `PRJ-837` by routing high-confidence behavior-feedback evidence
    through planning/action while keeping low-confidence output descriptive

## Fresh Behavior Feedback Interpretation Contract (2026-05-01)

- `PRJ-835` is DONE as the first implementation slice of the behavior-feedback
  learning lane:
  - `.codex/tasks/PRJ-835-add-behavior-feedback-interpretation-contract.md`
- purpose:
  - make natural feedback about Aviary's own behavior visible as structured
    current-turn interpretation before broader assessor or persistence routing
    work depends on it
- implemented:
  - added `BehaviorFeedbackOutput` with target, polarity, suggested relation
    family/value, confidence, evidence, and source
  - added `PerceptionOutput.behavior_feedback`
  - mirrored the same interpretation through `system_debug.behavior_feedback`
  - reused existing communication-boundary signals for the initial contract
    without adding a second memory subsystem or a new durable write path
  - updated architecture and runtime behavior-testing docs for the new debug
    evidence contract
- focused validation:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_graph_state_contract.py tests/test_runtime_pipeline.py -k "behavior_feedback or system_debug_surface or runtime_result_to_graph_state_maps_orchestrator_contract or graph_state_to_runtime_result_roundtrip"; Pop-Location`
  - result: `4 passed, 111 deselected`
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_graph_state_contract.py tests/test_runtime_pipeline.py; Pop-Location`
  - result: `115 passed`
- next smallest useful task:
  - start `PRJ-836` by implementing the broader behavior feedback assessor
    while keeping low-confidence feedback descriptive-only

## Fresh Behavior Feedback Learning System Plan (2026-05-01)

- `PRJ-834` is DONE as a planning freeze:
  - `.codex/tasks/PRJ-834-freeze-behavior-feedback-learning-plan.md`
  - `docs/planning/behavior-feedback-learning-system-plan.md`
- purpose:
  - turn the user's approved direction into an execution-ready lane where
    Aviary learns from natural feedback about its behavior rather than only
    rigid commands
- planned follow-up queue:
  - `PRJ-835` Add Behavior Feedback Interpretation Contract
  - `PRJ-836` Implement Behavior Feedback Assessor
  - `PRJ-837` Route Feedback Evidence Through Planning And Action
  - `PRJ-838` Add Evidence Accumulation And Reflection Consolidation
  - `PRJ-839` Add Expression Self-Review For Known Communication Preferences
  - `PRJ-840` Add End-To-End Behavior Learning Scenarios
  - `PRJ-841` Sync Runtime Docs, Ops Notes, And Learning Journal
- guardrail:
  - the lane must reuse existing perception/context, planning, action, memory,
    reflection, and expression owners
  - expression must stay side-effect-free
  - low-confidence feedback must remain descriptive-only
- validation:
  - planning/docs-only; no automated tests run
- next smallest useful task:
  - start `PRJ-835` by adding the behavior-feedback interpretation contract
    and debug-visible output without durable mutation

## Fresh Context Recency And Natural Communication Feedback Boundary Pass (2026-05-01)

- `PRJ-833` is DONE as a bounded runtime-continuity fix:
  - `.codex/tasks/PRJ-833-context-recency-and-observed-greeting-boundary-pass.md`
- purpose:
  - reduce repeated greeting behavior and improve short-gap conversation
    continuity without introducing a parallel short-term memory subsystem
  - let Aviary learn from natural communication feedback rather than only from
    rigid imperative commands
- implemented:
  - observational repeated-greeting feedback such as "osobowość za kążdą
    wiadomością się wita" now maps to the existing
    `interaction_ritual_preference=avoid_repeated_greeting` relation
  - looser observations such as "zawsze zaczyna od hej" and "pisze do mnie
    zbyt często" can map into the existing interaction-ritual and contact-
    cadence relation families
  - planning persists that observation through the existing
    `maintain_relation` intent path
  - context summaries now include a bounded recency hint when already-loaded
    recent memory has timestamps, for example that the latest remembered turn
    was about three minutes before the current turn
- focused validation:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_communication_boundary.py tests/test_context_agent.py tests/test_planning_agent.py -k "greeting or recency or communication_boundary"; Pop-Location`
  - result: `8 passed, 128 deselected`
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_communication_boundary.py tests/test_context_agent.py tests/test_planning_agent.py; Pop-Location`
  - result: `139 passed`
- next smallest useful task:
  - replay or inspect a real multi-turn chat trace after this change and
    confirm expression stops greeting repeatedly once the relation is
    persisted

## Fresh Chat First 10 Slice Batch And Foundation Pass (2026-05-01)

- `PRJ-832` is now IN_PROGRESS as the active `chat` lane opener:
  - `.codex/tasks/PRJ-832-chat-first-10-slice-batch-and-foundation-pass.md`
- purpose:
  - freeze a dedicated 100-slice closure map for `chat` and execute the first
    bounded foundation batch
- implemented in the current slice:
  - wrote a dedicated `chat` 100-slice closure map
  - redirected canonical planning truth from `dashboard` to `chat`
  - calmed the chat topbar, control pills, transcript cadence, and
    assistant/user bubble materials
  - increased portrait-stage authority, calmed portrait notes/connectors, and
    narrowed the cognitive rail
  - reduced density in motivation, active goal, related memory, and suggested
    actions so the right rail reads less list-heavy
  - tightened quick actions, composer tray density, and long-form transcript
    polish
  - reduced topbar control weight, softened the lead card, and narrowed the
    rail for a stronger transcript-first balance
  - reduced remaining chrome by trimming top controls, quick actions, and
    scenic-note copy
  - reduced the remaining summary chrome to one top-control pill and one
    primary quick action, with calmer solo-material styling for both
- focused validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css docs/planning/canonical-100-slice-closure-map.md docs/planning/chat-canonical-100-slice-closure-map.md .codex/tasks/PRJ-832-chat-first-10-slice-batch-and-foundation-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- next smallest useful task:
  - take the next deploy-side chat proof after the solo-control batch
  - if drift remains, open the next bounded `chat` continuation lane only on
    proof-backed residual drift

## Fresh Dashboard First 10 Slice Batch And Intro Pass (2026-05-01)

- `PRJ-831` is now IN_PROGRESS as the active dashboard lane opener:
  - `.codex/tasks/PRJ-831-dashboard-first-10-slice-batch-and-intro-pass.md`
- purpose:
  - freeze the first 10 dashboard micro-slices and execute the first bounded
    intro, crop, and signal-softness passes
- implemented in the current slice:
  - recorded the first 10 dashboard slices in the canonical closure map
  - compressed the dashboard intro/header rhythm
  - shortened the hero body copy and cleaned the hero badge glyph drift
  - tightened the central hero crop and persona-stage authority
  - softened left and right signal-card scale, spacing, and connector weight
  - calmed the figure-note positions and shortened their connector lengths
  - tightened the guidance rail so it reads more editorial and less panel-like
  - reduced recent-activity density and made the intention card calmer
- focused validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css docs/planning/canonical-100-slice-closure-map.md .codex/tasks/PRJ-831-dashboard-first-10-slice-batch-and-intro-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- next smallest useful task:
  - take the next deploy-side dashboard proof
  - if drift remains, open the next bounded dashboard continuation lane

## Fresh Authenticated Sidebar Quote CSS Consolidation Pass (2026-05-01)

- `PRJ-830` is now IN_PROGRESS as a sidebar implementation cleanup slice:
  - `.codex/tasks/PRJ-830-authenticated-sidebar-quote-css-consolidation-pass.md`
- purpose:
  - remove the remaining duplicated quote-closure CSS so the sidebar rail is
    easier to maintain before proof
- implemented in the current slice:
  - removed the older overridden quote-closure CSS block
  - kept one canonical live quote block with stable punctuation content and
    final spacing values
- focused validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/index.css .codex/tasks/PRJ-830-authenticated-sidebar-quote-css-consolidation-pass.md`
- next smallest useful task:
  - compare the deployed authenticated sidebar
  - if the parity gate clears, move to `dashboard`

## Fresh Authenticated Sidebar Final Gap And Copy Rhythm Pass (2026-05-01)

- `PRJ-829` is now IN_PROGRESS as the fourth exactness slice of the
  authenticated sidebar group:
  - `.codex/tasks/PRJ-829-authenticated-sidebar-final-gap-and-copy-rhythm-pass.md`
- purpose:
  - apply one last bounded rail/copy-rhythm refinement before deploy-side
    sidebar proof
- implemented in the current slice:
  - tightened rail-to-canvas column proportion and shell gap
  - slightly tightened rail padding and shadow weight
  - tightened lower-stack spacing and micro-typography rhythm
- focused validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-829-authenticated-sidebar-final-gap-and-copy-rhythm-pass.md`
- next smallest useful task:
  - compare the deployed authenticated sidebar
  - if the parity gate clears, move to `dashboard`

## Fresh Authenticated Sidebar Decomponentize Support Stack (2026-05-01)

- `PRJ-828` is now IN_PROGRESS as the third exactness slice of the
  authenticated sidebar group:
  - `.codex/tasks/PRJ-828-authenticated-sidebar-decomponentize-support-stack.md`
- purpose:
  - remove redundant utility framing from the lower sidebar stack so the rail
    reads less like assembled panels and more like one canonical layout family
- implemented in the current slice:
  - removed `rounded-*` and `p-*` utility framing from the health, identity,
    and quote cards in JSX
  - moved lower-card geometry ownership into sidebar-specific CSS
  - unified support-card border/shadow/background treatment
- focused validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-828-authenticated-sidebar-decomponentize-support-stack.md`
- next smallest useful task:
  - compare the deployed authenticated sidebar
  - if still needed, do one final bounded sidebar slice only on last gap and
    copy-rhythm drift before moving on

## Fresh Authenticated Sidebar Support Closure Pass (2026-05-01)

- `PRJ-827` is now IN_PROGRESS as the second exactness slice of the
  authenticated sidebar group:
  - `.codex/tasks/PRJ-827-authenticated-sidebar-support-closure-pass.md`
- purpose:
  - reduce the remaining heaviness in the sidebar lower support stack before
    moving on from the rail
- implemented in the current slice:
  - reduced `System Health` emblem scale, rings, and shadow weight
  - tightened the health-card text hierarchy and diagnostics button
  - tightened identity/quote closure spacing and quote typography
  - corrected the active 100-slice planning note so it no longer points back
    to `home`
- focused validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css docs/planning/canonical-100-slice-closure-map.md .codex/tasks/PRJ-827-authenticated-sidebar-support-closure-pass.md`
- next smallest useful task:
  - compare the deployed authenticated sidebar
  - if still needed, do one final bounded sidebar slice on bottom-stack gap
    balance and health-copy rhythm

## Fresh Authenticated Sidebar Lockup And Nav Rhythm Pass (2026-05-01)

- `PRJ-826` is now IN_PROGRESS as the first exactness slice of the
  authenticated sidebar group:
  - `.codex/tasks/PRJ-826-authenticated-sidebar-lockup-and-nav-rhythm-pass.md`
- purpose:
  - narrow and calm the authenticated desktop rail before deeper support-card
    or route-level parity work resumes
- implemented in the current slice:
  - reduced sidebar rail width, internal padding, and shell gap
  - reduced brand-lockup scale and tightened subtitle posture
  - tightened nav-row height, icon scale, label rhythm, and active-pill
    softness
  - tightened the support-stack density and quiet-button weight
  - removed visible glyph drift from the shell emblem and quote closure
- focused validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-826-authenticated-sidebar-lockup-and-nav-rhythm-pass.md`
- next smallest useful task:
  - compare the deployed authenticated sidebar
  - if needed, do one more bounded sidebar slice on health-emblem weight and
    bottom-stack closure rhythm

## Fresh Authenticated Shell Canvas Opening Pass (2026-04-30)

- `PRJ-825` is now IN_PROGRESS as the second slice of the authenticated-shell
  group:
  - `.codex/tasks/PRJ-825-authenticated-shell-canvas-opening-pass.md`
- purpose:
  - tighten the shell opening between rail, toolbar, backdrop, and active
    canvas before moving to sidebar exactness
- implemented in the current slice:
  - reduced outer shell padding and frame gap
  - reduced shell-backdrop and stage-atmosphere intensity
  - tightened toolbar spacing before the route canvas
- focused validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/index.css .codex/tasks/PRJ-825-authenticated-shell-canvas-opening-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- next smallest useful task:
  - compare the deployed authenticated shell
  - if the frame feels calm enough, move to the first sidebar exactness slice

## Fresh Authenticated Shell Utility Bar Calm Pass (2026-04-30)

- `PRJ-824` is now IN_PROGRESS as the first slice of the authenticated-shell
  group:
  - `.codex/tasks/PRJ-824-authenticated-shell-utility-bar-calm-pass.md`
- proof and gate update:
  - fresh production evidence for `home` now exists in:
    - `.codex/artifacts/prj823-prod-home-root-proof.png`
    - `.codex/artifacts/prj823-prod-home-proof.png`
  - current judgment:
    - `home` is now close enough to stop broad polishing and open the next
      dependent surface group
- purpose:
  - calm the authenticated utility bar so route surfaces gain more authority
- implemented in the current slice:
  - reduced utility-bar padding, chrome weight, and cardiness
  - tightened search, signal, pill, and account-control rhythm
  - slightly tightened the shell opening around the utility frame
- focused validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/index.css .codex/tasks/PRJ-824-authenticated-shell-utility-bar-calm-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- next smallest useful task:
  - compare the deployed authenticated shell
  - then continue the shell group before reopening route-local dashboard/chat/personality polish

## Fresh Public Home Bridge And Trust Closure Pass (2026-04-30)

- `PRJ-823` is now IN_PROGRESS as a bounded `home` lower-closure slice:
  - `.codex/tasks/PRJ-823-home-bridge-and-trust-closure-pass.md`
- purpose:
  - calm the remaining chip-like feeling in the proof bridge and trust band
- implemented in the current slice:
  - enriched proof-bridge pills with semantic iconography
  - tightened proof-pill spacing and material weight
  - tightened trust-band spacing, icon scale, and label rhythm
- focused validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-823-home-bridge-and-trust-closure-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- next smallest useful task:
  - compare the deployed `home`
  - if still needed, spend one final bounded `home` slice on remaining live first-viewport drift

## Fresh Public Home Header And Proof Iconography Pass (2026-04-30)

- `PRJ-822` is now IN_PROGRESS as a bounded `home` first-viewport slice:
  - `.codex/tasks/PRJ-822-home-header-and-proof-iconography-pass.md`
- purpose:
  - replace placeholder-like proof dots with real iconography and calm the
    header posture in the landing hero
- implemented in the current slice:
  - upgraded the micro-proof row to reuse semantic public glyphs
  - softened public nav link and button rhythm
  - tightened hero body and first-viewport spacing
- focused validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-822-home-header-and-proof-iconography-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- next smallest useful task:
  - compare the deployed `home`
  - if still needed, spend one last bounded `home` slice on final hero-note and trust-band drift

## Fresh Canonical 100 Slice Closure Map (2026-04-30)

- `PRJ-821` is now DONE as a planning freeze:
  - `.codex/tasks/PRJ-821-freeze-canonical-100-slice-closure-map.md`
- planning output:
  - `docs/planning/canonical-100-slice-closure-map.md`
- purpose:
  - convert the flagship parity lane into one numbered execution map instead
    of continuing with ad hoc micro-polish across surfaces
- frozen closure order:
  - public `home`
  - authenticated shell frame
  - authenticated sidebar
  - `dashboard`
  - `chat`
  - `personality`
  - final cross-surface proof
- map shape:
  - slices `1..15`: `home`
  - slices `16..25`: authenticated shell
  - slices `26..40`: sidebar
  - slices `41..55`: dashboard
  - slices `56..70`: chat
  - slices `71..85`: personality
  - slices `86..100`: final family-wide proof
- focused validation:
  - `git diff --check -- docs/planning/canonical-100-slice-closure-map.md .codex/tasks/PRJ-821-freeze-canonical-100-slice-closure-map.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- next smallest useful task:
  - keep `home` active until the live `95%` gate is confirmed
  - then move to the next numbered slice group instead of reopening random lanes

## Fresh Public Home Live Crop And Closure Pass (2026-04-30)

- `PRJ-820` is now IN_PROGRESS as a bounded `home` polish slice:
  - `.codex/tasks/PRJ-820-home-live-crop-and-closure-pass.md`
- purpose:
  - close the remaining wide-screen drift on `home` by tuning scenic crop,
    copy width, note-card positions, and the lower closure rhythm
- implemented in the current slice:
  - narrowed the desktop public-nav and hero-copy rhythm
  - shifted the scenic crop toward the canonical right-weighted composition
  - softened and repositioned the four landing note cards
  - narrowed and raised `feature bridge` and `trust band` to read more like
    one continuation
- focused validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/index.css .codex/tasks/PRJ-820-home-live-crop-and-closure-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- next smallest useful task:
  - compare the deployed `home`
  - if needed, do one final micro-pass only on live note positions and hero crop

## Fresh Public Home Scenic Crop And Note Polish (2026-04-30)

- `PRJ-819` is now DONE as a bounded `home` polish slice:
  - `.codex/tasks/PRJ-819-home-scenic-crop-and-note-polish-pass.md`
- purpose:
  - reduce the remaining card-heavy feel on `home` after the full-bleed shell
    pass
- implemented:
  - strengthened the scenic hero crop and slightly enlarged the stage feel
  - softened and repositioned the hero note cards
  - tightened `feature bridge` overlap, material, and proof rhythm
  - tightened `trust band` overlap and spacing so the lower closure reads more
    like one continuation
- focused validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/index.css .codex/tasks/PRJ-819-home-scenic-crop-and-note-polish-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- next smallest useful task:
  - compare deployed `home`
  - if needed, do one last note-position micro-pass only

## Fresh Public Home Full-Bleed Hero Shell Pass (2026-04-30)

- `PRJ-818` is now DONE as a bounded `home` shell-framing slice:
  - `.codex/tasks/PRJ-818-home-full-bleed-hero-shell-pass.md`
- purpose:
  - apply the user's explicit shell interpretation so `home` stops reading as
    a nested panel and starts reading as a true full-bleed flagship landing
- implemented:
  - replaced the nested public window structure with full-width
    `header / hero / footer` sections
  - moved the navigation into an overlay layer above the scenic hero
  - constrained public content rhythm without keeping the old nested panel
  - turned the hero into a `100vh` stage on desktop
  - retuned `feature bridge` and `trust band` to follow the new shell rhythm
- focused validation:
  - `Push-Location .\web; npm exec tsc -b; Pop-Location`
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css docs/ux/design-memory.md .codex/tasks/PRJ-818-home-full-bleed-hero-shell-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- next smallest useful task:
  - compare the deployed `home` against the canonical crop
  - then, only if needed, do one last micro-pass on note-card styling and
    bridge/trust spacing

## Fresh Web Copy Encoding Regression Fix (2026-04-30)

- `PRJ-817` is now DONE as a bounded shell-quality fix:
  - `.codex/tasks/PRJ-817-fix-web-copy-encoding-regression.md`
- purpose:
  - remove visible mojibake and broken Polish diacritics from the flagship
    web shell before more UX/UI polishing continues
- current audit found:
  - the real regression is concentrated in `web/src/App.tsx`
  - Polish route, auth, tools, settings, personality, and landing strings
    drifted through a mix of mojibake and plain-ASCII fallback forms
  - PowerShell console rendering can make some already-correct UTF-8 lines
    look suspicious, so raw file inspection must be the final truth source
- implemented in the current fix slice:
  - repaired the broken Polish flagship-shell strings in the source file
  - re-audited the public-entry and route-copy blocks after the repair
  - opened a dedicated task and recorded the detection guardrail in context
- focused validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx .codex/tasks/PRJ-817-fix-web-copy-encoding-regression.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md .codex/context/LEARNING_JOURNAL.md`
- next smallest useful task:
  - verify the deployed shell no longer shows broken Polish characters
  - then return to the active flagship route lane

## Fresh Chat Canonical Parity Closure Lane (2026-04-30)

- `PRJ-816` is now IN_PROGRESS as the active flagship surface:
  - `.codex/tasks/PRJ-816-chat-canonical-parity-closure-lane.md`
- purpose:
  - bring the `chat` route above the current `97%` parity gate before opening
    more flagship drift at once
- current audit found:
  - the chat route is functional and materially better than the older
    production proof, but it still reads as `thread + stacked support column`
    rather than the canonical `thread + embodied stage + cognitive rail`
  - the composer is calmer than earlier builds, yet it still lacks the
    integrated mode posture and feels more app-like than canonical
  - the right-side support hierarchy is too abstract and does not yet match
    the canonical order of intent, motivation, goal, memory, actions, and
    proactive continuity
- implemented in the first closure slice:
  - introduced a dedicated `PRJ-816` chat-only parity lane
  - restructured the chat workspace toward a three-part composition:
    thread column, embodied portrait stage, and cognitive context rail
  - upgraded the composer with integrated mode tabs and calmer support layout
  - replaced the abstract support stack with clearer canonical sections for
    current intent, motivation, active goal, related memory, suggested
    actions, and next proactive check-in
  - added calmer transcript metadata and plan-like ordered-list treatment
    inside assistant messages so structured replies read closer to the
    canonical conversation cards
- implemented in the latest refinement slice:
  - tightened transcript density, bubble sizing, and message-meta hierarchy so
    the thread reads closer to the canonical conversation cadence
  - enlarged and retuned the embodied portrait stage with calmer note-card
    density and a stronger scenic crop
  - compressed the right rail and shortened its copy so it feels more
    editorial and less widget-like
  - replaced rough text glyphs in the composer with real icon components
  - fixed the remaining chat-specific Polish copy and sample-plan text that
    still suffered from encoding drift
- implemented in the newest compression slice:
  - removed the extra explanatory paragraph from the chat topbar
  - tightened control-pill density and stage spacing one more step
  - increased embodied-stage authority while slightly narrowing the right rail
  - replaced the last remaining rail action glyph with CSS-owned icon output
- implemented in the latest cleanup slice:
  - removed the extra `Persona` control pill from the chat topbar
  - removed the mode-tab strip above the composer
  - simplified the composer tray so the route reads less tool-like and closer
    to the canonical conversation workspace
- implemented in the latest proportion slice:
  - replaced mini action-links inside the right rail with quieter support
    accents
  - tightened the right-rail card rhythm and padding
  - enlarged the persona crop and reduced portrait-note weight so the central
    embodied stage reads more authoritatively
- implemented in the latest transcript-first slice:
  - reduced the quick-action tray from four chips to three
  - removed the helper line below the composer
  - tightened transcript and composer spacing so the route keeps more focus on
    the conversation thread
- implemented in the latest polish slice:
  - replaced the headline star with the Aviary logomark treatment
  - reduced topbar control-pill density
  - tightened bubble widths and padding for a calmer transcript read
- implemented in the latest rail-shortening slice:
  - reduced the related-memory list from three items to two
  - reduced suggested actions from three items to two
  - shortened the proactive check-in label and tightened memory/action card
    spacing so the right rail reads less like a stacked list
- implemented in the latest rail-consolidation slice:
  - reduced motivation metrics from four to three
  - folded the proactive check-in into the active-goal card
  - tightened topbar and message-meta rhythm for a calmer flagship read
- implemented in the latest rail-copy slice:
  - reduced motivation metrics from three to two
  - removed the extra `Cognitive context` subtitle
  - shortened the lead-card and memory-copy text
  - simplified suggested actions into title-first rows
- focused validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-816-chat-canonical-parity-closure-lane.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- next smallest useful task:
  - compare the deployed chat against the canonical desktop reference
  - then, only if needed, spend one last bounded slice on portrait crop,
    topbar density, and closure polish

## Fresh Internal Chat And Telegram Message Quality Implementation (2026-04-30)

- `PRJ-811..PRJ-815` are now DONE:
  - `.codex/tasks/PRJ-811-fix-internal-chat-local-transcript-reconciliation.md`
  - `.codex/tasks/PRJ-812-render-safe-markdown-in-internal-chat.md`
  - `.codex/tasks/PRJ-813-prove-full-length-internal-chat-message-rendering.md`
  - `.codex/tasks/PRJ-814-improve-telegram-sentence-aware-segmentation.md`
  - `.codex/tasks/PRJ-815-align-telegram-and-internal-chat-markdown-support.md`
- implemented:
  - internal chat optimistic reconciliation now matches durable transcript
    truth by exact message id or role-aware event key instead of event id alone
  - internal chat renders safe Markdown as React elements, covering bold,
    italic, inline code, fenced code, ordered lists, and unordered lists
  - long chat message bodies expand naturally inside the transcript scroll
    surface
  - Telegram segmentation now prefers paragraph, newline, sentence, then word
    boundaries before hard splitting
  - Telegram supported Markdown metadata now includes italic and plain-text
    list readability
- evidence:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_delivery_router.py tests/test_telegram_client.py; Pop-Location`
    - `15 passed`
  - `Push-Location .\web; npm run build; Pop-Location`
    - passed
  - responsive proof:
    - `.codex/artifacts/prj811-815-chat-message-quality/chat-long-markdown-desktop.png`
    - `.codex/artifacts/prj811-815-chat-message-quality/chat-long-markdown-tablet.png`
    - `.codex/artifacts/prj811-815-chat-message-quality/chat-long-markdown-mobile.png`
    - `.codex/artifacts/prj811-815-chat-message-quality/chat-long-markdown-proof.json`
- additional validation:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py -k "telegram_round_trip_readiness_state or chat"; Pop-Location`
    - `9 passed, 108 deselected`
  - final diff check still pending before closure

## Fresh Internal Chat And Telegram Message Quality Plan (2026-04-30)

- `PRJ-810` is now DONE as the planning slice:
  - `.codex/tasks/PRJ-810-plan-internal-chat-and-telegram-message-quality.md`
- purpose:
  - turn the latest user notes about internal chat reliability, long-message
    readability, Telegram splitting, and Markdown rendering into one bounded
    execution lane
- planning output:
  - `docs/planning/internal-chat-and-telegram-message-quality-plan.md`
- analysis found:
  - internal chat already uses `/app/chat/history` plus optimistic local items,
    but local reconciliation can remove items too early because it matches by
    event id instead of exact message identity
  - internal chat currently renders transcript text directly, so Markdown
    markers such as `**bold**` and `*italic*` remain visible
  - Telegram already has delivery-layer segmentation and partial Markdown
    formatting, so the next work should refine sentence-aware splitting and
    supported Markdown rather than replace the delivery router
- new execution queue:
  - `PRJ-811` fix internal chat local transcript reconciliation
  - `PRJ-812` render safe Markdown in internal chat
  - `PRJ-813` prove full-length internal chat message rendering
  - `PRJ-814` improve Telegram sentence-aware segmentation
  - `PRJ-815` align Telegram and internal chat Markdown support
- validation:
  - planning-only code/doc cross-review; no automated tests run
- next smallest useful task:
  - `PRJ-811` fix internal chat local transcript reconciliation

## Fresh Skill-Guided Bounded Action Loop Plan (2026-04-30)

- `PRJ-803` is now DONE as the planning/architecture freeze:
  - `.codex/tasks/PRJ-803-freeze-skill-guided-bounded-action-loop-plan.md`
- purpose:
  - record the approved direction for skill-guided tool use and bounded
    action-owned execution loops before runtime implementation starts
- implemented in this slice:
  - added the canonical skill-guided bounded action loop contract to
    `docs/architecture/16_agent_contracts.md`
  - added the staged implementation plan in
    `docs/planning/skill-guided-bounded-action-loop-plan.md`
  - recorded that `web_search`, `web_browser`, and ClickUp are the first
    skill-tool binding targets
  - kept Gmail and other new providers deferred until the loop contract is
    proven on existing tools
- focused validation:
  - `git diff --check -- docs/architecture/16_agent_contracts.md docs/planning/skill-guided-bounded-action-loop-plan.md docs/planning/next-iteration-plan.md docs/planning/open-decisions.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md .codex/tasks/PRJ-803-freeze-skill-guided-bounded-action-loop-plan.md`
- next smallest useful task:
  - `PRJ-804` expose skill-tool bindings in `/app/tools/overview` and the web
    tools UI for search, browser, and ClickUp

## Fresh Landing Surface Closure At 95 Percent Parity Gate (2026-04-30)

- `PRJ-800L` is now DONE as the closed `home` surface:
  - `.codex/tasks/PRJ-800L-public-home-lower-story-and-auth-priority-pass.md`
- purpose:
  - finish the public landing to the approved `95%` parity gate before opening
    the next flagship route
- implemented across this closure lane:
  - generated and wired one new landing-specific scenic hero artwork based on
    the shared Aviary identity
  - kept the same persona continuity while removing dashboard/personality
    staging from the public-entry scene
  - tightened hero copy, bridge width, trust-band width, and auth-panel
    spacing to preserve a calmer first-screen read
  - froze a 10-step micro-slice queue for finishing the remaining `home`
    closure without opening other route lanes
  - executed the next home-only micro-slices for scenic crop, note-card
    density, bridge compaction, trust-band compactness, and quieter auth
    offset
  - executed one more viewport-only compaction pass for top-nav density,
    smaller bridge footprint, narrower trust band, and later auth entry
  - replaced inline session entry with a true auth modal opened from the
    landing CTAs and top-nav actions
  - changed the landing illustration treatment so the persona scene behaves
    more like scenic stage background than a nested image card
  - replaced numeric/dot placeholders with semantic iconography in the landing
    feature strip and trust band so the lower closure reads closer to the
    canonical public entry
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css docs/ux/design-memory.md docs/ux/canonical-web-screen-reference-set.md .codex/tasks/PRJ-800L-public-home-lower-story-and-auth-priority-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- closure evidence:
  - live `/` and `/login` proof now confirm the home route is above the `95%`
    parity gate for the active canonical spec
- post-closure interpretation refinement:
  - applied the user-requested wrapper cleanup for `home`
  - moved copy into the shared scenic hero stage instead of leaving it beside
    the background art
  - kept a clearer desktop `40/60` split between copy and scene inside that
    same shared stage
  - removed unnecessary outer scenic nesting so the background art has more room
  - retuned the landing note cards so the copy keeps its own protected zone
- next smallest useful task:
  - return to `dashboard` as the next single active flagship surface

## Fresh Dashboard Route-Corrected Hero Artwork Pass (2026-04-30)

- `PRJ-800F` remains IN_PROGRESS as the only active flagship surface:
  - `.codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md`
- purpose:
  - correct the newly integrated dashboard hero so it uses dashboard-appropriate
    props instead of repeating the `personality` book-and-writing composition
- implemented in this continuation:
  - generated and wired a new `v4` dashboard hero artwork based on the same
    Aviary identity
  - replaced the book/page/writing-tool staging with orchestration,
    cognition-field, and overview symbolism
  - kept the hero as one continuous scenic dashboard composition
- focused validation:
  - pending final rerun after this exact asset swap and truth sync
- remaining work before DONE:
  - final build and diff validation for the route-corrected dashboard hero
  - deploy-side screenshot proof for the new dashboard-specific artwork

## Fresh Dashboard Proportion Compression Pass (2026-04-30)

- `PRJ-800F` remains IN_PROGRESS as the only active flagship surface:
  - `.codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md`
- purpose:
  - keep closing the dashboard through proportion-only refinement instead of
    adding new elements, so the route reads more like one canonical tableau
- implemented in this continuation:
  - increased the relative authority of the central hero stage against the two
    signal columns
  - narrowed and softened the right editorial rail through tighter spacing and
    calmer card density
  - compressed the flow and lower closure so the bottom of the dashboard reads
    more panoramic and less stacked
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/index.css .codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- remaining work before DONE:
  - deploy-side screenshot proof for this exact proportions-only pass
  - then decide whether only hero crop and rail spacing drift remain

## Fresh Dashboard Hero Crop And Rail Spacing Pass (2026-04-30)

- `PRJ-800F` remains IN_PROGRESS as the only active flagship surface:
  - `.codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md`
- purpose:
  - spend one more bounded dashboard slice only on crop and spacing drift now
    that the larger compositional contract is already in place
- implemented in this continuation:
  - raised the dashboard persona crop and gave the center stage a touch more
    vertical authority
  - tightened the right editorial rail row density and recent-activity cadence
  - shortened the intention block and scenic closure panel for a calmer ending
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/index.css .codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- remaining work before DONE:
  - deploy-side screenshot proof for this exact crop-and-spacing pass
  - then decide whether `dashboard` crosses the `95%` gate or still needs one last micro-pass

## Fresh Dashboard Signal And Callout Scale Pass (2026-04-30)

- `PRJ-800F` remains IN_PROGRESS as the only active flagship surface:
  - `.codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md`
- purpose:
  - reduce the last visibly card-like details inside the dashboard hero and
    closure without touching the route structure
- implemented in this continuation:
  - scaled down side signal cards and their typography
  - scaled down the figure callouts and badge so the central persona keeps more
    visual authority
  - reduced the size of the harmony ring so the summary band feels less like a
    dashboard widget and more like part of one calm ending
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/index.css .codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- remaining work before DONE:
  - deploy-side screenshot proof for this exact scale pass
  - then decide whether `dashboard` is finally ready to close at the `95%` gate

## Fresh Dashboard Flow And Closure Rhythm Pass (2026-04-30)

- `PRJ-800F` remains IN_PROGRESS as the only active flagship surface:
  - `.codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md`
- purpose:
  - reduce the last middle-and-bottom widget rhythm so the dashboard keeps one
    calmer flagship read below the hero
- implemented in this continuation:
  - softened flow-step density, icon weight, and active-step emphasis
  - compressed the lower focus, memory, and reflection cards
  - tightened the summary-band shadow, chart spacing, and reflection tags so
    the closure feels less operational
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/index.css .codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- remaining work before DONE:
  - deploy-side screenshot proof for this exact flow-and-closure pass
  - then decide whether only tiny spacing drift remains before the `95%` gate

## Fresh Shared Persona Adaptation Rule Freeze (2026-04-30)

- purpose:
  - prevent future flagship assets from repeating the exact `personality`
    shot across `landing`, `dashboard`, and `chat`
- implemented in this rule freeze:
  - recorded that one shared Aviary identity must persist across routes
  - recorded that props and staging must change by module context
  - explicitly limited the book and writing-tool family to
    `personality`-appropriate compositions unless the user approves otherwise
- next visual implication:
  - future `dashboard` and `chat` hero-image passes should replace
    personality-specific props with route-specific guidance and
    conversation-oriented symbols

## Fresh Unified Dashboard Hero Artwork And Home Continuation Pass (2026-04-30)

- `PRJ-800F` remains IN_PROGRESS as the active flagship surface:
  - `.codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md`
- `PRJ-800L` continues only as the quieter public-home follow-up:
  - `.codex/tasks/PRJ-800L-public-home-lower-story-and-auth-priority-pass.md`
- purpose:
  - replace the split dashboard hero implementation with one integrated scenic
    artwork and remove the lingering non-canonical lower proof grid from
    `home`
- implemented in this continuation:
  - generated and wired one new wide dashboard hero artwork derived from the
    canonical dashboard and the shared Aviary persona figure
  - removed the separate dashboard atmosphere layer in code so the hero now
    reads from one raster stage instead of two visible image systems
  - removed the lingering lower proof-story block from `home`, leaving the
    auth panel as a quieter continuation below the trust closure
- focused validation:
  - pending final rerun after source-of-truth sync in this exact slice
- remaining work before DONE:
  - final build and diff validation for this combined dashboard/home pass
  - deploy-side screenshot proof for the new dashboard hero and the calmer
    public-home continuation

## Fresh Dashboard Figure-Caption And Rail Simplification Pass (2026-04-30)

- `PRJ-800F` remains IN_PROGRESS as the only active flagship surface:
  - `.codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md`
- purpose:
  - keep closing `dashboard` toward the canonical screenshot without opening a
    second route lane before this surface reaches the new `95%` gate
- implemented in this continuation:
  - removed the extra dashboard figure-caption card that had no close
    canonical counterpart
  - expanded `recent activity` to five leaner rows and removed the extra
    descriptive subline
  - trimmed the intention card to the shorter, more poster-like copy structure
    seen in the canonical dashboard
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- remaining work before DONE:
  - deploy-side screenshot proof for this exact dashboard continuation
  - then one last decision whether only crop/spacing drift remains

## Fresh Pixel-Perfect Surface Closure Workflow Freeze (2026-04-30)

- `PRJ-802` is now DONE as the UX process-hardening slice:
  - `.codex/tasks/PRJ-802-freeze-pixel-perfect-surface-closure-and-user-override-rules.md`
- purpose:
  - prevent repeated flagship UX drift by freezing a stricter `one surface at a
    time` workflow with a `95%` parity gate and explicit user-override rules
- implemented in this slice:
  - recorded the `95%` parity gate in repo instructions and canonical workflow
  - recorded that canonical screenshot plus explicit user notes becomes the
    active merged spec
  - recorded that contradictory user notes must be escalated before
    implementation
  - captured the recurring pitfall in the learning journal
- focused validation passed:
  - `git diff --check -- AGENTS.md docs/ux/canonical-visual-implementation-workflow.md docs/ux/design-memory.md .codex/context/LEARNING_JOURNAL.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md .codex/tasks/PRJ-802-freeze-pixel-perfect-surface-closure-and-user-override-rules.md`
- next workflow expectation:
  - finish one flagship surface to `95%+` before opening the next dependent
    lane

## Fresh Dashboard Canonical Action Hierarchy Correction (2026-04-30)

- `PRJ-800F` remains IN_PROGRESS as the current dashboard parity lane:
  - `.codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md`
- purpose:
  - correct the previous CTA-decluttering continuation so the dashboard matches
    the canonical screen more faithfully instead of merely becoming quieter
- implemented in this continuation:
  - restored the quiet support actions that are present in the canonical
    dashboard rail, flow card, lower cards, and scenic closure
  - restored the fourth guidance row and the fourth goal/reflection row where
    the canonical screen benefits from that denser editorial cadence
  - kept the actions visually soft so they read as support, not as loud app
    chrome
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- remaining work before DONE:
  - deploy-side screenshot proof for the corrected canonical-action hierarchy
  - then decide whether only crop/spacing drift remains

## Fresh Dashboard CTA Decluttering Continuation (2026-04-30)

- `PRJ-800F` remains IN_PROGRESS as the current dashboard parity lane:
  - `.codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md`
- purpose:
  - keep removing the last app-like dashboard cues now that non-canonical
    route sections were already pruned from the broader flagship set
- implemented in this continuation:
  - removed secondary CTA clutter from the right editorial rail, flow-phase
    card, lower goal/focus cards, and scenic closure
  - reduced guidance-row count so the right rail reads less like stacked
    workflow widgets
  - shortened goal and reflection lists to keep the lower dashboard region
    calmer and more panoramic
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- remaining work before DONE:
  - deploy-side screenshot proof for the decluttered dashboard slice
  - decide whether only micro-level crop/spacing drift remains afterward

## Fresh Non-Canonical Route Pruning Pass (2026-04-30)

- `PRJ-800M` is now DONE as the flagship section-pruning slice:
  - `.codex/tasks/PRJ-800M-prune-non-canonical-route-sections.md`
- purpose:
  - remove route-level sections that do not belong to the approved canonical
    `home / dashboard / chat / personality` compositions before doing more
    screenshot-parity work
- implemented in this slice:
  - removed the separate bottom feature strip from `chat`
  - removed the extra summary-chip row, preview-nav strip, and highlights panel
    from `personality`
  - removed the corresponding dead component/data/CSS remnants that only
    supported those non-canonical sections
  - explicitly re-checked `home` and confirmed that the older proof-stack
    section was already gone from the current JSX, so no additional whole
    section needed removal there
  - explicitly checked `dashboard` and left it structurally unchanged because
    its remaining drift is compositional rather than sectional
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-800M-prune-non-canonical-route-sections.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- remaining work after this cleanup:
  - deploy-side screenshot proof for the pruned route inventory
  - continue canonical parity work only on sections that genuinely belong to
    the target screens

## Fresh Dashboard Hero And Rail Tightening Continuation (2026-04-30)

- `PRJ-800F` remains IN_PROGRESS as the current dashboard parity lane:
  - `.codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md`
- purpose:
  - keep pushing the authenticated dashboard toward the canonical flagship
    tableau after `home` became calmer again
- implemented in this continuation:
  - increased center-stage authority through a wider figure column and calmer
    signal-card density
  - softened the editorial rail by shrinking row/token weight and tightening
    `guidance / recent / intention` cadence
  - compressed the lower dashboard closure so it reads less like stacked cards
    and more like one panoramic ending
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- parity evidence:
  - `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`
  - `.codex/artifacts/production-audit-2026-04-26/dashboard-desktop.png`
- remaining work before DONE:
  - deploy-side screenshot proof for the exact tightened dashboard slice
  - then decide whether `dashboard` is finally ready for closure or needs one last micro-pass

## Fresh Public-Home Lower Story And Auth Priority Pass (2026-04-30)

- `PRJ-800L` is now IN_PROGRESS as the next landing refinement slice:
  - `.codex/tasks/PRJ-800L-public-home-lower-story-and-auth-priority-pass.md`
- purpose:
  - keep the first landing screen product-first by promoting the dark trust
    closure and demoting the lower auth block into a quieter continuation
- implemented in this slice:
  - moved the trust band directly under the bridge, closer to the canonical
    first-screen closure
  - narrowed and softened the auth panel so it reads less like a co-equal hero
    companion
  - tightened the lower proof/auth region into a calmer editorial follow-up
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-800K-public-home-hero-content-canonical-pass.md .codex/tasks/PRJ-800L-public-home-lower-story-and-auth-priority-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- parity evidence:
  - `.codex/artifacts/prod-login-live-after-prj800k.png`
  - `docs/ux/assets/aion-landing-canonical-reference-v1.png`
- remaining work before DONE:
  - deploy-side confirmation for this exact lower-story/auth-priority slice
  - then decide whether `home` is finally calm enough to return focus to `dashboard`

## Fresh Public-Home Hero Content Canonical Pass (2026-04-29)

- `PRJ-800K` is now DONE as the previous landing hero-content slice:
  - `.codex/tasks/PRJ-800K-public-home-hero-content-canonical-pass.md`
- purpose:
  - bring the hero message itself closer to canonical posture after the
    first-viewport composition was stabilized
- implemented in this slice:
  - replaced the long slogan-like hero title with a shorter introductory lead
  - moved more explanation into calmer supporting body copy
  - rebalanced the hero proportions around the lighter message and shared persona
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-800J-public-home-first-viewport-live-closure-pass.md .codex/tasks/PRJ-800K-public-home-hero-content-canonical-pass.md`
- parity evidence:
  - `.codex/artifacts/prod-login-live-after-prj800k.png`
  - `.codex/artifacts/local-login-after-prj800k.png`
  - `docs/ux/assets/aion-landing-canonical-reference-v1.png`
- closed with parity evidence:
  - `.codex/artifacts/prod-login-live-after-prj800k.png`
  - `.codex/artifacts/local-login-after-prj800k.png`
  - the next remaining landing drift is intentionally carried into `PRJ-800L`

## Fresh Public-Home First Viewport Live Closure Pass (2026-04-29)

- `PRJ-800J` is now DONE as the previous viewport-only landing refinement:
  - `.codex/tasks/PRJ-800J-public-home-first-viewport-live-closure-pass.md`
- purpose:
  - close the next visible gaps in the first landing viewport after live proof
    from `PRJ-800I`
- implemented in this slice:
  - reduced headline dominance again through proportion tuning
  - increased persona-stage authority and pushed the shared figure closer to a
    central scenic read
  - tightened the bridge band so it ends the hero more cleanly and delays the
    lower auth surface from entering the first read
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/index.css .codex/tasks/PRJ-800I-public-home-live-hero-bridge-parity-pass.md .codex/tasks/PRJ-800J-public-home-first-viewport-live-closure-pass.md`
- parity evidence:
  - `.codex/artifacts/prod-login-live-after-prj800i-wait.png`
  - `.codex/artifacts/local-login-after-prj800j.png`
  - `docs/ux/assets/aion-landing-canonical-reference-v1.png`
- closed with parity evidence:
  - `.codex/artifacts/prod-login-live-after-prj800i-wait.png`
  - `.codex/artifacts/local-login-after-prj800j.png`
  - the next remaining hero drift is intentionally carried into `PRJ-800K`

## Fresh Public-Home Live Hero And Bridge Parity Pass (2026-04-29)

- `PRJ-800I` is now DONE as the previous live-driven landing refinement:
  - `.codex/tasks/PRJ-800I-public-home-live-hero-bridge-parity-pass.md`
- purpose:
  - reduce remaining first-viewport drift after the landing-first entry fix by
    calming hero copy, re-centering the shared persona stage, and simplifying
    the bridge band
- implemented in this slice:
  - shortened public-home bridge and feature-strip copy where text density was
    creating visual heaviness
  - tightened hero proportions so the left copy column yields more authority to
    the shared persona scene
  - repositioned and softened motif notes and persona crop for a more composed
    canonical tableau
  - removed the repeated hero quote from the bridge band and replaced it with a
    shorter editorial lead plus a lighter pill cluster
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-800I-public-home-live-hero-bridge-parity-pass.md`
- closed with parity evidence:
  - `.codex/artifacts/prod-login-live-after-prj800i-wait.png`
  - the next remaining drift is intentionally carried forward into `PRJ-800J`

## Fresh Public Entry Landing-First Fix (2026-04-29)

- `PRJ-800H` is now DONE as the structural public-entry correction:
  - `.codex/tasks/PRJ-800H-make-public-entry-landing-first.md`
- purpose:
  - make the public shell truly landing-first instead of auth-first on root entry
- implemented:
  - `/` now resolves to the public landing route instead of dashboard
  - the fullscreen bootstrap card now stays scoped to private routes
  - unauthenticated entry renders the public landing immediately on both `/` and `/login`
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx .codex/tasks/PRJ-800H-make-public-entry-landing-first.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- route evidence:
  - `.codex/artifacts/local-root-after-prj800h.png`
  - `.codex/artifacts/local-login-after-prj800h.png`
- highest-value remaining drift after this slice:
  - production must pick up the new revision so `/` can be rechecked live
  - then continue the next parity loop for `home` and `dashboard`

## Fresh Public-Home Production Parity Slice (2026-04-29)

- `PRJ-800G` is now IN_PROGRESS as the next production-driven home refinement:
  - `.codex/tasks/PRJ-800G-public-home-production-parity-slice.md`
- purpose:
  - bring the landing first viewport closer to canonical rhythm using the live
    `/login` screenshot as the parity source
- implemented in this slice:
  - shortened and calmed the hero headline block
  - replaced the heavier hero feature pills with a lighter micro-proof row
    based on existing trust-band content
  - compressed the overlapping feature bridge to feel less tall and less text-heavy
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-800G-public-home-production-parity-slice.md`
- parity evidence used:
  - `.codex/artifacts/prod-login-live-2026-04-29.png`
  - `docs/ux/assets/aion-landing-canonical-reference-v1.png`
- remaining work before DONE:
  - deploy-side screenshot proof for this exact slice
  - then continue the next public-home/dashboard micro-tuning loop

## Fresh Dashboard Editorial Parity Slice (2026-04-29)

- `PRJ-800F` is now IN_PROGRESS as the next dashboard closure loop:
  - `.codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md`
- purpose:
  - tighten the dashboard hero, editorial rail, and lower closure on the now
    stabilized shell and landing family
- implemented in this slice:
  - increased the center-stage authority by narrowing side columns and calming
    signal-card density
  - tightened the right rail so guidance, recent activity, and intention feel
    closer to one editorial support stack
  - compressed flow and summary spacing so the lower half reads more panoramic
    and less modular
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-800F-dashboard-editorial-parity-slice.md`
- remaining work before DONE:
  - deploy-side screenshot comparison against
    `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`
  - one more micro-tuning pass from live evidence if needed

## Fresh Public-Home Screenshot Parity Pass (2026-04-29)

- `PRJ-800E` is now DONE as the screenshot-driven landing refinement slice:
  - `.codex/tasks/PRJ-800E-public-home-screenshot-parity-pass.md`
- purpose:
  - push the public landing closer to canonical first-viewport parity by
    integrating the hero, motif scene, and bridge band more tightly
- implemented:
  - tightened the landing frame, hero proportions, and copy rhythm again
  - softened and enlarged the motif scene so the shared persona reads less
    like a boxed panel and more like one flagship atmosphere
  - turned the bridge band into an overlapping continuation of the hero instead
    of a separate strip below it
  - calmed the immediate lower story pacing so the first screen reads more like
    one editorial composition
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-800E-public-home-screenshot-parity-pass.md .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md`
- parity evidence:
  - `.codex/artifacts/local-home-after-prj800e-v2.png`
  - `docs/ux/assets/aion-landing-canonical-reference-v1.png`
- highest-value remaining drift after this slice:
  - deployed screenshot compare for the landing
  - then another dashboard parity loop on the stabilized shell and landing family

## Fresh Dashboard Canonical Convergence Pass (2026-04-29)

- `PRJ-800D` is now DONE as the next execution slice after `public home`:
  - `.codex/tasks/PRJ-800D-dashboard-canonical-convergence-pass.md`
- purpose:
  - compress the dashboard into a more canonical one-screen flagship read
- implemented:
  - removed the extra hero-note bridge and the non-canonical dashboard
    conversation-channel card
  - rebuilt the right rail into one editorial guidance surface plus quieter
    recent activity and scenic intention closure
  - converted the flow band into a track-plus-phase instrument instead of a
    stack of flow cards
  - rebuilt the bottom summary closure toward the canonical
    `system harmony / balance across layers / weekly summary` composition
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-800D-dashboard-canonical-convergence-pass.md`
- highest-value remaining drift after this slice:
  - deploy screenshot tuning for dashboard hero crop and editorial-rail spacing
  - tablet/mobile proof for dashboard parity
  - then the next screenshot-driven closure loop across `layout + sidebar + home + dashboard`

## Fresh Public-Home Structural Convergence Pass (2026-04-29)

- `PRJ-800C` is now DONE as the next execution slice after shell and sidebar:
  - `.codex/tasks/PRJ-800C-public-home-structural-convergence-pass.md`
- purpose:
  - move the landing closer to the canonical editorial story by strengthening
    the hero, calming the bridge band, and demoting auth below the product narrative
- implemented:
  - public nav density and hero proportion were tightened
  - the bridge band now reads more like one continuation of the hero and less
    like a row of equal cards
  - the lower public story now leads with proof/editorial content while auth
    behaves more like a supporting entry module
  - the bottom trust closure now carries a stronger dark-teal canonical mood
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md .codex/tasks/PRJ-800C-public-home-structural-convergence-pass.md`
- highest-value remaining drift after this slice:
  - deploy screenshot tuning for the public landing
  - the next major route-level pass is now `dashboard`

## Fresh Sidebar Pixel-Close Refinement Pass (2026-04-29)

- `PRJ-800B` is now DONE as the next execution slice after shell-frame
  calming:
  - `.codex/tasks/PRJ-800B-sidebar-pixel-close-refinement-pass.md`
- purpose:
  - move the authenticated desktop rail closer to the frozen canonical sidebar
    through tighter brand, nav, and support-card anatomy
- implemented:
  - the sidebar brand lockup is now more delicate and left-anchored
  - nav rows are calmer, denser, and closer to the canonical active-pill
    treatment
  - the health, identity, and quote cards now read more like one coherent
    support family and less like appended widgets
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md .codex/tasks/PRJ-800B-sidebar-pixel-close-refinement-pass.md`
- highest-value remaining drift after this slice:
  - deploy screenshot tuning for the sidebar
  - structural convergence of `public home`
  - later dashboard composition pass on top of the improved shell and rail

## Fresh Authenticated Shell Frame Exactness Pass (2026-04-29)

- `PRJ-800A` is now DONE as the first execution slice from the master parity
  ledger:
  - `.codex/tasks/PRJ-800A-authenticated-shell-frame-exactness-pass.md`
- purpose:
  - calm the authenticated parent shell before deeper route-level parity work
- implemented:
  - the desktop utility bar now behaves more like premium framing and less
    like generic app chrome
  - the shell gap and rail-to-canvas relationship were tightened
  - the wide desktop account panel was replaced with a compact anchored
    popover that no longer interrupts route composition
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/context/TASK_BOARD.md .codex/context/PROJECT_STATE.md .codex/tasks/PRJ-800A-authenticated-shell-frame-exactness-pass.md`
- highest-value remaining drift after this slice:
  - deploy screenshot tuning for the authenticated shell frame
  - sidebar pixel-close refinement on top of the calmer shell
  - structural convergence of `public home` and `dashboard`

## Fresh Layout Sidebar Home Dashboard Micro Parity Checklist (2026-04-29)

- `PRJ-801` is now DONE as a planning supplement to `PRJ-800`:
  - `.codex/tasks/PRJ-801-freeze-layout-sidebar-home-dashboard-micro-parity-checklist.md`
- checklist artifact:
  - `docs/planning/layout-sidebar-home-dashboard-micro-parity-checklist.md`
- purpose:
  - enumerate visible sub-elements so future parity work can no longer hide
    behind broad statements like "the shell is closer"
- status model:
  - `MATCHED`
  - `DRIFT`
  - `BLOCKED`
- current conclusion from the checklist:
  - the majority of high-impact sub-elements in `layout`, `sidebar`, `home`,
    and `dashboard` are still in `DRIFT`
  - this confirms that the lane still needs a disciplined structural execution
    sequence before final screenshot parity can be claimed

## Fresh Layout Sidebar Home Dashboard Master Parity Ledger (2026-04-29)

- `PRJ-800` is now DONE as a planning slice:
  - `.codex/tasks/PRJ-800-freeze-layout-sidebar-home-dashboard-canonical-parity-ledger.md`
- one new master ledger now defines the remaining convergence work for:
  - authenticated parent layout
  - authenticated sidebar
  - public layout and public home
  - dashboard
- audit artifact:
  - `docs/planning/layout-sidebar-home-dashboard-canonical-parity-master-ledger.md`
- key conclusion:
  - remaining drift is now primarily structural and hierarchical, not
    decorative
  - future work on this lane should prioritize:
    - shell/frame exactness
    - sidebar exactness
    - public-home structural convergence
    - dashboard one-screen flagship convergence
    - then screenshot parity closure
- explicit blocking issues now recorded:
  - sidebar inventory mismatch versus current route contract
  - authenticated shell still too app-like
  - public home still too auth-derived in its lower half
  - dashboard still too modular below the hero

## Fresh Shared Persona Chat Route Pass (2026-04-29)

- `PRJ-796` is now DONE as the next flagship continuity slice:
  - `.codex/tasks/PRJ-796-apply-shared-persona-to-chat-route.md`
- purpose:
  - move `chat` from route-specific portrait atmosphere toward the same
    embodied Aviary persona already frozen for other flagship routes
- implementation in progress:
  - the chat portrait panel now layers the shared canonical persona over the
    existing atmospheric backdrop
  - conversation-specific note cards now frame memory continuity, expression,
    and linked-channel posture
  - assistant transcript avatars now reuse the same persona crop instead of a
    generic letter avatar
- highest-value remaining drift after this slice:
  - deploy screenshot tuning for `chat` crop and support-column rhythm
  - another parity pass for `dashboard` and `personality` after the shared-persona chat proof

## Fresh Shared Canonical Persona Figure Freeze (2026-04-29)

- `PRJ-795` is now IN_PROGRESS as the next flagship persona-continuity slice:
  - `.codex/tasks/PRJ-795-freeze-shared-canonical-persona-figure-and-dashboard-pass.md`
- purpose:
  - freeze one shared canonical persona figure across flagship routes and stop
    route drift toward different humanoid artwork
- implementation in progress:
  - the supplied figure is now stored in:
    - `docs/ux/assets/aviary-persona-figure-canonical-reference-v1.png`
    - `web/public/aviary-persona-figure-canonical-reference-v1.png`
  - UX source-of-truth now requires reusing the same embodied persona across
    flagship modules
  - `landing`, `dashboard`, `sidebar`, and `personality` are being moved away
    from the older figure asset to the shared canonical persona
  - dashboard now begins a route-specific adaptation pass with anchored notes
    for identity, learned knowledge, and planning posture
- highest-value remaining drift after this slice:
  - chat-specific use of the same persona
  - deploy screenshot tuning for dashboard note rhythm and crop balance

## Fresh Backend Architecture Quality Audit And Improvement Plan (2026-04-29)

- `PRJ-785` is now READY as a planning/audit slice:
  - `.codex/tasks/PRJ-785-backend-architecture-quality-audit-and-improvement-plan.md`
- purpose:
  - compare the current backend against the canonical architecture and convert
    remaining quality risks into small, architecture-aligned follow-up tasks
- audit conclusion:
  - the backend is architecturally coherent and production health is green
  - no new memory, subconscious, proactive, or communication-preference
    subsystem is recommended
  - the next improvements should strengthen behavior proof, close remaining
    production follow-up evidence, and reduce the blast radius of large backend
    owners through behavior-neutral extraction
- production evidence checked:
  - `GET https://aviary.luckysparrow.ch/health` returned `status=ok`
  - deployed runtime build revision:
    `9f04a928f907afaa30d0bdeced6e21ce4b2dce53`
  - `release_readiness.ready=true`
  - `proactive.communication_boundary_contract` is present
  - semantic retrieval reports provider-backed `ready` posture
  - Telegram reports `provider_backed_ready`
- proposed follow-up order:
  - `PRJ-786` production communication-boundary backfill closure
  - `PRJ-787` behavior validation expansion for backend continuity
  - `PRJ-788` health surface ownership refactor
  - `PRJ-789` memory repository domain interface extraction
  - `PRJ-790` planning intent builder extraction
  - `PRJ-791` action domain executor extraction
  - `PRJ-792` proactive and subconscious decision evidence
  - `PRJ-793` governed affective assessment rollout
  - `PRJ-794` runtime script entrypoint and ops consistency audit

## Fresh Backend Continuity Validation And Ops Hardening (2026-04-29)

- `PRJ-787` is now DONE:
  - `.codex/tasks/PRJ-787-backend-continuity-behavior-validation-expansion.md`
  - `backend/tests/test_runtime_pipeline.py` now includes behavior scenarios
    for:
    - stored memory influencing later context
    - communication-boundary relations reaching expression
    - cross-user memory isolation under prompt-injection-style pressure
  - behavior validation CI gate passed:
    - `Push-Location .\backend; ..\.venv\Scripts\python scripts\run_behavior_validation.py --gate-mode ci --artifact-path artifacts\behavior_validation\prj785-report.json; Pop-Location`
    - result: `18 passed`, `gate_status=pass`
- `PRJ-788` is now DONE:
  - `.codex/tasks/PRJ-788-health-surface-ownership-refactor.md`
  - `backend/app/api/health_response.py` now owns final `/health` response
    assembly while the existing route keeps snapshot collection for this first
    behavior-neutral slice
  - focused health regression passed:
    - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py -k "health"; Pop-Location`
    - result: `51 passed, 66 deselected`
- `PRJ-794` is now DONE:
  - `.codex/tasks/PRJ-794-runtime-script-entrypoint-and-ops-consistency.md`
  - backend operator scripts that import `app.*` now bootstrap the backend root
    before imports when executed as direct files
  - operator script help regression passed:
    - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py -k "backend_operator_scripts_expose_help"; Pop-Location`
    - result: `8 passed, 42 deselected`
- `PRJ-786` remains a production-ops follow-up:
  - local session does not expose `DATABASE_URL`/production DB credentials
  - run from Coolify shell:
    - `python scripts/run_communication_boundary_backfill_once.py --dry-run --limit 500`
    - `python scripts/run_communication_boundary_backfill_once.py --limit 500`
- `PRJ-789..PRJ-793` remain intentionally separate backend slices:
  - repository, planning, and action extraction should not be bundled into the
    same commit as behavior validation and ops hardening
- full backend gate passed after the slice:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q; Pop-Location`
  - result: `980 passed in 105.96s`

## Fresh Proactive And Subconscious Decision Evidence (2026-04-29)

- `PRJ-792` is now DONE:
  - `.codex/tasks/PRJ-792-proactive-and-subconscious-decision-evidence.md`
- implemented:
  - proactive scheduler tick summaries now include:
    - `decision_reason_counts`
    - `delivery_guard_reason_counts`
    - bounded `decision_evidence`
  - evidence records candidate trigger, action status, actions, decision
    reason, delivery-guard reason, decision score, interrupt posture, and
    recent/unanswered counters
  - evidence is exposed through the existing `/health.proactive.scheduler_tick_summary`
    surface after a proactive tick runs
  - evidence intentionally avoids candidate text and chat id
- validation passed:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py -k "proactive"; Pop-Location`
    - result: `4 passed, 15 deselected`
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py -k "external_scheduler_cutover_proof"; Pop-Location`
    - result: `1 passed, 116 deselected`
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py -k "proactive"; Pop-Location`
    - result: `5 passed, 102 deselected`
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q; Pop-Location`
    - result: `981 passed in 106.20s`
- next backend slices remain:
  - `PRJ-789` memory repository domain interface extraction
  - `PRJ-790` planning intent builder extraction
  - `PRJ-791` action domain executor extraction
  - `PRJ-793` governed affective assessment rollout

## Fresh Communication Boundary Backfill And Health Contract (2026-04-29)

- `PRJ-783` is now DONE as the architecture-completion slice after
  `PRJ-778`:
  - `.codex/tasks/PRJ-783-implement-communication-boundary-backfill-and-health-contract.md`
- purpose:
  - close the gap where historical user-authored episode text may already
    contain communication-boundary instructions that predate the new relation
    model
- implemented locally:
  - `MemoryRepository.backfill_communication_boundary_relations(...)`
  - `backend/scripts/run_communication_boundary_backfill_once.py`
  - `/health.proactive.communication_boundary_contract`
  - operations runbook instructions for dry-run, user-scoped, and write runs
- validation passed:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_communication_boundary.py tests/test_memory_repository.py tests/test_api_routes.py -q; Pop-Location`
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q; Pop-Location`
  - `971 passed in 100.49s`
- deployment follow-up:
  - after deploy, run the production backfill dry-run and write-run from the
    app container or equivalent Coolify shell

## Fresh Public Home First-Viewport Pass (2026-04-29)

- `PRJ-784` is now IN_PROGRESS as the next landing-convergence slice:
  - `.codex/tasks/PRJ-784-public-home-first-viewport-canonical-pass.md`
- `web/src/App.tsx` now:
  - removes the extra public hero kicker
  - replaces the abstract right-side motif treatment with a real embodied
    figure stage using the approved figure asset
  - integrates the cognition cards directly into that stage
  - upgrades the first strip under the hero into a connected bridge band with
    proof/trust pills
- `web/src/index.css` now:
  - rebalances first-viewport hero proportions
  - adds landing-specific figure-stage styling and anchored note positioning
  - restyles the feature strip into a calmer bridge band
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-784-public-home-first-viewport-canonical-pass.md`
- fresh screenshot evidence captured:
  - `.codex/artifacts/local-public-home-hero-pass-v2-2026-04-29.png`
- highest-value remaining drift after this slice:
  - the hero still needs a closer match to the canonical bust-scale composition
  - the lower public story grid still feels more product-panel than editorial landing
  - dashboard remains the next structural route pass once public-home parity is steadier

## Fresh Flagship Frame Cleanup Pass (2026-04-29)

- `PRJ-782` is now IN_PROGRESS as the next layout-convergence slice:
  - `.codex/tasks/PRJ-782-remove-window-chrome-and-audit-layout-frame-drift.md`
- a deployed public-home audit confirmed one explicit mismatch:
  - the shared `WindowChrome` wrapper is unwanted shell ornament and should
    not be part of the canonical flagship layout
- `web/src/App.tsx` now:
  - removes `WindowChrome` from both the public and authenticated shell
    branches
  - keeps the premium framed shell while letting route content start directly
    inside the layout canvas
- `web/src/index.css` now:
  - removes obsolete `aion-window-chrome*` styling
  - slightly rebalances shell-body padding after the chrome removal
- source-of-truth updates now record the new direction:
  - `docs/planning/layout-dashboard-public-home-canonical-master-audit.md`
  - `docs/ux/design-memory.md`
  - `docs/ux/canonical-web-screen-reference-set.md`
- highest-value remaining drift after this slice:
  - public home hero still needs deeper canonical parity
  - dashboard still needs a new post-shell structural pass

## Fresh Canonical Sidebar Desktop Spine Pass (2026-04-29)

- `PRJ-781` is now IN_PROGRESS as the first implementation slice after the
  sidebar freeze:
  - `.codex/tasks/PRJ-781-implement-canonical-sidebar-desktop-spine-pass.md`
- `web/src/App.tsx` now:
  - introduces sidebar-specific icon primitives
  - replaces token-letter nav rows with icon-led one-line rows
  - adds a sidebar-specific brand block
  - rebuilds the support stack into:
    - compact health card
    - compact identity card
    - quieter aphorism closure card
  - keeps account access through the existing shell account state
- `web/src/index.css` now:
  - narrows and softens the rail material
  - redesigns active nav pill treatment
  - adds sidebar-specific brand, card, avatar, quote, and quiet-button styling
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css`
- highest-value remaining drift after this slice:
  - post-deploy pixel tuning of spacing, icon scale, and support-card proportions
  - explicit decision on full canonical nav inventory beyond current route contracts
- the latest local refinement narrowed the desktop rail further and tightened:
  - shell-frame gap
  - brand lockup scale
  - active-label contrast
  - support-card density
  - quote-signature treatment

## Fresh Canonical Sidebar Layout Freeze (2026-04-29)

- `PRJ-780` is now READY as a planning slice:
  - `.codex/tasks/PRJ-780-freeze-canonical-sidebar-layout-and-plan-shell-convergence.md`
- the supplied sidebar image is now frozen as the canonical authenticated rail:
  - `docs/ux/assets/aviary-sidebar-layout-canonical-reference-v1.png`
- UX source of truth now explicitly records this sidebar in:
  - `docs/ux/canonical-web-screen-reference-set.md`
- a detailed shell-planning audit now exists in:
  - `docs/planning/sidebar-layout-canonical-convergence-plan.md`
- key drift captured for future implementation:
  - current rail is too wide and too panel-like
  - current nav uses token letters and secondary descriptions instead of
    icon-led one-line rows
  - current support stack diverges in health-card, identity-card, and quote-card anatomy
  - canonical sidebar shows more modules than the current route contract
- recommended next implementation lane:
  - sidebar desktop shell pass using current route contracts only
  - explicit later decision on route expansion for the full canonical nav inventory

## Fresh Short-Term Memory And Proactive Style Respect Repair (2026-04-29)

- `PRJ-778` is now DONE as an implementation slice:
  - `.codex/tasks/PRJ-778-plan-short-term-memory-and-proactive-style-respect.md`
- fresh user evidence showed repeated proactive Telegram-style check-ins every
  ~30 minutes on 2026-04-29, despite user instructions not to write that often
  and not to greet on every message
- root cause was not simply a one-message context window or missing phrase
  exception:
  - foreground runtime already loads `RuntimeOrchestrator.MEMORY_LOAD_LIMIT=12`
  - proactive scheduler candidate selection is driven by persisted
    `proactive_opt_in` truth plus candidate state
  - `persist_episode()` writes `proactive_preference_update`, but
    `extract_episode_fields()` does not expose that field to reflection
  - relation updates currently cover delivery reliability, collaboration
    dynamic, and support intensity, but not contact cadence, interruption
    tolerance, or interaction rituals such as repeated greetings
- implementation now reuses existing relation/conclusion, reflection, planning
  intent, action persistence, proactive guard, and expression paths rather than
  introducing a new short-term memory subsystem
- backend now includes `backend/app/communication/boundary.py` as the shared
  communication-boundary model:
  - `contact_cadence_preference`
  - `interruption_tolerance`
  - `interaction_ritual_preference`
- planning now persists explicit communication-boundary directives as
  `maintain_relation` intents
- reflection now sees `relation_update`, `proactive_preference_update`, and
  `proactive_state_update` episode fields and can derive boundary relations
  from episode text
- proactive scheduler candidate selection, proactive planning, and delivery
  guardrails now block or dampen outreach from high-confidence boundary
  relations such as `on_demand`, `scheduled_only`, and `low_frequency`
- expression now passes communication-boundary summaries into OpenAI prompting
  and removes repeated greeting openings when the relation model says to avoid
  them
- external research grounding now supports the layered model:
  - working context is a bounded integration workspace
  - episodic memory records what happened
  - reflection derives higher-level state
  - communication common ground must be updated as interaction proceeds
  - interruption timing should be governed by context and user boundaries, not
    fixed cadence
- focused validation passed:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_communication_boundary.py tests/test_planning_agent.py tests/test_expression_agent.py tests/test_openai_prompting.py tests/test_memory_repository.py -q; Pop-Location`
- full backend gate passed:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q; Pop-Location`
  - `970 passed in 98.32s`

## Fresh Dashboard Structural Convergence Pass (2026-04-29)

- `PRJ-779` is now IN_PROGRESS as the next execution slice after `PRJ-776`:
  - `.codex/tasks/PRJ-779-dashboard-structural-canonical-convergence-pass.md`
- `web/src/App.tsx` now reshapes the dashboard through:
  - a hero-note bridge beneath the cognition scene
  - a more editorial right column ordered around guidance, intention, channel,
    and recent activity
  - a simpler `cognitive flow` bridge without the competing sidecard
  - a differentiated lower row that now includes a dedicated reflection card
  - a lighter summary-metric column so scenic closure carries more of the ending
- `web/src/index.css` now supports:
  - the new dashboard hero-note rhythm
  - calmer flow-bridge layout
  - compact summary metrics
  - reflection-list treatment in the lower row
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css`
- highest-value remaining drift after this slice:
  - browser screenshot parity for `public home + dashboard`
  - final crop and responsive tuning after deploy review

## Fresh Public Home And Parent Shell Frame Pass (2026-04-29)

- `PRJ-776` is now IN_PROGRESS as the first execution slice from the
  `PRJ-775` master audit:
  - `.codex/tasks/PRJ-776-implement-public-home-and-authenticated-shell-frame-pass.md`
- `web/src/App.tsx` now:
  - converts the unauthenticated `!me` branch from auth-first to landing-first
  - introduces a shared `WindowChrome` primitive
  - wraps authenticated routes in a flagship framed shell
- `web/src/index.css` now:
  - adds the shared browser-like chrome treatment
  - adds the new public-home layout system
  - adds responsive support for the new public and parent shell framing
- `docs/ux/design-memory.md` now records:
  - window-chrome shell framing
  - landing-first public entry
- focused validation passed:
  - `Push-Location .\web; npm run build; Pop-Location`
  - `git diff --check -- web/src/App.tsx web/src/index.css`
- highest-value remaining drift after this slice:
  - dashboard still needs its dedicated structural convergence pass on top of
    the new parent frame
  - browser screenshot parity is still required before calling the shell or
    landing final

## Fresh Layout, Public Home, Dashboard Master Audit (2026-04-28)

- `PRJ-775` is now DONE as a planning slice:
  - `.codex/tasks/PRJ-775-freeze-layout-dashboard-public-home-canonical-master-plan.md`
- one detailed master audit now exists in:
  - `docs/planning/layout-dashboard-public-home-canonical-master-audit.md`
- the audit focuses on the highest-value remaining structural drift:
  - shared authenticated parent layout
  - public layout
  - public home / landing
  - dashboard
- the main conclusion is that current drift is still primarily structural, not
  cosmetic:
  - the public surface is still auth-first instead of landing-first
  - the parent shell is still app-first instead of flagship-frame-first
  - dashboard still needs one coordinated structural pass, not only local
    polish
- the recommended next implementation lane is now explicit:
  - authenticated parent layout contract freeze
  - public layout + public home canonical rebuild
  - dashboard structural canonical convergence

## Fresh Production Deploy Drift Check (2026-04-28)

- production health was rechecked after the latest local flagship and chat UI
  slices:
  - `GET https://aviary.luckysparrow.ch/health` returned `status=ok`
  - `release_readiness.ready=true`
  - `/health.deployment.runtime_build_revision=35727c8f0451d9c7f95f338c345e67021084c219`
  - local `HEAD=38960d9555ea40359623d978f48bce4fa43b5f48`
  - `origin/main=35727c8f0451d9c7f95f338c345e67021084c219`
- current deploy drift:
  - production matches `origin/main`
  - production does not yet include local commits through `38960d9`
  - therefore deployed screenshot parity for `PRJ-743` should wait until the
    latest local web changes are pushed/deployed
- Telegram health in the same check showed provider-ready posture but zero
  process-local counters after the current deployed process start:
  - `round_trip_state=provider_backed_ready`
  - `ingress_attempts=0`
  - `delivery_attempts=0`
  - this is a live-process telemetry state, not proof by itself of webhook
    failure

## Fresh Internal Chat Send Responsiveness Fix (2026-04-28)

- `PRJ-774` is now DONE:
  - root cause was isolated to frontend send-state timing, not the backend chat
    contract:
    - the old UI only added an assistant pending item after
      `api.sendChatMessage(text)` returned
    - the user-authored message therefore stayed invisible until the later
      `/app/chat/history` refresh, making the user message and assistant answer
      appear together
  - `web/src/App.tsx` now appends a transient local user turn immediately on
    submit, marks it `sending`, marks it `delivered` when the real
    `/app/chat/message` response returns, appends the real assistant reply, and
    then reconciles local items away against `/app/chat/history`
  - `web/src/index.css` adds compact localized delivery-status treatment for
    sending, delivered, and failed local user turns
  - the durable source of truth remains the existing backend-owned
    `/app/chat/history` transcript; no second chat store, backend route, or
    persistence path was added
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`
    - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py -k "chat"; Pop-Location`
      - result: `8 passed, 109 deselected`
    - `git diff --check -- web/src/App.tsx web/src/index.css .codex/tasks/PRJ-774-fix-internal-chat-optimistic-turn-status.md`
  - browser-client UI verification was attempted against
    `http://127.0.0.1:5177/chat` but is blocked locally because the available
    Node runtime is `v22.13.0` and the in-app browser client requires
    `>= v22.22.0`
  - task file:
    - `.codex/tasks/PRJ-774-fix-internal-chat-optimistic-turn-status.md`

## Fresh Production Conversation Silence Triage (2026-04-28)

- production triage was run after the user reported sending messages and
  receiving no reply:
  - `GET https://aviary.luckysparrow.ch/health` returned `status=ok`
  - `release_readiness.ready=true`
  - `conversation_channels.telegram.round_trip_state=provider_backed_ready`
  - Telegram counters were all zero:
    - `ingress_attempts=0`
    - `ingress_processed=0`
    - `delivery_attempts=0`
    - `delivery_failures=0`
    - `last_ingress={}`
    - `last_delivery={}`
  - `POST https://aviary.luckysparrow.ch/event` with an API smoke payload
    returned a normal foreground reply and `runtime.action_status=success`
  - current evidence points away from foreground runtime failure and toward a
    Telegram webhook/linking/transport visibility issue
  - production is currently on runtime build revision:
    - `ba714425afba00a2756b318bad1f74b7f42405a7`
- `PRJ-770` is now DONE:
  - the dashboard now includes a conversation-channel status signal over
    existing backend health truth
  - `web/src/lib/api.ts` now exposes the minimal `/health` client contract
  - `web/src/App.tsx` derives Telegram status from:
    - `round_trip_ready`
    - ingress counters
    - delivery counters
    - `last_ingress`
    - `last_delivery`
    - attention pending count
  - `web/src/index.css` styles the dashboard-local status band for live,
    quiet, failure, loading, and unavailable states
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`
  - local dashboard smoke passed:
    - `http://127.0.0.1:5177/dashboard`
    - HTTP `200`, `content-type=text/html`
  - task file:
    - `.codex/tasks/PRJ-770-plan-dashboard-conversation-channel-status-banner.md`
- deeper production verification narrowed the runtime diagnosis further:
  - local session does not have `TELEGRAM_BOT_TOKEN` or
    `TELEGRAM_WEBHOOK_SECRET`, so Telegram API `getWebhookInfo` cannot be run
    from this shell without operator-provided secrets
  - a synthetic Telegram-shaped request without the webhook secret was sent to
    production `/event`
  - expected result was observed:
    - response: `403 Invalid Telegram webhook secret token.`
    - `/health.conversation_channels.telegram.ingress_attempts=1`
    - `/health.conversation_channels.telegram.ingress_rejections=1`
    - `/health.conversation_channels.telegram.last_ingress.state=rejected`
    - `/health.conversation_channels.telegram.last_ingress.reason=invalid_webhook_secret`
  - this proves production `/event` recognizes Telegram webhook payloads and
    updates telemetry when Telegram-shaped traffic reaches the app
  - therefore the likely incident boundary is upstream of runtime processing:
    Telegram webhook URL, webhook secret parity, bot/chat selection, or proxy
    delivery from Telegram into the production host
- `PRJ-773` is now DONE:
  - production webhook was reset through the existing server-owned
    `POST https://aviary.luckysparrow.ch/telegram/set-webhook` route
  - Telegram API returned:
    - `ok=true`
    - `result=true`
    - `description=Webhook was set`
  - post-repair `/health.conversation_channels.telegram` showed:
    - `ingress_attempts=2`
    - `ingress_processed=1`
    - `ingress_runtime_failures=0`
    - `delivery_attempts=1`
    - `delivery_successes=1`
    - `delivery_failures=0`
    - `last_ingress.state=processed`
    - `last_delivery.state=sent`
  - focused Telegram regressions passed:
    - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py -k "telegram" tests/test_delivery_router.py tests/test_telegram_client.py tests/test_runtime_pipeline.py -k "telegram"; Pop-Location`
    - result: `24 passed, 210 deselected`
  - task file:
    - `.codex/tasks/PRJ-773-verify-production-telegram-webhook-and-plan-repair.md`

## Fresh Chat Canonical Reference V4 Freeze (2026-04-28)

- user direction now replaces the active canonical `chat` visual target with a
  more precise approved snapshot:
  - source:
    - `C:\Users\wrobl\Desktop\UIUX\aion - chat - v4.png`
  - canonical repo asset:
    - `docs/ux/assets/aion-chat-canonical-reference-v4.png`
- `PRJ-769` is complete as a docs-and-asset source-of-truth slice:
  - `docs/ux/canonical-web-screen-reference-set.md` now points the `chat`
    route target at v4
  - active shell/chat convergence plans now use v4 as the `chat` comparison
    input
  - `PRJ-743` design-source references now point future parity work at v4
- implementation was intentionally not changed in this slice; the next
  smallest UX loop should compare the live `chat` route against v4 before
  making crop, spacing, support-column, composer, or shell-density changes

## Fresh Flagship Canonical Calm-Down Pass (2026-04-27)

- `PRJ-743` received another local implementation slice toward the canonical
  `dashboard / chat / personality` family:
  - dashboard closure is now shorter and more scenic
  - chat transcript is now calmer and less payload-browser-like
  - personality preview is now shorter and closer to the canonical overview
- the latest route-family implementation specifically removed:
  - the extra chat `response path` card
  - the flagship transcript payload-details drawer
  - the extra personality `layer map` explainer block
- one proof constraint is now explicit for future compare loops:
  - in-app browser automation is currently blocked locally because the
    available `node_repl` runtime reports Node `v22.13.0`, below the browser
    runtime requirement of `>= v22.22.0`
- the next smallest parity loop after this slice is now:
  - deploy the latest local shell pass
  - capture fresh logged-in `dashboard / chat / personality` screenshots
  - compare the new closure rhythm and right-column calmness against the
    canonical references
  - if drift still remains, focus the next slice only on:
    - dashboard hero-stage atmosphere / connectors
    - chat portrait-stage crop and support-column spacing
    - personality callout visibility and stage balance

## Fresh Flagship Hero-Stage Parity Pass (2026-04-28)

- `PRJ-743` received another local convergence slice focused only on the most
  visual flagship drift:
  - dashboard hero-stage atmosphere and card connectors
  - chat portrait crop and support-column posture
  - personality callout visibility and embodied-stage balance
- the latest route-family implementation now adds:
  - stronger connector tension from dashboard signal cards into the center
  - a larger and more atmospheric dashboard figure stage
  - a warmer and calmer chat portrait treatment with the planning inset moved
    lower
  - clearer connector endpoints and taller ceremonial space in personality
- the next smallest parity loop after this slice is now:
  - deploy the latest local shell pass
  - compare fresh logged-in screenshots against the canonical assets
  - if drift still remains, focus only on:
    - dashboard guidance-column tiering
    - chat topbar/control-pill density
    - personality right-column hierarchy and mobile crop

## Fresh Aviary Web Brand Parity Repair Plan (2026-04-27)

- fresh UX audit now confirms the current web implementation still leaks the old
  product name in user-facing shell output despite the approved Aviary baseline:
  - `Aviary` fonts are wired
  - `aviary-logomark.svg` exists in the web app
  - but multiple visible strings in `web/src/App.tsx` still render `AION`
  - the reusable wordmark component still outputs `AION` text
- `PRJ-768` is now ready for implementation:
  - one implementation-ready repair plan now lives in:
    - `.codex/tasks/PRJ-768-repair-aviary-web-brand-parity-and-shell-fidelity.md`
  - execution must repair:
    - shell brand lockup truth
    - locale copy parity
    - SVG logo activation parity
    - final responsive screenshot verification
  - focused implementation validation must include:
    - `Push-Location .\web; npm run build; Pop-Location`
    - real browser review on desktop, tablet, and mobile

- local implementation is now complete for the code-side repair slice:
  - active user-facing `AION` product-name strings were removed from the live
    shell source
  - the reusable shell wordmark now renders the visible `AVIARY` wordmark next
    to the provided SVG mark
  - lockup typography was tuned closer to the approved premium branding
  - remaining gap is now narrowed to:
    - real browser screenshot parity once the browser runtime is available

## Fresh Aviary Production Host Baseline (2026-04-26)

- user direction now freezes one production-host rename without adding a new
  deploy topology:
  - old host:
    - `https://personality.luckysparrow.ch`
  - new canonical host:
    - `https://aviary.luckysparrow.ch`
  - approved deploy shape remains:
    - one same-origin host for SPA plus backend routes
    - no `api.*` subdomain in the baseline
- `PRJ-767` is now complete locally:
  - operator and testing docs now point active release-smoke examples to:
    - `https://aviary.luckysparrow.ch`
  - runtime ops guidance now explicitly records:
    - same-origin deploy posture
    - Telegram webhook target:
      - `https://aviary.luckysparrow.ch/event`
  - project context truth is synchronized with the renamed host baseline
  - focused validation target for this slice is:
    - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_api_routes.py; Pop-Location`
    - `Push-Location .\web; npm run build; Pop-Location`

## Fresh Aviary Brand And Unnamed Personality Baseline (2026-04-26)

- fresh user direction now freezes one canonical first-party brand baseline for
  web UX/UI:
  - the product name is now `Aviary`
  - `Cormorant Garamond` for header and logo treatment
  - `Inter` for body and operational UI
  - the provided bird mark plus `AVIARY` wordmark is the canonical shell
    branding source
  - the embodied digital personality currently has no fixed proper name
- `PRJ-766` is now complete locally:
  - canonical brand docs now record the font pairing, logotype asset, and
    naming boundary in:
    - `docs/ux/brand-personality-tokens.md`
    - `docs/ux/aion-visual-motif-system.md`
    - `docs/ux/design-memory.md`
    - `docs/README.md`
    - `docs/architecture/architecture-source-of-truth.md`
  - the provided logo assets are now stored in:
    - `docs/ux/assets/aviary-logomark.svg`
    - `docs/ux/assets/aviary-logomark-preview.png`
    - `web/public/aviary-logomark.svg`
    - `web/public/aviary-logomark-preview.png`
  - the web shell now uses the Aviary brand lockup in the authenticated
    desktop rail and compact mobile header
  - the first-party typography baseline now uses:
    - `Cormorant Garamond` as `font-display`
    - `Inter` as the shared UI/body family
  - user-facing copy now treats:
    - `Aviary` as the app brand
    - the digital presence as intentionally unnamed
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`

## Fresh Canonical Multi-Channel Conversation And Relational Outreach Plan (2026-04-26)

- user direction now resolves the previously open cross-channel policy gate:
  - the authenticated app chat is the canonical conversation owner
  - linked Telegram is an ingress/egress mirror over the same continuity after
    explicit linking
  - user-authored Telegram turns should enter canonical app continuity and
    receive mirrored replies on both app truth and Telegram transport
  - proactive propagation may adapt by relation and channel fit, but silent
    internal wakeups remain allowed
  - transport adaptation may segment long Telegram delivery, but it must
    preserve one canonical reply meaning
- `PRJ-764` is now complete:
  - architecture and ops truth are updated for canonical multi-channel
    conversation and relational outreach
  - one execution-ready plan now lives in:
    - `docs/planning/canonical-multi-channel-conversation-and-relational-outreach-plan.md`
  - the execution queue is now grouped into:
    - Group A: contract freeze
    - Group B: channel-fit memory and preference inputs
    - Group C: canonical ingress and mirrored egress
    - Group D: relational proactive channel choice
    - Group E: observability, testing, and rollout proof
- the next smallest execution slice in this lane is now `PRJ-750`:
  - freeze the canonical multi-channel conversation contract in implementation
    truth and tests before channel-behavior code changes

## Fresh Proactive Transcript Truth And Conscious Outbound Governance Plan (2026-04-26)

- fresh production analysis now confirms one runtime-truth drift in the
  no-UI conversation baseline:
  - scheduler-owned proactive ticks can surface as `Ty/api` transcript entries
    with synthetic text such as `time check-in follow up`
  - the drift is not only UI-facing
  - it also reflects a missing explicit communication-governance rule between:
    - user-originated turns that must always receive a reply
    - scheduler or subconscious wakeups that may stay silent unless conscious
      evaluation finds real outreach value
- `PRJ-744` is now complete:
  - the repo now contains one execution-ready plan in:
    - `docs/planning/proactive-transcript-truth-and-conscious-outbound-governance-plan.md`
  - the plan freezes the repair into four bounded slices:
    - `PRJ-745` Freeze transcript truth and communication governance contract
    - `PRJ-746` Repair transcript projection and runtime persistence semantics
    - `PRJ-747` Tighten proactive wakeup execution and anti-spam behavior
    - `PRJ-748` Add regression proof, runbook notes, and context sync
  - the plan also records one explicit decision gate before any
    cross-channel proactive escalation is implemented:
    - conservative no-escalation
    - delivery-failure-only escalation
    - silence-window escalation with explicit preference ownership
- local execution on 2026-04-26 is now complete for `PRJ-745..PRJ-748`:
  - `PRJ-745`
    - architecture now freezes one explicit transcript-truth and
      communication-governance contract
  - `PRJ-746`
    - episodic persistence now marks transcript visibility explicitly
    - `/app/chat/history` no longer projects scheduler-owned synthetic prompts
      as `role=user`
  - `PRJ-747`
    - plain `time_checkin` wakeups are now materially harder to escalate into
      outbound chatter without active-work or relation signal support
    - unanswered proactive counting now ignores internal/system memory rows
      instead of resetting the anti-spam streak
  - `PRJ-748`
    - regression coverage now pins transcript truth and silent wakeup posture
    - runbook and context truth are synchronized with the repaired behavior
- validation completed locally:
  - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_api_routes.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py; Pop-Location`
- the next explicit decision in this lane is no longer transcript repair
- it is the still-open product policy gate for cross-channel proactive
  escalation after silence:
  - no escalation
  - delivery-failure-only escalation
  - silence-window escalation with explicit preference ownership

## Fresh Dashboard Route Baseline (2026-04-26)

- `PRJ-742` is now complete locally:
  - the authenticated shell now has one real `/dashboard` route as the first
    post-login destination
  - default route normalization now lands authenticated users on
    `dashboard` instead of dropping directly into `chat`
  - shell navigation and mobile route navigation now include:
    - `dashboard`
    - `chat`
    - `personality`
    - `tools`
    - `settings`
  - the new flagship dashboard reuses existing shell data and motifs through:
    - central embodied figure stage
    - left and right signal cards
    - insights and guidance side column
    - cognitive-flow band
    - lower goal, focus, memory, and reflection surfaces
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`
- the next explicit parity task is now `PRJ-743`:
  - route-family material polish across `dashboard`, `chat`, and `personality`
  - responsive and accessibility proof
  - local and deployed screenshot parity against the canonical route assets
- dashboard-specific compare-loop planning is now explicit in:
  - `docs/planning/dashboard-canonical-convergence-loop-plan.md`
  - the main currently recorded dashboard drift is no longer route absence
  - it is now:
    - hero-stage atmospheric depth
    - stronger connective detail around the figure
    - guidance-column tiering
    - cognitive-flow integration
    - bespoke art need for some dashboard surfaces
- one additional dashboard asset pass is now complete locally:
  - scenic intention-card artwork now exists and is wired into the route
  - scenic summary-band artwork now exists and is wired into the route
  - this reduces the flat CSS-only look in the dashboard closure surfaces
  - the next most valuable dashboard gap remains:
    - hero-stage connective detail and atmosphere
    - real authenticated screenshot parity on deploy
- one further flagship-route pass is now complete locally:
  - the shared utility bar now carries canonical-style continuity, language,
    and linked-channel signals instead of a more generic search-first posture
  - dashboard now includes a dedicated hero-stage atmosphere asset plus
    stronger scenic captioning and connective ornament
  - chat now has a calmer ambient overlay
  - personality now has explicit callout connectors to strengthen the
    embodied-system reading
- the next most valuable remaining route-family gap is now:
  - browser-verified proportion tuning for the dashboard hero stage
  - possible cognitive-flow de-modularization if the band still feels too
    component-like after deploy
  - authenticated deployed screenshot parity for `dashboard`, `chat`, and
    `personality`
- another local visual pass is now complete:
  - the dashboard cognitive-flow band has been simplified materially
  - the personality right-column insight family now has a stronger premium
    hierarchy
- the next most valuable remaining route-family gap is now narrower:
  - deployed screenshot parity
  - final dashboard hero proportion tuning
  - final chat and personality spacing polish after real-browser review
- one more local proportion pass is now complete:
  - dashboard center-stage dominance is stronger
  - chat is slightly more transcript-first
  - personality hero is more ceremonial and closer to the canonical preview
- the next most valuable remaining route-family gap is now:
  - deployed screenshot parity
  - final shell and spacing tuning after real-browser comparison
  - possible last dashboard-hero crop pass if production still feels flatter
    than the canonical reference
- one logged-in production audit is now complete for the three flagship
  authenticated routes:
  - evidence now exists in:
    - `.codex/artifacts/production-audit-2026-04-26/`
  - the detailed audit and final convergence queue now live in:
    - `docs/planning/flagship-production-audit-and-final-convergence-plan.md`
- the latest local implementation pass now answers the highest-value audited
  drift through:
  - removing redundant route-hero banners from `dashboard` and `personality`
  - shortening the dashboard by removing the extra module-entry / route
    highlights row
  - adding a premium starter transcript for empty-history `chat`
  - moving the `chat` portrait panel higher inside the support column
  - removing the long payload-browser section from the flagship
    `personality` route
- the next smallest remaining parity loop after this pass is now:
  - redeploy and capture fresh logged-in screenshots
  - verify that dashboard height and rhythm are now close enough to the
    canonical overview
  - if needed, run one final crop/connector/material pass on:
    - dashboard hero stage
    - chat portrait stage
    - personality callout visibility

## Fresh Canonical Screen-Set Freeze (2026-04-26)

- fresh user direction now freezes four route-level web references as the
  canonical UX target for convergence work:
  - landing
  - dashboard
  - personality
  - chat
- `PRJ-733` is now complete:
  - the approved route assets are now stored in:
    - `docs/ux/assets/aion-landing-canonical-reference-v1.png`
    - `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`
    - `docs/ux/assets/aion-personality-canonical-reference-v1.png`
    - `docs/ux/assets/aion-chat-canonical-reference-v2.png`
  - the canonical route-screen set and parity workflow now live in:
    - `docs/ux/canonical-web-screen-reference-set.md`
  - future implementation and polish slices touching these routes must capture
    post-deploy screenshot proof and compare it directly against the matching
    canonical asset before claiming visual convergence

## Fresh Canonical Shell-Convergence Analysis (2026-04-26)

- fresh production and local screenshot review now exposes one remaining
  motif-led web gap:
  - the current authenticated shell and `chat` route are directionally strong,
    but still drift from the canonical route targets in composition, shell
    weight, and support-panel hierarchy
- the main problem is no longer missing art direction
- the main problem is now convergence between:
  - the parent authenticated shell
  - the calmer canonical `chat` target
  - the richer canonical `personality` target
- `PRJ-734` is now complete:
  - the repo now contains one execution-ready convergence plan:
    - `docs/planning/canonical-authenticated-shell-and-chat-convergence-plan.md`
  - the plan freezes the main drift categories:
    - shell is still too heavy and dashboard-like for canonical `chat`
    - transcript and support panels still expose too much process structure
    - right-column support should become calmer, smaller, and more ambient
    - cross-route shell grammar still needs stronger parent-frame consistency
- planned execution order for this lane:
  - `PRJ-735` Shared Authenticated Shell Spine And Chrome Reduction
  - `PRJ-736` Chat Transcript, Quick Actions, And Composer Convergence
  - `PRJ-737` Chat Support Column And Ambient Embodiment Convergence
  - `PRJ-738` Personality Convergence On The Shared Canonical Shell
  - `PRJ-739` Shared Route Art, Material, And Typography Polish
  - `PRJ-740` Responsive, State, And Accessibility Proof
  - `PRJ-741` Production Screenshot Parity And Baseline Freeze
  - a later detailed parity pass now tightens that execution into the current
    flagship route family:
    - shared dashboard-first shell framing
    - `chat`
    - `personality` preview
  - execution-ready detailed plan:
    - `docs/planning/dashboard-chat-personality-canonical-parity-plan.md`
- implementation progress on 2026-04-26:
  - `PRJ-735` is now complete locally:
    - the authenticated shell rail is lighter, narrower, and less visually dominant
    - `chat` now replaces the large explicit process rail with a calmer support-column structure
    - the right side now combines:
      - smaller conversation-context cards
      - a softer portrait block
      - a condensed response-path summary
    - the composer zone now reads more like one integrated premium tray
    - focused validation passed:
      - `Push-Location .\web; npm run build; Pop-Location`
  - the next smallest visual gap is now `PRJ-736`:
    - transcript cards still need to feel softer and less inspector-like
    - top controls are still slightly denser than the canonical target
    - the quick-action plus composer area still has room for tighter premium integration
  - `PRJ-736` is now complete locally:
    - top controls now use lighter stacked pill hierarchy instead of heavier label-value chips
    - transcript metadata, message copy, and detail affordances now read more editorially
    - quick actions and composer now form one tighter bottom action region
    - focused validation passed:
      - `Push-Location .\web; npm run build; Pop-Location`
  - the next remaining visual gap now shifts toward:
    - final cross-route premium polish
    - `personality` convergence onto the refined shell
    - responsive and post-deploy screenshot parity proof
  - `PRJ-737..PRJ-739` are now complete locally:
    - the authenticated shell now has a richer dashboard-first utility bar and
      stronger flagship framing
    - `personality` now uses a route-specific embodied figure asset:
      - `docs/ux/assets/aion-personality-figure-reference-v1.png`
      - `web/public/aion-personality-figure-reference-v1.png`
    - the `personality` top preview now includes:
      - anchored identity/knowledge/planning/skills/role callouts
      - a mind-layers timeline panel
      - stronger conscious/subconscious/recent-activity side panels
    - focused validation passed:
      - `Push-Location .\web; npm run build; Pop-Location`
  - the next remaining parity gap is now narrower and more explicit:
    - final shared premium polish across `dashboard-first shell + chat + personality`
    - responsive desktop/tablet/mobile proof
    - post-deploy screenshot comparison against the canonical assets
  - one more premium polish pass is now complete locally:
    - the shared shell now has calmer flagship framing with richer utility-bar context
    - the left rail now reads more like a narrative premium surface and less
      like a utility-only sidebar
    - `chat` now has a cleaner canonical hierarchy through:
      - lighter route headline treatment
      - less duplicate account chrome
      - a more integrated composer tray with embedded support actions
    - `personality` now has one extra canonical cue:
      - a preview-tab strip that strengthens the route's overview posture
    - focused validation passed:
      - `Push-Location .\web; npm run build; Pop-Location`

## Fresh Profile Local-Time Fix (2026-04-26)

- fresh user-reported local-time drift now seeds one bounded continuity fix
  through `PRJ-732`
- `PRJ-732` is now complete:
  - authenticated profile settings now persist one explicit `utc_offset`
    value in `aion_profile`
  - `/app/me/settings` and the web settings screen now expose that offset as
    bounded `UTC±HH:MM` user input
  - runtime now localizes current-turn timestamp truth from the stored profile
    offset before the personality answers date or time questions
  - focused validation passed:
    - backend targeted suite passed
    - web production build passed

## Fresh Data Reset Analysis (2026-04-25)

- fresh user product and ops analysis now seeds one bounded destructive-data
  lane through `PRJ-722`:
  - the repo needs one explicit split between:
    - operator-owned production cleanup during the Telegram-first to web-first
      transition
    - authenticated self-service reset of one user's runtime data
  - the current backend already has the right ownership boundaries:
    - backend-owned auth/session
    - backend-owned profile/settings
    - per-user runtime continuity keyed by `user_id`
  - the main missing piece is not a new subsystem but one shared cleanup owner
    plus product and ops contracts for destructive behavior
- `PRJ-718` is complete:
  - the repo now contains one execution-ready plan in
    `docs/planning/user-data-reset-and-production-cleanup-plan.md`
  - the plan freezes the safe boundary that production-wide cleanup must stay
    operator-only while account settings may expose only per-user runtime reset
  - later user clarification now freezes that per-user reset as:
    - preserve connected APIs, linked integrations, and user settings
    - clear runtime continuity so the account can start fresh without
      reconfiguration
- planned execution order for this lane:
  - `PRJ-719` Reset Boundary Contract And Retention Policy Freeze
  - `PRJ-720` Shared Backend Cleanup Owner And Operator Script
  - `PRJ-721` Account Settings Reset UX And Confirmation Flow
  - `PRJ-722` Regression Proof, Ops Runbook, And Context Sync
- `PRJ-719` is now complete:
  - the reset retention boundary is now frozen around one explicit split:
    - preserve auth identity, profile settings, linked integrations, linked
      channels, and user-managed operational preferences
    - remove per-user runtime continuity, adaptive state, internal planning
      state, and queue/proposal state
  - the first implementation also now freezes session posture:
    - self-service reset revokes all auth sessions, including the current one
  - operator-owned production cleanup remains separate from product UI and
    still targets runtime-only cleanup first
- `PRJ-720` is now complete:
  - backend now has one shared runtime-cleanup owner in
    `MemoryRepository` reused by:
    - `POST /app/me/reset-data`
    - operator cleanup scripts
  - self-service reset now clears runtime continuity, preserves auth/profile
    boundary fields, preserves user-managed operational preferences, and
    revokes all auth sessions
  - operator entrypoints now exist for:
    - `single_user_runtime_reset`
    - `runtime_only_preserve_auth`
- `PRJ-721` is now complete:
  - the authenticated settings route now exposes one dedicated destructive
    reset card on top of the shared backend cleanup owner
  - the flow requires the exact confirmation phrase before enabling reset
  - success now drops the local session back to `/login` after backend session
    revocation, keeping the product behavior aligned with the backend contract
- `PRJ-722` is now complete:
  - full-lane validation is now green:
    - backend: `937 passed`
    - web: production build passed
  - runtime ops guidance now documents:
    - self-service reset boundary
    - bounded operator cleanup commands
    - destructive guardrails
  - the destructive-data lane seeded through `PRJ-722` is now complete

## Fresh Visual Motif Planning (2026-04-26)

- fresh user-approved design direction now seeds one bounded UX/UI lane through
  `PRJ-731`
- the approved direction keeps the current product and architecture boundaries:
  - backend-owned `/app/*` contracts stay unchanged
  - route topology stays intact unless a later task explicitly changes it
  - the new work is visual-system, layout, illustration, and responsive-proof
    scope
- the new design source is now frozen in:
  - `docs/ux/assets/aion-visual-motif-reference.png`
  - `docs/ux/aion-visual-motif-system.md`
- planned execution order for this lane:
  - `PRJ-723` Freeze AION Visual Motif And V1 Web UX Direction
  - `PRJ-724` Freeze Dashboard-First Visual System And Component Contract
  - `PRJ-725` Shared Tokens, Surfaces, And Motif Infrastructure
  - `PRJ-726` Authenticated Dashboard Shell And Responsive Layout Foundation
  - `PRJ-727` Dashboard Continuity, Flow, And Module Entry Sections
  - `PRJ-728` Dashboard Proof Across States, Accessibility, And Breakpoints
  - `PRJ-729` Freeze Personality Module Information Architecture And Motif Mapping
  - `PRJ-730` Personality Module Implementation On Shared Visual Foundations
  - `PRJ-731` Cross-Module Proof, Design Memory Update, And Future-App Baseline Sync
- `PRJ-723` is now complete:
  - the concept image is stored in the repository as the approved UX snapshot
  - the motif, constraints, route translation rules, and future asset family
    are now documented in `docs/ux/aion-visual-motif-system.md`
  - the next web visual lane is now explicit and execution-ready
  - the detailed rollout plan now prioritizes dashboard foundation first and
    `personality` second, both on top of one reusable component system
- implementation progress on 2026-04-26:
  - `PRJ-724..PRJ-727` are complete locally:
    - the web shell now has one dashboard-first visual foundation with shared
      motif-aware surfaces and background primitives in `web/src/index.css`
    - `/chat` now acts as the authenticated front door with a motif-led hero,
      transcript-first continuity panel, cognitive-flow rail, and route-entry
      cards for deeper modules
    - `settings`, `tools`, and `personality` now reuse the same shared surface
      language instead of sitting in the previous flatter shell styling
    - the latest local app pass now pushes the shared contract further:
      - `settings` and `tools` now open with the same hero structure as the
        dashboard shell
      - `personality` now includes the richer embodied layer map and pipeline
        rail planned for the motif-based route
      - mobile authenticated navigation now has an explicit route strip
      - the chat composer no longer blocks transcript reading order
    - focused validation passed:
      - `Push-Location .\web; npm run build; Pop-Location`
  - `PRJ-728` is now `IN_PROGRESS`:
    - initial mocked proof now exists for:
      - `chat` desktop and mobile
      - `personality` desktop and mobile
      - `tools` desktop
      - `settings` desktop
    - evidence currently lives in `.codex/artifacts/`
    - the chat route has now moved into a stronger reference-aligned shell:
      - desktop left rail
      - chat-specific top control bar
      - transcript + cognitive flow + portrait composition
      - bottom feature strip tied to continuity, channels, memory, reflection,
        and privacy
    - chat now also has a real route-specific art asset instead of a CSS-only
      symbolic portrait zone:
      - `docs/ux/assets/aion-chat-background-reference-v1.png`
      - `web/public/aion-chat-background-reference-v1.png`
      - refreshed proof:
        - `chat-background-asset-pass-desktop.png`
        - `chat-background-asset-pass-mobile.png`
    - refreshed chat evidence now includes:
      - `chat-reference-pass-desktop.png`
      - `chat-reference-pass-mobile-v2.png`
    - a further premium-polish pass is now complete locally:
      - stronger live-state cue in the header
      - planning overlay inside the portrait zone
      - more editorial bottom feature strip treatment
      - proof: `chat-premium-polish-pass-desktop.png`
    - before closure, the slice still needs:
      - tablet capture
      - live backend state coverage for loading, empty, error, and success
      - keyboard, touch, pointer, contrast, and reduced-motion review
      - post-deploy screenshot comparison against
        `docs/ux/canonical-web-screen-reference-set.md` for motif-led routes
    - fresh canonical review also showed that `PRJ-728` alone is not enough to
      declare convergence:
      - the current `chat` shell still needs one additional design-and-implementation lane
        through `PRJ-741` before parity should be treated as accepted

## Current Active Lane

- `PRJ-655` freezes the approved `v2` product topology:
  - `backend/`
  - `web/`
  - `mobile/`
- `PRJ-655..PRJ-666` are now complete:
  - repository truth, auth/session baseline, app-facing client APIs, web shell,
    and deploy-proof topology are aligned for the first `v2` browser release
- `PRJ-669..PRJ-674` are now seeded as the next product-facing web lane:
  - add one backend-owned tools and channels overview for the browser client
  - keep provider secrets outside product UI
  - add user-owned tool enablement where architecture already allows it
  - plan Telegram as identity linking, not secret entry
- `PRJ-669..PRJ-670` are complete:
  - the app-facing tools and channels contract is frozen
  - backend now exposes grouped tools and channels truth through
    `/app/tools/overview`
- `PRJ-671` is complete:
  - web now renders the first tools screen directly from backend truth
- `PRJ-672` is complete:
  - allowed tool and channel preferences now persist through backend truth and
    are editable from the web tools screen
- `PRJ-673` is complete:
  - backend auth identities can now generate a bounded Telegram link code
  - Telegram `/link CODE` confirmation now binds the chat identity back to the
    authenticated app user
  - the web tools screen now exposes the link-code flow instead of pretending
    Telegram is ready without user linking
- `PRJ-674` is complete:
  - tools/channels validations now pin backend truth, Telegram link-state
    transitions, and provider-blocked posture
  - testing, overview, ops, and env/config docs now describe the same
    backend-owned product boundary
- the tools-and-channels web lane is now complete through `PRJ-674`
- `PRJ-667` is complete:
  - the initial mobile stack is now frozen as Expo-managed React Native with
    TypeScript and Expo Router
  - the shared backend-owned client-contract baseline for `web` and `mobile`
    is now explicit
- user direction on 2026-04-25 now freezes the mobile lane after `PRJ-667`:
  - `PRJ-668` is intentionally deferred until mobile work is explicitly resumed
  - near-term execution should stay on `web + backend` slices only
- fresh production UI analysis on 2026-04-25 now seeds the next `web + backend`
  stabilization lane through `PRJ-680`:
  - restore backend-owned chat history and settings persistence for the
    first-party web shell
  - make app-facing API errors truthful in the browser client instead of
    surfacing JSON parser noise
  - fix web route lifecycle regressions so `Tools` and `Personality` finish
    loading and render backend payloads
  - harden loading, empty, error, and success states across the shell
  - add end-to-end and production smoke proof for the repaired baseline
- `PRJ-675` is now the first `READY` slice:
  - restore `GET /app/chat/history` and `PATCH /app/me/settings` so the
    current production shell is functionally complete before further UI polish
- implementation progress on 2026-04-25:
  - `PRJ-675` is complete locally:
    - app chat history now serializes `source` correctly instead of failing
      during response shaping
    - app settings writes now treat `proactive_opt_in` and tool toggles as
      operational preferences instead of sending them through semantic
      embedding paths
  - `PRJ-676` is complete locally:
    - local web transport now handles plain-text backend failures
    truthfully instead of surfacing JSON parser errors
  - `PRJ-677` is complete locally:
    - local web route lifecycle no longer self-cancels successful
    `Tools` and `Personality` loads
  - `PRJ-678` is complete:
    - stale route-level errors clear on navigation
    - production verification confirms the repaired shell now feels coherent
      across login, chat, settings, tools, personality, and logout
  - `PRJ-679` is complete:
    - local regression and release-smoke coverage now include the first-party
      web shell routes `/`, `/chat`, `/settings`, `/tools`, and `/personality`
    - first live smoke on deployed commit `7ff715e` exposed one remaining
      parity gap: the web shell HTML still emitted `aion-web-build-revision`
      as `unknown` even though backend runtime build truth was correct
    - follow-up deploy on commit `ddb327f` fixed that gap and final production
      smoke now passes
- `PRJ-680` is complete:
  - task board, project state, and learning journal now describe the same
    repaired production baseline and the confirmed deploy-parity pitfall
- the web-shell stabilization lane seeded through `PRJ-680` is now complete
- fresh repo analysis on 2026-04-25 now seeds the next backend+web identity
  continuity lane through `PRJ-684`:
  - Telegram link confirmation currently updates authenticated profile state
    and tools-screen posture, but normal Telegram events still appear to run
    under raw Telegram identity instead of the linked backend auth identity
  - this leaves memory continuity split between `/app/*` traffic and Telegram
    traffic even after the user-visible link flow reports `linked`
  - the next queue should therefore repair runtime identity resolution first,
    then add end-to-end regression proof for shared memory continuity, then
    sync docs/context and record the pitfall
- `PRJ-681` is now the first `READY` slice:
  - freeze the linked Telegram identity-resolution contract and choose the
    conflict posture for relinking a Telegram chat that is already attached to
    another backend auth identity
- planned execution order for this lane:
  - `PRJ-681` Linked Telegram Identity Resolution Contract Freeze
  - `PRJ-682` Runtime Identity Resolution Implementation
  - `PRJ-683` Shared Memory Continuity Regression Proof
  - `PRJ-684` Context, Docs, And Learning Sync
- implementation progress on 2026-04-25:
  - `PRJ-681` is complete:
    - the linked Telegram identity-resolution contract is now frozen around
      the existing profile-owned link fields, and relinking now transfers chat
      ownership to the latest authenticated user instead of leaving ambiguous
      multi-owner linkage
  - `PRJ-682` is complete:
    - normal Telegram ingress now resolves linked backend auth identity before
      event normalization, so the foreground runtime uses the same memory owner
      as `/app/chat/message` after linking
    - unlinked Telegram traffic keeps the raw Telegram identity fallback
  - `PRJ-683` is complete:
    - backend regressions now pin linked Telegram-to-auth identity reuse,
      raw-user fallback for unlinked Telegram ingress, Telegram identity lookup
      by linked profile fields, and relink ownership transfer in the memory
      repository
  - `PRJ-684` is complete:
    - task board, project state, overview, next-iteration plan, and learning
      journal now describe the same linked-identity continuity repair
  - follow-up continuity hardening on 2026-04-25 is now complete:
    - manual repo repro confirmed one remaining gap after the first fix:
      pre-link Telegram memories persisted under the legacy raw Telegram
      `user_id`, so linking future ingress alone did not make old Telegram
      recall visible from the authenticated app account
    - Telegram linking now merges that legacy raw Telegram memory bucket into
      the authenticated backend user during `set_user_telegram_link(...)`,
      preserving old episodic and conclusion continuity instead of orphaning it
  - the linked UI-Telegram identity continuity lane seeded through `PRJ-684`
    is now complete
- fresh browser UX/UI analysis on 2026-04-25 now seeds the next
  product-facing web lane through `PRJ-691`:
  - freeze one mobile-first authenticated app-shell baseline before route
    redesign splits the layout in different directions
  - freeze the UI-language boundary before changing settings UX:
    - GUI language is interface-only
    - conversation language remains runtime-owned and live
    - the current conversation-language setting must not be overloaded as UI locale
  - make `Chat` the first product-quality route with conversation and composer
    priority
  - simplify `Settings` into a shorter preference flow while removing manual
    `response style` and `collaboration preference` controls
  - turn `Tools` from inspection-heavy backend truth into status-plus-action
    product cards
  - split `Personality` product insight from raw inspector posture
  - finish with one visual-system and responsive-proof pass across mobile,
    tablet, and desktop
- implementation progress on 2026-04-25:
  - `PRJ-685` is complete:
    - the authenticated shell now uses a compact sticky top bar instead of a
      repeated hero-plus-account block on every signed-in route
    - desktop navigation now lives in the top bar, while mobile uses a fixed
      bottom navigation better aligned with later app transfer
    - account access and sign-out now live behind one dedicated account panel
      instead of a permanently expanded summary card
  - `PRJ-686` is complete:
    - `preferred_language` is now explicitly frozen as profile-owned
      conversation continuity in canonical architecture docs
    - the planned first-party shell locale field is now explicitly named
      `ui_language`
    - the future selector contract is frozen around `system`, `en`, `pl`,
      and `de` plus a `flag + label` UI pattern
    - `response_style` and `collaboration_preference` remain runtime-shaped
      and should leave the product-facing settings form
  - `PRJ-687..PRJ-691` are now complete:
    - `Chat` now leads with conversation-first hierarchy, a mobile-friendly
      sticky composer, and a supporting continuity panel
    - `Settings` now focus on profile, `ui_language`, and proactive follow-up
      control, while manual `response_style` and
      `collaboration_preference` inputs are gone from the product shell
    - app-facing settings now persist `ui_language` separately from
      `preferred_language`
    - `Tools` now emphasize current state, next action, and on-demand
      technical detail instead of inspection-heavy payload density
    - `Personality` now shows summary-first insights with raw payload behind
      explicit inspect affordances
    - shared copy and mobile/tablet/desktop class posture now align across the
      authenticated shell
  - the product-facing UX/UI lane seeded through `PRJ-691` is now complete
  - `PRJ-692` is now complete:
    - repository-driven Coolify deploys now include one one-shot `migrate`
      service that runs `python -m alembic -c /app/backend/alembic.ini upgrade head`
      after database health
    - `app`, `maintenance_cadence`, and `proactive_cadence` now wait for that
      migration owner to complete successfully before startup
    - deployment guidance and the runtime ops runbook now describe the same
      migration-first startup order and operator verification path
  - `PRJ-693` is now complete:
    - `backend/scripts/run_release_smoke.ps1` now supports opt-in
      `-WaitForDeployParity` polling with bounded timeout and poll interval
    - deployment-trigger regressions can now distinguish short Coolify
      propagation lag from a true missing deploy without weakening the default
      strict parity check
    - targeted script tests and live production smoke now prove both the new
      wait mode and the current post-push convergence posture
  - `PRJ-694` is now complete:
    - release smoke now retries transient `/health` failures with a bounded
      attempt budget before failing the deploy check
    - script regressions now distinguish one brief `503` from a real sustained
      outage
- fresh runtime-behavior analysis on 2026-04-25 now seeds the next foreground
  awareness repair lane through `PRJ-702`:
  - linked Telegram identity continuity is repaired, but the foreground answer
    path can still behave as if it lacks memory continuity, current-time
    awareness, or practical access to bounded search and page reading
  - the repo already has memory, linked identity, `event.timestamp`, bounded
    search, and bounded page-read execution, so the next lane must repair
    propagation and intent inference rather than inventing a new subsystem
  - the next queue should therefore:
    - freeze the foreground-awareness contract first
    - add explicit turn-awareness payload propagation through runtime, context,
      and expression
    - surface human-facing identity facts and prevent false capability-denial
      answers
    - expand bounded tool use from keyword-only triggers toward intent-aware
      heuristics for weather, latest facts, and website-content requests
    - add regression proof for the reported Telegram, time, weather, and
      website scenarios before syncing docs and context
- `PRJ-695` is complete:
  - the repo now contains one detailed execution-ready plan for the foreground
    memory, time, and bounded-tool awareness repair lane in
    `docs/planning/foreground-memory-time-and-tool-awareness-repair-plan.md`
- planned execution order for this lane:
  - `PRJ-696` Foreground Awareness Contract Freeze
  - `PRJ-697` Runtime Turn-Awareness Payload And Prompt Propagation
  - `PRJ-698` Identity Facts Flow And Truthful Capability Claims
  - `PRJ-699` Implicit Tool Invocation Heuristics For External Facts
  - `PRJ-700` Behavior Regression Proof For Memory, Time, And Tool Awareness
  - `PRJ-701` Canonical Docs And Testing Guidance Sync
  - `PRJ-702` Final Validation, Context Sync, And Learning Closure
- implementation progress on 2026-04-25:
  - explicit user reprioritization resumed the foreground-awareness lane even
    though it had been deferred behind the second UX/UI pass
  - `PRJ-696..PRJ-702` are now complete:
    - foreground context now carries explicit turn-awareness truth for current
      turn time, known user name, memory continuity posture, and bounded tool
      readiness
    - runtime and OpenAI prompting now propagate that foreground-awareness
      contract into the reply path
    - auth-owned `display_name` now reaches identity/context outputs and can
      answer direct name-recall turns
    - expression now answers direct time questions from `event.timestamp` and
      rejects false capability-denial wording when foreground truth is present
    - planning now infers bounded weather/latest-fact search and page-read for
      explicit URLs or bare domains without requiring literal `search the web`
      or `read page`
    - same-turn bounded external-read results can now be summarized in the
      delivered reply while action remains the side-effect owner
    - focused validation for the lane passed:
      - `tests/test_identity_service.py`
      - `tests/test_openai_prompting.py`
      - `tests/test_context_agent.py`
      - `tests/test_expression_agent.py`
      - `tests/test_planning_agent.py`
      - `tests/test_action_executor.py`
      - `tests/test_runtime_pipeline.py`
      - result: `293 passed`
- fresh product analysis on 2026-04-25 now also seeds the next linked-channel
  chat transcript lane through `PRJ-717`:
  - linked Telegram identity continuity is already repaired, so the next
    product blocker is not identity ownership
  - `/app/chat/history` still returns memory entries and the web shell still
    splits local `sessionMessages` from backend continuity, which prevents the
    product from feeling like one continuous chat across Telegram and app
    surfaces
- `PRJ-711` is complete:
  - the repo now contains one execution-ready plan for shared chat transcript
    continuity in
    `docs/planning/shared-chat-transcript-and-telegram-continuity-plan.md`
- `PRJ-712` is now complete:
  - `/app/chat/history` is now frozen as a shared transcript contract instead
    of a memory-entry surface
  - the contract now fixes one backend-owned continuity owner, a default
    latest-`10` window, chronological ordering, and one bounded message item
    shape for web and later mobile
- `PRJ-713` is now complete:
  - backend now projects existing episodic turn memory into transcript items
    for `/app/chat/history` instead of raw memory entries
  - the endpoint now defaults to the latest `10` transcript items and returns
    them in chronological oldest-to-newest order
  - focused backend regressions passed for route shape and transcript ordering
- `PRJ-714` is now complete:
  - the web client now consumes the backend transcript item shape instead of
    the previous memory-entry interpretation
  - `/chat` now renders one merged conversation stream instead of split
    `sessionMessages` plus a continuity sidebar
  - the initial transcript load scrolls to the bottom, and new assistant
    replies are revealed from the top edge after send
  - focused validation passed:
    - `Push-Location .\web; npm run build; Pop-Location`
- `PRJ-715` is now the first `READY` slice:
  - prove that linked Telegram and first-party app turns appear in the same
    shared transcript continuity
- `PRJ-715` is now complete:
  - route regressions now prove linked Telegram and app turns appear in the
    same authenticated `/app/chat/history` transcript
  - optional-channel posture is now pinned so unlinked Telegram traffic stays
    outside app-auth transcript continuity
  - runtime regression now proves one shared continuity owner can project both
    `api` and `telegram` turns into the same transcript
  - focused validation passed:
    - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py; Pop-Location`
      -> `218 passed`
- `PRJ-716` is now the first `READY` slice:
  - sync shared client baseline and product docs with the now-proven
    transcript-safe contract
- `PRJ-716` is now complete:
  - `docs/planning/mobile-client-baseline.md` now defines
    `/app/chat/history` as a shared message transcript with latest-`10`
    posture and oldest-to-newest ordering
  - `mobile/README.md` and `docs/overview.md` now point at the same
    transcript-safe first-party client contract
  - doc-and-context cross-review passed for the shared client baseline
- `PRJ-717` is now the first `READY` slice:
  - attach final lane validation, context sync, and learning closure for the
    shared transcript continuity work
- `PRJ-717` is now complete:
  - final validation passed:
    - `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q; Pop-Location`
      -> `942 passed`
    - `Push-Location .\web; npm run build; Pop-Location`
      -> build passed
  - source-of-truth files now reflect the shared transcript lane as complete
    through `PRJ-717`
  - learning journal now records the scheduler quiet-hours test guardrail
    confirmed during full-suite validation
- the shared transcript continuity lane seeded through `PRJ-717` is now
  complete
- planned execution order for this lane:
  - `PRJ-712` Shared Chat Transcript Contract Freeze
  - `PRJ-713` Backend Transcript Projection And Chat History API Update
  - `PRJ-714` Web Chat Thread Unification And Scroll Behavior
  - `PRJ-715` Cross-Channel Regression Proof For Linked Telegram And App Chat
  - `PRJ-716` Shared Client Baseline And Product Docs Sync
  - `PRJ-717` Final Validation, Context Sync, And Learning Closure
- planned execution order for the completed UX/UI lane was:
  - `PRJ-685` Mobile-First App Shell Baseline
  - `PRJ-686` UI Language Boundary And Locale Switcher Plan
  - `PRJ-687` Chat Experience And Composer Priority
  - `PRJ-688` Settings Simplification And Runtime-Shaped Preference Cleanup
  - `PRJ-689` Tools Information Architecture And Actionability
  - `PRJ-690` Personality Productization And Inspector Split
  - `PRJ-691` Visual System Hardening, Responsive Proof, And Context Sync
- fresh browser UX/UI second-pass analysis on 2026-04-25 now seeds the next
  product-facing web lane through `PRJ-710`:
  - the first UX/UI lane improved structure and responsiveness, but the shell
    still presents too much system framing and not enough product-first value
  - `/login` still spends the first viewport on architecture-oriented hero
    content rather than trust and session entry
  - shared shell copy still leaks terms such as `backend truth`,
    `live contract`, and endpoint posture into user-facing surfaces
  - tablet still needs explicit layout rules instead of scaled-mobile posture
  - current loading, empty, success, and error states remain too system-like
    in tone
  - `ui_language` is now contractually correct, but its selector still needs a
    durable locale-metadata plan for later mobile reuse
  - badge density and card emphasis still flatten visual hierarchy across the
    shell
- user direction on 2026-04-25 now prioritizes this fresh UX/UI lane ahead of
  the foreground-awareness queue through `PRJ-702`:
  - that defer note is now superseded by later explicit user reprioritization:
    `PRJ-696..PRJ-702` were executed and completed on 2026-04-25
- `PRJ-703` is now complete:
  - `/login` now leads with product-value and trust framing instead of
    architecture-heavy badges and contract language
  - the public build revision badge is no longer shown on the unauthenticated
    session-entry surface
  - supporting cards now reinforce return-to-chat value, preference control,
    and runtime-reset ownership instead of endpoint or contract wording
- `PRJ-704` is now complete:
  - shared shell copy no longer leaks backend, contract, endpoint, or payload
    wording into primary product surfaces
  - route descriptions, settings language, loading states, and personality
    highlights now read as product copy across `en`, `pl`, and `de`
  - remaining technical detail is now framed as secondary details rather than
    front-and-center value language
- `PRJ-705` is now complete:
  - tablet now has a distinct shell posture with top navigation, summary-strip
    quick stats, and responsive sticky behavior instead of behaving like a
    scaled mobile screen
  - chat, settings, tools, and personality now shift into earlier tablet and
    desktop multi-column layouts without forking the shared shell
  - screenshot proof now lives in `.codex/artifacts/prj705-responsive-proof/`
- `PRJ-706` is now complete:
  - loading, empty, success, and error states now share one product-facing
    posture across login, bootstrap, chat continuity, tools, and personality
  - short recovery-first messaging now leads, while truthful error detail
    remains available through expandable details
- `PRJ-707` is now complete:
  - the GUI-language selector now uses one shared locale metadata model with
    value, native label, localized label, icon token, and system fallback
    posture
  - locale icon rendering is now explicitly token-based instead of depending
    on implicit emoji behavior
- `PRJ-708` is now complete:
  - decorative badges were reduced across login, shell summary, settings,
    tools, and personality so chips mostly return to state-bearing roles
  - hierarchy now leans on overlines, headings, stat tiles, and grouped detail
    cards instead of repeating bordered badge affordances
  - refreshed screenshot proof now lives in
    `.codex/artifacts/prj708-visual-hierarchy-proof/`
- `PRJ-709` is now complete:
  - authenticated `chat`, `settings`, `tools`, and `personality` were reviewed
    after the second UX/UI lane with mobile, tablet, and desktop proof
  - the accepted baseline now shows only polish-level follow-up, not
    product-structure gaps
  - evidence lives in `.codex/artifacts/prj709-authenticated-route-sweep/`
- `PRJ-710` is now complete:
  - planning docs, board state, project state, and learning references now
    describe one accepted second-pass UX/UI baseline
  - accepted evidence now points to the responsive proof, hierarchy proof, and
    authenticated route sweep artifacts without overstating mobile readiness
  - the second UX/UI lane is now explicitly closed
- `PRJ-712` is now complete:
  - `/app/chat/history` is now frozen as a shared transcript contract instead
    of a memory-entry surface
  - the contract now fixes one backend-owned continuity owner, a default
    latest-`10` window, chronological ordering, and one bounded message item
    shape for web and later mobile
- `PRJ-713` is now complete:
  - backend now projects existing episodic turn memory into transcript items
    for `/app/chat/history` instead of raw memory entries
  - the endpoint now defaults to the latest `10` transcript items and returns
    them in chronological oldest-to-newest order
- planned execution order for this lane:
  - `PRJ-703` Login Value Framing And Trust Cleanup
  - `PRJ-704` Product Copy And Terminology Cleanup Across The Shell
  - `PRJ-705` Responsive Tier Rules For Mobile Tablet Desktop
  - `PRJ-706` Productive State System For Loading Empty Error And Success
  - `PRJ-707` Locale Metadata Foundation For GUI Language UX
  - `PRJ-708` Visual Hierarchy And Badge Semantics Hardening
  - `PRJ-709` Authenticated Route Second Pass And Screenshot Proof
  - `PRJ-710` Context Docs And Learning Sync For The Second UX/UI Lane

## Agent Workflow Refresh (2026-04-18)

- This board is the canonical execution queue for Personality / AION.
- If no task is `READY`, the Planning Agent should derive the next smallest
  executable task from:
  - `docs/planning/next-iteration-plan.md`
  - `docs/planning/open-decisions.md`
- Default delivery loop for every execution slice:
  - plan
  - implement
  - run relevant tests and validations
  - capture architecture follow-up if discovered
  - sync task state, project state, and learning journal when needed
- Architecture convergence work is complete through `PRJ-453`.
- The repo is now in post-convergence follow-up mode:
  - no seeded execution queue remains
  - the next task must be derived from newly discovered gaps, drift, or
    hardening opportunities
  - new slices should prefer runtime truth, health/debug visibility,
    deployment evidence, and canonical-doc consistency over synthetic backlog
    generation
- Post-convergence Groups 57 through 59 are now complete through `PRJ-453`.
- Shared debug-ingress posture vocabulary, affective input-versus-final
  diagnostics, and embedding execution-class visibility are now explicit
  runtime surfaces instead of requiring operator inference across multiple
  fields.
- Memory, continuity, failure handling, adaptive governance, scheduler and
  connector boundaries, retrieval posture, and release evidence are now
  validated as living-system behavior rather than planning-only follow-ups.
- Post-convergence Group 60 is now complete through `PRJ-457`.
- Attention contract-store docs, config guidance, ops runbook visibility, and
  planning/context truth now consistently describe repository-backed durable
  inbox posture instead of mixing rollout-era wording with current runtime
  reality.
- Post-convergence Group 61 is now complete through `PRJ-460`.
- Persisted subconscious proposals and post-convergence operator health
  surfaces are now described consistently across runtime reality, runbook, and
  planning/context truth.
- Post-convergence Group 62 is now complete through `PRJ-463`.
- Affective health visibility and retrieval execution-class triage are now
  described consistently across the runbook and planning/context truth instead
  of being discoverable only through runtime reality and tests.
- The post-convergence execution queue seeded through `PRJ-491` is now
  complete.
- A new architecture-hardening queue is now seeded through `PRJ-515`.
- The next architecture lane prioritizes retiring remaining transitional
  runtime surfaces first, then external cadence ownership, connector-read
  posture, retrieval lifecycle closure, reflection supervision, and
  observability/export evidence.
- Fresh post-`PRJ-515` analysis has now seeded a new execution queue through
  `PRJ-539`.
- This queue is intentionally narrower and more production-facing than the
  previous hardening wave:
  - incident evidence must become easier for operators to export, retain, and
    attach to repeatable triage flows
  - shared debug compatibility routes should move from monitored posture to an
    actual retirement lane
  - externalized cadence ownership needs machine-visible cutover proof, not
    only target-policy surfaces
  - connector expansion should widen along bounded read-only slices
    (`calendar`, then `cloud_drive`) instead of generic capability growth
  - retrieval should close the remaining relation-source rollout question with
    explicit policy and evidence instead of leaving it as an open optional
    family forever
- A new `v1` productization queue is now seeded through `PRJ-567`.
- Product-stage interpretation is now explicit:
  - `MVP` is already exceeded by the current runtime baseline
  - `v1` means a no-UI but production-usable life assistant reachable through
    Telegram or API
  - `v2` starts when a dedicated UI consumes stable backend inspection and
    orchestration surfaces
- work-partner is now treated as a role of the same personality that may use
  selected skills and authorized tools through the existing planning and
  action boundary, not as a separate persona.
- the next queue is intentionally ordered around real `v1` blockers:
  - production conversation reliability first, because user-reported Telegram
    no-response posture blocks product reality more directly than any new tool
    lane
  - then life-assistant workflow activation
  - then learned-state inspection surfaces for future UI
  - then architecture-first web search and browser tooling
  - then bounded tool expansion and work-partner role orchestration
  - finally `v1` release closure and `v2` backend API readiness
- the seeded `v1` productization queue is now complete through `PRJ-567`
- no seeded `READY`, `BACKLOG`, or `FUTURE` queue remains after the no-UI `v1`
  closure lane; the next task should be derived from fresh production/runtime
  analysis
- `PRJ-568` is complete: startup now wires durable attention to the shared
  memory repository instead of leaving `durable_inbox` unable to use the
  repository-backed contract store.
- `PRJ-569` is complete: PostgreSQL semantic-vector deploys now require the
  Python `pgvector` package as a normal runtime dependency, and app startup
  blocks before database initialization when semantic vectors are enabled on
  PostgreSQL without that binding.
- `PRJ-570` is complete: repository-driven Coolify production now uses a
  pgvector-capable PostgreSQL 15 image, forced deploy
  `ihgdzv1gug3ketq0u7sm3n2s` finished on commit `e41772e`, `/health` is green
  again, Telegram round-trip telemetry shows successful ingress and delivery,
  and the post-deploy migration hook is normalized back to
  `python -m alembic upgrade head`.
- `PRJ-571` is complete: fresh post-`v1` planning truth is now seeded from the
  live production runtime instead of historical backlog. The next queue starts
  with the remaining operational drift already visible in `/health` and
  startup logs:
  - reflection external-driver posture still runs in `in_process`
    compatibility mode
  - scheduler cadence ownership still runs in `in_process`
  - both lanes already expose target owner policies and therefore should be
    externalized before another broad capability expansion
- `PRJ-572` is complete: repository-driven Coolify production now defaults
  `REFLECTION_RUNTIME_MODE` to `deferred`, forced deploy
  `nlcp1kpmxxhvq094fssz7qfk` finished on commit `13d8972`, production
  `/health.reflection.external_driver_policy.selected_runtime_mode` now
  reports `deferred`, and Telegram/API foreground turn handling remained
  healthy through the cutover.
- `PRJ-573` is complete: repository-driven Coolify production now defaults
  `SCHEDULER_EXECUTION_MODE` to `externalized`, forced deploy
  `m8jd7i3sqiv8f8fuvlo367ki` finished on commit `2a4a573`, and production
  `/health.scheduler.external_owner_policy` now reports
  `selected_execution_mode=externalized`, `cutover_proof_ready=true`, and
  `production_baseline_ready=true` with recent repository-backed maintenance
  and proactive cadence evidence while Telegram foreground round-trip posture
  remained healthy.
- `PRJ-574` is complete: runtime reality, testing guidance, planning docs,
  runbook, and repository context now describe the same post-v1 production
  owner baseline where reflection runs with deferred external-driver
  ownership, cadence runs with external scheduler ownership, and release smoke
  plus production `/health` are the canonical proof surfaces.
- the post-v1 production-hardening queue seeded by `PRJ-571` is now complete
  through `PRJ-574`; no seeded `READY` slice remains in this lane.
- `PRJ-575` is complete: fresh architecture-gap analysis now compares the live
  production `/health` snapshot against canonical architecture and seeds the
  next queue through `PRJ-595`.
- the next queue intentionally targets the five clearest remaining
  architecture-to-production gaps:
  - durable attention production cutover
  - proactive opt-in production activation
  - retrieval provider baseline alignment
  - richer backend introspection of learned personality growth
  - production organizer-tool readiness for ClickUp, Calendar, and Drive
- `PRJ-576` is now the first `READY` slice because production already proves
  deferred reflection and externalized cadence, while `/health.attention`
  still shows `coordination_mode=in_process` even though durable-inbox
  readiness is green.
- `PRJ-576` is complete: durable attention now has one explicit production
  cutover gate with target owner, required proof surfaces, and rollback
  posture frozen before the runtime switch.
- `PRJ-577` is complete: repository-driven Coolify production now runs
  `ATTENTION_COORDINATION_MODE=durable_inbox`, deployment
  `amz31iyapwr3t9z9tanpe2jb` finished on commit `d3707a0`, public `/health`
  reports `attention.coordination_mode=durable_inbox`,
  `contract_store_mode=repository_backed`, and Telegram round-trip remained
  healthy through release smoke.
- `PRJ-578` is complete: release smoke, exported incident evidence,
  incident-evidence bundles, and CI behavior validation now require the live
  durable-attention owner posture plus `runtime_topology.attention_switch`
  proof, and burst-coalescing stability no longer depends on manual operator
  inspection.
- `PRJ-579` is complete: durable-attention production truth is now synchronized
  across runtime reality, testing guidance, ops notes, planning, and context.
- `PRJ-580..PRJ-583` are complete: production now runs bounded proactive
  follow-up under external scheduler ownership, release smoke plus
  incident-evidence gates now require the same proactive owner posture, and
  docs/context truth no longer describe proactive as `disabled_by_policy`.
- `PRJ-584` is complete: production retrieval keeps `openai_api_embeddings` as
  the steady-state target baseline, `local_hybrid` remains transition-only,
  deterministic remains compatibility fallback, and enforcement stays
  explicitly `warn` until runtime alignment lands in `PRJ-585`.
- `PRJ-585..PRJ-587` are complete: repository-driven Coolify production now
  aligns with the OpenAI retrieval baseline, release smoke plus incident
  evidence fail on retrieval drift, and docs/context truth now describe the
  same aligned provider-owned baseline and strict evidence path.
- `PRJ-588` is complete: the repo now records one explicit bounded backend
  contract for personality-growth introspection, separating learned knowledge,
  learned preferences, role/skill metadata, reflection-backed summaries, and
  planning continuity while explicitly rejecting self-modifying executable
  skill learning.
- `PRJ-589` is complete: `/health.learned_state` now exposes the richer
  section contract, and `GET /internal/state/inspect?user_id=...` now returns
  bounded preference, knowledge, role/skill, and planning-continuity summaries
  for future UI or operator inspection instead of leaving growth visibility at
  policy-owner level only.
- `PRJ-590` is complete: release smoke, incident-evidence bundle validation,
  and targeted regression fixtures now require the richer learned-state section
  contract instead of only checking owner or path posture.
- `PRJ-591` is complete: canonical contracts, runtime reality, testing
  guidance, ops notes, planning docs, and repository context now describe the
  same richer learned-state and personality-growth inspection baseline.
- `PRJ-592` is complete: the first production organizer-tool stack is now
  frozen as ClickUp `create_task/list_tasks/update_task`, Google Calendar
  `read_availability`, and Google Drive `list_files`, with opt-in and
  confirmation boundaries left explicit.
- `PRJ-593` is complete: `/health.connectors.organizer_tool_stack` now exposes
  one shared acceptance snapshot for the frozen ClickUp/Calendar/Drive stack,
  including approved operations, credential gaps, opt-in requirements, and
  confirmation boundaries.
- `PRJ-594` is complete: release smoke, incident-evidence exports and bundles,
  behavior validation, and runtime behavior scenarios now prove the same
  bounded organizer-tool posture that `/health.connectors.organizer_tool_stack`
  exposes for ClickUp, Calendar, and Drive.
- `PRJ-595` is complete: canonical contracts, runtime reality, testing
  guidance, ops notes, planning docs, and repository context now describe the
  same first production organizer-tool baseline and its proof path.
- the queue seeded through `PRJ-595` is now complete; no seeded `READY`,
  `BACKLOG`, or `FUTURE` slice remains after the organizer-tool production
  readiness lane.
- `PRJ-596` is complete: fresh production analysis now seeds the next queue
  through `PRJ-611`, focused on the remaining productization gaps between a
  healthy no-UI `v1` runtime and a production-ready external-tool learning
  baseline.
- the next queue intentionally targets four live gaps:
  - Coolify deployment automation still needs explicit source-truth repair and
    proof after the repository rename
  - the organizer-tool stack is machine-visible but still blocked by provider
    credentials in production
  - bounded search/browser/tool reads still lack an explicit durable
    tool-grounded learning capture contract
  - future UI/admin work still needs one clearer backend capability catalog for
    tools, role presets, and registry-backed skills
- `PRJ-612` is complete: canonical architecture now allows durable role
  presets with prompt-oriented definitions, durable skill descriptions with
  evolving usage guidance, and per-user tool authorization records, while
  keeping tools user-authorized, secrets externalized, and execution inside
  the existing planning -> permission-gate -> action boundary.
- `PRJ-597` is complete: repo-driven Coolify deployment automation now has one
  explicit frozen baseline with canonical app identity, primary automation
  path, bounded fallback path, and operator proof surfaces.
- `PRJ-598` is complete: `/health.deployment`, deploy webhook evidence,
  exported incident evidence, and release smoke now share one machine-visible
  deployment-automation posture with explicit provenance fields for primary
  source automation versus webhook/UI fallback.
- `PRJ-599` is complete: runbook, planning truth, and repository context now
  describe the same repo-driven Coolify deployment-provenance baseline as the
  runtime and smoke contract.
- `PRJ-600` is complete: canonical contracts, env/config guidance, ops notes,
  and planning/context truth now freeze one production credential-activation
  baseline for the first organizer-tool stack.
- `PRJ-601` is complete: `/health.connectors.organizer_tool_stack` now exposes
  one activation snapshot with provider-specific missing settings, opt-in or
  confirmation posture, and next actions for ClickUp, Google Calendar, and
  Google Drive.
- `PRJ-602` is complete: release smoke, incident evidence, and
  incident-evidence bundles now validate the same organizer-tool activation
  snapshot exposed through `/health.connectors.organizer_tool_stack`, so
  provider-readiness evidence no longer depends on `/health` alone.
- `PRJ-603` is complete: runtime reality, testing guidance, ops notes,
  planning truth, and repository context now describe the same
  organizer-tool activation snapshot, activation-state triage, and
  provider-specific next-action posture as the release-smoke and
  incident-evidence contract.
- `PRJ-604` is complete: canonical architecture now freezes one bounded
  tool-grounded learning contract where approved external reads may become
  durable learned knowledge only through action-owned summaries and
  memory-owned persistence.
- `PRJ-605` is complete: approved external reads now persist bounded
  tool-grounded semantic conclusions and learned-state inspection exposes the
  richer tool-grounded knowledge summaries instead of leaving external reads
  purely turn-local.
- `PRJ-606` is complete: behavior validation, `/health`, incident evidence,
  and release smoke now prove the same bounded tool-grounded learning
  contract instead of leaving external-read reuse to manual debug inspection.
- `PRJ-607` is complete: runtime reality, testing guidance, ops notes,
  planning truth, and repository context now describe the same bounded
  tool-grounded learning baseline and its evidence path.
- `PRJ-608` is complete: canonical architecture now freezes one bounded
  backend capability-catalog contract composed from existing health, internal
  inspection, role-skill, and connector surfaces instead of leaving future UI
  or admin work to reconstruct capability truth client-side.
- `PRJ-609..PRJ-611` are complete: `/health.capability_catalog`, internal
  inspection, release smoke, and incident-evidence bundle validation now share
  one bounded backend capability-catalog contract, and the queue seeded
  through `PRJ-611` is complete.
- `PRJ-613` is complete: fresh analysis now seeds a final operational
  `v1`-closure queue through `PRJ-633`.
- `PRJ-616` is complete: the canonical Coolify production app was corrected
  from `Public GitHub` to the GitHub App source `vps-luckysparrow`, the
  source repository path was corrected to `Wroblewski-Patryk/Aviary`, local
  `origin` now matches the same renamed repository, and the current Coolify UI
  path is `Aviary > production > aviary`.
- `PRJ-617` is complete: planning truth, runbook guidance, and repository
  context now treat `Public GitHub` on the canonical production app as
  deployment drift instead of an acceptable source variant.
- `PRJ-634` is complete: deploy parity is now fully green in live production.
  The repo-owned compose contract uses `${APP_BUILD_REVISION:-unknown}`, the
  canonical Coolify app maps `APP_BUILD_REVISION=$SOURCE_COMMIT` as a
  runtime-only variable, shadowing `SOURCE_COMMIT=unknown` variables were
  removed, and release smoke now proves that production `runtime_build_revision`
  matches local repo `HEAD`.
- the previously seeded final no-UI `v1` closure lane through `PRJ-633` is now
  superseded by the approved architecture revision for core time-aware planned
  work.
- core no-UI `v1` is now defined around:
  - stable conversation
  - bounded internet reading
  - tool-grounded learning
  - internal time-aware planned work
- organizer tools remain prepared and valuable, but they now belong to a later
  extension lane instead of blocking core `v1`.
- the next queue is now seeded through `PRJ-642` and intentionally targets:
  - a durable internal planned-work model instead of a standalone reminder
    subsystem
  - scheduler-owned reevaluation with foreground delivery through the existing
    attention -> planning -> expression -> action path
  - bounded autonomous research windows built on the same future-work model
- `PRJ-635` is complete: canonical architecture now freezes one explicit
  time-aware planned-work baseline for core no-UI `v1`, where reminders,
  check-ins, routines, and future follow-ups are all variants of internal
  planned work, due delivery still crosses
  `attention -> planning -> expression -> action`, and organizer-tool
  activation is no longer a hidden core-`v1` blocker.
- `PRJ-636` is complete: runtime contracts, storage, action-owned persistence,
  and test coverage now share one durable `planned_work` baseline instead of
  leaving time-aware future work as reminder-only phrasing or transient task
  heuristics.
- `PRJ-637` is complete: maintenance cadence now reevaluates due planned work,
  marks it as `due`, and hands it to the existing subconscious proposal
  boundary instead of sending user-visible delivery directly from the
  background scheduler.
- `PRJ-638` is complete: due planned-work handoffs now re-enter the normal
  foreground runtime path, proposal resolution remains explicit, and scheduler
  delivery no longer needs a direct-send escape hatch outside
  `planning -> expression -> action`.
- `PRJ-639` is complete: recurring planned work now advances through bounded
  recurrence rules, quiet-hours-sensitive items delay instead of bypassing the
  boundary, and expired one-off items skip cleanly without growing a second
  scheduler.
- `PRJ-640` is complete: behavior validation now includes `T19.1` and
  `T19.2`, `/health.v1_readiness` plus incident evidence expose the same
  time-aware planned-work posture, and release smoke now fails when that proof
  drifts.
- `PRJ-641` is complete: bounded autonomous research windows are now frozen as
  `planned_work` variants with explicit triggers, read-only tool limits, and
  tool-grounded-learning guardrails.
- `PRJ-642` is complete: product, runtime, testing, ops, planning, and
  context truth now describe the same core no-UI `v1` boundary and later
  organizer-tool extension.
- the queue seeded through `PRJ-642` is now complete; no seeded `READY`,
  `BACKLOG`, or `FUTURE` slice remains in this lane.
- 2026-04-25 fresh analysis now seeds the next queue through `PRJ-654`.
- the highest-signal remaining gaps before a fully convincing no-UI `v1`
  are now:
  - truthful `v1_readiness` semantics after the core-v1 boundary revision
  - foreground capability/time awareness, so implemented planning, temporal,
    and bounded web capabilities become explicitly knowable to the active turn
  - channel-aware Telegram delivery for long messages and formatting
  - high-level docs drift between live runtime reality and older
    "still planned" wording
- the next queue is intentionally ordered as:
  - `PRJ-647..PRJ-650` V1 Readiness Truth And Acceptance Boundary
  - `PRJ-651..PRJ-654` Foreground Capability And Time Awareness
  - `PRJ-643..PRJ-646` Channel-Aware Delivery Baseline
- retained dormant task ids `PRJ-643..PRJ-646` stay valid, but they now depend
  on the readiness-truth and awareness lanes because delivery polish should not
  land on top of an ambiguous final-acceptance story or an under-signaled
  foreground capability model.
- fresh code analysis on 2026-04-25 confirms:
  - planned work and scheduler handoff are implemented
  - bounded `knowledge_search.search_web` and `web_browser.read_page` are
    implemented and action-executed
  - but foreground turn awareness of current time, approved tools, and active
    planned-work posture is still only partially explicit across context,
    prompt, and runtime capability surfaces
- the next post-`PRJ-650` lane should therefore prioritize explicit awareness
  before Telegram delivery polish.
- fresh user-reported Telegram behavior now also confirms a later,
  still-unfrozen gap after the current readiness-truth and channel-delivery
  lanes:
  - the repo still lacks one explicit multimodal interaction contract for
    photo context, voice-note transcription, and generated image reply
    delivery
- `PRJ-647` is complete: canonical architecture, planning truth, testing
  guidance, and runtime reality now distinguish core no-UI `v1` gates from
  mirrored extension posture. Organizer daily-use is now explicit extension
  readiness rather than a hidden core blocker inside the post-`PRJ-642`
  product boundary.
- 2026-04-25: fresh user-approved `v2` direction now also seeds a later
  product-entry lane through `PRJ-668`.
- that lane is intentionally ordered after the current no-UI `v1` truth and
  awareness backlog because it changes repository topology and production
  deploy shape:
  - `PRJ-655..PRJ-659` V2 Product Topology And Repository Migration
  - `PRJ-660..PRJ-663` First-Party Auth And Client API Boundary
  - `PRJ-664..PRJ-666` Web Product Shell And Production Topology
  - `PRJ-667..PRJ-668` Mobile Product Foundation

## READY

- [x] PRJ-648 Implement truthful v1-readiness gate evaluation
  - Owner: Backend Builder
  - Group: V1 Readiness Truth And Acceptance Boundary
  - Depends on: PRJ-647
  - Priority: P0
  - Status: DONE
  - Validation: `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_api_routes.py -k "v1_readiness or telegram_round_trip_readiness_state or deploy_parity_manual_fallback"; Pop-Location`

- [x] PRJ-649 Add proof for v1-readiness truthfulness
  - Owner: QA/Test
  - Group: V1 Readiness Truth And Acceptance Boundary
  - Depends on: PRJ-648
  - Priority: P0
  - Status: DONE
  - Validation: `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py -k "v1_readiness"; Pop-Location`

- [x] PRJ-650 Sync docs and context for truthful v1-readiness
  - Owner: Product Docs Agent
  - Group: V1 Readiness Truth And Acceptance Boundary
  - Depends on: PRJ-649
  - Priority: P1
  - Status: DONE
  - Validation: doc-and-context sync

- [x] PRJ-651 Freeze the foreground capability-and-time awareness contract
  - Owner: Planning Agent
  - Group: Foreground Capability And Time Awareness
  - Depends on: PRJ-650
  - Priority: P0
  - Status: DONE
  - Validation: architecture and runtime-contract cross-review

- [x] PRJ-652 Implement explicit foreground awareness for time and approved tools
  - Owner: Backend Builder
  - Group: Foreground Capability And Time Awareness
  - Depends on: PRJ-651
  - Priority: P0
  - Status: DONE
  - Validation: targeted runtime, planning, and prompt-path coverage

- [x] PRJ-653 Add proof for indirect capability use and temporal reasoning
  - Owner: QA/Test
  - Group: Foreground Capability And Time Awareness
  - Depends on: PRJ-652
  - Priority: P0
  - Status: DONE
  - Validation: targeted pytest plus behavior scenarios

- [x] PRJ-654 Sync docs and context for foreground capability awareness
  - Owner: Product Docs Agent
  - Group: Foreground Capability And Time Awareness
  - Depends on: PRJ-653
  - Priority: P1
  - Status: DONE
  - Validation: doc-and-context sync

- [x] PRJ-643 Freeze the channel-aware delivery constraint baseline
  - Owner: Planning Agent
  - Group: Channel-Aware Delivery Baseline
  - Depends on: PRJ-654
  - Priority: P1
  - Status: DONE
  - Validation: architecture and delivery-contract cross-review

- [x] PRJ-644 Implement channel-aware Telegram segmentation and formatting
  - Owner: Backend Builder
  - Group: Channel-Aware Delivery Baseline
  - Depends on: PRJ-643
  - Priority: P1
  - Status: DONE
  - Validation: `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_delivery_router.py tests/test_telegram_client.py tests/test_action_executor.py -k "telegram or delivery_router" tests/test_api_routes.py -k "telegram_link or telegram_webhook or telegram" tests/test_runtime_pipeline.py -k "telegram"; Pop-Location`

- [x] PRJ-645 Add proof for long-message and markdown delivery
  - Owner: QA/Test
  - Group: Channel-Aware Delivery Baseline
  - Depends on: PRJ-644
  - Priority: P1
  - Status: DONE
  - Validation: `Push-Location .\backend; ..\.venv\Scripts\python -m pytest -q tests/test_delivery_router.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py tests/test_observability_policy.py; Pop-Location`

- [x] PRJ-646 Sync docs for channel-aware delivery
  - Owner: Product Docs Agent
  - Group: Channel-Aware Delivery Baseline
  - Depends on: PRJ-645
  - Priority: P2
  - Status: DONE
  - Validation: doc-and-context sync

- [x] PRJ-636 Add the durable planned-work contract and storage shape
  - Owner: Backend Builder
  - Group: Core V1 Time-Aware Planned Work
  - Depends on: PRJ-635
  - Priority: P0
  - Status: DONE
  - Validation: `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_schema_baseline.py`

- [x] PRJ-637 Implement scheduler reevaluation and due-item attention handoff
  - Owner: Backend Builder
  - Group: Core V1 Time-Aware Planned Work
  - Depends on: PRJ-636
  - Priority: P0
  - Status: DONE
  - Validation: `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_scheduler_worker.py tests/test_runtime_pipeline.py`

- [x] PRJ-638 Implement foreground delivery for due planned work
  - Owner: Backend Builder
  - Group: Core V1 Time-Aware Planned Work
  - Depends on: PRJ-637
  - Priority: P0
  - Status: DONE
  - Result:
    - due planned-work handoffs now become normal foreground runtime turns and
      can be delivered through the existing Telegram/API response path
    - scheduler cadence emits one foreground event per newly-due item and does
      not repeatedly reselect already-`due` rows
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_scheduler_worker.py tests/test_runtime_pipeline.py`

- [x] PRJ-639 Add recurring work and context-aware delivery rules
  - Owner: Backend Builder
  - Group: Core V1 Time-Aware Planned Work
  - Depends on: PRJ-638
  - Priority: P1
  - Status: DONE
  - Result:
    - recurring planned work now uses bounded recurrence rules on the existing
      entity instead of a second scheduling subsystem
    - maintenance cadence now delays, skips, or advances due items through
      explicit planned-work state transitions
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_planning_agent.py tests/test_scheduler_worker.py tests/test_memory_repository.py`

- [x] PRJ-640 Add behavior and release proof for time-aware planned work
  - Owner: QA/Test
  - Group: Core V1 Time-Aware Planned Work
  - Depends on: PRJ-639
  - Priority: P0
  - Status: DONE
  - Result:
    - behavior validation now proves due planned-work foreground delivery and
      recurring reevaluation through `T19.1..T19.2`
    - `/health.v1_readiness`, incident evidence, and release smoke now pin the
      same compact time-aware planned-work posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py::test_runtime_behavior_time_aware_planned_work_scenarios`
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py::test_health_endpoint_shows_strict_rollout_hint_when_production_is_ready`
    - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py -k "v1_readiness or time_aware_planned_work"`

- [x] PRJ-641 Freeze the bounded autonomous research-window policy
  - Owner: Planning Agent
  - Group: Bounded Autonomous Research Windows
  - Depends on: PRJ-640
  - Priority: P1
  - Status: DONE
  - Result:
    - `research_window` is now frozen as a planned-work variant instead of a
      separate autonomy engine
    - approved triggers, bounded read-only tool limits, and tool-grounded
      learning guardrails are now explicit in canonical contracts
  - Validation:
    - architecture and product cross-review

- [x] PRJ-642 Sync docs and context for core V1 time-aware planning
  - Owner: Product Docs Agent
  - Group: Bounded Autonomous Research Windows
  - Depends on: PRJ-641
  - Priority: P1
  - Status: DONE
  - Result:
    - architecture, runtime, testing, ops, planning, and context truth now
      describe the same core no-UI `v1` time-aware-planning boundary
    - organizer tools are consistently described as a later extension instead
      of a core-`v1` blocker
    - no seeded queue remains after this lane; future follow-up should come
      from fresh analysis
  - Validation:
    - doc-and-context cross-review

## BACKLOG

- [ ] PRJ-649 Add proof for v1-readiness truthfulness
  - Owner: QA/Test
  - Group: V1 Readiness Truth And Acceptance Boundary
  - Depends on: PRJ-648
  - Priority: P0
  - Status: BACKLOG
  - Validation: targeted pytest plus release-smoke regressions

- [ ] PRJ-650 Sync docs and context for truthful v1-readiness
  - Owner: Product Docs Agent
  - Group: V1 Readiness Truth And Acceptance Boundary
  - Depends on: PRJ-649
  - Priority: P1
  - Status: BACKLOG
  - Validation: doc-and-context sync

- [ ] PRJ-651 Freeze the foreground capability-and-time awareness contract
  - Owner: Planning Agent
  - Group: Foreground Capability And Time Awareness
  - Depends on: PRJ-650
  - Priority: P0
  - Status: BACKLOG
  - Validation: architecture and runtime-contract cross-review

- [ ] PRJ-652 Implement explicit foreground awareness for time and approved tools
  - Owner: Backend Builder
  - Group: Foreground Capability And Time Awareness
  - Depends on: PRJ-651
  - Priority: P0
  - Status: BACKLOG
  - Validation: targeted runtime, planning, and prompt-path coverage

- [ ] PRJ-653 Add proof for indirect capability use and temporal reasoning
  - Owner: QA/Test
  - Group: Foreground Capability And Time Awareness
  - Depends on: PRJ-652
  - Priority: P0
  - Status: BACKLOG
  - Validation: targeted pytest plus behavior scenarios

- [ ] PRJ-654 Sync docs and context for foreground capability awareness
  - Owner: Product Docs Agent
  - Group: Foreground Capability And Time Awareness
  - Depends on: PRJ-653
  - Priority: P1
  - Status: BACKLOG
  - Validation: doc-and-context sync

- [ ] PRJ-643 Freeze the channel-aware delivery constraint baseline
  - Owner: Planning Agent
  - Group: Channel-Aware Delivery Baseline
  - Depends on: PRJ-654
  - Priority: P1
  - Status: BACKLOG
  - Validation: architecture and delivery-contract cross-review

- [ ] PRJ-644 Implement channel-aware Telegram segmentation and formatting
  - Owner: Backend Builder
  - Group: Channel-Aware Delivery Baseline
  - Depends on: PRJ-643
  - Priority: P1
  - Status: BACKLOG
  - Validation: targeted delivery-router and Telegram client coverage

- [ ] PRJ-645 Add proof for long-message and markdown delivery
  - Owner: QA/Test
  - Group: Channel-Aware Delivery Baseline
  - Depends on: PRJ-644
  - Priority: P1
  - Status: BACKLOG
  - Validation: targeted pytest plus release or evidence checks

- [ ] PRJ-646 Sync docs for channel-aware delivery
  - Owner: Product Docs Agent
  - Group: Channel-Aware Delivery Baseline
  - Depends on: PRJ-645
  - Priority: P2
  - Status: BACKLOG
  - Validation: doc-and-context sync

- [x] PRJ-655 Freeze the `backend/web/mobile` v2 product topology and naming
  - Owner: Planning Agent
  - Group: V2 Product Topology And Repository Migration
  - Depends on: PRJ-646
  - Priority: P1
  - Status: DONE
  - Validation: architecture, governance, and planning cross-review

- [x] PRJ-656 Move the current Python runtime into `backend/` without behavior drift
  - Owner: Backend Builder
  - Group: V2 Product Topology And Repository Migration
  - Depends on: PRJ-655
  - Priority: P1
  - Status: DONE
  - Validation: targeted pytest plus path and script regression coverage

- [x] PRJ-657 Normalize tooling, docs, and deploy paths after the `backend/` move
  - Owner: Ops/Release
  - Group: V2 Product Topology And Repository Migration
  - Depends on: PRJ-656
  - Priority: P1
  - Status: DONE
  - Validation: compose, migration, smoke, and script path verification

- [x] PRJ-658 Scaffold the `web/` workspace with React, TypeScript, Vite, Tailwind, and daisyUI
  - Owner: Frontend Builder
  - Group: V2 Product Topology And Repository Migration
  - Depends on: PRJ-657
  - Priority: P1
  - Status: DONE
  - Validation: workspace bootstrap and production build smoke

- [x] PRJ-659 Scaffold the `mobile/` workspace as a reserved product surface
  - Owner: Frontend Builder
  - Group: V2 Product Topology And Repository Migration
  - Depends on: PRJ-658
  - Priority: P2
  - Status: DONE
  - Validation: workspace bootstrap and contract-boundary review

- [x] PRJ-660 Freeze first-party backend auth/session and user mapping contracts
  - Owner: Planning Agent
  - Group: First-Party Auth And Client API Boundary
  - Depends on: PRJ-659
  - Priority: P1
  - Status: DONE
  - Validation: architecture and runtime-contract cross-review

- [x] PRJ-661 Implement the backend auth/session baseline for first-party clients
  - Owner: Backend Builder
  - Group: First-Party Auth And Client API Boundary
  - Depends on: PRJ-660
  - Priority: P1
  - Status: DONE
  - Validation: targeted auth, API, and security regression coverage

- [x] PRJ-662 Freeze the app-facing client API boundary for web and mobile
  - Owner: Planning Agent
  - Group: First-Party Auth And Client API Boundary
  - Depends on: PRJ-661
  - Priority: P1
  - Status: DONE
  - Validation: architecture and endpoint-contract cross-review

- [x] PRJ-663 Implement UI-safe app-facing API surfaces over existing backend truth
  - Owner: Backend Builder
  - Group: First-Party Auth And Client API Boundary
  - Depends on: PRJ-662
  - Priority: P1
  - Status: DONE
  - Validation: targeted endpoint and runtime contract coverage

- [x] PRJ-664 Build the first `web/` shell for login, settings, chat, and personality inspection
  - Owner: Frontend Builder
  - Group: Web Product Shell And Production Topology
  - Depends on: PRJ-663
  - Priority: P1
  - Status: DONE
  - Validation: `npm run build`

- [x] PRJ-665 Integrate `web/` build and serving into the production topology
  - Owner: Ops/Release
  - Group: Web Product Shell And Production Topology
  - Depends on: PRJ-664
  - Priority: P1
  - Status: DONE
  - Validation: `docker compose config`; `docker build -f docker/Dockerfile . --build-arg APP_BUILD_REVISION=test-web-build-rev -t aion-web-smoke:local`

- [x] PRJ-666 Add release smoke and repo-driven post-push deploy proof for `backend + web`
  - Owner: QA/Test
  - Group: Web Product Shell And Production Topology
  - Depends on: PRJ-665
  - Priority: P1
  - Status: DONE
  - Validation: targeted `tests/test_deployment_trigger_scripts.py` parity coverage

- [ ] PRJ-667 Freeze the mobile client stack and shared contract baseline
  - Owner: Planning Agent
  - Group: Mobile Product Foundation
  - Depends on: PRJ-666
  - Priority: P2
  - Status: BACKLOG
  - Validation: product and architecture cross-review

- [ ] PRJ-668 Build the initial `mobile/` foundation on the shared auth and client API boundary
  - Owner: Frontend Builder
  - Group: Mobile Product Foundation
  - Depends on: PRJ-667
  - Priority: P2
  - Status: BACKLOG
  - Validation: mobile workspace smoke and shared-client contract verification

## DONE

- [x] PRJ-647 Freeze the core-v1 versus extension acceptance boundary
  - Owner: Planning Agent
  - Group: V1 Readiness Truth And Acceptance Boundary
  - Depends on: PRJ-642
  - Priority: P0
  - Status: DONE
  - Result:
    - canonical architecture and planning truth now explicitly separate core
      no-UI `v1` gates from later extension posture
    - organizer daily-use posture is now described as mirrored extension
      readiness, not as a hidden blocker of the post-`PRJ-642` core boundary
    - the next runtime slice now has one clear contract target for truthful
      `v1_readiness`
  - Validation:
    - architecture and planning cross-review

- [x] PRJ-635 Freeze the time-aware planned-work baseline for core no-UI V1
  - Owner: Planning Agent
  - Group: Core V1 Time-Aware Planned Work
  - Depends on: PRJ-631
  - Priority: P0
  - Status: DONE
  - Result:
    - canonical architecture now states that reminders, check-ins, routines,
      and future follow-ups are all variants of one internal planned-work
      model
    - core no-UI `v1` now explicitly treats organizer-tool activation as a
      later extension instead of a hidden closure prerequisite
    - planned-work storage and due-delivery posture now stay tied to internal
      planning state plus the existing
      `attention -> planning -> expression -> action` boundary
  - Validation:
    - architecture and planning cross-review

- [x] PRJ-614 Freeze the final operational V1-closure baseline
  - Owner: Planning Agent
  - Group: Production Truth And Deploy Automation Closure
  - Depends on: PRJ-613
  - Priority: P0
  - Status: DONE
  - Why now:
    - the repo already meets the no-UI `v1` contract on paper, but the user
      still needs one explicit final closure baseline that distinguishes
      healthy backend contracts from truly daily-usable production behavior
  - Result:
    - one explicit `v1` operational-closure contract now records what must be
      green in live production before the personality is treated as truly
      ready for daily conversation, bounded web reading, and external-tool
      onboarding, together with explicit fallback posture when live production
      drifts from that bar
  - Validation:
    - architecture/product/ops cross-review against live production `/health`

- [x] PRJ-615 Add machine-visible repo-vs-production truth and deploy-parity evidence
  - Owner: Backend Builder
  - Group: Production Truth And Deploy Automation Closure
  - Depends on: PRJ-614
  - Priority: P0
  - Status: DONE
  - Why now:
    - final no-UI `v1` closure now depends explicitly on live production
      parity, so the next slice must make repo-vs-production truth
      machine-visible instead of leaving it as operator inference
  - Result:
    - production-facing surfaces and release evidence distinguish intended repo
      baseline from last-deployed baseline and explicit fallback deploy
      provenance
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_deployment_trigger_scripts.py tests/test_coolify_compose.py`
    - `.\scripts\run_release_smoke.ps1 -BaseUrl 'https://personality.luckysparrow.ch'`

- [x] PRJ-616 Harden the Coolify primary deploy path and explicit fallback workflow
  - Owner: Ops/Release
  - Group: Production Truth And Deploy Automation Closure
  - Depends on: PRJ-615
  - Priority: P0
  - Status: DONE
  - Why now:
    - the repo now exposes parity drift explicitly, and live production smoke
      is failing because deployed truth is behind repo truth, so the next slice
      must harden the primary Coolify deploy path and make fallback usage
      explicit instead of operator-implicit
  - Result:
    - repo-driven deploy remains the primary path, fallback remains bounded,
      and release evidence can prove which path actually produced the running
      production baseline
  - Validation:
    - targeted pytest coverage
    - live deploy plus release-smoke verification
  - Evidence:
    - the canonical Coolify app `jr1oehwlzl8tcn3h8gh2vvih` was corrected from
      `Public GitHub` to the GitHub App source `vps-luckysparrow`
    - the source repository was corrected from the pre-rename
      `Wroblewski-Patryk/LuckySparrow` to `Wroblewski-Patryk/Personality`
    - local `origin` was aligned to
      `https://github.com/Wroblewski-Patryk/Personality.git` so push target and
      deploy source now describe the same repository
    - the bounded fallback posture remains webhook first, then UI redeploy only
      when source automation proof is missing

- [x] PRJ-634 Wire runtime build revision to Coolify predefined source commit
  - Owner: Ops/Release
  - Group: Production Truth And Deploy Automation Closure
  - Depends on: PRJ-616
  - Priority: P0
  - Status: DONE
  - Why now:
    - source automation was repaired, but production still reported
      `runtime_build_revision=unknown`, so release smoke could not yet prove
      full repo-to-production parity
  - Result:
    - the repo-owned compose contract now references
      `${APP_BUILD_REVISION:-unknown}` instead of `SOURCE_COMMIT` directly
    - the canonical Coolify app now maps `APP_BUILD_REVISION=$SOURCE_COMMIT`
      as a runtime-only variable, and the shadowing `SOURCE_COMMIT=unknown`
      variables were removed
    - live production now exposes a declared `runtime_build_revision` that
      matches local repo `HEAD`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_coolify_compose.py tests/test_deployment_trigger_scripts.py` -> `40 passed`
    - `docker compose -f docker-compose.coolify.yml config` -> OK
    - `.\scripts\run_release_smoke.ps1 -BaseUrl 'https://personality.luckysparrow.ch'` -> passed

- [x] PRJ-618 Freeze the first live website-reading workflow baseline
  - Owner: Planning Agent
  - Group: Live Web-Knowledge Workflow Activation
  - Depends on: PRJ-617
  - Priority: P0
  - Status: DONE
  - Why now:
    - deploy parity is now repaired, so the next blocker is no longer
      production ambiguity but the missing explicit product contract for
      "check this website and tell me what it says"
  - Result:
    - canonical architecture now freezes one bounded website-reading workflow
      that allows either direct URL review or search-first page review through
      the existing planning -> permission-gate -> action boundary
    - input, output, safety, and memory-capture boundaries are explicit and do
      not rely on test inference alone
  - Validation:
    - architecture/product/runtime cross-review

- [x] PRJ-619 Implement operator-visible website-reading readiness and guardrails
  - Owner: Backend Builder
  - Group: Live Web-Knowledge Workflow Activation
  - Depends on: PRJ-618
  - Priority: P0
  - Status: DONE
  - Why now:
    - the workflow contract is now frozen, so backend truth should expose
      whether live website reading is available, bounded, and blocked by
      provider or policy posture
  - Result:
    - existing health/debug surfaces expose website-reading readiness,
      bounded read semantics, and operator-visible blockers or next actions
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py` -> `187 passed`

- [x] PRJ-620 Add behavior and release proof for live web-knowledge workflows
  - Owner: QA/Test
  - Group: Live Web-Knowledge Workflow Activation
  - Depends on: PRJ-619
  - Priority: P0
  - Status: DONE
  - Why now:
    - the workflow is now frozen and machine-visible, so the next slice should
      prove the same website-reading contract through behavior-validation and
      release evidence instead of `/health` only
  - Result:
    - release smoke, debug incident evidence, and incident-evidence bundles now
      require the same bounded `website_reading_workflow` contract as `/health`
    - bounded web-knowledge behavior proof stays anchored in the existing
      `T14.1`, `T14.2`, and `T17.1` scenario lane instead of a parallel harness
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_observability_policy.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py` -> `122 passed`
    - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json` -> `14 passed`, `gate_status=pass`

- [x] PRJ-621 Sync docs/context for live web-knowledge workflows
  - Owner: Product Docs Agent
  - Group: Live Web-Knowledge Workflow Activation
  - Depends on: PRJ-620
  - Priority: P1
  - Status: DONE
  - Why now:
    - behavior and release proof are now live, so runtime reality, testing
      notes, ops guidance, and planning truth should describe the same bounded
      website-reading contract
  - Result:
    - docs and source-of-truth files now describe one shared proof path across
      `/health`, incident evidence, health snapshots, and bounded behavior
      scenarios
  - Validation:
    - docs/context cross-review against `PRJ-620` runtime and test evidence

- [x] PRJ-622 Freeze the durable capability-record baseline
  - Owner: Planning Agent
  - Group: Durable Role/Skill/Tool-Authorization Catalog
  - Depends on: PRJ-621
  - Priority: P1
  - Status: DONE
  - Why now:
    - the website-reading baseline is already frozen and proven, so the next
      truthful step is to freeze how durable role presets, durable skill
      descriptions, and per-user tool authorization records should coexist
      without widening execution authority
  - Result:
    - canonical architecture now defines one bounded durable capability-record
      layer where:
      - role presets remain descriptive records and runtime still owns active
        role selection
      - skill records remain metadata and planning guidance, not executable
        authority
      - tool authorization records remain bounded per-user permission posture,
        not a second action engine
      - backend callers must preserve description, selection, and authorization
        as separate truths
  - Validation:
    - architecture/product cross-review of `docs/architecture/03_identity_roles_skills.md`,
      `docs/architecture/16_agent_contracts.md`, existing backend capability
      surfaces, and planning/context truth

- [x] PRJ-623 Implement runtime-backed role, skill, and tool-authorization catalog surfaces
  - Owner: Backend Builder
  - Group: Durable Role/Skill/Tool-Authorization Catalog
  - Depends on: PRJ-622
  - Priority: P1
  - Status: DONE
  - Why now:
    - the durable capability-record truth model is frozen, so runtime should
      now expose that same model through existing `/health` and internal
      inspection surfaces instead of leaving callers to reconstruct it from
      disconnected role, skill, and connector snapshots
  - Result:
    - `capability_catalog` now distinguishes:
      - described role presets
      - described skill records
      - runtime selection surfaces for current role and selected skills
      - authorization posture for approved tool families and operations
    - `/health` shows the global policy-backed capability posture, while
      internal inspection shows the same catalog for the requested user scope
      without inventing a parallel authorization system
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py` -> `87 passed`

- [x] PRJ-624 Add release and behavior evidence for capability-record truthfulness
  - Owner: QA/Test
  - Group: Durable Role/Skill/Tool-Authorization Catalog
  - Depends on: PRJ-623
  - Priority: P1
  - Status: DONE
  - Why now:
    - capability records are now visible in runtime, so release and behavior
      evidence must prove the catalog does not blur described metadata into
      executable or authorized authority
  - Result:
    - release smoke now checks the capability-record truth model, described
      role and skill coverage, and the distinction between public read
      operations and confirmation-gated organizer mutations
    - runtime behavior coverage now proves that described work-partner skill
      metadata does not magically grant unrelated organizer mutations during a
      bounded website-reading turn
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_deployment_trigger_scripts.py` -> `131 passed`

- [x] PRJ-625 Sync docs/context for the durable capability-record baseline
  - Owner: Product Docs Agent
  - Group: Durable Role/Skill/Tool-Authorization Catalog
  - Depends on: PRJ-624
  - Priority: P1
  - Status: DONE
  - Why now:
    - capability-record truth and evidence are already live, so runtime
      reality, testing guidance, ops notes, planning, and context should all
      describe the same model before organizer daily-use work continues
  - Result:
    - runtime reality, testing guidance, runbook, planning, and repository
      context now all describe the same durable capability-record boundary:
      described metadata, runtime selection, and authorization posture remain
      separate truths
  - Validation:
    - doc/context cross-review against `PRJ-622..PRJ-624` architecture,
      runtime, tests, and release-smoke contract

- [x] PRJ-626 Freeze the daily-use organizer workflow baseline
  - Owner: Planning Agent
  - Group: Organizer-Tool Daily-Use Activation
  - Depends on: PRJ-625
  - Priority: P1
  - Status: DONE
  - Why now:
    - the organizer stack is already machine-visible and technically frozen,
      but `v1` still needs one explicit product baseline for what daily-use
      organizer help really means in practice
  - Result:
    - one bounded daily-use organizer workflow set is now frozen for ClickUp
      task review and mutation, Google Calendar availability inspection, and
      Google Drive metadata-only file inspection, together with explicit
      provider boundaries, opt-in posture, and confirmation posture
  - Validation:
    - architecture/product/ops cross-review against canonical contracts and
      live organizer-stack health posture

- [x] PRJ-627 Implement operator-facing provider activation and user-facing readiness summaries
  - Owner: Backend Builder
  - Group: Organizer-Tool Daily-Use Activation
  - Depends on: PRJ-626
  - Priority: P1
  - Status: DONE
  - Why now:
    - the frozen daily-use organizer baseline needs a clearer runtime-visible
      readiness summary so operators and future UI callers can tell whether
      each workflow is truly ready for daily use
  - Result:
    - `/health.connectors.organizer_tool_stack` now exposes workflow-level
      daily-use readiness for ClickUp, Google Calendar, and Google Drive, and
      `/health.v1_readiness` reuses that same truth as a simpler product-stage
      summary
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py` -> `87 passed`

- [x] PRJ-628 Add end-to-end proof for organizer daily-use workflows
  - Owner: QA/Test
  - Group: Organizer-Tool Daily-Use Activation
  - Depends on: PRJ-627
  - Priority: P1
  - Status: DONE
  - Why now:
    - the frozen organizer daily-use baseline must be proven through the same
      release, incident-evidence, and behavior gates that claim no-UI `v1`
      readiness
  - Result:
    - release smoke, incident-evidence bundles, and behavior validation now
      prove the same organizer daily-use acceptance posture instead of only
      abstract provider readiness
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py` -> `30 passed`
    - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json` -> `15 passed`

- [x] PRJ-629 Sync docs/context for organizer daily-use activation
  - Owner: Product Docs Agent
  - Group: Organizer-Tool Daily-Use Activation
  - Depends on: PRJ-628
  - Priority: P1
  - Status: DONE
  - Why now:
    - the organizer daily-use lane is only trustworthy if runtime reality,
      testing guidance, ops notes, and planning/context describe the same proof
      path
  - Result:
    - canonical docs and repository context now describe organizer daily-use
      readiness as one shared runtime and evidence contract rather than as
      only abstract provider readiness
  - Validation:
    - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json` -> `15 passed`

- [x] PRJ-630 Freeze the final no-UI V1 daily-use acceptance bundle
  - Owner: Planning Agent
  - Group: Final No-UI V1 Acceptance Closure
  - Depends on: PRJ-629
  - Priority: P0
  - Status: DONE
  - Why now:
    - the repo needs one explicit final contract that says when no-UI `v1`
      is genuinely real for daily use, rather than only implying it from many
      separate healthy surfaces
  - Result:
    - `/health.v1_readiness` now exposes one final acceptance bundle contract
      with named gate states and canonical runtime surfaces for conversation,
      learned-state inspection, website reading, tool-grounded learning,
      organizer daily use, and deploy parity
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py` -> `87 passed`

- [x] PRJ-631 Add end-to-end daily-use scenarios for conversation, web reading, learning, and organizer posture
  - Owner: QA/Test
  - Group: Final No-UI V1 Acceptance Closure
  - Depends on: PRJ-630
  - Priority: P0
  - Status: DONE
  - Why now:
    - the final acceptance bundle needs scenario-level proof that the
      personality can actually help in a believable day-to-day no-UI flow, not
      just expose many healthy runtime surfaces
  - Result:
    - final `T18.1..T18.2` scenarios now prove website-reading recall and
      organizer follow-up inside the no-UI `v1` acceptance lane
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py -k "tool_grounded_learning_scenarios or final_v1_daily_use_scenarios"` -> `2 passed`
    - `.\.venv\Scripts\python -m pytest -q tests/test_behavior_validation_script.py tests/test_api_routes.py` -> `108 passed`
    - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json` -> `16 passed`

- [x] PRJ-611 Sync docs/context for the capability-catalog baseline
  - Owner: Product Docs Agent
  - Group: Capability Catalog And Future-UI Bootstrap
  - Depends on: PRJ-610
  - Priority: P1
  - Status: DONE
  - Why now:
    - the capability-catalog surface and proof path are live, so docs and
      repository truth must describe the same backend-owned baseline
  - Result:
    - runtime reality, testing guidance, ops notes, planning truth, and
      repository context now describe the same bounded capability-catalog
      surface and its future UI/admin role
  - Validation:
    - docs/context cross-review against runtime and smoke contract

- [x] PRJ-610 Add release and regression evidence for the capability catalog
  - Owner: QA/Test
  - Group: Capability Catalog And Future-UI Bootstrap
  - Depends on: PRJ-609
  - Priority: P1
  - Status: DONE
  - Why now:
    - the capability catalog is now live in backend surfaces, so smoke and
      regression evidence must pin it before future UI/admin callers depend on
      it
  - Result:
    - release smoke and incident-evidence bundle validation now require the
      same bounded capability-catalog contract that API regressions pin
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_deployment_trigger_scripts.py`

- [x] PRJ-609 Expose one backend capability catalog for future UI/admin callers
  - Owner: Backend Builder
  - Group: Capability Catalog And Future-UI Bootstrap
  - Depends on: PRJ-608
  - Priority: P1
  - Status: DONE
  - Why now:
    - the capability-catalog contract is now frozen, so the backend can expose
      one bounded catalog payload without inventing new source-of-truth rules
  - Result:
    - `/health.capability_catalog` and internal inspection now expose one
      bounded aggregated capability view composed from already approved backend
      truth
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_deployment_trigger_scripts.py`

- [x] PRJ-608 Freeze the backend capability-catalog baseline
  - Owner: Planner
  - Group: Capability Catalog And Future-UI Bootstrap
  - Depends on: PRJ-607
  - Priority: P1
  - Status: DONE
  - Why now:
    - deploy automation, organizer activation, and tool-grounded learning are
      now machine-visible, but future UI/admin work still lacks one combined
      backend contract for capability, role, skill, and provider readiness
  - Result:
    - canonical architecture now defines one bounded backend
      capability-catalog contract that composes existing health,
      internal-inspection, role-skill, and connector surfaces without creating
      a parallel execution or authorization system
  - Validation:
    - architecture/product cross-review

- [x] PRJ-607 Sync docs/context for tool-grounded learning capture
  - Owner: Product Docs Agent
  - Group: Tool-Grounded Learning Capture
  - Depends on: PRJ-606
  - Priority: P1
  - Status: DONE
  - Why now:
    - the bounded tool-grounded learning contract and proof path are now live,
      so runtime reality, testing guidance, ops notes, and planning truth
      must describe the same baseline
  - Result:
    - runtime reality, testing guidance, ops notes, architecture testing
      guidance, and context truth now describe one shared bounded
      tool-grounded learning baseline and evidence path
  - Validation:
    - docs/context cross-review against `PRJ-606` validation outputs

- [x] PRJ-606 Add behavior and release evidence for tool-grounded learning
  - Owner: QA/Test
  - Group: Tool-Grounded Learning Capture
  - Depends on: PRJ-605
  - Priority: P1
  - Status: DONE
  - Why now:
    - tool-grounded learning is now live in runtime and inspection surfaces,
      but release and behavior proof still did not pin that same bounded
      contract
  - Result:
    - behavior validation, release smoke, and incident-evidence gates now
      prove that approved external reads can influence later cognition only
      through the bounded action-owned and memory-owned learning contract
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py` -> `233 passed`
    - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json` -> `14 passed`, `gate_status=pass`
    - targeted pytest coverage
    - behavior-validation or smoke evidence

- [x] PRJ-605 Implement bounded memory capture for approved external-read results
  - Owner: Backend Builder
  - Group: Tool-Grounded Learning Capture
  - Depends on: PRJ-604
  - Priority: P1
  - Status: DONE
  - Why now:
    - the architecture now allows bounded tool-grounded learning, but approved
      external reads still ended at turn-local notes instead of durable learned
      knowledge
  - Result:
    - action now emits bounded tool-grounded learning candidates for approved
      read operations and memory persists them as semantic conclusions
    - learned-state inspection now distinguishes tool-grounded semantic
      conclusions from other semantic learned knowledge
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py` -> `228 passed`

- [x] PRJ-604 Freeze the bounded tool-grounded learning contract
  - Owner: Planner
  - Group: Tool-Grounded Learning Capture
  - Depends on: PRJ-603
  - Priority: P1
  - Status: DONE
  - Why now:
    - external reads already exist through bounded search, browser, and
      organizer-tool operations, but the repo still lacks one explicit durable
      contract for how those reads may become learned knowledge
  - Result:
    - canonical architecture now defines one bounded tool-grounded learning
      contract with approved source families, action-owned capture,
      memory-owned persistence, and forbidden raw-payload persistence
  - Validation:
    - architecture/product/runtime cross-review

- [x] PRJ-603 Sync docs/context for organizer-tool credential activation
  - Owner: Product Docs Agent
  - Group: Organizer-Tool Credential Activation
  - Depends on: PRJ-602
  - Priority: P1
  - Status: DONE
  - Why now:
    - activation posture is now actionable in `/health` and proven through
      smoke plus incident evidence, but canonical docs and repository truth
      still need the richer activation contract
  - Result:
    - runtime reality, testing guidance, ops notes, planning truth, and
      repository context now describe the richer organizer-tool activation
      snapshot plus provider-specific next-action posture consistently
  - Validation:
    - docs/context cross-review against `/health.connectors.organizer_tool_stack`
      and the `PRJ-602` release-smoke contract

- [x] PRJ-602 Add release and incident evidence for organizer-tool activation posture
  - Owner: QA/Test
  - Group: Organizer-Tool Credential Activation
  - Depends on: PRJ-601
  - Priority: P1
  - Status: DONE
  - Why now:
    - activation is now actionable in `/health.connectors.organizer_tool_stack`,
      but release and incident evidence still only distinguished the frozen
      stack from a provider-ready stack at a coarser level
  - Result:
    - release smoke, incident evidence, and incident-evidence bundles now
      validate the same `activation_snapshot` contract and next-action posture
      as `/health.connectors.organizer_tool_stack`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_api_routes.py` -> `111 passed`

- [x] PRJ-601 Expose one actionable onboarding surface for organizer-tool activation
  - Owner: Backend Builder
  - Group: Organizer-Tool Credential Activation
  - Depends on: PRJ-600
  - Priority: P1
  - Status: DONE
  - Why now:
    - the credential baseline is now frozen, but operators still have to infer
      activation steps from multiple provider-specific fields
  - Done when:
    - backend surfaces expose one operator-facing activation snapshot with
      credential gaps, opt-in posture, and provider-specific next actions
  - Result:
    - `/health.connectors.organizer_tool_stack.activation_snapshot` now gives
      one shared onboarding view with provider-specific required settings,
      missing settings, readiness, confirmation posture, and next actions
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py` -> `87 passed`

- [x] PRJ-600 Freeze the production credential-activation baseline for organizer tools
  - Owner: Planner
  - Group: Organizer-Tool Credential Activation
  - Depends on: PRJ-599
  - Priority: P0
  - Status: DONE
  - Why now:
    - the first organizer-tool stack is already behavior-proven and
      machine-visible, but production still cannot treat it as truly live
      until credential posture and provider-specific activation requirements
      are frozen in one place
  - Done when:
    - one explicit operator baseline records required secrets, opt-ins, and
      provider-specific readiness checks for the first organizer-tool stack
  - Result:
    - the frozen production organizer stack now has one explicit credential
      baseline for ClickUp, Google Calendar, and Google Drive
    - read-only activation versus confirmation-bound mutation posture is now
      explicit in canonical docs instead of being implied from scattered
      runtime fields
  - Validation:
    - architecture/product/ops cross-review

- [x] PRJ-599 Sync docs/context for the deployment-automation baseline
  - Owner: Product Docs Agent
  - Group: Coolify Deployment Automation Reliability
  - Depends on: PRJ-598
  - Priority: P1
  - Status: DONE
  - Why now:
    - runtime and release smoke now expose deployment provenance through one
      shared contract, but the runbook and planning truth still need the same
      vocabulary and proof path
  - Done when:
    - runbook, planning truth, and repository context describe the same
      repo-driven Coolify automation posture and bounded fallback evidence path
  - Validation:
    - doc-and-context sync
    - release-smoke wording cross-check against the current production failure
      mode before redeploy

- [x] PRJ-612 Freeze the durable role/skill/tool-authorization architecture baseline
  - Owner: Product Docs Agent
  - Group: Future UI/Admin Capability Catalog
  - Depends on: none
  - Priority: P1
  - Status: DONE
  - Why now:
    - future UI/admin work needs one explicit architecture baseline for
      prompt-backed role presets, revisable skill descriptions, and
      per-user tool activation without reopening action-boundary or secret
      ownership rules later
  - Done when:
    - canonical architecture defines durable role presets with prompt-oriented
      definitions and runtime selection ownership
    - canonical architecture defines durable skill descriptions with bounded
      revision posture and linked approved tool families
    - canonical architecture defines per-user tool authorization posture while
      preserving external secret ownership and action-owned execution
  - Validation:
    - architecture cross-review

- [x] PRJ-598 Add machine-visible release evidence for deployment automation posture
  - Owner: Ops/Release
  - Group: Coolify Deployment Automation Reliability
  - Depends on: PRJ-597
  - Priority: P0
  - Status: DONE
  - Why now:
    - the repo now has a frozen deploy baseline, but production still lacks
      one machine-visible proof that distinguishes source-automation success
      from webhook or UI fallback
    - later tool-activation work should not depend on manually inferred deploy
      provenance
  - Done when:
    - release evidence records whether the current production deploy came from
      the primary automation path or from bounded fallback
    - smoke or deploy evidence can fail clearly when deployment provenance is
      missing or ambiguous
  - Result:
    - `/health.deployment` now exposes the shared deployment-automation owner,
      canonical Coolify app identity, and primary/fallback trigger baseline
    - deploy webhook evidence now records provenance fields
      (`policy_owner`, `trigger_mode`, `trigger_class`,
      `canonical_coolify_app`)
    - exported incident evidence and release smoke now validate the same
      deployment provenance contract instead of relying on manual operator
      inference
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_observability_policy.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py` -> `115 passed`

- [x] PRJ-575 Analyze post-v1 architecture gaps and seed the next execution queue
  - Owner: Planning Agent
  - Group: Post-V1 Architecture Gap Analysis
  - Depends on: PRJ-574
  - Priority: P0
  - Status: DONE
  - Why now:
    - no seeded queue remained after `PRJ-574`
    - the next slices needed to come from fresh production truth instead of
      historical backlog carry-over
  - Done when:
    - canonical docs, runtime reality, and live production `/health` are
      compared together
    - a new detailed queue with one explicit `READY` task is seeded in
      planning and context files
  - Result:
    - a new queue is now seeded through `PRJ-595`
    - the next wave is intentionally ordered around attention, proactive,
      retrieval provider alignment, learned-state introspection, and
      organizer-tool production readiness
  - Validation:
    - architecture/runtime/context review plus live production `/health`
      snapshot

- [x] PRJ-576 Freeze the durable-attention production baseline and cutover gate
  - Owner: Planner
  - Group: Durable Attention Production Cutover
  - Depends on: PRJ-575
  - Priority: P0
  - Status: DONE
  - Why now:
    - production `/health.attention` still reports
      `coordination_mode=in_process` and `contract_store_mode=in_process_only`
      even though repository-backed durable inbox readiness is already green
    - this is now the clearest remaining runtime-topology mismatch after
      reflection and cadence externalization
  - Done when:
    - one explicit production cutover baseline records when durable attention
      becomes the selected owner in production
    - cutover criteria, rollback posture, and proof surfaces are frozen before
      the production switch
  - Validation:
    - architecture/runtime/ops cross-review plus live production
      `/health.attention`
  - Result:
    - durable inbox is now frozen as the target production attention owner
    - cutover proof is now explicitly tied to `/health.attention`,
      `/health.runtime_topology`, `/health.conversation_channels.telegram`,
      and release smoke
    - rollback posture is now explicitly `ATTENTION_COORDINATION_MODE=in_process`
      until burst claim, cleanup, and reply-order semantics are proven stable

- [x] PRJ-577 Switch production attention ownership to durable inbox
  - Owner: Backend Builder
  - Group: Durable Attention Production Cutover
  - Depends on: PRJ-576
  - Priority: P0
  - Status: DONE
  - Done when:
    - production uses `ATTENTION_COORDINATION_MODE=durable_inbox`
    - Telegram burst coalescing and reply delivery remain healthy after deploy
    - `/health.attention` shows the durable contract-store baseline instead of
      `in_process_only`
  - Result:
    - the production attention owner is now `durable_inbox`
    - repository-backed contract-store posture is now live in public `/health`
    - the live cutover required selecting the correct Coolify team scope,
      then force-starting the queued deployment from the canonical
      application page
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_coolify_compose.py tests/test_api_routes.py tests/test_main_lifespan_policy.py` -> `93 passed`
    - `docker compose -f docker-compose.coolify.yml config` -> OK
    - `.\scripts\run_release_smoke.ps1 -BaseUrl 'https://personality.luckysparrow.ch'` -> passed
    - production deployment `amz31iyapwr3t9z9tanpe2jb` imported commit `d3707a0`
    - production `/health.attention.coordination_mode=durable_inbox`
    - production `/health.conversation_channels.telegram.round_trip_ready=true`

- [x] PRJ-578 Add durable-attention release and behavior evidence
  - Owner: QA/Test
  - Group: Durable Attention Production Cutover
  - Depends on: PRJ-577
  - Priority: P1
  - Status: DONE
  - Done when:
    - release smoke, incident evidence, and behavior validation all prove the
      durable-attention production baseline
    - burst-message coalescing no longer depends on manual operator inspection
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_observability_policy.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py` -> `124 passed`
    - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json` -> `12 passed`
  - Result:
    - release smoke, debug `incident_evidence`, and incident-evidence bundles now require durable-attention posture and `runtime_topology.attention_switch` proof
    - behavior validation now includes a durable-attention burst-coalescing regression path instead of leaving burst assembly to manual operator inspection

- [x] PRJ-579 Sync docs/context for durable-attention production baseline
  - Owner: Product Docs
  - Group: Durable Attention Production Cutover
  - Depends on: PRJ-578
  - Priority: P1
  - Status: DONE
  - Done when:
    - architecture, runtime reality, ops, testing, planning, and context truth
      describe the same durable-attention production baseline
  - Validation:
    - `.\scripts\run_release_smoke.ps1 -BaseUrl 'https://personality.luckysparrow.ch'` -> passed
  - Result:
    - architecture, runtime reality, testing guidance, ops notes, task truth,
      and project state now all describe the same live durable-attention
      production baseline
    - the durable-attention proof path is now explicit across public `/health`,
      exported `incident_evidence`, release smoke, and behavior validation

- [x] PRJ-580 Freeze the proactive opt-in production policy baseline
  - Owner: Planner
  - Group: Proactive Opt-In Production Activation
  - Depends on: PRJ-579
  - Priority: P1
  - Status: DONE
  - Done when:
    - one explicit policy records whether production proactive remains disabled
      or becomes enabled for bounded opt-in follow-up
    - delivery eligibility, anti-spam posture, and rollback conditions are
      frozen before activation
  - Validation:
    - architecture/product/ops cross-review plus live production `/health.proactive`
  - Result:
    - production proactive is now frozen as bounded opt-in follow-up instead
      of a permanently disabled posture
    - external scheduler remains the cadence owner, existing anti-spam
      thresholds remain the minimum guardrail contract, and rollback remains
      one explicit switch back to `PROACTIVE_ENABLED=false`

- [x] PRJ-581 Enable bounded proactive follow-up in production
  - Owner: Backend Builder
  - Group: Proactive Opt-In Production Activation
  - Depends on: PRJ-580
  - Priority: P1
  - Status: DONE
  - Done when:
    - production proactive runtime follows the frozen opt-in policy
    - `/health.proactive` no longer reports `disabled_by_policy` for the chosen
      bounded baseline
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_coolify_compose.py tests/test_api_routes.py tests/test_scheduler_worker.py` -> `105 passed`
    - `docker compose -f docker-compose.coolify.yml config` -> OK
    - production `/health.proactive.enabled=true`
    - production `/health.proactive.production_baseline_state=external_scheduler_target_owner`
  - Result:
    - repository-driven Coolify production now defaults `PROACTIVE_ENABLED` to the bounded proactive baseline
    - live production no longer reports `disabled_by_policy`
    - the production cutover also confirmed that an explicit Coolify env override can silently mask repo-driven defaults

- [x] PRJ-582 Prove proactive delivery and anti-spam behavior in release evidence
  - Owner: QA/Test
  - Group: Proactive Opt-In Production Activation
  - Depends on: PRJ-581
  - Priority: P1
  - Status: DONE
  - Done when:
    - behavior validation proves both delivery-ready and blocked-by-guardrail
      proactive cases against the production policy
    - incident evidence and smoke checks expose the same proactive posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_observability_policy.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py` -> `126 passed`
    - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json` -> `12 passed`
    - `.\scripts\run_release_smoke.ps1 -BaseUrl 'https://personality.luckysparrow.ch'` -> passed
  - Result:
    - exported `incident_evidence`, incident-evidence bundle validation, and release smoke now require the same proactive owner posture as `/health.proactive`
    - proactive drift is now release-blocking instead of operator-inferred

- [x] PRJ-583 Sync docs/context for proactive production baseline
  - Owner: Product Docs
  - Group: Proactive Opt-In Production Activation
  - Depends on: PRJ-582
  - Priority: P1
  - Status: DONE
  - Done when:
    - docs and context truth align on the chosen proactive production posture
  - Validation:
    - `.\scripts\run_release_smoke.ps1 -BaseUrl 'https://personality.luckysparrow.ch'` -> passed
  - Result:
    - runtime reality, testing guidance, ops notes, planning, and repository context now describe the same live bounded proactive production baseline
    - the queue now advances to retrieval-provider baseline alignment

- [x] PRJ-584 Freeze the production retrieval-provider baseline and enforcement posture
  - Owner: Planner
  - Group: Retrieval Provider Baseline Alignment
  - Depends on: PRJ-583
  - Priority: P1
  - Status: DONE
  - Done when:
    - one explicit provider baseline is chosen for production retrieval
    - the strictness posture for provider/model/source enforcement is frozen
      before runtime changes
  - Validation:
    - architecture/runtime/ops cross-review
    - live production `/health.memory_retrieval`
  - Result:
    - `openai_api_embeddings` remains the explicit steady-state production baseline
    - `local_hybrid` remains the bounded transition owner and deterministic remains compatibility fallback
    - provider/model/source-rollout enforcement stays `warn` during runtime alignment and becomes release-strict only after `PRJ-585`

- [x] PRJ-585 Align production retrieval configuration and execution to the chosen provider baseline
  - Owner: Backend Builder
  - Group: Retrieval Provider Baseline Alignment
  - Depends on: PRJ-584
  - Priority: P1
  - Status: DONE
  - Done when:
    - production no longer reports `provider_baseline_not_aligned`
    - `/health.memory_retrieval` shows the chosen provider as both target and
      effective baseline
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_coolify_compose.py` -> `7 passed`
    - `docker compose -f docker-compose.coolify.yml config` -> OK
    - production `/health.memory_retrieval` shows requested/effective `openai`,
      `provider_owned_openai_api`, `aligned_openai_provider_owned`,
      `aligned_target_provider`, `aligned_with_defined_lifecycle_baseline`, and
      empty pending gaps
    - `.\scripts\run_release_smoke.ps1 -BaseUrl 'https://personality.luckysparrow.ch'` -> passed
  - Result:
    - repository-driven Coolify production now defaults to the approved OpenAI
      embedding provider and model baseline
    - live production no longer reports `provider_baseline_not_aligned`
    - retrieval lifecycle alignment now matches the provider baseline frozen in
      `PRJ-584`

- [x] PRJ-586 Add strict release and incident evidence for retrieval-provider alignment
  - Owner: QA/Test
  - Group: Retrieval Provider Baseline Alignment
  - Depends on: PRJ-585
  - Priority: P1
  - Status: DONE
  - Done when:
    - release smoke and incident evidence fail on retrieval provider drift for
      the selected production baseline
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py` -> `38 passed`
    - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json` -> `12 passed`
    - `.\scripts\run_release_smoke.ps1 -BaseUrl 'https://personality.luckysparrow.ch'` -> passed
  - Result:
    - release smoke now fails on retrieval-provider drift from `/health.memory_retrieval`
    - exported `incident_evidence` and incident-evidence bundles now prove the
      same retrieval alignment posture
    - CI behavior validation now fails when retrieval-provider incident
      evidence drifts from the approved baseline

- [x] PRJ-587 Sync docs/context for retrieval-provider baseline
  - Owner: Product Docs
  - Group: Retrieval Provider Baseline Alignment
  - Depends on: PRJ-586
  - Priority: P1
  - Status: DONE
  - Done when:
    - docs and context truth align on the selected retrieval provider baseline
      and enforcement posture
  - Validation:
    - `.\scripts\run_release_smoke.ps1 -BaseUrl 'https://personality.luckysparrow.ch'` -> passed
  - Result:
    - runtime reality, testing guidance, ops notes, planning docs, and context
      now describe the same aligned OpenAI retrieval-provider production
      baseline
    - the queue now advances to learned-state and personality-growth
      introspection in `PRJ-588`

- [x] PRJ-588 Freeze the backend introspection contract for learned personality growth
  - Owner: Planner
  - Group: Learned-State And Personality-Growth Introspection
  - Depends on: PRJ-587
  - Priority: P1
  - Status: DONE
  - Done when:
    - the repo records one explicit backend contract for exposing learned
      roles, selected skill metadata, reflection outputs, and planning
      continuity without pretending to expose self-modifying executable skills
  - Validation:
    - architecture/product cross-review
  - Result:
    - the learned-state lane now has one explicit bounded contract for
      personality-growth introspection
    - future widening stays backend-owned and must not imply self-modifying
      executable skill learning

- [x] PRJ-589 Expose richer backend-owned learned-state inspection surfaces
  - Owner: Backend Builder
  - Group: Learned-State And Personality-Growth Introspection
  - Depends on: PRJ-588
  - Priority: P1
  - Status: DONE
  - Done when:
    - internal inspection surfaces expose richer role, skill, preference,
      reflection, and planning-growth summaries for future UI consumption
    - health or internal inspection no longer reduce learned-state visibility
      to policy posture only
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py` -> `86 passed`
  - Result:
    - `/health.learned_state` now publishes the richer inspection section and
      summary contract instead of only owner/path posture
    - `GET /internal/state/inspect?user_id=...` now exposes backend-owned
      preference, knowledge, reflection-growth, role/skill visibility, and
      planning-continuity summaries for future UI or admin callers

- [ ] PRJ-590 Add regression and release evidence for learned-state introspection
  - Owner: QA/Test
  - Group: Learned-State And Personality-Growth Introspection
  - Depends on: PRJ-589
  - Priority: P2
  - Status: DONE
  - Done when:
    - regression and incident-evidence flows pin the richer learned-state
      inspection contract
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py tests/test_api_routes.py` -> `126 passed`
  - Result:
    - release smoke now validates the richer learned-state section contract
      from `/health`, exported `incident_evidence`, and incident bundles
    - targeted smoke regressions now fail when learned-state contract sections
      are partially missing instead of silently degrading to owner-only posture

- [x] PRJ-591 Sync docs/context for learned-state introspection
  - Owner: Product Docs
  - Group: Learned-State And Personality-Growth Introspection
  - Depends on: PRJ-590
  - Priority: P2
  - Status: DONE
  - Done when:
    - docs and context truth align on the richer backend personality-growth
      introspection baseline
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py tests/test_api_routes.py` -> `126 passed`
  - Result:
    - canonical contracts, runtime reality, testing guidance, ops notes, and
      planning/context truth now describe the richer bounded learned-state
      section and summary contract

- [x] PRJ-592 Freeze the first production organizer-tool stack baseline
  - Owner: Planner
  - Group: Production Organizer-Tool Readiness
  - Depends on: PRJ-591
  - Priority: P2
  - Status: DONE
  - Done when:
    - one explicit backend baseline records which ClickUp, Calendar, and Drive
      slices count as the first real organization stack for life/work support
    - confirmation, opt-in, and bounded-read constraints remain explicit
  - Validation:
    - architecture/product/connector cross-review
  - Result:
    - one explicit organizer-tool baseline now records the first production
      ClickUp, Calendar, and Drive slices for no-UI assistant and work-partner
    - ClickUp reads/writes, Google Calendar availability reads, and Google
      Drive file-list reads are the only approved organizer-tool stack members
      in this first production baseline

- [x] PRJ-593 Expose one acceptance surface for organizer-tool readiness and opt-in gaps
  - Owner: Backend Builder
  - Group: Production Organizer-Tool Readiness
  - Depends on: PRJ-592
  - Priority: P2
  - Status: DONE
  - Done when:
    - backend surfaces expose one operator-visible readiness bundle for
      ClickUp, Calendar, and Drive instead of fragmented credential states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py` -> `87 passed`
  - Result:
    - `/health.connectors.organizer_tool_stack` now summarizes approved
      organizer operations, credential gaps, opt-in requirements, and
      confirmation boundaries in one shared acceptance surface

- [x] PRJ-594 Add behavior and smoke evidence for work-partner organizer-tool posture
  - Owner: QA/Test
  - Group: Production Organizer-Tool Readiness
  - Depends on: PRJ-593
  - Priority: P2
  - Status: DONE
  - Done when:
    - behavior or smoke evidence proves the same organizer-tool posture that
      backend readiness surfaces describe
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py tests/test_api_routes.py` -> `228 passed`
    - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json` -> `13 passed`, `gate_status=pass`
  - Result:
    - release smoke now validates the frozen organizer-tool stack contract from
      `/health.connectors.organizer_tool_stack`
    - incident evidence and incident-evidence bundles now carry the same
      organizer-tool proof surface
    - runtime behavior scenarios now prove work-partner organizer usage through
      `T16.1..T16.3` for ClickUp task reads, Google Calendar availability, and
      Google Drive metadata listing

- [x] PRJ-595 Sync docs/context for organizer-tool production readiness
  - Owner: Product Docs
  - Group: Production Organizer-Tool Readiness
  - Depends on: PRJ-594
  - Priority: P2
  - Status: DONE
  - Done when:
    - docs and context truth align on the first production organizer-tool
      baseline for work-partner and no-UI assistant flows
  - Validation:
    - doc-and-context sync
  - Result:
    - canonical contracts, runtime reality, testing guidance, runbook notes,
      planning docs, and repository context now describe the same organizer
      stack baseline
    - the organizer-tool lane no longer has a seeded follow-up slice after this
      sync

- [x] PRJ-572 Externalize production reflection queue ownership
  - Owner: Ops/Release
  - Group: Post-V1 Production Hardening
  - Depends on: PRJ-571
  - Priority: P0
  - Why now:
    - live production `/health.reflection.external_driver_policy` still reports
      `production_baseline_ready=false`
    - the runtime already exposes the external entrypoint and supervision
      policy, so the next smallest useful step is to make production actually
      use that owner path
  - Done when:
    - production no longer runs app-local reflection queue drain as the active
      baseline
    - `/health.reflection.external_driver_policy` and supervision posture move
      to the externalized baseline without breaking turn handling
  - Validation:
    - relevant pytest coverage
    - Coolify deploy
    - production `/health` and release-smoke evidence
  - Status: DONE
  - Result:
    - repository-driven Coolify production now defaults
      `REFLECTION_RUNTIME_MODE` to `deferred`
    - forced deploy `nlcp1kpmxxhvq094fssz7qfk` finished on commit `13d8972`,
      and production `/health.reflection.external_driver_policy` now reports
      `selected_runtime_mode=deferred`
    - app-local reflection worker no longer starts in production, while
      Telegram foreground round-trip posture remained healthy through the
      cutover

- [x] PRJ-573 Externalize maintenance and proactive cadence ownership
  - Owner: Ops/Release
  - Group: Post-V1 Production Hardening
  - Depends on: PRJ-572
  - Priority: P0
  - Why now:
    - production `/health.scheduler.external_owner_policy` still shows
      `in_process` ownership
    - proactive and maintenance cadence already have target entrypoints and
      proof surfaces, so the next gap is operational cutover
  - Done when:
    - selected scheduler execution mode is externalized in production
    - cadence cutover proof remains green after deploy
  - Validation:
    - relevant pytest coverage
    - release smoke
    - production `/health.scheduler`
  - Status: DONE
  - Result:
    - repository-driven Coolify production now defaults
      `SCHEDULER_EXECUTION_MODE` to `externalized`
    - dedicated Coolify cadence services now run the canonical
      `scripts/run_maintenance_tick_once.py` and
      `scripts/run_proactive_tick_once.py` entrypoints with a short
      retry-on-failure backoff so post-deploy migration races do not delay
      cutover proof for a full cadence interval
    - forced deploy `m8jd7i3sqiv8f8fuvlo367ki` finished on commit `2a4a573`,
      and production `/health.scheduler.external_owner_policy` now reports
      `selected_execution_mode=externalized`, `cutover_proof_ready=true`, and
      `production_baseline_ready=true`
    - production `/health.reflection.supervision.blocking_signals` is empty
      and Telegram/API foreground round-trip posture remained healthy through
      the cutover

- [x] PRJ-574 Sync post-v1 production-hardening docs and release evidence
  - Owner: Product Docs
  - Group: Post-V1 Production Hardening
  - Depends on: PRJ-573
  - Priority: P1
  - Why now:
    - once reflection and cadence owners are externalized, runtime reality,
      runbook, testing, and planning truth must stop describing those lanes as
      transitional
  - Done when:
    - docs, context, and ops guidance describe the same externalized production
      baseline and evidence path
  - Validation:
    - doc-and-context sync across architecture, implementation, ops, testing,
      planning, and context
  - Status: DONE
  - Result:
    - runtime reality, testing guidance, planning docs, ops guidance, and
      repository context now describe the same externalized production-owner
      baseline
    - the post-v1 production-hardening queue is now complete through
      `PRJ-574`
    - release smoke plus production `/health` remain the canonical proof path
      for both reflection and cadence owner cutovers

- [ ] PRJ-540 Freeze the no-UI `v1` product contract and conversation-reliability gate
  - Owner: Planner
  - Group: Production Conversation Reliability
  - Depends on: PRJ-539
  - Priority: P0
  - Status: DONE
  - Why now:
    - the current runtime already exceeds classic MVP scope, but a
      user-reported Telegram no-response posture means `v1` cannot yet be
      called production-real
    - the repo needs one explicit product gate that says Telegram or API
      round-trip reliability is part of the `v1` release contract
  - Done when:
    - one explicit `v1` baseline records:
      - no UI is required for `v1`
      - Telegram or API conversation reliability is release-blocking
      - work-partner remains a role inside the same personality
      - future UI belongs to `v2`
  - Result:
    - canonical planning surfaces and `docs/architecture/10_future_vision.md`
      now align on one product interpretation where `v1` is backend-first and
      no-UI, `v2` begins with a dedicated UI or admin surface, and
      work-partner remains a role of the same personality rather than a
      separate persona
  - Validation:
    - architecture, runtime-reality, ops, and planning cross-review

- [ ] PRJ-541 Repair and instrument the Telegram ingress-to-delivery path
  - Owner: Backend Builder
  - Group: Production Conversation Reliability
  - Depends on: PRJ-540
  - Priority: P0
  - Status: DONE
  - Result:
    - Telegram conversation reliability now has one shared owner-level
      telemetry surface in `app/integrations/telegram/telemetry.py`
    - webhook ingress records received, rejected, queued, processed, and
      runtime-failed states, while Telegram delivery records attempt, success,
      and failure posture through the same bounded telemetry owner
    - `/health.conversation_channels.telegram` now exposes machine-visible
      round-trip readiness (`provider_backed_ready|missing_bot_token`) plus the
      latest ingress and delivery evidence for operator triage
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_delivery_router.py`
    - `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_runtime_pipeline.py`

- [ ] PRJ-542 Add Telegram round-trip smoke and incident-evidence coverage
  - Owner: QA/Test
  - Group: Production Conversation Reliability
  - Depends on: PRJ-541
  - Priority: P0
  - Status: DONE
  - Result:
    - runtime incident evidence now treats `conversation_channels.telegram` as
      a required policy posture surface alongside runtime policy, retrieval,
      scheduler, reflection, and connector execution
    - release smoke now validates Telegram conversation posture from `/health`,
      debug-mode `incident_evidence`, and incident-evidence bundles
    - behavior-validation gates now fail when incident evidence is missing the
      Telegram conversation reliability posture or carries an invalid
      round-trip baseline
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_observability_policy.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py`

- [ ] PRJ-543 Sync docs/context for the `v1` conversation-reliability baseline
  - Owner: Product Docs
  - Group: Production Conversation Reliability
  - Depends on: PRJ-542
  - Priority: P1
  - Status: DONE
  - Result:
    - canonical logging/debugging docs, runtime reality, testing guidance, ops
      notes, and planning truth now describe the same `v1`
      conversation-reliability evidence baseline
    - `/health.conversation_channels.telegram`, exported
      `incident_evidence.policy_posture["conversation_channels.telegram"]`,
      release smoke, and behavior-validation gates are now documented as one
      shared release-blocking proof surface for no-UI `v1`
  - Validation:
    - doc-and-context sync across architecture, implementation, ops, testing,
      planning, and context

- [x] PRJ-544 Freeze the canonical `v1` life-assistant workflow set
  - Owner: Planner
  - Group: Life Assistant Workflow Activation
  - Depends on: PRJ-543
  - Priority: P1
  - Status: DONE
  - Result:
    - canonical docs now freeze one bounded no-UI `v1` workflow set:
      reminder capture and follow-up, daily planning activation, task or goal
      check-in, and reflection-backed continuity over time
    - the same baseline now records explicit non-goals for this lane:
      no separate reminder subsystem, no calendar-grade due-date or recurrence
      contract yet, and no reminder UI
  - Validation:
    - cross-review across `09_mvp_scope`, `10_future_vision`,
      `16_agent_contracts`, and runtime reality

- [x] PRJ-545 Implement missing bounded workflow execution for reminders and daily support
  - Owner: Backend Builder
  - Group: Life Assistant Workflow Activation
  - Depends on: PRJ-544
  - Priority: P1
  - Status: DONE

- [x] PRJ-546 Add end-to-end behavior validation for life-assistant scenarios
  - Owner: QA/Test
  - Group: Life Assistant Workflow Activation
  - Depends on: PRJ-545
  - Priority: P1
  - Status: DONE

- [ ] PRJ-547 Sync docs/context for the `v1` life-assistant workflow baseline
  - Owner: Product Docs
  - Group: Life Assistant Workflow Activation
  - Depends on: PRJ-546
  - Priority: P1
  - Status: DONE

- [ ] PRJ-548 Freeze the learned-state model for `v1`
  - Owner: Planner
  - Group: Learned-State And Skill Introspection
  - Depends on: PRJ-547
  - Priority: P1
  - Status: DONE

- [ ] PRJ-549 Expose backend inspection surfaces for learned state and planning state
  - Owner: Backend Builder
  - Group: Learned-State And Skill Introspection
  - Depends on: PRJ-548
  - Priority: P1
  - Status: DONE

- [ ] PRJ-550 Add regression and incident-evidence coverage for introspection surfaces
  - Owner: QA/Test
  - Group: Learned-State And Skill Introspection
  - Depends on: PRJ-549
  - Priority: P1
  - Status: DONE
  - Result:
    - runtime incident evidence now treats `learned_state` as a required
      policy posture surface alongside runtime policy, retrieval, scheduler,
      reflection, connector execution, and Telegram conversation posture
    - release smoke now validates the learned-state introspection owner and
      internal inspection path from `/health`, debug-mode `incident_evidence`,
      and incident-evidence bundles
    - behavior-validation gate fixtures now fail when the learned-state
      posture is missing from incident evidence or carries the wrong owner/path
      contract
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py`
    - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`

- [ ] PRJ-551 Sync docs/context for learned-state and skill introspection
  - Owner: Product Docs
  - Group: Learned-State And Skill Introspection
  - Depends on: PRJ-550
  - Priority: P1
  - Status: DONE
  - Result:
    - canonical contracts, logging/debugging guidance, runtime reality,
      testing guidance, ops notes, and planning/context truth now describe the
      same learned-state inspection baseline for future UI and admin callers
    - `/health.learned_state`, internal
      `GET /internal/state/inspect?user_id=...`, and exported
      `incident_evidence.policy_posture["learned_state"]` are now documented
      as one shared backend introspection contract
  - Validation:
    - doc-and-context sync across architecture, implementation, ops, testing,
      planning, and context

- [ ] PRJ-552 Define the architecture baseline for web search and browser tool families
  - Owner: Planner
  - Group: Web Knowledge And Tooling Architecture
  - Depends on: PRJ-551
  - Priority: P1
  - Status: DONE
  - Result:
    - canonical architecture now records web search and browser access as new
      action-owned external capability kinds (`knowledge_search`,
      `web_browser`) under the same planning, permission-gate, and action
      validation boundary as existing connectors
    - the repo now explicitly rejects treating search or browsing as
      self-executing skills or as a second execution subsystem outside the
      action layer
  - Validation:
    - architecture and planning cross-review with explicit boundary note

- [ ] PRJ-553 Implement shared capability and permission-gate policy for web knowledge tools
  - Owner: Backend Builder
  - Group: Web Knowledge And Tooling Architecture
  - Depends on: PRJ-552
  - Priority: P1
  - Status: DONE
  - Result:
    - shared typed intents now model `knowledge_search` and `web_browser`
      under the same action-owned permission-gate path as existing external
      capability families
    - planner now emits bounded search and browser intents through the shared
      connector policy owner, and action blocks mode drift for those intents
      before any delivery or side effect path continues
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- [ ] PRJ-554 Expose readiness and debug visibility for the selected tool-family posture
  - Owner: Backend Builder
  - Group: Web Knowledge And Tooling Architecture
  - Depends on: PRJ-553
  - Priority: P1
  - Status: DONE
  - Result:
    - `/health.connectors` now exposes one shared web-knowledge posture
      snapshot plus policy-only execution-baseline entries for
      `knowledge_search` and `web_browser`
    - runtime `system_debug.adaptive_state` now mirrors the same
      web-knowledge tooling posture so future UI and operator triage can see
      authorization, fallback, and non-live provider state in one place
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py`

- [ ] PRJ-555 Sync docs/context for the web knowledge and tooling baseline
  - Owner: Product Docs
  - Group: Web Knowledge And Tooling Architecture
  - Depends on: PRJ-554
  - Priority: P1
  - Status: DONE
  - Result:
    - contracts, runtime reality, testing guidance, ops notes, and
      planning/context truth now describe the same action-owned but
      still-policy-only web-knowledge tooling baseline
    - `/health.connectors.web_knowledge_tools`,
      `/health.connectors.execution_baseline`, and runtime
      `system_debug.adaptive_state["web_knowledge_tools"]` are now documented
      as one shared visibility surface for future UI and operator triage
  - Validation:
    - doc-and-context sync across architecture, implementation, ops, testing,
      planning, and context

- [ ] PRJ-556 Freeze the first bounded provider-backed search, browser, and organization slices
  - Owner: Planner
  - Group: Search, Browser, And Organization Tool Expansion
  - Depends on: PRJ-555
  - Priority: P2
  - Status: DONE
  - Result:
    - the first provider-backed expansion set is now frozen as:
      - `knowledge_search:search_web` with `provider_hint=duckduckgo_html`
      - `web_browser:read_page` with `provider_hint=generic_http`
      - `task_system:update_task` with `provider_hint=clickup`
    - each slice now has an explicit bounded evidence contract instead of raw
      provider payload ambitions
  - Validation:
    - connector or tool policy cross-review across architecture and ops docs

- [ ] PRJ-557 Implement the selected bounded search, browser, and ClickUp slices
  - Owner: Backend Builder
  - Group: Search, Browser, And Organization Tool Expansion
  - Depends on: PRJ-556
  - Priority: P2
  - Status: DONE
  - Result:
    - planner now emits the frozen provider-backed slice set through the
      existing action-owned boundary:
      - `knowledge_search:search_web` via `duckduckgo_html`
      - `web_browser:read_page` via `generic_http`
      - `task_system:update_task` via ClickUp
    - action now executes those typed intents through bounded provider
      adapters, keeping output constrained to safe search-result previews,
      bounded page-read evidence, and status-only ClickUp task updates instead
      of raw provider payload passthrough
    - `/health.connectors`, runtime `system_debug.adaptive_state`, and the
      connector execution baseline now expose these slices as live first-path
      provider-backed execution instead of policy-only placeholders
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- [ ] PRJ-558 Add role-governed behavior validation for tool usage
  - Owner: QA/Test
  - Group: Search, Browser, And Organization Tool Expansion
  - Depends on: PRJ-557
  - Priority: P2
  - Status: DONE
  - Result:
    - behavior-validation scenarios now prove that life-organization and work
      turns can use the new bounded tool slices only through the existing
      role, planning, permission-gate, and action boundary
    - scenario-level coverage now pins:
      - analyst-driven DuckDuckGo web search
      - analyst-driven bounded browser page read
      - executor-aligned ClickUp task update with connector guardrail
    - the shared behavior-validation artifact and CI gate now include this
      tool-usage proof instead of relying only on unit and integration tests
  - Validation:
    - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`

- [ ] PRJ-559 Sync docs/context for bounded search, browser, and organization tooling
  - Owner: Product Docs
  - Group: Search, Browser, And Organization Tool Expansion
  - Depends on: PRJ-558
  - Priority: P2
  - Status: DONE
  - Result:
    - contracts, runtime reality, behavior-testing guidance, ops notes, and
      planning/context truth now all describe the same live bounded tool
      slices:
      - DuckDuckGo web search
      - generic HTTP page read
      - ClickUp task update
    - the same docs now point to scenario-level proof through behavior
      validation `T14.1..T14.3` instead of describing search and browser as
      policy-only placeholders
  - Validation:
    - doc-and-context sync across architecture, implementation, ops, testing,
      planning, and context

- [ ] PRJ-560 Freeze the backend work-partner role baseline
  - Owner: Planner
  - Group: Work-Partner Role And Capability Orchestration
  - Depends on: PRJ-559
  - Priority: P1
  - Status: DONE
  - Result:
    - canonical product and contract docs now freeze `work_partner` as a role
      of the same personality, not a second persona or separate execution
      subsystem
    - the role is now bounded to metadata-only skills plus already approved
      tool families under the existing planning -> permission-gate -> action
      boundary
  - Validation:
    - architecture cross-review across identity, role, skill, planning, and
      connector contracts

- [ ] PRJ-561 Implement work-partner capability orchestration and selection evidence
  - Owner: Backend Builder
  - Group: Work-Partner Role And Capability Orchestration
  - Depends on: PRJ-560
  - Priority: P1
  - Status: DONE
  - Result:
    - role selection now supports explicit `work_partner` orchestration turns
      through the shared role-selection owner
    - work-partner turns now expose a bounded skill mix and machine-visible
      role-skill policy baseline for backend inspection surfaces
    - runtime integration now proves that work-partner can orchestrate
      approved search and ClickUp tool paths through typed intents and the
      existing action boundary
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_role_agent.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- [ ] PRJ-562 Add behavior validation for work-organization and decision-support scenarios
  - Owner: QA/Test
  - Group: Work-Partner Role And Capability Orchestration
  - Depends on: PRJ-561
  - Priority: P1
  - Status: DONE
  - Result:
    - behavior validation now proves that `work_partner` can organize work and
      support decisions through the approved backend boundary
    - scenario-level proof now covers:
      - `T15.1` work-partner organization with bounded web search plus ClickUp
        update
      - `T15.2` work-partner decision support with bounded page-read browsing
  - Validation:
    - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`

- [ ] PRJ-563 Sync docs/context for work-partner role orchestration
  - Owner: Product Docs
  - Group: Work-Partner Role And Capability Orchestration
  - Depends on: PRJ-562
  - Priority: P1
  - Status: DONE
  - Result:
    - contracts, runtime reality, behavior-testing guidance, ops notes, and
      planning/context truth now all describe the same backend work-partner
      baseline plus behavior proof through `T15.1..T15.2`
  - Validation:
    - doc-and-context sync across architecture, implementation, ops, testing,
      planning, and context

- [ ] PRJ-564 Freeze the `v1` release gate and production acceptance bundle
  - Owner: Planner
  - Group: V1 Release Closure And V2 API Readiness
  - Depends on: PRJ-563
  - Priority: P1
  - Status: DONE
  - Result:
    - one explicit no-UI `v1` release contract is now frozen across:
      - conversation reliability
      - life-assistant workflow proof
      - learned-state inspection readiness
      - approved tooling and work-partner posture
    - the production acceptance bundle is now explicitly backend-facing rather
      than UI-dependent
  - Validation:
    - ops, testing, and architecture cross-review

- [ ] PRJ-565 Implement missing release and operator evidence for the `v1` gate
  - Owner: Backend Builder
  - Group: V1 Release Closure And V2 API Readiness
  - Depends on: PRJ-564
  - Priority: P1
  - Status: DONE
  - Result:
    - `/health.v1_readiness` now exposes one shared backend release-gate owner
      for no-UI `v1`
    - exported `incident_evidence.policy_posture["v1_readiness"]` now mirrors
      the same release-gate posture
    - release smoke and behavior-validation incident-evidence ingestion now
      require that `v1_readiness` surface
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py tests/test_api_routes.py`

- [ ] PRJ-566 Expose stable backend API-readiness surfaces for future `v2` UI
  - Owner: Backend Builder
  - Group: V1 Release Closure And V2 API Readiness
  - Depends on: PRJ-565
  - Priority: P1
  - Status: DONE
  - Result:
    - `/health.api_readiness` now exposes one shared backend-readiness owner
      for future `v2` UI callers, covering learned-state, role-skill,
      connector, and `v1` release surfaces
    - internal `GET /internal/state/inspect?user_id=...` now carries the same
      `api_readiness` snapshot so backend-owned inspection sections and
      current-turn debug surfaces are stable in one place
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py`

- [ ] PRJ-567 Sync docs/context for `v1` closure and `v2` API readiness
  - Owner: Product Docs
  - Group: V1 Release Closure And V2 API Readiness
  - Depends on: PRJ-566
  - Priority: P1
  - Status: DONE
  - Result:
    - canonical architecture notes, runtime reality, testing guidance, ops
      notes, and planning/context truth now describe the same completed no-UI
      `v1` acceptance bundle plus the backend API-readiness contract for later
      `v2` UI integration
    - `/health.v1_readiness`, `/health.api_readiness`, and internal
      `GET /internal/state/inspect?user_id=...` are now documented together as
      the stable backend-owned starting point for future UI work
  - Validation:
    - doc-and-context sync across architecture, implementation, ops, testing,
      planning, and context

- [ ] PRJ-568 Repair durable attention wiring for production Telegram ingress
  - Owner: Backend Builder
  - Group: Production Telegram Hotfix
  - Depends on: PRJ-567
  - Priority: P0
  - Status: DONE
  - Why now:
    - production Telegram stopped replying after recent changes
    - startup wiring can differ from route-level tests when production-only
      `durable_inbox` attention mode is enabled
  - Done when:
    - app startup wires the durable attention coordinator to the shared memory
      repository when `ATTENTION_COORDINATION_MODE=durable_inbox`
    - regression coverage pins the startup wiring path so production attention
      mode cannot silently fall back away from the repository-backed store
  - Result:
    - `app.main` now wires `memory_repository` into
      `AttentionTurnCoordinator`, so production `durable_inbox` mode can use
      the repository-backed turn store instead of silently degrading away from
      it
    - lifespan-level regression coverage now pins this startup dependency path
      directly, which route-level attention tests did not cover before
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_lifespan_policy.py tests/test_api_routes.py`

- [x] PRJ-516 Define the operator-facing incident evidence bundle and retention baseline
  - Owner: Planner
  - Group: Incident Evidence Bundle And Retention
  - Depends on: PRJ-515
  - Priority: P1
  - Status: DONE
  - Why now:
    - the repo can already export `incident_evidence`, but operators still do
      not have one canonical artifact bundle, retention rule, or retrieval
      path for real incidents and release investigations
    - this closes the gap between exportable debug data and actionable
      operational evidence without inventing a new observability stack
  - Done when:
    - one explicit contract defines the bundle contents, naming/retention
      expectations, and the canonical producer or retrieval path for incident
      evidence artifacts
  - Result:
    - canonical architecture docs now freeze one operator-facing
      incident-evidence bundle contract built around `manifest.json`,
      `incident_evidence.json`, `health_snapshot.json`, and optional
      `behavior_validation_report.json`
    - runtime reality and ops guidance now explicitly state that current
      runtime exports only the raw `incident_evidence.json` surface while
      bundle collection remains an operator workflow until a helper lands
  - Validation:
    - cross-review across `docs/architecture/17_logging_and_debugging.md`,
      `docs/architecture/29_runtime_behavior_testing.md`,
      `docs/implementation/runtime-reality.md`, and
      `docs/operations/runtime-ops-runbook.md`

- [x] PRJ-517 Implement canonical incident evidence export or bundle generation flow
  - Owner: Backend Builder
  - Group: Incident Evidence Bundle And Retention
  - Depends on: PRJ-516
  - Priority: P1
  - Status: DONE
  - Done when:
    - operators can produce or collect the agreed incident-evidence bundle
      through one canonical path without ad hoc manual JSON harvesting from
      debug responses
  - Result:
    - the repo now exposes one canonical bundle helper at
      `scripts/export_incident_evidence_bundle.py`, which collects
      `/health`, debug-mode `incident_evidence`, and optional behavior
      validation output into the frozen artifact shape
    - `/health.observability` now exposes bundle-helper availability and the
      canonical entrypoint path through the existing observability owner
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_observability_policy.py tests/test_api_routes.py tests/test_runtime_pipeline.py`

- [x] PRJ-518 Add regression and smoke coverage for incident evidence bundle integrity
  - Owner: QA/Test
  - Group: Incident Evidence Bundle And Retention
  - Depends on: PRJ-517
  - Priority: P1
  - Status: DONE
  - Done when:
    - release smoke and focused regression coverage verify the selected bundle
      contract, required fields, and failure posture for unreadable or partial
      artifacts
  - Result:
    - `run_release_smoke.ps1` now verifies a full incident-evidence bundle via
      `-IncidentEvidenceBundlePath`, including manifest, required files,
      trace/event parity, health snapshot status, and optional behavior report
    - regression coverage now pins both the valid bundle path and partial
      bundle failure posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_behavior_validation_script.py tests/test_deployment_trigger_scripts.py tests/test_observability_policy.py`
    - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_api_routes.py`

- [x] PRJ-519 Sync docs/context for incident evidence bundle and retention baseline
  - Owner: Product Docs
  - Group: Incident Evidence Bundle And Retention
  - Depends on: PRJ-518
  - Priority: P1
  - Status: DONE
  - Done when:
    - architecture, runtime reality, ops guidance, testing guidance, and
      context truth all describe the same operator-facing incident evidence
      bundle baseline
  - Result:
    - canonical docs, runtime reality, testing guidance, ops guidance, and
      context truth now all describe the same bundle helper, bundle file set,
      release-smoke verification path, and remaining observability limit
    - Group 76 is now complete and the next active lane is dedicated debug
      ingress compatibility retirement
  - Validation:
    - doc-and-context sync across architecture, implementation, ops, testing,
      planning, and context

- Group 76 note:
  - `PRJ-516..PRJ-519` are now complete.
  - the bundle contract is now frozen, implemented, smoke-covered, and fully
    synchronized in docs/context truth.

- Group 77 note:
  - `PRJ-520..PRJ-523` are now complete.
  - shared debug retirement now has one explicit checklist, enforced
    dedicated-admin-only default posture, and machine-readable release plus
    behavior evidence for dedicated-admin-only incident-evidence posture.
  - docs, runtime reality, testing guidance, ops notes, and context truth now
    describe the same incident-evidence-backed retirement proof.
  - `PRJ-524` seeded the bounded calendar read lane that is now active through
    `PRJ-525`.

- Group 78 note:
  - `PRJ-524..PRJ-527` are now complete.
  - the bounded calendar read lane now has one explicit provider
    (`google_calendar`), one provider-backed action adapter, and one bounded
    output shape limited to normalized availability evidence instead of raw
    event payloads.
  - `/health.connectors.execution_baseline` now distinguishes calendar
    `policy_only` remainder from bounded `google_calendar_read_availability`
    posture through machine-visible `credentials_missing` vs
    `provider_backed_ready` states.
  - canonical contracts, runtime reality, testing guidance, ops notes, and
    context truth now describe the same bounded calendar live-read baseline.
  - `PRJ-528` is the next active slice for the first bounded cloud-drive
    metadata read contract.

- Group 79 note:
  - `PRJ-528..PRJ-531` are now complete.
  - the next bounded cloud-drive live-read path is frozen as
    `cloud_drive:list_files` with `provider_hint=google_drive`.
  - safe output is intentionally metadata-only, leaving document contents,
    downloads, and writes outside the selected baseline.
  - the provider-backed adapter now executes only bounded metadata listing
    notes before delivery and preserves the planning-to-action boundary.
  - `/health.connectors.execution_baseline.cloud_drive.google_drive_list_files`
    now exposes one shared `provider_backed_when_configured` readiness
    contract with machine-visible `credentials_missing|provider_backed_ready`
    posture for the bounded cloud-drive metadata-read path.
  - canonical contracts, runtime reality, testing guidance, ops notes, and
    context truth now describe the same bounded Google Drive metadata-read
    baseline.
  - `PRJ-532` is the next active slice for external cadence cutover proof.

- [x] PRJ-520 Freeze the shared debug compatibility retirement gate
  - Owner: Planner
  - Group: Dedicated Debug Ingress Compatibility Retirement
  - Depends on: PRJ-519
  - Priority: P1
  - Status: DONE
  - Done when:
    - the repo records one explicit checklist and cutover posture for retiring
      shared `POST /event/debug` and query-compat `POST /event?debug=true`
      surfaces in favor of dedicated internal ingress only
  - Result:
    - shared debug retirement now has one explicit owner-level checklist and
      cutover posture in `app/core/debug_ingress_policy.py` instead of only a
      loose blocker list
    - `/health.runtime_policy` now exposes machine-readable retirement target,
      cutover posture, gate checklist, and gate state so the next enforcement
      slice can rely on one source of truth
  - Validation:
    - runtime-policy, architecture, and ops cross-review

- [x] PRJ-521 Enforce dedicated-admin-only debug ingress by default after retirement gate closure
  - Owner: Backend Builder
  - Group: Dedicated Debug Ingress Compatibility Retirement
  - Depends on: PRJ-520
  - Priority: P1
  - Status: DONE
  - Done when:
    - shared debug compatibility routes no longer behave as normal runtime
      ingress and the dedicated internal route is the sole canonical debug
      payload path outside narrowly bounded rollback handling
  - Result:
    - `EVENT_DEBUG_SHARED_INGRESS_MODE` now defaults to `break_glass_only`,
      and `EVENT_DEBUG_QUERY_COMPAT_ENABLED` now defaults to disabled even
      outside production
    - runtime policy and route behavior now treat `/internal/event/debug` as
      the only normal debug ingress, while shared paths require explicit
      compatibility or break-glass posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py`

- [x] PRJ-522 Add release and behavior evidence for dedicated-admin-only debug posture
  - Owner: Ops/Release
  - Group: Dedicated Debug Ingress Compatibility Retirement
  - Depends on: PRJ-521
  - Priority: P1
  - Status: DONE
  - Done when:
    - smoke and policy evidence prove dedicated-admin-only debug posture and
      make any fallback or rollback exception explicit
  - Result:
    - `run_release_smoke.ps1` now verifies dedicated-admin-only debug posture
      directly from runtime `incident_evidence` and bundle-attached
      `incident_evidence.json`, not only from `/health.runtime_policy`
    - `run_behavior_validation.py` now treats incident-evidence debug posture
      drift and missing explicit rollback-exception state as CI gate
      violations, with machine-visible context fields for admin target,
      shared-route posture, and exception state
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py tests/test_api_routes.py`

- [x] PRJ-523 Sync docs/context for dedicated debug-ingress retirement
  - Owner: Product Docs
  - Group: Dedicated Debug Ingress Compatibility Retirement
  - Depends on: PRJ-522
  - Priority: P1
  - Status: DONE
  - Done when:
    - canonical docs, runtime reality, ops notes, testing guidance, and
      context truth all describe the same post-compat debug ingress posture
  - Result:
    - architecture docs, runtime reality, testing guidance, ops runbook, and
      planning/context truth now all describe dedicated-admin-only debug
      retirement as evidence proven from incident-evidence posture, not only
      from `/health.runtime_policy`
  - Validation:
    - doc-and-context sync across architecture, implementation, ops, testing,
      planning, and context

- [ ] PRJ-524 Define the first bounded calendar read baseline
  - Owner: Planner
  - Group: Calendar Read Connector Baseline
  - Depends on: PRJ-523
  - Priority: P2
  - Status: DONE
  - Done when:
    - one explicit contract defines the first provider-backed calendar read
      slice, its safe output shape, and its read-only permission posture
      without widening planning or context ownership
  - Result:
    - the first provider-backed calendar read slice is now explicitly frozen as
      `calendar:read_availability` with `provider_hint=google_calendar`
    - the safe output contract is bounded to action-owned availability evidence
      only: normalized window/timezone posture, bounded free/busy summary, and
      top candidate free-slot preview without raw event titles or attendee
      payloads
  - Validation:
    - connector policy, architecture, and ops cross-review

- [x] PRJ-525 Implement the selected calendar read adapter behind existing connector policy gates
  - Owner: Backend Builder
  - Group: Calendar Read Connector Baseline
  - Depends on: PRJ-524
  - Priority: P2
  - Status: DONE
  - Done when:
    - the selected calendar read path executes from explicit read-only typed
      intents and returns bounded execution notes through action
  - Result:
    - planner now emits `calendar:read_availability` with
      `provider_hint=google_calendar` as the bounded live-read baseline instead
      of leaving the provider implicit
    - action now executes that typed intent through a dedicated
      `GoogleCalendarAvailabilityClient`, returning bounded availability
      evidence only: normalized window, busy-window count, and top free-slot
      preview without raw event titles or attendee payloads
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- [x] PRJ-526 Expose calendar-read readiness and failure posture through `/health.connectors`
  - Owner: Ops/Release
  - Group: Calendar Read Connector Baseline
  - Depends on: PRJ-525
  - Priority: P2
  - Status: DONE
  - Done when:
    - operators can distinguish policy-only, credentials-missing, and
      provider-backed-ready calendar read posture through the existing health
      contract
  - Result:
    - `/health.connectors.execution_baseline` now exposes bounded calendar
      read posture under `calendar.google_calendar_read_availability` with one
      shared `provider_backed_when_configured` contract
    - operators can now distinguish configured live-read posture from missing
      credentials through machine-visible `ready`, `state`, and `hint` fields
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- [x] PRJ-527 Sync docs/context for the bounded calendar read baseline
  - Owner: Product Docs
  - Group: Calendar Read Connector Baseline
  - Depends on: PRJ-526
  - Priority: P2
  - Status: DONE
  - Done when:
    - canonical contracts, runtime reality, ops notes, testing guidance, and
      context truth all describe the same bounded calendar read baseline
  - Result:
    - canonical contracts, runtime reality, testing guidance, ops notes, and
      context truth now align on one bounded Google Calendar live-read baseline
      plus `/health.connectors.execution_baseline` readiness posture
  - Validation:
    - doc-and-context sync across architecture, implementation, ops, testing,
      planning, and context

- [ ] PRJ-528 Define the first bounded cloud-drive metadata read baseline
  - Owner: Planner
  - Group: Cloud-Drive Metadata Read Baseline
  - Depends on: PRJ-527
  - Priority: P2
  - Status: DONE
  - Done when:
    - one explicit contract defines the first provider-backed cloud-drive
      metadata read slice, safe output fields, and its read-only permission
      boundary
  - Result:
    - the first bounded cloud-drive metadata-read slice is now explicitly
      frozen as `cloud_drive:list_files` with `provider_hint=google_drive`
    - safe output posture is limited to action-owned file metadata evidence:
      bounded file-name preview, provider file id, mime type or file kind,
      modified-time or recency note, and optional truncation posture
  - Validation:
    - connector policy, architecture, and ops cross-review

- [x] PRJ-529 Implement the selected cloud-drive metadata read adapter behind existing connector policy gates
  - Owner: Backend Builder
  - Group: Cloud-Drive Metadata Read Baseline
  - Depends on: PRJ-528
  - Priority: P2
  - Status: DONE
  - Done when:
    - the selected cloud-drive read path executes from explicit read-only
      typed intents and preserves the planning-to-action execution boundary
  - Result:
    - planner now emits `cloud_drive:list_files` with
      `provider_hint=google_drive` as the bounded metadata-read baseline when
      the user asks to list drive files
    - action now executes that typed intent through a dedicated
      `GoogleDriveMetadataClient`, returning bounded file metadata previews
      only and keeping document contents plus write semantics out of scope
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- [x] PRJ-530 Expose cloud-drive metadata-read readiness and failure posture through `/health.connectors`
  - Owner: Ops/Release
  - Group: Cloud-Drive Metadata Read Baseline
  - Depends on: PRJ-529
  - Priority: P2
  - Status: DONE
  - Done when:
    - `/health.connectors.execution_baseline` distinguishes the new
      cloud-drive metadata-read posture from both policy-only families and
      existing task-system live paths
  - Result:
    - `/health.connectors.execution_baseline.cloud_drive.google_drive_list_files`
      now exposes the bounded cloud-drive metadata-read path through one shared
      `provider_backed_when_configured` contract
    - operator posture now distinguishes `credentials_missing` from
      `provider_backed_ready` for the Google Drive metadata adapter instead of
      leaving cloud-drive under one generic policy-only hint
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- [x] PRJ-531 Sync docs/context for the cloud-drive metadata read baseline
  - Owner: Product Docs
  - Group: Cloud-Drive Metadata Read Baseline
  - Depends on: PRJ-530
  - Priority: P2
  - Status: DONE
  - Done when:
    - canonical contracts, runtime reality, ops notes, testing guidance, and
      context truth all describe the same cloud-drive metadata-read baseline
  - Result:
    - canonical contracts now record `cloud_drive.google_drive_list_files` as
      the first live bounded metadata-read path with action-owned metadata-only
      output and `credentials_missing|provider_backed_ready` health posture
    - runtime reality, testing guidance, ops notes, and planning/context truth
      now describe the same bounded Google Drive baseline instead of mixing
      implementation-ready wording with rollout-era future tense
  - Validation:
    - doc-and-context sync across architecture, implementation, ops, testing,
      planning, and context

- [ ] PRJ-532 Define the external cadence cutover proof baseline
- [x] PRJ-532 Define the external cadence cutover proof baseline
  - Owner: Planner
  - Group: External Cadence Cutover Proof
  - Depends on: PRJ-531
  - Priority: P1
  - Status: DONE
  - Done when:
    - one explicit contract defines what evidence is required before
      production can treat externalized maintenance and proactive cadence as
      the real owner instead of policy-only target posture
  - Result:
    - canonical contracts now freeze one external cadence cutover-proof
      baseline that requires recent maintenance/proactive last-run evidence,
      duplicate-protection posture, stale-or-missing evidence state, release
      visibility, and explicit rollback posture before production can treat
      the external scheduler as the real cadence owner
    - runtime reality and ops guidance now explicitly say that
      `/health.scheduler.external_owner_policy` is still target-policy truth
      until those proof items become machine-visible
  - Validation:
    - scheduler, runtime policy, and ops cross-review

- [x] PRJ-533 Implement machine-visible last-run and idempotency evidence for external cadence entrypoints
  - Owner: Backend Builder
  - Group: External Cadence Cutover Proof
  - Depends on: PRJ-532
  - Priority: P1
  - Status: DONE
  - Done when:
    - health or runtime evidence shows recent external cadence execution and
      bounded duplicate-protection posture instead of only selected target mode
  - Result:
    - `/health.scheduler.external_owner_policy` now exposes per-cadence
      external run evidence for maintenance and proactive entrypoints,
      including recent-success vs missing/stale posture, last-run timestamps,
      and stale thresholds
    - external cadence policy now also exposes bounded duplicate-protection
      posture plus `cutover_proof_ready`, so target-mode selection and proven
      cutover are no longer conflated into one field
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- [x] PRJ-534 Add smoke and behavior evidence for external cadence cutover readiness
  - Owner: QA/Test
  - Group: External Cadence Cutover Proof
  - Depends on: PRJ-533
  - Priority: P1
  - Status: DONE
  - Done when:
    - release and behavior evidence can prove external cadence ownership
      posture through the agreed cutover fields and failure cases
  - Result:
    - `run_release_smoke.ps1` now validates external cadence cutover proof
      owner, per-cadence evidence states, duplicate-protection posture, and
      missing-field failures through `/health.scheduler.external_owner_policy`
    - `run_behavior_validation.py` now validates the same external cadence
      proof surface from exported `incident_evidence`, so CI gate artifacts
      fail on incomplete scheduler cutover payloads instead of only recording
      debug-posture evidence
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_behavior_validation_script.py`

- [ ] PRJ-535 Sync docs/context for external cadence cutover proof
- [x] PRJ-535 Sync docs/context for external cadence cutover proof
  - Owner: Product Docs
  - Group: External Cadence Cutover Proof
  - Depends on: PRJ-534
  - Priority: P1
  - Status: DONE
  - Done when:
    - implementation reality, ops guidance, testing guidance, planning, and
      context truth all describe the same external cadence cutover evidence
      baseline
  - Result:
    - runtime reality, testing guidance, ops notes, and context truth now all
      describe the same external cadence cutover proof surface, including
      per-cadence evidence states, duplicate-protection posture, and
      `cutover_proof_ready`
    - Group 80 is now complete and the next active lane is relation retrieval
      source completion
  - Validation:
    - doc-and-context sync across implementation, ops, testing, planning, and
      context

- [ ] PRJ-536 Decide the relation-source retrieval completion posture
- [x] PRJ-536 Decide the relation-source retrieval completion posture
  - Owner: Planner
  - Group: Relation Retrieval Source Completion
  - Depends on: PRJ-535
  - Priority: P2
  - Status: DONE
  - Done when:
    - the repo explicitly records whether relation embeddings stay optional
      long-term or become part of the steady-state retrieval rollout, together
      with influence and refresh boundaries
  - Result:
    - canonical contracts now freeze semantic+affective as the steady-state
      retrieval completion baseline, while relation remains an explicit
      optional follow-on embedding family
    - runtime reality and ops guidance now explicitly say that relation
      records remain live adaptive inputs, but relation embeddings do not count
      as a required steady-state retrieval completion condition
  - Validation:
    - retrieval architecture, runtime reality, and ops cross-review

- [x] PRJ-537 Implement the selected relation-source rollout or governance boundary
  - Owner: Backend Builder
  - Group: Relation Retrieval Source Completion
  - Depends on: PRJ-536
  - Priority: P2
  - Status: DONE
  - Done when:
    - retrieval code and health surfaces reflect the selected relation-source
      posture instead of keeping it as a silent optional family
  - Result:
    - retrieval code and `/health.memory_retrieval` now treat
      semantic+affective as the foreground rollout-completion baseline instead
      of keeping relation as an implicit pending source
    - relation source posture now has one shared owner-level surface
      (`relation_source_retrieval_policy`) with explicit optional-family
      state, hint, recommendation, and enabled/alignment visibility
    - `MemoryRepository.get_hybrid_memory_bundle()` now consumes the same
      shared foreground retrieval-source helper as the health policy surface
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_context_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- [x] PRJ-538 Add regression and release evidence for relation-aware retrieval posture
  - Owner: QA/Test
  - Group: Relation Retrieval Source Completion
  - Depends on: PRJ-537
  - Priority: P2
  - Status: DONE
  - Done when:
    - runtime and release evidence pin the selected relation-source posture,
      including alignment or bounded exclusion from the steady-state retrieval
      baseline
  - Result:
    - runtime `system_debug.adaptive_state` now exposes the same shared
      relation-source policy posture as `/health.memory_retrieval`, so
      behavior-level traces can prove whether relation is disabled, enabled,
      or still ahead of baseline
    - release smoke now requires relation-source policy owner/state/enabled
      evidence in `memory_retrieval`, and focused regression coverage pins both
      the green path and the missing-evidence failure posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_deployment_trigger_scripts.py tests/test_memory_repository.py`

- [x] PRJ-539 Sync docs/context for relation retrieval source completion
  - Owner: Product Docs
  - Group: Relation Retrieval Source Completion
  - Depends on: PRJ-538
  - Priority: P2
  - Status: DONE
  - Done when:
    - architecture, runtime reality, ops guidance, testing guidance, and
      context truth all describe the same relation-source retrieval posture
  - Result:
    - architecture, runtime reality, runtime behavior testing, ops guidance,
      testing guidance, and context truth now all describe the same
      optional-family relation-source posture plus its `/health`,
      `system_debug`, and release-smoke evidence surfaces
    - Group 81 is now complete and no seeded `READY` items remain on the board
  - Validation:
    - doc-and-context sync across architecture, implementation, ops, testing,
      planning, and context

- [x] PRJ-512 Define the minimum exportable observability baseline beyond local logs and `/health`
  - Owner: Planner
  - Group: Observability Export And Incident-Evidence Baseline
  - Depends on: PRJ-511
  - Priority: P1
  - Status: DONE
  - Why now:
    - reflection supervision is now fully closed, so the next remaining hardening
      lane is exportable observability and incident evidence
  - Done when:
    - one explicit contract records which runtime evidence must be exportable
      for incidents and releases beyond local logs and `/health`
  - Result:
    - the repo now has one shared observability export policy owner in
      `app/core/observability_policy.py`, and `/health.observability` exposes
      the minimum incident-evidence contract together with the remaining
      machine-readable export gaps
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_observability_policy.py tests/test_api_routes.py`

- [x] PRJ-513 Implement exportable runtime evidence for stage timings and policy posture
  - Owner: Backend Builder
  - Group: Observability Export And Incident-Evidence Baseline
  - Depends on: PRJ-512
  - Priority: P1
  - Status: DONE
  - Done when:
    - the repo can produce machine-readable incident or release evidence for
      stage timings, policy posture, and key owner-mode surfaces without
      depending on ad hoc operator capture
  - Result:
    - debug responses now expose `incident_evidence` built from one shared
      observability owner, including stage timings and machine-readable policy
      posture snapshots for runtime policy, retrieval, scheduler, reflection,
      and connector execution
    - `/health.observability` now marks exportable incident evidence as ready,
      and release smoke can verify exported incident evidence directly in debug
      mode
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py tests/test_observability_policy.py`

- [x] PRJ-514 Extend behavior or smoke flows to consume the exported incident-evidence baseline
  - Owner: QA/Test
  - Group: Observability Export And Incident-Evidence Baseline
  - Depends on: PRJ-513
  - Priority: P1
  - Status: DONE
  - Result:
    - release smoke now validates exported `incident_evidence` directly in
      debug mode, and behavior-validation artifacts can optionally ingest a
      runtime incident-evidence file without inventing a second ad hoc format
    - observability export is now part of repeatable evidence flow instead of
      remaining only a local debug convenience
  - Validation:
    - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`
    - `.\.venv\Scripts\python -m pytest -q tests/test_behavior_validation_script.py tests/test_deployment_trigger_scripts.py`

- [x] PRJ-515 Sync docs/context for observability export and incident-evidence baseline
  - Owner: Product Docs
  - Group: Observability Export And Incident-Evidence Baseline
  - Depends on: PRJ-514
  - Priority: P1
  - Status: DONE
  - Result:
    - architecture, runtime reality, testing guidance, ops guidance, planning,
      and context truth now describe the same exportable observability baseline
      for `/health.observability`, debug-response `incident_evidence`, and
      behavior or smoke consumption
    - Group 75 is now complete and no seeded `READY` task remains on the board
  - Validation:
    - doc-and-context sync across architecture, implementation, ops, testing, planning, and context

- [x] PRJ-498 Add release and health evidence for external scheduler ownership posture
  - Owner: Ops/Release
  - Group: External Scheduler Ownership Rollout
  - Depends on: PRJ-497
  - Priority: P1
  - Status: DONE
  - Result:
    - `/health.scheduler.external_owner_policy`, startup logs, and release
      smoke now expose one shared external cadence-owner policy with target
      entrypoints and baseline readiness posture
    - operators can now distinguish `externalized` target alignment from
      in-process fallback without reading scheduler code
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_deployment_trigger_scripts.py tests/test_main_runtime_policy.py`

- [x] PRJ-499 Sync docs/context for external scheduler ownership rollout
  - Owner: Product Docs
  - Group: External Scheduler Ownership Rollout
  - Depends on: PRJ-498
  - Priority: P1
  - Status: DONE
  - Result:
    - implementation reality, ops guidance, testing guidance, planning, and
      context truth now describe the same external cadence-owner baseline with
      canonical maintenance/proactive entrypoints and explicit in-process
      fallback posture
    - Group 71 is now complete and the next active lane is connector read
      posture and provider expansion baseline
  - Validation:
    - doc-and-context sync across planning, ops, implementation, and context

- [x] PRJ-500 Decide the first live read-capable connector baseline beyond ClickUp task creation
  - Owner: Planner
  - Group: Connector Read Posture And Provider Expansion Baseline
  - Depends on: PRJ-499
  - Priority: P1
  - Status: DONE
  - Result:
    - the repo now records `task_system:list_tasks` with `provider_hint=clickup`
      as the next live read-capable expansion path behind the existing task
      connector family
    - calendar and cloud-drive reads remain policy-only until their narrower
      read-scope boundaries are designed explicitly
  - Validation:
    - connector policy and architecture cross-review

- [x] PRJ-501 Implement the selected read-capable connector adapter behind existing permission gates
  - Owner: Backend Builder
  - Group: Connector Read Posture And Provider Expansion Baseline
  - Depends on: PRJ-500
  - Priority: P1
  - Status: DONE
  - Result:
    - the repo now executes `task_system:list_tasks` for ClickUp through the
      existing provider adapter when a read-only typed intent reaches action
    - the provider-backed read path runs before delivery and leaves the
      planning/action boundary intact by returning execution notes instead of
      mutating expression ownership
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- [x] PRJ-502 Expose provider-read readiness and failure posture for the expanded connector baseline
  - Owner: Ops/Release
  - Group: Connector Read Posture And Provider Expansion Baseline
  - Depends on: PRJ-501
  - Priority: P1
  - Status: DONE
  - Result:
    - `/health.connectors.execution_baseline` now exposes separate ClickUp
      mutation and read-capable live paths under the same task-system family
    - operators can distinguish read-capable posture from policy-only
      connector families without reading action code
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- [x] PRJ-503 Sync docs/context for connector read posture and provider expansion baseline
  - Owner: Product Docs
  - Group: Connector Read Posture And Provider Expansion Baseline
  - Depends on: PRJ-502
  - Priority: P1
  - Status: DONE
  - Result:
    - contracts, runtime reality, ops notes, testing guidance, and
      planning/context truth now describe the same expanded task-system
      baseline with ClickUp create plus list support
    - Group 72 is now complete and the next active lane is retrieval lifecycle
      and source-rollout closure
  - Validation:
    - doc-and-context sync across architecture, implementation, ops, testing, and context

- [x] PRJ-504 Define the production retrieval lifecycle baseline beyond current provider-owned materialization
  - Owner: Planner
  - Group: Retrieval Lifecycle And Source-Rollout Closure
  - Depends on: PRJ-503
  - Priority: P1
  - Status: DONE
  - Result:
    - the repo now records one explicit retrieval lifecycle owner for provider
      target, transition owner, compatibility fallback, steady-state refresh,
      and source-rollout completion posture
    - semantic plus affective sources are now frozen as the foreground
      steady-state baseline, while relation remains optional after that
      baseline is stable
  - Validation:
    - retrieval architecture/planning cross-review

- [x] PRJ-505 Implement lifecycle visibility for refresh, pending source families, and provider fallback drift
  - Owner: Backend Builder
  - Group: Retrieval Lifecycle And Source-Rollout Closure
  - Depends on: PRJ-504
  - Priority: P1
  - Status: DONE
  - Result:
    - `/health.memory_retrieval` now exposes one retrieval lifecycle owner plus
      provider drift posture, pending lifecycle gaps, and baseline alignment
      state
    - operators can now see lifecycle drift in one surface instead of
      reconstructing it from multiple embedding rollout fields
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_runtime_policy.py tests/test_api_routes.py`

- [x] PRJ-506 Add behavior and release evidence for retrieval lifecycle alignment
  - Owner: QA/Test
  - Group: Retrieval Lifecycle And Source-Rollout Closure
  - Depends on: PRJ-505
  - Priority: P1
  - Status: DONE
  - Result:
    - release smoke now verifies retrieval lifecycle policy ownership plus
      drift/alignment posture from `/health.memory_retrieval`
    - runtime regression coverage now pins that the local-hybrid transition
      owner still exercises the active hybrid retrieval path under the defined
      lifecycle baseline
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_runtime_pipeline.py`

- [x] PRJ-507 Sync docs/context for retrieval lifecycle and source-rollout closure
  - Owner: Product Docs
  - Group: Retrieval Lifecycle And Source-Rollout Closure
  - Depends on: PRJ-506
  - Priority: P1
  - Status: DONE
  - Result:
    - implementation reality, ops guidance, testing guidance, planning, and
      context truth now describe one shared retrieval steady-state lifecycle
      owner together with provider-drift, alignment, and pending-gap posture
    - Group 73 is now complete and the next active lane is reflection worker
      supervision and durability closure
  - Validation:
    - doc-and-context sync across implementation, ops, testing, planning, and context

- [x] PRJ-508 Define the production supervision baseline for deferred reflection workers
  - Owner: Planner
  - Group: Reflection Worker Supervision And Durability Closure
  - Depends on: PRJ-507
  - Priority: P1
  - Status: DONE
  - Result:
    - the repo now has one explicit supervision policy owner for deferred
      reflection operations, freezing target runtime mode, external
      queue-drain owner, durable retry owner, queue-health states, and
      recovery actions before runtime surfaces expose them
    - `PRJ-509` can now reuse one shared baseline instead of re-encoding
      supervision semantics in local health logic
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_supervision_policy.py`

- [x] PRJ-509 Implement machine-visible supervision posture for deferred reflection execution
  - Owner: Backend Builder
  - Group: Reflection Worker Supervision And Durability Closure
  - Depends on: PRJ-508
  - Priority: P1
  - Status: DONE
  - Result:
    - `/health.reflection` now exposes one shared supervision snapshot with
      queue-health state, blocking signals, and recovery actions from the
      deferred reflection supervision policy owner
    - operators can now distinguish recoverable backlog, hard recovery
      blockers, and aligned deferred supervision posture without manually
      combining task counters with topology fields
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_scheduler_worker.py tests/test_api_routes.py`

- [x] PRJ-510 Add release evidence for deferred reflection supervision and recovery posture
  - Owner: Ops/Release
  - Group: Reflection Worker Supervision And Durability Closure
  - Depends on: PRJ-509
  - Priority: P1
  - Status: DONE
  - Result:
    - startup logs and release smoke now consume the same deferred reflection
      supervision contract, including queue-health state, readiness posture,
      blocking signals, and recovery actions
    - operator evidence can now prove reflection supervision posture without
      reading `/health` manually or inferring recovery guidance from raw task
      counters
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_main_runtime_policy.py tests/test_api_routes.py`

- [x] PRJ-511 Sync docs/context for reflection worker supervision and durability closure
  - Owner: Product Docs
  - Group: Reflection Worker Supervision And Durability Closure
  - Depends on: PRJ-510
  - Priority: P1
  - Status: DONE
  - Result:
    - canonical contracts, runtime reality, ops guidance, testing guidance,
      planning, and context truth now describe one shared supervised deferred
      reflection baseline with queue-health, blockers, and recovery actions
    - Group 74 is now complete and the next active lane is observability export
      and incident-evidence baseline
  - Validation:
    - doc-and-context sync across architecture, implementation, ops, planning, and context

- [x] PRJ-497 Implement canonical external cadence entrypoints and ownership checks
  - Owner: Backend Builder
  - Group: External Scheduler Ownership Rollout
  - Depends on: PRJ-496
  - Priority: P1
  - Status: DONE
  - Result:
    - the repo now provides canonical external cadence entrypoints for
      maintenance and proactive ticks, with dedicated `run_once` Python,
      PowerShell, and shell wrappers
    - `SchedulerWorker` now exposes explicit external-owner execution methods
      so `externalized` cadence ownership is no longer only a config label
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- [x] PRJ-496 Define the production external-scheduler owner baseline for maintenance and proactive cadence
  - Owner: Planner
  - Group: External Scheduler Ownership Rollout
  - Depends on: PRJ-495
  - Priority: P1
  - Status: DONE
  - Result:
    - the repo now has one explicit external cadence owner policy in
      `app/core/external_scheduler_policy.py`, with `externalized` as the
      target production mode and app-local scheduler as explicit fallback only
    - canonical maintenance and proactive entrypoint paths are frozen for the
      next implementation slice
  - Validation:
    - scheduler/attention/planning cross-review across architecture, runtime reality, and ops

- [x] PRJ-495 Sync docs/context for debug ingress retirement and admin boundary closure
  - Owner: Product Docs
  - Group: Debug Ingress Retirement And Admin Boundary Closure
  - Depends on: PRJ-494
  - Priority: P1
  - Status: DONE
  - Result:
    - canonical contracts, runtime-reality notes, testing guidance, ops docs,
      and planning/context truth now describe one shared dedicated-admin debug
      boundary with machine-visible shared-retirement blockers
    - Group 70 is now complete and the next active lane is external scheduler
      ownership rollout
  - Validation:
    - doc-and-context sync across planning, ops, implementation, architecture, and context

- [x] PRJ-494 Add release-smoke and operator guidance for dedicated-admin debug posture
  - Owner: Ops/Release
  - Group: Debug Ingress Retirement And Admin Boundary Closure
  - Depends on: PRJ-493
  - Priority: P1
  - Status: DONE
  - Result:
    - startup logs now emit one shared `runtime_policy_debug_ingress_hint`
      surface for dedicated-admin posture and shared-compat blockers in
      production
    - runtime ops runbook and release smoke now consume the same
      machine-visible admin-ingress policy fields from `/health.runtime_policy`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py tests/test_main_runtime_policy.py tests/test_api_routes.py`

- [x] PRJ-493 Expose machine-visible admin-ingress posture and shared-ingress retirement blockers
  - Owner: Backend Builder
  - Group: Debug Ingress Retirement And Admin Boundary Closure
  - Depends on: PRJ-492
  - Priority: P1
  - Status: DONE
  - Result:
    - `runtime_policy_snapshot()` now exposes one machine-visible admin debug
      boundary with policy owner, target ingress path, posture state, and
      retirement blockers for shared compat ingress
    - release smoke now verifies those fields so operator evidence and runtime
      policy stay aligned on the same dedicated-admin target
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py`

- [x] PRJ-492 Freeze the dedicated-admin debug ingress target and compatibility-retirement checklist
  - Owner: Planner
  - Group: Debug Ingress Retirement And Admin Boundary Closure
  - Depends on: PRJ-491
  - Priority: P1
  - Status: DONE
  - Result:
    - the repo now has one shared owner for the long-term debug-ingress target
      in `app/core/debug_ingress_policy.py`, including the dedicated internal
      admin path, temporary compatibility paths, and the explicit retirement
      checklist for shared ingress
    - later runtime, ops, and release evidence work can now consume one policy
      baseline instead of repeating local strings
  - Validation:
    - architecture/planning cross-review across runtime policy, ops notes, and
      debug-surface contracts

## BLOCKED

- [ ] (none)

## REVIEW

- [ ] (none)

## DONE

- [x] PRJ-491 Sync docs/context for role/skill maturity and behavior-validation expansion
  - Status: DONE
  - Group: Role/Skill Maturity And Behavior-Validation Expansion
  - Owner: Product Docs
  - Depends on: PRJ-490
  - Priority: P1
  - Result:
    - architecture, implementation reality, ops guidance, testing guidance,
      behavior-validation docs, and planning/context truth now describe one
      shared metadata-only role/skill boundary plus the expanded
      behavior-validation baseline
    - no seeded `READY` task remains after `PRJ-491`
  - Validation:
    - doc-and-context sync across canonical docs, implementation docs, ops,
      testing, and planning/context surfaces

- [x] PRJ-490 Expand behavior-validation coverage for post-convergence architecture lanes
  - Status: DONE
  - Group: Role/Skill Maturity And Behavior-Validation Expansion
  - Owner: QA/Test
  - Depends on: PRJ-489
  - Priority: P1
  - Result:
    - behavior validation now covers role/skill metadata-only boundary,
      connector execution posture, proactive cadence posture, and deferred
      reflection enqueue expectations
    - CI gate evidence now proves the strongest remaining post-convergence
      behavior boundaries instead of relying only on targeted unit tests
  - Validation:
    - `.\scripts\run_behavior_validation.ps1 -GateMode ci -ArtifactPath artifacts/behavior_validation/report.json`

- [x] PRJ-489 Apply the selected role/skill maturity baseline in runtime surfaces and contracts
  - Status: DONE
  - Group: Role/Skill Maturity And Behavior-Validation Expansion
  - Owner: Backend Builder
  - Depends on: PRJ-488
  - Priority: P1
  - Result:
    - runtime contracts, `/health.role_skill`, and
      `system_debug.adaptive_state.role_skill_policy` now expose one shared
      metadata-only skill boundary instead of leaving role/skill maturity as
      implied local behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_role_agent.py tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- [x] PRJ-488 Decide the long-term role-versus-skill execution boundary
  - Status: DONE
  - Group: Role/Skill Maturity And Behavior-Validation Expansion
  - Owner: Planner
  - Depends on: PRJ-487
  - Priority: P1
  - Result:
    - the repo now records one explicit long-term role/skill boundary:
      skills remain metadata-only capability hints that inform role and
      planning, but never execute tools or side effects on their own
    - later capability growth now requires an explicit contract change instead
      of quiet expansion from helper logic
  - Validation:
    - architecture/planning cross-review across role/skill docs and runtime contracts

- [x] PRJ-487 Sync docs/context for proactive runtime activation
  - Status: DONE
  - Group: Proactive Runtime Activation
  - Owner: Product Docs
  - Depends on: PRJ-486
  - Priority: P1
  - Result:
    - planning, implementation reality, ops guidance, testing guidance, and
      context truth now describe one shared proactive runtime baseline with
      live scheduler cadence ownership, explicit anti-spam posture, and
      machine-visible health/debug policy snapshots
    - the next active lane is role/skill maturity and behavior-validation
      expansion
  - Validation:
    - doc-and-context sync across planning, implementation, ops, testing, and
      context surfaces

- [x] PRJ-486 Add scenario-level behavior validation for proactive outreach quality and anti-spam posture
  - Status: DONE
  - Group: Proactive Runtime Activation
  - Owner: QA/Test
  - Depends on: PRJ-485
  - Priority: P1
  - Result:
    - behavior validation now covers proactive delivery-ready and
      anti-spam-blocked posture so proactive runtime is proven through
      scenario evidence, not only helper or unit coverage
  - Validation:
    - `.\scripts\run_behavior_validation.ps1 -GateMode operator`
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py`

- [x] PRJ-485 Implement live proactive cadence ownership beyond passive scheduler plumbing
  - Status: DONE
  - Group: Proactive Runtime Activation
  - Owner: Backend Builder
  - Depends on: PRJ-484
  - Priority: P1
  - Result:
    - in-process scheduler ownership can now emit bounded proactive wakeups
      through repository-backed candidate selection, runtime execution, and
      machine-visible tick summaries instead of only holding proactive guard
      primitives
    - `/health.proactive` now exposes cadence-owner, delivery baseline, and
      anti-spam contract posture for operator triage
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- [x] PRJ-484 Define the true MVP proactive runtime baseline and anti-spam contract
  - Status: DONE
  - Group: Proactive Runtime Activation
  - Owner: Planner
  - Depends on: PRJ-483
  - Priority: P1
  - Result:
    - the repo now records one explicit proactive runtime policy owner with
      cadence owner, delivery-target baseline, opted-in candidate selection,
      cooldown, and unanswered/outbound anti-spam thresholds
    - runtime, ops, and behavior validation can proceed without ambiguity
      about what counts as live proactive cadence posture
  - Validation:
    - cross-review across proactive architecture, guardrails, and runtime reality

- [x] PRJ-483 Sync docs/context for background worker externalization
  - Status: DONE
  - Group: Background Worker Externalization
  - Owner: Product Docs
  - Depends on: PRJ-482
  - Priority: P1
  - Result:
    - canonical contracts, runtime reality, ops guidance, testing guidance,
      and planning/context truth now describe one shared deferred reflection
      external-driver baseline with explicit queue-drain entrypoint and
      health-visible policy owner
    - the next active lane is proactive runtime activation
  - Validation:
    - doc-and-context sync across canonical docs, implementation docs,
      ops guidance, testing guidance, and planning surfaces

- [x] PRJ-482 Add release-smoke and health evidence for external worker posture
  - Status: DONE
  - Group: Background Worker Externalization
  - Owner: Ops/Release
  - Depends on: PRJ-481
  - Priority: P1
  - Result:
    - `/health.reflection.external_driver_policy` now exposes machine-visible
      policy ownership, canonical queue-drain entrypoint, and baseline
      readiness posture
    - release smoke verifies that external-driver policy evidence is present
      and internally consistent before summarizing reflection posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_deployment_trigger_scripts.py`

- [x] PRJ-481 Implement the external-driver-ready reflection execution path and ownership checks
  - Status: DONE
  - Group: Background Worker Externalization
  - Owner: Backend Builder
  - Depends on: PRJ-480
  - Priority: P1
  - Result:
    - the repo now provides a canonical external queue-drain entrypoint
      (`scripts/run_reflection_queue_once.py`) with PowerShell/bash wrappers
    - startup logs and `/health.reflection` expose one shared owner contract
      for deferred reflection external-driver posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_reflection_worker.py`
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_deployment_trigger_scripts.py`

- [x] PRJ-480 Define the production external-worker baseline for deferred reflection
  - Status: DONE
  - Group: Background Worker Externalization
  - Owner: Planner
  - Depends on: PRJ-479
  - Priority: P1
  - Result:
    - the repo now records one explicit deferred reflection external-driver
      baseline through a shared policy owner and canonical queue-drain
      entrypoint
    - `in_process` reflection remains a compatibility posture, not the target
      external-worker production baseline
  - Validation:
    - reflection topology and ops cross-review

- [x] PRJ-479 Sync docs/context for retrieval provider completion
  - Status: DONE
  - Group: Retrieval Provider Completion
  - Owner: Product Docs
  - Depends on: PRJ-478
  - Priority: P1
  - Result:
    - architecture, implementation reality, ops guidance, testing guidance,
      and planning/context truth now describe one shared retrieval production
      baseline:
      `openai_api_embeddings` is the target provider-owned path,
      `local_hybrid` remains a local transition owner, and deterministic stays
      as explicit compatibility fallback
    - operator docs now call out the health-visible production-baseline fields
      used to distinguish aligned OpenAI ownership from fallback or transition
      posture
  - Validation:
    - doc-and-context sync across canonical docs, implementation docs,
      ops/config guidance, and planning surfaces

- [x] PRJ-478 Add rollout/readiness evidence for provider-owned retrieval execution
  - Status: DONE
  - Group: Retrieval Provider Completion
  - Owner: Ops/Release
  - Depends on: PRJ-477
  - Priority: P1
  - Result:
    - `/health.memory_retrieval` now exposes explicit production-baseline
      posture through `semantic_embedding_production_baseline`,
      `semantic_embedding_production_baseline_state`, and
      `semantic_embedding_production_baseline_hint`
    - startup warning behavior now distinguishes configured OpenAI ownership
      from missing-credential fallback posture instead of treating all
      non-deterministic paths as the same rollout state
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_runtime_policy.py`

- [x] PRJ-477 Implement provider-owned semantic embedding execution for the selected baseline
  - Status: DONE
  - Group: Retrieval Provider Completion
  - Owner: Backend Builder
  - Depends on: PRJ-476
  - Priority: P1
  - Result:
    - repository and action persistence now share one materialization path that
      can execute OpenAI provider-owned embeddings when configured
    - deterministic and `local_hybrid` paths remain explicit bounded fallbacks
      instead of hidden implementation branches
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_memory_repository.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- [x] PRJ-476 Define the target provider-owned retrieval baseline beyond deterministic fallback
  - Status: DONE
  - Group: Retrieval Provider Completion
  - Owner: Planner
  - Depends on: PRJ-475
  - Priority: P1
  - Result:
    - the repo now records one explicit provider-owned retrieval target:
      OpenAI API embeddings are the intended production baseline when
      configured
    - `local_hybrid` remains a local transition owner and deterministic
      remains the explicit compatibility fallback baseline
  - Validation:
    - cross-review across retrieval docs, env/config guidance, and
      `docs/planning/open-decisions.md`

- [x] PRJ-475 Sync docs/context for connector execution productionization
  - Status: DONE
  - Group: Connector Execution Productionization
  - Owner: Product Docs
  - Depends on: PRJ-474
  - Priority: P1
  - Result:
    - canonical contracts, runtime reality, env/config guidance, ops notes,
      testing guidance, and planning/context truth now describe one narrow
      connector execution baseline
    - the selected live path is explicit: ClickUp task creation is
      provider-backed when configured, while calendar, drive, and remaining
      task-system operations stay policy-only on purpose
  - Validation:
    - doc-and-context sync across canonical docs, implementation docs,
      ops/config guidance, and planning surfaces

- [x] PRJ-474 Add health/debug visibility and failure posture for provider-backed connector execution
  - Status: DONE
  - Group: Connector Execution Productionization
  - Owner: Ops/Release
  - Depends on: PRJ-473
  - Priority: P1
  - Result:
    - `/health.connectors.execution_baseline` now exposes one explicit
      execution owner, the selected MVP boundary, and ClickUp readiness/failure
      posture
    - operator triage can now distinguish policy-only connector families from
      the one configured provider-backed path without reading action code
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- [x] PRJ-473 Implement the first provider-backed connector execution path behind existing policy gates
  - Status: DONE
  - Group: Connector Execution Productionization
  - Owner: Backend Builder
  - Depends on: PRJ-472
  - Priority: P1
  - Result:
    - action can now execute `task_system:create_task` for
      `provider_hint=clickup` through a dedicated provider adapter when ClickUp
      credentials are configured
    - the new path stays inside the existing `planning -> expression -> action`
      boundary and remains guarded by shared connector policy plus delivery
      envelope parity
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- [x] PRJ-472 Decide the MVP production boundary for connector execution adapters
  - Status: DONE
  - Group: Connector Execution Productionization
  - Owner: Planner
  - Depends on: PRJ-471
  - Priority: P1
  - Result:
    - the repo now records one explicit MVP execution boundary:
      `task_system:create_task` for ClickUp is the first live provider-backed
      path
    - `calendar`, `cloud_drive`, and other task-system operations remain
      policy-only until pre-action read posture and more provider adapters
      exist
  - Validation:
    - cross-review across `docs/planning/open-decisions.md`,
      `docs/architecture/16_agent_contracts.md`, and
      `docs/operations/runtime-ops-runbook.md`

- [x] PRJ-471 Sync planning/context for canonical docs consistency
  - Status: DONE
  - Group: Canonical Docs Consistency Sweep
  - Owner: Product Docs
  - Depends on: PRJ-470
  - Priority: P1
  - Result:
    - planning/context truth now records one completed architecture-doc sweep
      instead of leaving Group 64 as an implied docs cleanup
    - the next active lane is connector execution productionization
  - Validation:
    - doc-and-context sync across `.codex/context/` and `docs/planning/`

- [x] PRJ-470 Align overview and docs index with the corrected canonical architecture narrative
  - Status: DONE
  - Group: Canonical Docs Consistency Sweep
  - Owner: Product Docs
  - Depends on: PRJ-469
  - Priority: P1
  - Result:
    - `docs/README.md` and `docs/overview.md` now point readers to `02`, `15`,
      and `16` as the canonical source of stage order and ownership semantics
    - older numbered architecture docs are no longer implicitly treated as
      alternate canonical flows
  - Validation:
    - doc sync across `docs/README.md` and `docs/overview.md`

- [x] PRJ-469 Rewrite stale architecture docs to match the current canonical contract set
  - Status: DONE
  - Group: Canonical Docs Consistency Sweep
  - Owner: Product Docs
  - Depends on: PRJ-468
  - Priority: P1
  - Result:
    - `docs/architecture/05_conscious_subconscious.md` now uses the canonical
      `planning -> expression -> action -> memory -> reflection trigger`
      narrative instead of the older `plan -> action -> expression -> memory`
      ordering
    - `docs/architecture/20_action_system.md` now distinguishes action-owned
      side effects from runtime-owned post-action follow-ups
      (`memory`, `reflection enqueue`) instead of treating all persistence as
      generic action work
  - Validation:
    - cross-doc consistency review across `docs/architecture/05_*`,
      `20_action_system.md`, `02_architecture.md`,
      `15_runtime_flow.md`, and `16_agent_contracts.md`

- [x] PRJ-468 Audit canonical architecture docs for flow/order drift against `02`, `15`, and `16`
  - Status: DONE
  - Group: Canonical Docs Consistency Sweep
  - Owner: Planner
  - Depends on: PRJ-467
  - Priority: P1
  - Result:
    - audit identified two concrete canonical-doc drifts:
      `docs/architecture/05_conscious_subconscious.md` still reversed
      `expression` and `action`, and `docs/architecture/20_action_system.md`
      still treated memory/trigger follow-ups as generic action ownership
    - `docs/README.md` and `docs/overview.md` were also identified as the
      right reader-entry surfaces to restate `02/15/16` precedence
  - Validation:
    - targeted cross-review across `docs/architecture/02_architecture.md`,
      `docs/architecture/15_runtime_flow.md`,
      `docs/architecture/16_agent_contracts.md`,
      `docs/architecture/05_conscious_subconscious.md`,
      `docs/architecture/20_action_system.md`, `docs/README.md`, and
      `docs/overview.md`

- [x] PRJ-467 Sync docs/context for migration parity and schema governance
  - Status: DONE
  - Group: Migration Parity And Schema Governance
  - Owner: Product Docs
  - Depends on: PRJ-466
  - Priority: P0
  - Result:
    - planning, implementation reality, ops guidance, testing guidance, and
      context truth now describe one migration-first schema baseline for the
      full live model set, including durable attention and subconscious
      proposal storage
    - migration parity is no longer implied only by metadata/docs; it is now a
      recorded release expectation with regression evidence
  - Validation:
    - doc-and-context sync across `.codex/context/`, `docs/planning/`,
      `docs/implementation/`, `docs/operations/`, and `docs/engineering/`

- [x] PRJ-466 Add schema-parity regressions for migration-first startup against the current model baseline
  - Status: DONE
  - Group: Migration Parity And Schema Governance
  - Owner: QA/Test
  - Depends on: PRJ-465
  - Priority: P0
  - Result:
    - schema-baseline coverage now proves a fresh database can reach the
      current runtime schema via `alembic upgrade head` instead of relying only
      on `Base.metadata` expectations
    - migration drift for durable attention/proposal storage becomes
      release-visible before production startup or deploy smoke
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_schema_baseline.py tests/test_main_lifespan_policy.py tests/test_main_runtime_policy.py`

- [x] PRJ-465 Add Alembic revisions for durable attention and subconscious proposal persistence
  - Status: DONE
  - Group: Migration Parity And Schema Governance
  - Owner: DB/Migrations
  - Depends on: PRJ-464
  - Priority: P0
  - Result:
    - Alembic head now creates `aion_attention_turn` and
      `aion_subconscious_proposal` with the same table/index/constraint
      expectations as the live repository-backed runtime
    - migration-first bootstrap no longer lags the actual durable attention and
      proposal contract-store surfaces
  - Validation:
    - `.\.venv\Scripts\python -m alembic upgrade head --sql`
    - `.\.venv\Scripts\python -m pytest -q tests/test_schema_baseline.py tests/test_memory_repository.py`

- [x] PRJ-464 Audit model-vs-migration parity and define the missing Alembic delta set
  - Status: DONE
  - Group: Migration Parity And Schema Governance
  - Owner: Planner
  - Depends on: PRJ-463
  - Priority: P0
  - Result:
    - audit confirmed the migration chain already covered
      `aion_memory.payload`, scoped conclusions, semantic embeddings, and
      relation storage, but still missed `aion_attention_turn` and
      `aion_subconscious_proposal`
    - the missing delta set is now explicit before implementation:
      add durable attention table, add subconscious proposal table, and add a
      migration-parity regression that exercises fresh `upgrade head`
  - Validation:
    - targeted review across `app/memory/models.py`,
      `migrations/versions/`, `docs/implementation/runtime-reality.md`, and
      `docs/operations/runtime-ops-runbook.md`

- [x] PRJ-463 Sync planning/context for affective and retrieval health visibility docs convergence
  - Status: DONE
  - Group: Affective And Retrieval Health Visibility Docs Convergence
  - Owner: Product Docs
  - Depends on: PRJ-462
  - Priority: P1
  - Result:
    - task board, project state, next-iteration plan, and open decisions now
      describe one shared post-`PRJ-463` stance for operator-facing affective
      and retrieval health visibility
    - future follow-up discovery no longer needs to reconcile runbook drift
      around empathy triage and embedding execution posture
  - Validation:
    - doc-and-context sync across `.codex/context/` and `docs/planning/`

- [x] PRJ-462 Expand runbook guidance for affective health and retrieval execution-class triage
  - Status: DONE
  - Group: Affective And Retrieval Health Visibility Docs Convergence
  - Owner: Ops/Release
  - Depends on: PRJ-461
  - Priority: P1
  - Result:
    - runbook now explicitly calls out `/health.affective` and
      `memory_retrieval.semantic_embedding_execution_class` as operator-facing
      triage surfaces for empathy behavior and retrieval execution posture
  - Validation:
    - doc sync in `docs/operations/runtime-ops-runbook.md`

- [x] PRJ-461 Record post-convergence operator triage baseline for affective and retrieval health surfaces
  - Status: DONE
  - Group: Affective And Retrieval Health Visibility Docs Convergence
  - Owner: Planner
  - Depends on: PRJ-460
  - Priority: P1
  - Result:
    - the post-convergence runbook baseline now treats affective health and
      retrieval execution class as first-class operator diagnostics instead of
      runtime-only implementation details
  - Validation:
    - targeted runbook and planning-surface cross-review

- [x] PRJ-460 Sync planning/context for proposal inventory and operator health docs convergence
  - Status: DONE
  - Group: Proposal Inventory And Operator Health Docs Convergence
  - Owner: Product Docs
  - Depends on: PRJ-459
  - Priority: P1
  - Result:
    - task board, project state, next-iteration plan, and open decisions now
      describe one shared post-`PRJ-460` stance for persisted proposal
      inventory and operator-health visibility convergence
    - future post-convergence follow-up discovery no longer needs to reconcile
      docs drift around proposal durability or health-surface expectations
  - Validation:
    - doc-and-context sync across `.codex/context/` and `docs/planning/`

- [x] PRJ-459 Expand runbook guidance for post-convergence operator health surfaces
  - Status: DONE
  - Group: Proposal Inventory And Operator Health Docs Convergence
  - Owner: Ops/Release
  - Depends on: PRJ-458
  - Priority: P1
  - Result:
    - runbook health checks now call out the concrete operator meaning of
      `planning_governance`, `connectors`, `identity.adaptive_governance`, and
      `deployment` instead of leaving those surfaces as bare names
  - Validation:
    - doc sync in `docs/operations/runtime-ops-runbook.md`

- [x] PRJ-458 Record persisted subconscious proposal table in runtime reality inventory
  - Status: DONE
  - Group: Proposal Inventory And Operator Health Docs Convergence
  - Owner: Product Docs
  - Depends on: PRJ-457
  - Priority: P1
  - Result:
    - implementation-reality inventory now includes
      `aion_subconscious_proposal` as part of the live persisted schema
    - docs no longer imply that proposal lifecycle is contract-visible but not
      actually durably represented in the current data model
  - Validation:
    - doc sync in `docs/implementation/runtime-reality.md`

- [x] PRJ-457 Sync planning/context for attention contract-store docs convergence
  - Status: DONE
  - Group: Attention Contract-Store Docs Convergence
  - Owner: Product Docs
  - Depends on: PRJ-456
  - Priority: P1
  - Result:
    - task board, project state, next-iteration plan, and open decisions now
      describe one shared post-`PRJ-457` stance for durable attention
      contract-store documentation convergence
    - future follow-up discovery no longer needs to reconcile attention-owner
      drift across planning surfaces first
  - Validation:
    - doc-and-context sync across `.codex/context/` and `docs/planning/`

- [x] PRJ-456 Sync ops/config docs for durable attention contract-store visibility
  - Status: DONE
  - Group: Attention Contract-Store Docs Convergence
  - Owner: Ops/Release
  - Depends on: PRJ-455
  - Priority: P1
  - Result:
    - config and runbook guidance now describe the live repository-backed
      durable inbox posture and the exact `/health.attention` fields used for
      contract-store and cleanup triage
  - Validation:
    - doc sync across `docs/architecture/26_env_and_config.md` and
      `docs/operations/runtime-ops-runbook.md`

- [x] PRJ-455 Record durable attention contract-store baseline in canonical docs
  - Status: DONE
  - Group: Attention Contract-Store Docs Convergence
  - Owner: Product Docs
  - Depends on: PRJ-454
  - Priority: P1
  - Result:
    - canonical docs now explicitly state that durable attention uses
      repository-backed `aion_attention_turn` storage and exposes concrete
      contract-store posture fields for operator visibility
    - implementation-reality table inventory now includes
      `aion_attention_turn` as part of the live persisted schema
  - Validation:
    - doc sync across `docs/architecture/16_agent_contracts.md` and
      `docs/implementation/runtime-reality.md`

- [x] PRJ-454 Sync post-convergence planning surfaces after Groups 57 through 59
  - Status: DONE
  - Group: Post-Convergence Planning Hygiene
  - Owner: Product Docs
  - Depends on: PRJ-453
  - Priority: P1
  - Result:
    - top-level planning/context surfaces now describe one shared
      post-`PRJ-453` operating stance instead of mixing current
      post-convergence follow-up mode with stale queue-seeding notes from the
      earlier `PRJ-415..PRJ-442` wave
    - future execution can again be derived from concrete runtime or
      operational follow-ups without conflicting backlog headers
  - Validation:
    - doc-and-context sync across `.codex/context/` and `docs/planning/`

- [x] PRJ-453 Sync docs/context for embedding execution-class diagnostics
  - Status: DONE
  - Group: Embedding Execution-Class Diagnostics
  - Owner: Product Docs
  - Depends on: PRJ-452
  - Priority: P1
  - Result:
    - planning, implementation reality, testing guidance, and context truth
      now align on explicit embedding execution classes for deterministic
      baseline, local provider ownership, and fallback-to-deterministic
      posture
  - Validation:
    - doc-and-context sync across `.codex/context/`, `docs/planning/`,
      `docs/implementation/`, `docs/engineering/`, and `docs/architecture/`

- [x] PRJ-452 Add embedding execution-class diagnostics for provider-owned vs fallback retrieval posture
  - Status: DONE
  - Group: Embedding Execution-Class Diagnostics
  - Owner: Backend Builder
  - Depends on: PRJ-451
  - Priority: P1
  - Result:
    - `/health.memory_retrieval.semantic_embedding_execution_class` now
      distinguishes `deterministic_baseline`, `local_provider_owned`, and
      `fallback_to_deterministic`
    - operator triage no longer needs to infer actual execution class from
      requested/effective provider fields alone
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`
      (`71 passed`)

- [x] PRJ-451 Sync docs/context for affective diagnostics convergence
  - Status: DONE
  - Group: Affective Diagnostics Convergence
  - Owner: Product Docs
  - Depends on: PRJ-450
  - Priority: P1
  - Result:
    - architecture, runtime-reality, planning docs, testing guidance, and
      context truth now align on affective input ownership, final assessment
      resolution, and health/debug visibility
  - Validation:
    - doc-and-context sync across `.codex/context/`, `docs/planning/`,
      `docs/implementation/`, `docs/engineering/`, and `docs/architecture/`

- [x] PRJ-450 Add regressions for affective input, fallback reuse, and resolution diagnostics
  - Status: DONE
  - Group: Affective Diagnostics Convergence
  - Owner: QA/Test
  - Depends on: PRJ-449
  - Priority: P1
  - Result:
    - regressions now pin `/health.affective` plus `system_debug` resolution
      semantics for heuristic input, fallback reuse, and final assessment
      source visibility
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py`
      (`152 passed`)

- [x] PRJ-449 Expose affective input and final-resolution diagnostics through health and system debug
  - Status: DONE
  - Group: Affective Diagnostics Convergence
  - Owner: Backend Builder
  - Depends on: PRJ-448
  - Priority: P1
  - Result:
    - `/health.affective` now exposes the perception-owned affective input
      baseline alongside assessment rollout posture
    - runtime `system_debug.adaptive_state` now exposes `affective_input_policy`
      and per-turn `affective_resolution`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py`
      (`152 passed`)

- [x] PRJ-448 Define affective input-owner diagnostics baseline
  - Status: DONE
  - Group: Affective Diagnostics Convergence
  - Owner: Planner
  - Depends on: PRJ-447
  - Priority: P1
  - Result:
    - the repo now has one explicit diagnostics owner for heuristic affective
      input before the assessment stage rewrites or reuses that signal
    - fallback reuse semantics are now machine-describable instead of implicit
      in affective evidence strings only
  - Validation:
    - targeted runtime-debug and health contract review plus regression impact
      note

- [x] PRJ-447 Sync docs/context for shared debug-ingress vocabulary convergence
  - Status: DONE
  - Group: Shared Debug Ingress Vocabulary Convergence
  - Owner: Product Docs
  - Depends on: PRJ-446
  - Priority: P1
  - Result:
    - docs, planning truth, and context now align on final
      `shared_route_compatibility|shared_route_break_glass_only` posture
      vocabulary
  - Validation:
    - doc-and-context sync across `.codex/context/`, `docs/planning/`,
      `docs/implementation/`, `docs/engineering/`, and `docs/architecture/`

- [x] PRJ-446 Add regressions and release-smoke parity for final shared debug-ingress vocabulary
  - Status: DONE
  - Group: Shared Debug Ingress Vocabulary Convergence
  - Owner: QA/Test
  - Depends on: PRJ-445
  - Priority: P1
  - Result:
    - release smoke and API/runtime-policy tests now pin the final shared
      ingress posture vocabulary instead of the earlier `transitional_*`
      labels
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py`
      (`96 passed`)

- [x] PRJ-445 Apply final shared debug-ingress posture vocabulary to runtime policy and headers
  - Status: DONE
  - Group: Shared Debug Ingress Vocabulary Convergence
  - Owner: Backend Builder
  - Depends on: PRJ-444
  - Priority: P1
  - Result:
    - runtime policy and shared debug ingress headers now emit
      `shared_route_compatibility|shared_route_break_glass_only`
    - release evidence and operator tooling no longer describe the primary
      shared ingress posture as `transitional_*`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_deployment_trigger_scripts.py`
      (`96 passed`)

- [x] PRJ-444 Define final shared debug-ingress posture vocabulary owner
  - Status: DONE
  - Group: Shared Debug Ingress Vocabulary Convergence
  - Owner: Planner
  - Depends on: PRJ-443
  - Priority: P1
  - Result:
    - shared debug ingress posture now uses final route-owned terminology
      instead of rollout-era `transitional_*` wording
    - health, headers, and smoke evidence now have one stable vocabulary for
      compatibility vs break-glass posture
  - Validation:
    - targeted runtime-policy, API-header, and smoke-surface review

- [x] PRJ-443 Clean post-convergence backlog surfaces and planning truth
  - Status: DONE
  - Group: Post-Convergence Backlog Hygiene
  - Owner: Product Docs
  - Depends on: PRJ-442
  - Priority: P1
  - Result:
    - task board, project state, next-iteration plan, and open decisions now
      share one post-Group-56 operating stance instead of repeating stale
      queue-seeding notes from earlier convergence waves
    - the canonical backlog surface is now easier to derive from because it
      points to post-convergence follow-up discovery rather than historical
      queue scaffolding
  - Validation:
    - doc-and-context sync across `.codex/context/` and `docs/planning/`

- [x] PRJ-414 Sync docs/context for identity and language ownership baseline
  - Status: DONE
  - Group: Identity And Language Ownership Baseline
  - Owner: Product Docs
  - Depends on: PRJ-413
  - Priority: P1
  - Result:
    - architecture, runtime-reality, planning docs, testing guidance, and
      context truth now align on the shared identity-policy owner plus
      language-continuity diagnostics baseline
    - Group 49 is now complete and no seeded `READY` task remains
  - Validation:
    - doc-and-context sync across `docs/architecture/`,
      `docs/implementation/`, `docs/planning/`, `docs/engineering/`, and
      `.codex/context/`

- [x] PRJ-413 Add regressions for language-continuity posture and supported-language boundaries
  - Status: DONE
  - Group: Identity And Language Ownership Baseline
  - Owner: QA/Test
  - Depends on: PRJ-412
  - Priority: P1
  - Result:
    - explicit-request posture, profile-only continuity posture, and
      unsupported-profile fallback are now regression-pinned across language
      utility and runtime paths
    - supported-language boundary remains explicit at `en|pl` for current MVP
      continuity behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_language_runtime.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
      (`165 passed`)

- [x] PRJ-412 Expose language-continuity posture diagnostics through health and runtime debug
  - Status: DONE
  - Group: Identity And Language Ownership Baseline
  - Owner: Backend Builder
  - Depends on: PRJ-411
  - Priority: P1
  - Result:
    - `/health.identity.language_continuity` now exposes precedence baseline,
      supported codes, and continuity source families
    - runtime `system_debug.adaptive_state.language_continuity` now exposes
      selected source, candidate continuity inputs, continuity resolution, and
      fallback posture for the current event
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py`
      (`149 passed`)

- [x] PRJ-411 Define a shared identity/profile ownership policy and baseline visibility
  - Status: DONE
  - Group: Identity And Language Ownership Baseline
  - Owner: Planner
  - Depends on: PRJ-410
  - Priority: P1
  - Result:
    - runtime now has one shared `identity_policy` owner for
      `preferred_language` profile continuity versus conclusion-owned
      `response_style` and `collaboration_preference`
    - `/health.identity` and runtime `system_debug.adaptive_state.identity_policy`
      now expose that split so the boundary is machine-visible
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py`
      (`149 passed`)

- [x] PRJ-410 Sync docs/context for durable attention contract-store rollout
  - Status: DONE
  - Group: Durable Attention Contract-Store Rollout
  - Owner: Product Docs
  - Depends on: PRJ-409
  - Priority: P1
  - Result:
    - architecture, runtime-reality, planning docs, testing guidance, and
      context truth now align on repository-backed durable attention
      contract-store ownership plus cleanup visibility
    - there is no remaining seeded `READY`; the next architecture slice must
      be derived from planning docs and open decisions
  - Validation:
    - doc-and-context sync across `docs/architecture/`,
      `docs/implementation/`, `docs/planning/`, `docs/engineering/`, and
      `.codex/context/`

- [x] PRJ-409 Add regressions for durable attention contract-store parity and cleanup behavior
  - Status: DONE
  - Group: Durable Attention Contract-Store Rollout
  - Owner: QA/Test
  - Depends on: PRJ-408
  - Priority: P1
  - Result:
    - repository-backed attention rows, cleanup candidates, and durable
      owner-mode burst parity are now regression-pinned before any production
      default switch
    - cleanup visibility remains operator-visible through `/health.attention`
      rather than hidden behind repository-only behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_api_routes.py tests/test_runtime_pipeline.py`
      (`201 passed`)

- [x] PRJ-408 Add repository-backed durable attention store primitives behind owner-mode rollout
  - Status: DONE
  - Group: Durable Attention Contract-Store Rollout
  - Owner: Backend Builder
  - Depends on: PRJ-407
  - Priority: P1
  - Result:
    - `MemoryRepository` now owns durable attention-turn rows and cleanup
      primitives through `aion_attention_turn`
    - `AttentionTurnCoordinator` in `durable_inbox` mode now uses the
      repository-backed contract store while preserving existing burst
      coalescing semantics
  - Validation:
    - Group 48 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_api_routes.py tests/test_graph_state_contract.py`
      (`122 passed`)
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py`
      (`79 passed`)

- [x] PRJ-407 Define the durable attention contract-store shape and persistence responsibilities
  - Status: DONE
  - Group: Durable Attention Contract-Store Rollout
  - Owner: Planner
  - Depends on: PRJ-406
  - Priority: P1
  - Result:
    - durable attention now has one explicit contract-store shape keyed by
      `(user_id, conversation_key)` with `pending|claimed|answered` state,
      assembled text, source counts, coalesced event ids, and cleanup posture
    - persistence responsibility is explicit: the attention boundary owns turn
      state mutation while `MemoryRepository` owns durable storage and cleanup
      primitives
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_api_routes.py tests/test_graph_state_contract.py`
      (`122 passed`)

- [x] PRJ-406 Sync docs/context for reflection scope governance
  - Status: DONE
  - Group: Reflection Scope Governance
  - Owner: Product Docs
  - Depends on: PRJ-405
  - Priority: P1
  - Result:
    - architecture, runtime-reality, planning docs, testing guidance, and
      context truth now align on one reflection scope owner plus multi-goal
      leakage guardrails
    - `PRJ-407` is now the next `READY` task for durable attention
      contract-store rollout
  - Validation:
    - doc-and-context sync across `docs/architecture/`,
      `docs/implementation/`, `docs/planning/`, `docs/engineering/`, and
      `.codex/context/`

- [x] PRJ-405 Add regressions for no-cross-goal leakage in scoped reflection outputs
  - Status: DONE
  - Group: Reflection Scope Governance
  - Owner: QA/Test
  - Depends on: PRJ-404
  - Priority: P1
  - Result:
    - regressions now pin goal-scoped reflection writes, canonicalized
      repository reads, and runtime behavior when scoped rows could otherwise
      override global adaptive signals
    - future reflection-scope additions inherit explicit no-cross-goal
      leakage coverage across worker, repository, and runtime paths
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_memory_repository.py tests/test_runtime_pipeline.py`
      (`172 passed`)

- [x] PRJ-404 Apply scope policy to remaining reflection outputs and runtime readers
  - Status: DONE
  - Group: Reflection Scope Governance
  - Owner: Backend Builder
  - Depends on: PRJ-403
  - Priority: P1
  - Result:
    - reflection writes and memory/runtime readers now share one policy owner
      in `app/core/reflection_scope_policy.py`
    - repository canonicalizes invalid scoped writes for global reflection
      outputs and prevents scoped overrides from leaking into runtime
  - Validation:
    - Group 47 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_memory_repository.py tests/test_runtime_pipeline.py`
      (`172 passed`)

- [x] PRJ-403 Define explicit scope policy for reflection outputs with multi-goal risk
  - Status: DONE
  - Group: Reflection Scope Governance
  - Owner: Planner
  - Depends on: PRJ-402
  - Priority: P1
  - Result:
    - reflection scope ownership is now explicit through one shared owner for
      global, goal-scoped, and future task-scoped reflection families
    - goal-progress and milestone conclusions remain goal-scoped, while
      adaptive role/collaboration/affective outputs remain user-global unless
      architecture changes explicitly revise that baseline
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_memory_repository.py tests/test_runtime_pipeline.py`
      (`172 passed`)

- [x] PRJ-402 Sync docs/context for affective-assessment rollout policy
  - Status: DONE
  - Group: Affective Assessment Rollout Policy
  - Owner: Product Docs
  - Depends on: PRJ-401
  - Priority: P1
  - Result:
    - architecture, runtime-reality, planning docs, testing guidance, and
      context truth now align on explicit affective-assessment rollout
      ownership and fallback posture
    - `PRJ-403` is now the next `READY` task for reflection scope governance
  - Validation:
    - doc-and-context sync across `docs/architecture/`,
      `docs/implementation/`, `docs/planning/`, `docs/engineering/`, and
      `.codex/context/`

- [x] PRJ-401 Add regressions for affective rollout defaults and deterministic fallback gating
  - Status: DONE
  - Group: Affective Assessment Rollout Policy
  - Owner: QA/Test
  - Depends on: PRJ-400
  - Priority: P1
  - Result:
    - regressions now pin non-production default enablement, production default
      fallback posture, explicit AI-assisted posture, and disabled-policy
      fallback gating
    - health and system-debug surfaces remain contract-stable for affective
      rollout diagnostics
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_affective_assessor.py tests/test_config.py tests/test_api_routes.py tests/test_runtime_pipeline.py`
      (`199 passed`)
    - `.\.venv\Scripts\python -m pytest -q`
      (`734 passed`)

- [x] PRJ-400 Expose affective-assessment rollout posture through runtime policy and debug surfaces
  - Status: DONE
  - Group: Affective Assessment Rollout Policy
  - Owner: Backend Builder
  - Depends on: PRJ-399
  - Priority: P1
  - Result:
    - `/health.runtime_policy` now exposes affective rollout posture, policy
      source, classifier availability, and operator hints
    - runtime `system_debug.adaptive_state` now carries the same affective
      rollout snapshot from the live assessor
  - Validation:
    - Group 46 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`734 passed`)

- [x] PRJ-399 Define rollout policy ownership for AI-assisted affective assessment
  - Status: DONE
  - Group: Affective Assessment Rollout Policy
  - Owner: Planner
  - Depends on: PRJ-398
  - Priority: P1
  - Result:
    - affective assessment now has one explicit rollout policy owner with
      environment-default and explicit override semantics
    - the assessor can now distinguish policy-disabled fallback from
      classifier-unavailable fallback without hiding that posture in logs only
  - Validation:
    - Group 46 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`734 passed`)

- [x] PRJ-398 Sync docs/context for role-selection evidence baseline
  - Status: DONE
  - Group: Role-Selection Evidence Baseline
  - Owner: Product Docs
  - Depends on: PRJ-397
  - Priority: P1
  - Result:
    - architecture, runtime-reality, planning docs, testing guidance, and
      context truth now align on the shared role-selection policy owner,
      evidence metadata, and bounded goal-aware diagnostics
    - `PRJ-399` is now the next `READY` task for affective-assessment rollout
      policy
  - Validation:
    - doc-and-context sync across `docs/architecture/`,
      `docs/implementation/`, `docs/planning/`, `docs/engineering/`, and
      `.codex/context/`

- [x] PRJ-397 Add regressions for role-selection evidence precedence and bounded diagnostics
  - Status: DONE
  - Group: Role-Selection Evidence Baseline
  - Owner: QA/Test
  - Depends on: PRJ-396
  - Priority: P1
  - Result:
    - regressions now pin role-selection reasons/evidence for preferred-role
      tie breaks, active-goal planning context, and debug-surface visibility
    - role diagnostics remain metadata-only and do not affect action ownership
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_role_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
      (`160 passed`)
    - `.\.venv\Scripts\python -m pytest -q`
      (`729 passed`)

- [x] PRJ-396 Apply a shared role-selection policy owner with evidence-driven diagnostics
  - Status: DONE
  - Group: Role-Selection Evidence Baseline
  - Owner: Backend Builder
  - Depends on: PRJ-395
  - Priority: P1
  - Result:
    - role selection now routes through one shared policy owner with explicit
      `selection_reason` and `selection_evidence` metadata
    - active-goal context can now reinforce planning-role selection without
      turning role diagnostics into side-effect owners
  - Validation:
    - Group 45 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`729 passed`)

- [x] PRJ-395 Define a shared role-selection evidence contract and baseline policy owner
  - Status: DONE
  - Group: Role-Selection Evidence Baseline
  - Owner: Planner
  - Depends on: PRJ-394
  - Priority: P1
  - Result:
    - runtime contracts now treat role selection as an evidence-driven policy
      owner rather than a bare selected-string heuristic
    - role outputs now expose bounded, machine-readable diagnostics that can be
      consumed by runtime debug and behavior validation
  - Validation:
    - Group 45 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`729 passed`)

- [x] PRJ-394 Sync docs/context for retrieval-depth and theta-governance baseline
  - Status: DONE
  - Group: Retrieval-Depth And Theta-Governance Baseline
  - Owner: Product Docs
  - Depends on: PRJ-393
  - Priority: P1
  - Result:
    - architecture, runtime-reality, planning docs, testing guidance, and
      context truth now align on retrieval-depth policy snapshots and
      bounded theta-influence diagnostics
    - Groups 41 through 44 are now complete, so no `READY` task remains after
      `PRJ-394`
  - Validation:
    - doc-and-context sync across `docs/architecture/`,
      `docs/implementation/`, `docs/planning/`, `docs/engineering/`, and
      `.codex/context/`

- [x] PRJ-393 Add regressions for retrieval-depth governance and bounded theta influence
  - Status: DONE
  - Group: Retrieval-Depth And Theta-Governance Baseline
  - Owner: QA/Test
  - Depends on: PRJ-392
  - Priority: P1
  - Result:
    - regressions now pin retrieval-depth policy visibility plus
      theta-influence posture across role, planning, runtime debug, and health
      surfaces
    - background adaptive summaries, bounded selected-skill metadata, and
      durable attention parity baseline stay test-visible in the same runtime
      contract path
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_api_routes.py tests/test_role_agent.py tests/test_runtime_pipeline.py tests/test_graph_state_contract.py`
      (`212 passed`)
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_memory_repository.py tests/test_config.py`
      (`152 passed`)
    - `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- [x] PRJ-392 Expose theta-influence posture diagnostics across role, motivation, planning, and expression
  - Status: DONE
  - Group: Retrieval-Depth And Theta-Governance Baseline
  - Owner: Backend Builder
  - Depends on: PRJ-391
  - Priority: P1
  - Result:
    - runtime `system_debug.adaptive_state` now exposes shared
      `theta_influence` posture across role, motivation, planning, and
      expression stages
    - theta remains bounded to adaptive tie-break semantics instead of silent
      broader mutation posture
  - Validation:
    - Group 44 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- [x] PRJ-391 Define a shared retrieval-depth policy snapshot for hybrid memory loading
  - Status: DONE
  - Group: Retrieval-Depth And Theta-Governance Baseline
  - Owner: Planner
  - Depends on: PRJ-390
  - Priority: P1
  - Result:
    - one shared retrieval-depth policy snapshot now exposes episodic/conclusion
      limits, vector posture, and retrieval mode for runtime and `/health`
    - retrieval depth stops living only inside orchestrator internals
  - Validation:
    - Group 44 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- [x] PRJ-390 Sync docs/context for role-and-skill capability convergence
  - Status: DONE
  - Group: Role-And-Skill Capability Convergence
  - Owner: Product Docs
  - Depends on: PRJ-389
  - Priority: P1
  - Result:
    - architecture, runtime-reality, planning docs, testing guidance, and
      context truth now align on bounded role-to-skill capability metadata
      between role selection and action
    - future capability growth can extend selected-skill semantics without
      turning skills into tool or side-effect owners
  - Validation:
    - doc-and-context sync across `docs/architecture/`,
      `docs/implementation/`, `docs/planning/`, `docs/engineering/`, and
      `.codex/context/`

- [x] PRJ-389 Add regressions for role/skill separation and no-skill-side-effect posture
  - Status: DONE
  - Group: Role-And-Skill Capability Convergence
  - Owner: QA/Test
  - Depends on: PRJ-388
  - Priority: P1
  - Result:
    - regressions now pin that selected skills are bounded metadata on role and
      plan outputs and do not become independent side-effect owners
    - role, planning, runtime debug, and health surfaces remain aligned on
      `role != skill != action`
  - Validation:
    - Group 43 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- [x] PRJ-388 Extend foreground outputs with bounded selected-skill metadata without tool leakage
  - Status: DONE
  - Group: Role-And-Skill Capability Convergence
  - Owner: Backend Builder
  - Depends on: PRJ-387
  - Priority: P1
  - Result:
    - role and plan outputs now carry bounded `selected_skills` metadata
      describing turn-relevant capabilities without tool leakage
    - runtime debug also surfaces selected/planned skills while keeping action
      as the only side-effect owner
  - Validation:
    - Group 43 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- [x] PRJ-387 Define a shared skill-registry contract and role-to-skill capability model
  - Status: DONE
  - Group: Role-And-Skill Capability Convergence
  - Owner: Planner
  - Depends on: PRJ-386
  - Priority: P1
  - Result:
    - one shared skill-registry contract now maps role/topic posture into
      explicit capability-family metadata
    - the repo now has an explicit capability layer between role selection and
      action without changing external-side-effect boundaries
  - Validation:
    - Group 43 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- [x] PRJ-386 Sync docs/context for durable attention-inbox rollout baseline
  - Status: DONE
  - Group: Durable Attention-Inbox Rollout Baseline
  - Owner: Product Docs
  - Depends on: PRJ-385
  - Priority: P1
  - Result:
    - canonical docs, runtime reality, planning docs, and context truth now
      align on durable-attention parity baseline and health-visible owner
      posture
    - later repository-backed inbox rollout can extend this baseline without
      reopening turn-assembly semantics
  - Validation:
    - doc-and-context sync across `docs/architecture/`,
      `docs/implementation/`, `docs/planning/`, `docs/engineering/`, and
      `.codex/context/`

- [x] PRJ-385 Add regressions for in-process versus durable attention-owner parity
  - Status: DONE
  - Group: Durable Attention-Inbox Rollout Baseline
  - Owner: QA/Test
  - Depends on: PRJ-384
  - Priority: P1
  - Result:
    - regressions now pin burst-message coalescing parity and health posture
      consistency across `in_process` and `durable_inbox` owner modes
    - durable-attention rollout drift becomes visible before any future storage
      migration
  - Validation:
    - Group 42 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- [x] PRJ-384 Add runtime-owner adapter for `durable_inbox` mode with health-visible parity semantics
  - Status: DONE
  - Group: Durable Attention-Inbox Rollout Baseline
  - Owner: Backend Builder
  - Depends on: PRJ-383
  - Priority: P1
  - Result:
    - `durable_inbox` mode now routes through the same turn-assembly semantics
      as `in_process` while exposing health-visible parity posture
    - `/health.attention` now reports `persistence_owner` and `parity_state`
      instead of treating durable mode as a not-yet-ready blocker
  - Validation:
    - Group 42 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- [x] PRJ-383 Define the durable attention-inbox persistence contract and repository boundary
  - Status: DONE
  - Group: Durable Attention-Inbox Rollout Baseline
  - Owner: Planner
  - Depends on: PRJ-382
  - Priority: P1
  - Result:
    - durable attention rollout now has explicit persistence-owner and
      parity-state semantics instead of a placeholder blocker posture
    - attention coordination mode remains architecture-aligned while rollout
      stays reversible
  - Validation:
    - Group 42 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- [x] PRJ-382 Sync docs/context for background adaptive-output convergence
  - Status: DONE
  - Group: Background Adaptive-Output Convergence
  - Owner: Product Docs
  - Depends on: PRJ-381
  - Priority: P1
  - Result:
    - architecture, runtime-reality, planning docs, testing guidance, and
      context truth now align on background-owned adaptive outputs and
      foreground-visible summaries
    - later subconscious/adaptive work can extend the background contract
      without reopening output ownership
  - Validation:
    - doc-and-context sync across `docs/architecture/`,
      `docs/implementation/`, `docs/planning/`, `docs/engineering/`, and
      `.codex/context/`

- [x] PRJ-381 Add regressions for adaptive-output ownership and no-foreground-theta-mutation posture
  - Status: DONE
  - Group: Background Adaptive-Output Convergence
  - Owner: QA/Test
  - Depends on: PRJ-380
  - Priority: P1
  - Result:
    - regressions now pin adaptive-output ownership through reflection
      snapshots, runtime debug, and health surfaces
    - theta and relation/progress updates remain background-owned and do not
      mutate foreground state implicitly
  - Validation:
    - Group 41 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- [x] PRJ-380 Expose reflection adaptive-output summaries through runtime health and debug surfaces
  - Status: DONE
  - Group: Background Adaptive-Output Convergence
  - Owner: Backend Builder
  - Depends on: PRJ-379
  - Priority: P1
  - Result:
    - reflection worker snapshots now expose one adaptive-output summary and
      runtime/health surfaces now make that background posture operator-visible
    - adaptive evidence no longer lives only in repository rows and logs
  - Validation:
    - Group 41 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- [x] PRJ-379 Define a shared background adaptive-output contract for reflection results
  - Status: DONE
  - Group: Background Adaptive-Output Convergence
  - Owner: Planner
  - Depends on: PRJ-378
  - Priority: P1
  - Result:
    - one shared background adaptive-output contract now summarizes conclusion,
      relation, theta, and progress outputs produced by reflection
    - foreground/runtime consumers can depend on explicit adaptive-state
      surfaces instead of implicit repository behavior
  - Validation:
    - Group 41 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q`
      (`726 passed`)

- [x] PRJ-378 Sync docs/context for compatibility-sunset readiness governance
  - Status: DONE
  - Group: Compatibility Sunset Readiness
  - Owner: Product Docs
  - Depends on: PRJ-377
  - Priority: P1
  - Result:
    - planning, ops, architecture, testing guidance, and context truth now
      align on how migration compatibility and shared debug ingress move from
      transitional to retirement-ready posture
    - no `READY` task remains after Group 40, so the next slice should again
      be derived from planning docs and open decisions
  - Validation:
    - doc-and-context sync across `docs/architecture/`,
      `docs/planning/`, `docs/operations/`, `docs/engineering/`, and
      `.codex/context/`

- [x] PRJ-377 Add regressions for compatibility-sunset readiness and release-gate semantics
  - Status: DONE
  - Group: Compatibility Sunset Readiness
  - Owner: QA/Test
  - Depends on: PRJ-376
  - Priority: P1
  - Result:
    - regressions now pin migration-bootstrap sunset readiness,
      shared-debug-ingress sunset readiness, and smoke evidence gate
      semantics
    - compatibility readiness drift is now test-visible across runtime policy,
      `/health`, startup logs, and release smoke
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_deployment_trigger_scripts.py`
      (`127 passed`)

- [x] PRJ-376 Extend release smoke and runtime-policy gates for compatibility-sunset readiness evidence
  - Status: DONE
  - Group: Compatibility Sunset Readiness
  - Owner: Ops/Release
  - Depends on: PRJ-375
  - Priority: P1
  - Result:
    - release smoke now verifies compatibility-sunset evidence for
      migration-only bootstrap and shared debug ingress posture
    - smoke summary now carries explicit sunset-readiness posture for operator
      release notes and triage
  - Validation:
    - Group 40 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_deployment_trigger_scripts.py`
      (`127 passed`)

- [x] PRJ-375 Add compatibility-sunset readiness diagnostics for migration-only bootstrap and internal-only debug ingress
  - Status: DONE
  - Group: Compatibility Sunset Readiness
  - Owner: Backend Builder
  - Depends on: PRJ-374
  - Priority: P1
  - Result:
    - `/health.runtime_policy` now exposes machine-readable sunset-readiness
      posture for migration-only bootstrap and shared debug ingress
    - startup runtime-policy hints now surface compatibility-sunset readiness
      during production boot diagnostics
  - Validation:
    - Group 40 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_deployment_trigger_scripts.py`
      (`127 passed`)

- [x] PRJ-374 Sync docs/context for `ActionDelivery` extensibility baseline
  - Status: DONE
  - Group: Action Delivery Extensibility
  - Owner: Product Docs
  - Depends on: PRJ-373
  - Priority: P1
  - Result:
    - architecture, runtime-reality, planning docs, testing guidance, and
      context truth now align on one shared extensible expression-to-action
      handoff contract with connector-safe execution envelopes
    - Group 39 is now complete, and the next execution slice moves to
      compatibility-sunset readiness evidence in Group 40
  - Validation:
    - doc-and-context sync across `docs/architecture/`,
      `docs/implementation/`, `docs/planning/`, `docs/engineering/`, and
      `.codex/context/`

- [x] PRJ-373 Add regressions for shared handoff stability and connector-extension compatibility
  - Status: DONE
  - Group: Action Delivery Extensibility
  - Owner: QA/Test
  - Depends on: PRJ-372
  - Priority: P1
  - Result:
    - regressions now pin the shared `ActionDelivery` contract for standard
      responses, connector-safe execution envelopes, and graph/runtime handoff
      parity
    - stage-boundary drift between expression, action, delivery routing, and
      graph adapters is now test-visible
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_expression_agent.py tests/test_action_executor.py tests/test_delivery_router.py tests/test_runtime_pipeline.py tests/test_graph_stage_adapters.py tests/test_graph_state_contract.py`
      (`138 passed`)

- [x] PRJ-372 Consume `ActionDelivery` execution envelopes in action and integration routing without expression leakage
  - Status: DONE
  - Group: Action Delivery Extensibility
  - Owner: Backend Builder
  - Depends on: PRJ-371
  - Priority: P1
  - Result:
    - action now validates execution-envelope parity against planning before
      delivery side effects occur
    - delivery routing now surfaces bounded execution-envelope notes without
      leaking connector semantics back into expression
  - Validation:
    - Group 39 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q tests/test_expression_agent.py tests/test_action_executor.py tests/test_delivery_router.py tests/test_runtime_pipeline.py tests/test_graph_stage_adapters.py tests/test_graph_state_contract.py`
      (`138 passed`)

- [x] PRJ-371 Extend the shared `ActionDelivery` contract with connector-safe execution envelopes
  - Status: DONE
  - Group: Action Delivery Extensibility
  - Owner: Backend Builder
  - Depends on: PRJ-370
  - Priority: P1
  - Result:
    - one shared `ActionDelivery` contract now carries a bounded
      connector-safe execution envelope instead of fragmenting into
      connector-specific handoff owners
    - expression-to-action stage ordering remains explicit while connector
      permission gates and connector intent snapshots stay structured
  - Validation:
    - Group 39 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q tests/test_expression_agent.py tests/test_action_executor.py tests/test_delivery_router.py tests/test_runtime_pipeline.py tests/test_graph_stage_adapters.py tests/test_graph_state_contract.py`
      (`138 passed`)

- [x] PRJ-370 Sync docs/context for expanded typed-intent ownership
  - Status: DONE
  - Group: Typed Intent Coverage For Future Writes
  - Owner: Product Docs
  - Depends on: PRJ-369
  - Priority: P1
  - Result:
    - architecture, runtime-reality, planning docs, testing guidance, and
      context truth now align on typed-intent ownership for proactive
      follow-up state and relation-maintenance writes
    - Group 38 is now complete, and the next execution slice moves to shared
      `ActionDelivery` extensibility in Group 39
  - Validation:
    - doc-and-context sync across `docs/architecture/`,
      `docs/implementation/`, `docs/planning/`, `docs/engineering/`, and
      `.codex/context/`

- [x] PRJ-369 Add regressions for typed future-write boundaries and no-raw-text durable mutation posture
  - Status: DONE
  - Group: Typed Intent Coverage For Future Writes
  - Owner: QA/Test
  - Depends on: PRJ-368
  - Priority: P1
  - Result:
    - regressions now pin proactive planning state writes as typed intents and
      relation/proactive action writes as typed-intent-only durable mutation
      paths
    - planning and action no longer need generic fallback mutation posture for
      these write families
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_reflection_worker.py tests/test_scheduler_worker.py`
      (`225 passed`)

- [x] PRJ-368 Route future durable writes through typed-intent-only action execution
  - Status: DONE
  - Group: Typed Intent Coverage For Future Writes
  - Owner: Backend Builder
  - Depends on: PRJ-367
  - Priority: P1
  - Result:
    - action now routes relation-maintenance writes through explicit
      `maintain_relation` typed intents and proactive follow-up state through
      explicit `update_proactive_state` typed intents
    - proactive execution paths stop depending on generic `noop` placeholders
      when durable proactive state should still be recorded
  - Validation:
    - Group 38 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_reflection_worker.py tests/test_scheduler_worker.py`
      (`225 passed`)

- [x] PRJ-367 Add dedicated typed intents for relation-maintenance and proactive-state writes
  - Status: DONE
  - Group: Typed Intent Coverage For Future Writes
  - Owner: Backend Builder
  - Depends on: PRJ-366
  - Priority: P1
  - Result:
    - planning/runtime contracts now define `maintain_relation` and
      `update_proactive_state` as first-class typed intent families for future
      durable writes
    - proactive planning now emits explicit state intents for
      `delivery_ready|delivery_guard_blocked|interruption_deferred|attention_gate_blocked`
      instead of hiding write posture behind generic `noop`
  - Validation:
    - Group 38 consolidated validation:
      `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_reflection_worker.py tests/test_scheduler_worker.py`
      (`225 passed`)

- [x] PRJ-366 Sync docs/context for connector execution policy baseline
  - Status: DONE
  - Group: Connector Boundary Execution Policy
  - Owner: Product Docs
  - Depends on: PRJ-365
  - Priority: P1
  - Result:
    - architecture, implementation reality, planning docs, and context truth
      now align on the shared connector execution-policy owner plus action
      guardrail posture
    - Group 37 is now complete, and the next execution slice moves to typed
      future-write ownership in Group 38
  - Validation:
    - doc-and-context sync across `docs/architecture/`,
      `docs/implementation/`, `docs/planning/`, `docs/engineering/`, and
      `.codex/context/`

- [x] PRJ-365 Add regressions for connector execution posture and no-self-authorization rules
  - Status: DONE
  - Group: Connector Boundary Execution Policy
  - Owner: QA/Test
  - Depends on: PRJ-364
  - Priority: P1
  - Result:
    - regressions now pin shared-policy-derived permission gates for
      read-only, suggestion-only, mutate-with-confirmation, and proposal-only
      connector posture
    - action-layer guardrails now fail fast on connector intent mode mismatch
      before delivery side effects occur
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py`
      (`95 passed`)
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py`
      (`141 passed`)

- [x] PRJ-364 Apply shared connector execution policy to planning permission gates and action guardrails
  - Status: DONE
  - Group: Connector Boundary Execution Policy
  - Owner: Backend Builder
  - Depends on: PRJ-363
  - Priority: P1
  - Result:
    - planner permission gates now derive from shared helper logic in
      `app/core/connector_policy.py` instead of duplicating connector-family
      execution rules
    - action now applies the same connector policy as a guardrail, blocking
      inconsistent connector intent modes before response delivery
    - memory payloads now record connector guardrail posture alongside
      connector intent updates for runtime-visible triage
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py`
      (`95 passed`)
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py`
      (`141 passed`)

- [x] PRJ-363 Define shared connector operation policy for internal planning versus external systems
  - Status: DONE
  - Group: Connector Boundary Execution Policy
  - Owner: Planner
  - Depends on: PRJ-362
  - Priority: P1
  - Result:
    - connector operation defaults now have one shared owner in
      `app/core/connector_policy.py` across `calendar`, `task_system`, and
      `cloud_drive`
    - planner connector intents now derive their baseline
      `read_only|suggestion_only|mutate_with_confirmation` posture from the
      shared policy instead of open-coded literals
    - connector capability discovery now also uses the shared suggestion-only
      policy baseline for no-self-authorization posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_connector_policy.py tests/test_planning_agent.py tests/test_action_executor.py`
      (`91 passed`)
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py`
      (`141 passed`)

- [x] PRJ-362 Sync docs/context for attention timing baseline governance
  - Status: DONE
  - Group: Attention Timing Baseline Governance
  - Owner: Product Docs
  - Depends on: PRJ-361
  - Priority: P1
  - Result:
    - planning docs, ops guidance, and context truth now align on the chosen
      production-default attention timing baseline and health-visible
      alignment posture
    - no `READY` task remains after this attention timing baseline slice, so
      the next task should again be derived from planning docs and open
      decisions
  - Validation:
    - doc-and-context sync across `.codex/context/`, `docs/planning/`,
      `docs/operations/`, and `docs/engineering/` with targeted
      cross-reference checks

- [x] PRJ-361 Expose attention timing baseline and alignment posture through `/health`
  - Status: DONE
  - Group: Attention Timing Baseline Governance
  - Owner: Backend Builder
  - Depends on: PRJ-360
  - Priority: P1
  - Result:
    - `/health.attention` now exposes explicit production timing baseline
      values for burst window, answered TTL, and stale-turn cleanup posture
    - operators can now see whether the current attention timing config is
      aligned with the production baseline or running as a customized override
      through `timing_policy`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_config.py`
      (`111 passed`)
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_main_runtime_policy.py`
      (`111 passed`)

- [x] PRJ-360 Add regressions and docs/context sync for behavior-validation schema-major compatibility posture
  - Status: DONE
  - Group: Behavior Validation Artifact Compatibility Governance
  - Owner: Product Docs
  - Depends on: PRJ-359
  - Priority: P1
  - Result:
    - testing guidance, planning docs, and context truth now align on CI
      schema-major compatibility blocking versus operator-mode compatibility
    - no `READY` task remains after this compatibility-governance follow-up,
      so the next slice should again be derived from planning docs and open
      decisions
  - Validation:
    - doc-and-context sync across `.codex/context/`, `docs/planning/`, and
      `docs/engineering/` with targeted cross-reference checks

- [x] PRJ-359 Enforce schema-major compatibility gate for behavior-validation artifact input in CI mode
  - Status: DONE
  - Group: Behavior Validation Artifact Compatibility Governance
  - Owner: Backend Builder
  - Depends on: PRJ-358
  - Priority: P1
  - Result:
    - CI artifact-input evaluation now fails fast when a behavior-validation
      artifact declares an incompatible major schema version
    - operator-mode artifact evaluation remains backward-compatible for local
      inspection even when schema-major mismatch is present
    - gate violation context now reports input versus expected schema-major
      posture for machine-visible triage
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_behavior_validation_script.py`
      (`12 passed`)
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
      (`176 passed`)

- [x] PRJ-358 Sync docs/context for deployment-trigger SLO instrumentation lane
  - Status: DONE
  - Group: Deployment Trigger SLO Instrumentation
  - Owner: Product Docs
  - Depends on: PRJ-357
  - Priority: P1
  - Result:
    - planning, ops runbook, testing guidance, and context truth now align on
      deployment-trigger evidence capture, release-smoke evidence verification,
      and regression coverage posture
    - no `READY` task remains after Group 34, so the next slice should be
      derived from planning docs and open decisions
  - Validation:
    - doc-and-context sync across `.codex/context/`, `docs/planning/`,
      `docs/operations/`, and `docs/engineering/` with targeted
      cross-reference checks

- [x] PRJ-357 Add regressions for deployment-trigger evidence and release-smoke verification posture
  - Status: DONE
  - Group: Deployment Trigger SLO Instrumentation
  - Owner: QA/Test
  - Depends on: PRJ-356
  - Priority: P1
  - Result:
    - regression coverage now pins webhook evidence file shape for successful
      and failed Coolify trigger attempts
    - release-smoke verification is now test-visible for optional evidence
      omission plus freshness and unsuccessful-webhook failure posture
    - PowerShell release-smoke evidence parsing now remains compatible with
      runtimes that do not support `ConvertFrom-Json -Depth`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_deployment_trigger_scripts.py`
      (`6 passed`)
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_api_routes.py`
      (`101 passed`)

- [x] PRJ-356 Add release-smoke support for optional deployment-trigger evidence verification
  - Status: DONE
  - Group: Deployment Trigger SLO Instrumentation
  - Owner: Ops/Release
  - Depends on: PRJ-355
  - Priority: P1
  - Result:
    - release-smoke scripts now support optional deployment-evidence
      verification (freshness and successful webhook response posture) in both
      PowerShell and bash paths
    - existing smoke workflow remains backward-compatible when evidence path is
      not provided
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_main_runtime_policy.py`
      (`101 passed`)

- [x] PRJ-355 Add deployment-trigger evidence capture script for Coolify webhook invocations
  - Status: DONE
  - Group: Deployment Trigger SLO Instrumentation
  - Owner: Ops/Release
  - Depends on: PRJ-354
  - Priority: P1
  - Result:
    - Coolify deploy trigger now has a shared Python owner with optional
      machine-readable evidence output (`coolify_deploy_webhook_evidence`)
    - PowerShell and bash trigger scripts now route through the shared
      evidence-capable entrypoint while preserving existing trigger arguments
  - Validation:
    - `.\.venv\Scripts\python .\scripts\trigger_coolify_deploy_webhook.py --help`
      (argument contract verified)
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_api_routes.py`
      (`101 passed`)

- [x] PRJ-354 Sync docs/context for behavior-validation artifact-governance lane
  - Status: DONE
  - Group: Behavior Validation Artifact Governance
  - Owner: Product Docs
  - Depends on: PRJ-353
  - Priority: P1
  - Result:
    - planning, ops, testing guidance, and context truth now align on artifact
      schema versioning, reason taxonomy, and artifact-input gate evaluation
      posture
    - next derived queue continuity is now explicit through
      `PRJ-355..PRJ-358` for deployment-trigger SLO instrumentation follow-up
  - Validation:
    - doc-and-context sync across `.codex/context/`, `docs/planning/`,
      `docs/operations/`, and `docs/engineering/` with targeted
      cross-reference checks

- [x] PRJ-353 Add regressions for schema-version and local artifact gate-evaluation semantics
  - Status: DONE
  - Group: Behavior Validation Artifact Governance
  - Owner: QA/Test
  - Depends on: PRJ-352
  - Priority: P1
  - Result:
    - regressions now pin normalized gate reason taxonomy for failed/error/exit
      paths and schema-version contract presence in generated artifacts
    - malformed artifact-input paths (`missing`, `summary_missing`,
      `summary_invalid`) are now test-visible in CI gate mode
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_behavior_validation_script.py tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
      (`186 passed`)

- [x] PRJ-352 Add local artifact gate-evaluation mode for CI consumers without rerunning pytest
  - Status: DONE
  - Group: Behavior Validation Artifact Governance
  - Owner: Backend Builder
  - Depends on: PRJ-351
  - Priority: P1
  - Result:
    - behavior-validation script now supports artifact-input evaluation mode so
      CI gate checks can run on a pre-generated artifact without invoking
      pytest
    - artifact-input evaluation now tolerates UTF-8 BOM payloads (common from
      PowerShell writes) and keeps gate semantics deterministic
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_behavior_validation_script.py tests/test_main_runtime_policy.py tests/test_api_routes.py`
      (`108 passed`)
    - `.\.venv\Scripts\python .\scripts\run_behavior_validation.py --artifact-input-path artifacts/behavior_validation/prj352-input.json --artifact-path artifacts/behavior_validation/prj352-output.json --gate-mode ci`
      (`gate_status=pass`)

- [x] PRJ-351 Add artifact schema versioning and gate reason taxonomy for behavior-validation reports
  - Status: DONE
  - Group: Behavior Validation Artifact Governance
  - Owner: Backend Builder
  - Depends on: PRJ-350
  - Priority: P1
  - Result:
    - behavior-validation artifact now includes explicit schema-version
      metadata (`artifact_schema_version`) and gate-reason taxonomy version
      (`gate_reason_taxonomy_version`)
    - gate violations now use normalized taxonomy codes with explicit
      `violation_context`, making CI-consumer parsing deterministic
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_behavior_validation_script.py tests/test_runtime_pipeline.py`
      (`80 passed`)
    - `.\.venv\Scripts\python .\scripts\run_behavior_validation.py --artifact-path artifacts/behavior_validation/prj351-report.json --gate-mode ci`
      (`6 passed`)

- [x] PRJ-350 Sync docs/context for behavior-validation CI-ingestion lane
  - Status: DONE
  - Group: Behavior Validation CI-Ingestion Follow-up
  - Owner: Product Docs
  - Depends on: PRJ-349
  - Priority: P1
  - Result:
    - planning, ops, testing docs, and context truth now align on
      behavior-validation artifact contract and `operator|ci` gate posture
    - next derived queue continuity is now explicit through
      `PRJ-351..PRJ-354` for artifact-governance follow-up
  - Validation:
    - doc-and-context sync across `.codex/context/`, `docs/planning/`,
      `docs/operations/`, and `docs/engineering/` with targeted
      cross-reference checks

- [x] PRJ-349 Add regressions for behavior-validation artifact and CI gate semantics
  - Status: DONE
  - Group: Behavior Validation CI-Ingestion Follow-up
  - Owner: QA/Test
  - Depends on: PRJ-348
  - Priority: P1
  - Result:
    - regression coverage now pins behavior-validation gate semantics for
      `operator` versus `ci` posture, including CI `no tests collected`
      fail-fast behavior
    - artifact gate contract is now test-visible (`gate.mode`,
      `gate.status`, `gate.violations`, `gate.ci_require_tests`) through
      script-level regressions
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_behavior_validation_script.py`
      (`5 passed`)
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
      (`176 passed`)

- [x] PRJ-348 Add release/ops script support for behavior-validation CI gate posture
  - Status: DONE
  - Group: Behavior Validation CI-Ingestion Follow-up
  - Owner: Ops/Release
  - Depends on: PRJ-347
  - Priority: P1
  - Result:
    - `run_behavior_validation` wrappers now expose explicit gate posture
      controls (`operator|ci`) while preserving backward-compatible local
      evidence flow
    - behavior-validation artifact now includes machine-readable gate outcome
      metadata (`gate.mode`, `gate.status`, `gate.violations`) and CI mode can
      fail fast on artifact-level violations
  - Validation:
    - `.\.venv\Scripts\python .\scripts\run_behavior_validation.py --artifact-path artifacts/behavior_validation/prj348-operator.json --gate-mode operator`
      (`6 passed`)
    - `.\.venv\Scripts\python .\scripts\run_behavior_validation.py --artifact-path artifacts/behavior_validation/prj348-ci.json --gate-mode ci`
      (`6 passed`)
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_api_routes.py`
      (`101 passed`)

- [x] PRJ-347 Add machine-readable behavior-validation artifact output for CI consumers
  - Status: DONE
  - Group: Behavior Validation CI-Ingestion Follow-up
  - Owner: Backend Builder
  - Depends on: PRJ-346
  - Priority: P1
  - Result:
    - behavior validation run path now emits a machine-readable JSON artifact
      (`artifacts/behavior_validation/report.json`) with summary counts,
      per-test status, and pytest exit-code posture
    - `run_behavior_validation.{ps1,sh}` now use the shared Python entrypoint
      and remain backward-compatible for local/operator usage
  - Validation:
    - `.\.venv\Scripts\python .\scripts\run_behavior_validation.py --artifact-path artifacts/behavior_validation/prj347-report.json`
      (`6 passed`)
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py`
      (`140 passed`)

- [x] PRJ-346 Sync docs/context for relation-aware inferred promotion governance lane
  - Status: DONE
  - Group: Relation-Aware Inferred Promotion Governance
  - Owner: Product Docs
  - Depends on: PRJ-345
  - Priority: P1
  - Result:
    - architecture/runtime/planning/context docs now align on trust-aware
      inferred promotion gates and machine-visible diagnostics boundaries
    - next derived queue is now seeded for behavior-validation CI-ingestion
      follow-up (`PRJ-347..PRJ-350`)
  - Validation:
    - doc-and-context sync across `.codex/context/`, `docs/planning/`,
      `docs/architecture/`, and `docs/implementation/` with targeted
      cross-reference checks

- [x] PRJ-345 Add regressions for trust-aware inferred promotion gates and diagnostics
  - Status: DONE
  - Group: Relation-Aware Inferred Promotion Governance
  - Owner: QA/Test
  - Depends on: PRJ-344
  - Priority: P1
  - Result:
    - regression coverage now pins trust-aware inferred promotion behavior:
      low-trust threshold blocking, medium/high-trust promotion posture, and
      low-trust repeated-signal guardrails
    - diagnostics regressions now pin `reason=...` and `result=...` visibility
      across planning/runtime and API debug contract surfaces
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_reflection_worker.py`
      (`251 passed`)

- [x] PRJ-344 Add inferred-promotion gate diagnostics for planning and runtime debug surfaces
  - Status: DONE
  - Group: Relation-Aware Inferred Promotion Governance
  - Owner: Backend Builder
  - Depends on: PRJ-343
  - Priority: P1
  - Result:
    - planning now emits explicit inferred-promotion gate diagnostics
      (`reason=...`, `result=...`) for blocked and promoted inference paths
    - runtime/system-debug plan payload now surfaces
      `inferred_promotion_diagnostics` so trust-driven inference decisions are
      operator-visible in debug responses
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
      (`200 passed`)

- [x] PRJ-343 Add delivery-reliability-aware gates for inferred goal/task promotion
  - Status: DONE
  - Group: Relation-Aware Inferred Promotion Governance
  - Owner: Backend Builder
  - Depends on: PRJ-342
  - Priority: P1
  - Result:
    - inferred goal/task promotion thresholds now account for
      delivery-reliability posture (`low_trust|medium_trust|high_trust`)
      without weakening explicit user-declared intent handling
    - trust-aware gating now applies only to inferred promotion flow and keeps
      explicit user-declared goal/task intent extraction unchanged
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_adaptive_policy.py`
      (`145 passed`)

- [x] PRJ-342 Sync docs/context for manual runtime reliability fix lane
  - Status: DONE
  - Group: Manual Runtime Reliability Fixes
  - Owner: Product Docs
  - Depends on: PRJ-341
  - Priority: P1
  - Result:
    - planning docs, runbook guidance, and context truth now align for
      manual-runtime reliability fixes through `PRJ-342`
    - next derived queue is now seeded for relation-aware inferred promotion
      governance follow-up (`PRJ-343..PRJ-346`)
  - Validation:
    - doc-and-context sync across `.codex/context/`, `docs/planning/`, and
      `docs/operations/` with targeted cross-reference checks

- [x] PRJ-341 Add Telegram integration smoke workflow for webhook/listen mode switching
  - Status: DONE
  - Group: Manual Runtime Reliability Fixes
  - Owner: QA/Test
  - Depends on: PRJ-340
  - Priority: P1
  - Result:
    - operator-facing Telegram smoke helpers now validate both modes in one
      flow (`getWebhookInfo -> deleteWebhook -> getUpdates -> setWebhook`)
      across PowerShell and bash paths
    - runbook now includes explicit precondition checklist
      (`chat_id` availability, bot-start handshake, token/secret posture)
      to reduce false-negative delivery triage
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_event_normalization.py tests/test_delivery_router.py`
      (`83 passed`)
    - workspace execution did not include live Telegram API smoke because
      runtime bot credentials are not available in this environment; workflow
      scripts and runbook evidence checklist were added for operator execution.

- [x] PRJ-340 Expand goal/task signal detection beyond prefix-only phrasing
  - Status: DONE
  - Group: Manual Runtime Reliability Fixes
  - Owner: Backend Builder
  - Depends on: PRJ-339
  - Priority: P1
  - Result:
    - planning intent detection now supports deterministic inline command
      phrasing (for example `add goal ...`, `add task ...`, `dodaj cel ...`,
      `dodaj zadanie ...`) in addition to strict prefix forms
    - detection now keeps explicit false-positive guardrails for non-command
      mentions and preserves deterministic domain-intent extraction flow
      (`upsert_goal|upsert_task`)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_goal_task_signals.py`
      (`204 passed`)

- [x] PRJ-338 Harden Telegram delivery failure boundary to prevent 500 runtime crashes
  - Status: DONE
  - Group: Manual Runtime Reliability Fixes
  - Owner: Backend Builder
  - Depends on: PRJ-331
  - Priority: P0
  - Result:
    - Telegram delivery failures (`4xx/5xx`, transport errors, timeout) are
      now degraded at the integration boundary to controlled
      `ActionResult(status=fail)` responses, preventing uncaught action-stage
      exceptions from bubbling into runtime endpoint 500s.
    - runtime persistence and reflection follow-up remain deterministic on
      failed Telegram sends (`action=fail` persisted, reflection enqueue still
      evaluated) instead of short-circuiting on delivery exceptions.
    - debug-ingress API behavior now explicitly covers fail-action delivery
      posture so `/internal/event/debug` returns a structured fail response
      instead of crashing.
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_delivery_router.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
      (`160 passed`)
    - Negative debug-ingress boundary coverage is pinned in
      `tests/test_api_routes.py::test_internal_event_debug_endpoint_returns_fail_action_result_without_500`
      and `tests/test_runtime_pipeline.py::test_runtime_pipeline_degrades_telegram_delivery_exception_to_fail_action_result`.
    - App-lifespan manual smoke attempt through `POST /internal/event/debug`
      was blocked in this workspace by unresolved external DB host at startup;
      pitfall and guardrail were captured in `.codex/context/LEARNING_JOURNAL.md`.

- [x] PRJ-339 Enforce structured affective-classifier output parsing and fallback diagnostics
  - Status: DONE
  - Group: Manual Runtime Reliability Fixes
  - Owner: Backend Builder
  - Depends on: PRJ-338
  - Priority: P1
  - Result:
    - OpenAI affective classification now enforces a structured schema gate
      (required keys/types) and emits deterministic fallback diagnostics when
      parse/schema validation fails
    - fallback posture now remains explicit and traceable through structured
      fallback reason markers in affective evidence and runtime stage logs
      (`fallback_reason=...`) instead of silent classifier drift
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_affective_assessor.py tests/test_openai_client.py tests/test_affective_contract.py tests/test_expression_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
      (`165 passed`)

- [x] PRJ-331 Extend planning, motivation, and proactive logic with governed trust signals
  - Status: DONE
  - Group: Relation Lifecycle And Trust Influence
  - Owner: Backend Builder
  - Depends on: PRJ-330
  - Priority: P1
  - Result:
    - proactive trust governance now calibrates outreach behavior through
      delivery-reliability-aware interruption cost adjustments, relevance
      penalties/bonuses, and trust-shaped output-type posture for
      low-trust/high-trust paths
    - motivation now uses delivery-reliability tie-breaks on ambiguous turns
      (`high_trust -> execute`, `low_trust -> analyze`) without overriding
      explicit execution/analysis/emotional signals
    - planning now encodes explicit trust confidence posture steps
      (`plan_with_confident_next_step|plan_with_cautious_validation`) and
      trust-aware proactive outreach tone steps
      (`use_confident_outreach_tone|use_low_pressure_outreach_tone`)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_adaptive_policy.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`
      (`172 passed`)
    - `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
      (`247 passed`)

- [x] PRJ-332 Add relation lifecycle and trust-influence regressions
  - Status: DONE
  - Group: Relation Lifecycle And Trust Influence
  - Owner: QA/Test
  - Depends on: PRJ-331
  - Priority: P1
  - Result:
    - relation lifecycle regressions now pin value-shift reset behavior so
      evidence and decay posture restart when delivery trust changes state
    - trust-influence regressions now cover medium-trust derivation,
      low-confidence trust gating in proactive attention, and low-confidence
      support-intensity relation gating in expression tone selection
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_expression_agent.py`
      (`175 passed`)

- [x] PRJ-333 Sync docs/context for relation lifecycle and trust influence
  - Status: DONE
  - Group: Relation Lifecycle And Trust Influence
  - Owner: Product Docs
  - Depends on: PRJ-332
  - Priority: P1
  - Result:
    - docs, planning notes, and context truth now align on relation lifecycle
      behavior (refresh, value-shift reset, age-aware revalidation, expiration)
      and governed trust influence boundaries
    - relation rollout queue progression is synchronized so `PRJ-334` is the
      next executable slice for inferred planning growth
  - Validation:
    - doc-and-context sync plus targeted relation-lifecycle cross-doc review
      across `docs/overview.md`,
      `docs/implementation/runtime-reality.md`,
      `docs/planning/open-decisions.md`,
      `docs/planning/next-iteration-plan.md`,
      `.codex/context/TASK_BOARD.md`, and
      `.codex/context/PROJECT_STATE.md`

- [x] PRJ-334 Add inferred goal/task promotion rules to planning
  - Status: DONE
  - Group: Goal/Task Inference And Typed-Intent Expansion
  - Owner: Backend Builder
  - Depends on: PRJ-333
  - Priority: P1
  - Result:
    - planning now supports bounded inferred goal/task promotion from repeated
      blocker evidence when explicit declaration patterns are absent
    - inferred promotion is confidence-bounded (motivation/evidence gates),
      duplicate-aware against active state, and persisted through existing
      planning-owned typed domain intent flow
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_runtime_pipeline.py tests/test_memory_repository.py`
      (`167 passed`)

- [x] PRJ-335 Expand typed domain intents for inferred planning state and controlled maintenance writes
  - Status: DONE
  - Group: Goal/Task Inference And Typed-Intent Expansion
  - Owner: Backend Builder
  - Depends on: PRJ-334
  - Priority: P1
  - Result:
    - inferred planning promotion now uses explicit typed intents
      (`promote_inferred_goal`, `promote_inferred_task`) rather than
      reusing explicit user-declaration intent classes
    - repeated-blocker maintenance updates now stay behind explicit
      `maintain_task_status` intents, preserving action ownership for
      all durable inferred planning writes
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`
      (`150 passed`)

- [x] PRJ-336 Add regressions for inferred planning growth and no-duplicate/no-unsafe promotion behavior
  - Status: DONE
  - Group: Goal/Task Inference And Typed-Intent Expansion
  - Owner: QA/Test
  - Depends on: PRJ-335
  - Priority: P1
  - Result:
    - inferred planning growth now has explicit regression coverage for
      duplicate-avoidance and weak-evidence safety gates in planning and
      end-to-end runtime behavior
    - inference drift now fails fast when repeated blocker phrasing is weak,
      non-repeated, or already represented in active planning state
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_reflection_worker.py`
      (`202 passed`)

- [x] PRJ-337 Sync docs/context for goal/task inference and typed-intent expansion
  - Status: DONE
  - Group: Goal/Task Inference And Typed-Intent Expansion
  - Owner: Product Docs
  - Depends on: PRJ-336
  - Priority: P1
  - Result:
    - docs, planning notes, and context truth now align on bounded inferred
      planning growth, typed inferred/maintenance intents, and action ownership
      boundaries for durable state writes
    - queue progression is synchronized so manual runtime reliability fixes
      start from `PRJ-339`
  - Validation:
    - doc-and-context sync plus targeted planning-autonomy cross-doc review
      across `docs/architecture/16_agent_contracts.md`,
      `docs/implementation/runtime-reality.md`,
      `docs/planning/open-decisions.md`,
      `docs/planning/next-iteration-plan.md`,
      `.codex/context/TASK_BOARD.md`, and
      `.codex/context/PROJECT_STATE.md`

- [x] PRJ-330 Implement relation decay and confidence revalidation policy
  - Status: DONE
  - Group: Relation Lifecycle And Trust Influence
  - Owner: Backend Builder
  - Depends on: PRJ-329
  - Priority: P1
  - Result:
    - relation reads now apply age-aware confidence revalidation with
      evidence-sensitive decay, so stale relation signals weaken over time and
      expire from retrieval once confidence falls below expiration posture
    - relation upserts now refresh confidence and evidence through
      quality-weighted blending for repeated same-value signals, while
      value-shift updates reset relation posture for revalidation
    - reflection now persists relation-only updates (including
      `delivery_reliability=low_trust`) instead of treating those turns as noop
      when no conclusion/theta update is produced
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py`
      (`155 passed`)

- [x] PRJ-329 Sync docs/context for identity, language, and profile boundary hardening
  - Status: DONE
  - Group: Identity, Language, And Profile Boundary Hardening
  - Owner: Product Docs
  - Depends on: PRJ-328
  - Priority: P1
  - Result:
    - canonical docs, implementation reality, planning notes, and project
      context now describe the same identity continuity baseline
    - identity ownership boundaries are now explicit across docs:
      profile-language ownership in `aion_profile`, conclusion-owned
      response/collaboration preferences, and request-scoped API identity
      fallback precedence
  - Validation:
    - targeted identity-boundary cross-doc review recorded across
      `docs/overview.md`, `docs/implementation/runtime-reality.md`,
      `docs/planning/open-decisions.md`,
      `docs/planning/next-iteration-plan.md`,
      `.codex/context/TASK_BOARD.md`, and
      `.codex/context/PROJECT_STATE.md`

- [x] PRJ-328 Add identity and language continuity regressions across session and API fallback boundaries
  - Status: DONE
  - Group: Identity, Language, And Profile Boundary Hardening
  - Owner: QA/Test
  - Depends on: PRJ-327
  - Priority: P1
  - Result:
    - language continuity regressions now pin ambiguous-turn behavior for
      durable profile continuity across runtime session restarts
    - API fallback regressions now pin per-request user-id boundary semantics
      so header-based identity fallback does not leak across subsequent requests
      without explicit identity input
    - continuity drift between profile state and observable response language
      behavior is now test-visible across runtime and API boundaries
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_language_runtime.py tests/test_api_routes.py tests/test_runtime_pipeline.py`
      (`141 passed`)

- [x] PRJ-327 Add richer language continuity policy across profile, memory, and current turn context
  - Status: DONE
  - Group: Identity, Language, And Profile Boundary Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-326
  - Priority: P1
  - Result:
    - language decision logic now follows explicit precedence across
      current-turn signals, recent memory continuity, and durable profile
      preference signals
    - continuity heuristics now ingest structured episodic payload language
      hints (`payload.response_language`) and ignore unsupported language codes
      instead of inheriting arbitrary two-letter values
    - ambiguous follow-up tie-breaks now allow explicit durable profile
      preference to win against conflicting memory continuity without changing
      non-ambiguous turn behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_language_runtime.py tests/test_context_agent.py tests/test_expression_agent.py tests/test_runtime_pipeline.py`
      (`140 passed`)

- [x] PRJ-326 Refactor identity loading around explicit profile-versus-conclusion ownership
  - Status: DONE
  - Group: Identity, Language, And Profile Boundary Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-325
  - Priority: P1
  - Result:
    - runtime identity load now applies explicit owner boundaries:
      `aion_profile` remains the durable owner for profile language while
      identity response/collaboration preferences are conclusion-owned inputs
      only
    - relation fallback cues continue to support runtime planning/expression,
      but identity continuity no longer inherits relation-derived
      collaboration fallback as if it were a durable identity preference
    - runtime pipeline regression coverage now pins this owner boundary so
      profile-versus-conclusion identity continuity cannot silently drift
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_language_runtime.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
      (`136 passed`)

- [x] PRJ-325 Sync docs/context/runbook for scheduler externalization and attention ownership
  - Status: DONE
  - Group: Scheduler Externalization And Attention Ownership
  - Owner: Product Docs + Ops/Release
  - Depends on: PRJ-324
  - Priority: P1
  - Result:
    - canonical docs, implementation reality, planning notes, and ops runbook
      now align with owner-aware scheduler cadence posture
      (`SCHEDULER_EXECUTION_MODE`, cadence owner/readiness fields) and attention
      owner posture (`ATTENTION_COORDINATION_MODE`, deployment-readiness fields)
    - group handoff is explicit and queue progression is synchronized so
      identity/language hardening starts from `PRJ-326` without drift
  - Validation:
    - doc-and-context sync plus targeted scheduler/attention cross-doc review
      across `docs/overview.md`,
      `docs/architecture/26_env_and_config.md`,
      `docs/operations/runtime-ops-runbook.md`,
      `docs/implementation/runtime-reality.md`,
      `docs/planning/open-decisions.md`,
      `docs/planning/next-iteration-plan.md`,
      `.codex/context/TASK_BOARD.md`, and
      `.codex/context/PROJECT_STATE.md`

- [x] PRJ-324 Add attention-inbox ownership posture for future durable coordination rollout
  - Status: DONE
  - Group: Scheduler Externalization And Attention Ownership
  - Owner: Backend Builder
  - Depends on: PRJ-323
  - Priority: P1
  - Result:
    - attention coordination now exposes explicit owner posture
      (`in_process|durable_inbox`) with machine-visible ownership fields in
      `/health.attention`
    - attention boundary now has explicit deployment-readiness semantics and
      durable-owner blockers, creating a clean seam for future durable inbox
      rollout
    - in durable-owner posture, in-process turn assembly is explicitly bypassed
      so future durable coordination can replace local coalescing without
      hidden coupling
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py tests/test_scheduler_contracts.py tests/test_config.py`

- [x] PRJ-323 Route maintenance and proactive cadence through the shared owner-aware dispatch boundary
  - Status: DONE
  - Group: Scheduler Externalization And Attention Ownership
  - Owner: Backend Builder
  - Depends on: PRJ-322
  - Priority: P1
  - Result:
    - maintenance/proactive cadence now use shared owner-aware dispatch
      decisions (`in_process_owner_mode|externalized_owner_mode`) instead of
      reflection-only ownership assumptions
    - scheduler maintenance execution now honors cadence ownership mode and
      explicitly no-ops under externalized ownership posture
    - scheduler health/snapshot posture now exposes cadence dispatch reasons for
      maintenance and proactive paths
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_runtime_pipeline.py tests/test_action_executor.py tests/test_api_routes.py`

- [x] PRJ-322 Implement owner-aware scheduler execution mode and health snapshot
  - Status: DONE
  - Group: Scheduler Externalization And Attention Ownership
  - Owner: Backend Builder + Ops/Release
  - Depends on: PRJ-321
  - Priority: P1
  - Result:
    - scheduler/runtime now expose explicit cadence execution mode
      (`in_process|externalized`) through shared scheduler contracts and health
      snapshot posture
    - `/health.scheduler` now exposes explicit maintenance/proactive cadence
      owner signals (`in_process_scheduler|external_scheduler`) plus
      readiness/blocker posture so operators no longer infer ownership from
      scattered runtime flags
    - scheduler worker snapshot now carries owner-aware cadence execution
      posture (`execution_mode`, `configured_enabled`, proactive posture, and
      readiness signals)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_contracts.py tests/test_scheduler_worker.py tests/test_api_routes.py tests/test_config.py`

- [x] PRJ-321 Sync docs/context/runbook for internal debug ingress migration
  - Status: DONE
  - Group: Internal Debug Ingress Migration
  - Owner: Product Docs + Ops/Release
  - Depends on: PRJ-320
  - Priority: P1
  - Result:
    - canonical docs, planning, and runbook now align on primary internal
      debug ingress (`POST /internal/event/debug`) plus transitional shared
      posture (`POST /event/debug`)
    - architecture, operations, and planning docs now include shared
      break-glass posture controls and updated compatibility-header migration
      semantics
    - planning pointer is synchronized so next execution slice starts from
      `PRJ-322` without queue drift
  - Validation:
    - doc-and-context sync plus targeted debug-ingress cross-doc review recorded in this slice

- [x] PRJ-320 Add debug-ingress migration regressions and smoke coverage
  - Status: DONE
  - Group: Internal Debug Ingress Migration
  - Owner: QA/Test + Ops/Release
  - Depends on: PRJ-319
  - Priority: P1
  - Result:
    - API regressions now pin shared-ingress break-glass posture and health
      migration visibility in addition to internal-ingress ownership
    - release smoke scripts now fail fast when internal/shared debug-ingress
      path or break-glass posture contracts drift from runtime policy baseline
  - Validation:
    - `.\scripts\run_release_smoke.ps1` (not run in this slice: no live target URL in this environment)
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py`

- [x] PRJ-319 Add break-glass override and shared-endpoint sunset posture for debug access
  - Status: DONE
  - Group: Internal Debug Ingress Migration
  - Owner: Backend Builder
  - Depends on: PRJ-318
  - Priority: P1
  - Result:
    - shared endpoint `POST /event/debug` now supports explicit posture modes
      (`compatibility|break_glass_only`) and enforces break-glass override
      header in break-glass-only mode
    - runtime policy now exposes shared-ingress break-glass posture fields
      (`event_debug_shared_ingress_mode`,
      `event_debug_shared_ingress_break_glass_required`,
      `event_debug_shared_ingress_posture`) for release visibility
    - API/config/runtime-policy regression coverage now pins shared-ingress
      break-glass behavior and runtime posture signals
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`

- [x] PRJ-318 Implement a dedicated internal debug ingress boundary and shared guard path
  - Status: DONE
  - Group: Internal Debug Ingress Migration
  - Owner: Backend Builder
  - Depends on: PRJ-317
  - Priority: P1
  - Result:
    - runtime now exposes `POST /internal/event/debug` as the explicit primary
      internal debug ingress that owns `system_debug` access semantics
    - shared `POST /event/debug` now acts as compatibility ingress with
      migration headers, while `POST /event?debug=true` compatibility headers
      point to the internal ingress path
    - runtime policy snapshot now surfaces explicit debug-ingress ownership and
      path posture fields for operator visibility
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py`

- [x] PRJ-317 Make runtime behavior validation part of release-readiness and sync docs/context/runbook
  - Status: DONE
  - Group: Memory, Continuity, And Failure Validation
  - Owner: Product Docs + Ops/Release + QA/Test
  - Depends on: PRJ-316
  - Priority: P1
  - Result:
    - release readiness now includes behavior-validation evidence through
      `scripts/run_behavior_validation.{ps1,sh}` plus full regression checks
    - runbook, planning, and project state are synchronized with the
      living-system validation baseline
  - Validation:
    - `.\scripts\run_behavior_validation.ps1`
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-316 Add contradiction, missing-data, and noisy-input behavior scenarios
  - Status: DONE
  - Group: Memory, Continuity, And Failure Validation
  - Owner: QA/Test + Backend Builder
  - Depends on: PRJ-315
  - Priority: P1
  - Result:
    - failure-mode scenarios now validate contradiction, missing-data, and
      noisy-input handling through structured behavior-harness outputs
    - fallback quality is now explicitly regression-covered
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_motivation_engine.py tests/test_expression_agent.py`

- [x] PRJ-315 Add multi-session continuity and personality-stability simulation scenarios
  - Status: DONE
  - Group: Memory, Continuity, And Failure Validation
  - Owner: QA/Test
  - Depends on: PRJ-314
  - Priority: P1
  - Result:
    - continuity scenarios now pin identity/tone/language stability across
      session restart boundaries
    - context reuse across turns is now behavior-tested through scenario output
      contract
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_expression_agent.py tests/test_planning_agent.py tests/test_language_runtime.py`

- [x] PRJ-314 Add memory behavior scenarios for write, retrieval, influence, and delayed recall
  - Status: DONE
  - Group: Memory, Continuity, And Failure Validation
  - Owner: QA/Test + Backend Builder
  - Depends on: PRJ-313
  - Priority: P1
  - Result:
    - memory scenarios now pin `write -> retrieve -> influence -> delayed
      recall` through repeatable harness execution
    - memory cannot be considered complete when retrieval does not influence
      later context behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_memory_repository.py tests/test_api_routes.py`

- [x] PRJ-313 Sync docs/context for runtime behavior testing architecture and internal validation contract
  - Status: DONE
  - Group: Runtime Behavior Testing Architecture
  - Owner: Product Docs + QA/Test
  - Depends on: PRJ-312
  - Priority: P1
  - Result:
    - canonical docs, engineering guidance, and context now align around one
      behavior-validation baseline
    - open decisions now record runtime behavior-validation posture as resolved
      baseline
  - Validation:
    - doc-and-context sync plus targeted cross-doc consistency review recorded
      in this slice

- [x] PRJ-312 Add structured behavior-harness output and scenario execution helpers
  - Status: DONE
  - Group: Runtime Behavior Testing Architecture
  - Owner: QA/Test
  - Depends on: PRJ-311
  - Priority: P1
  - Result:
    - behavior-harness helpers now provide structured scenario result contract
      (`test_id/status/reason/trace_id/notes`)
    - dedicated behavior-validation scripts now make scenario execution
      repeatable across local/release workflows
  - Validation:
    - `.\scripts\run_behavior_validation.ps1`
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py tests/test_scheduler_contracts.py`

- [x] PRJ-311 Implement the internal system-debug validation surface for behavior checks
  - Status: DONE
  - Group: Runtime Behavior Testing Architecture
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-310
  - Priority: P1
  - Result:
    - internal debug responses now expose canonical `system_debug` fields for
      event normalization, memory bundle, context, motivation, role, plan
      intents, expression, and action traces
    - behavior debugging no longer depends on scattered endpoint payloads
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_pipeline.py tests/test_logging.py`

- [x] PRJ-310 Define the canonical runtime behavior testing contract and required system-debug surface
  - Status: DONE
  - Group: Runtime Behavior Testing Architecture
  - Owner: Planner + QA/Test
  - Depends on: PRJ-309
  - Priority: P1
  - Result:
    - architecture now explicitly defines required behavior-validation modes
      (`system_debug`, `user_simulation`) and minimum internal debug fields
    - future cognitive slices can use one shared behavior contract baseline
  - Validation:
    - doc-and-context sync plus targeted behavior-testing architecture review
      recorded in this slice

- [x] PRJ-309 Sync docs/context/runbook for post-reflection hardening queue decisions
  - Status: DONE
  - Group: Post-Reflection Hardening Queue
  - Owner: Product Docs + Ops/Release
  - Depends on: PRJ-308
  - Priority: P1
  - Result:
    - planning, project state, and ops runbook remain synchronized after
      post-reflection decision closure slices
    - release-readiness and runtime-governance docs stay aligned with the next
      hardening lane
  - Validation:
    - doc-and-context sync plus targeted cross-doc consistency review recorded
      in this slice

- [x] PRJ-308 Define long-term scheduler externalization boundary for maintenance/proactive cadence ownership
  - Status: DONE
  - Group: Post-Reflection Hardening Queue
  - Owner: Planner + Ops/Release
  - Depends on: PRJ-307
  - Priority: P1
  - Result:
    - scheduler/proactive follow-up now has one explicit target posture for
      app-local vs external cadence ownership after reflection rollout
    - later implementation slices can converge on one cadence owner model
      instead of reopening decision `12` every cycle
  - Validation:
    - doc-and-context sync plus targeted scheduler-boundary review recorded in
      this slice

- [x] PRJ-307 Define target internal debug ingress boundary and migration posture away from shared public API service endpoint
  - Status: DONE
  - Group: Post-Reflection Hardening Queue
  - Owner: Planner + Product Docs
  - Depends on: PRJ-306
  - Priority: P1
  - Result:
    - public-api follow-up decision now has explicit target-state ingress
      contract and migration ownership boundaries
    - debug-surface hardening can proceed without redefining runtime-policy
      baselines each slice
  - Validation:
    - doc-and-context sync plus targeted public-api boundary review recorded in
      this slice

- [x] PRJ-306 Define criteria and migration guardrails for removing `create_tables` compatibility startup path
  - Status: DONE
  - Group: Post-Reflection Hardening Queue
  - Owner: Planner + Ops/Release
  - Depends on: PRJ-305
  - Priority: P1
  - Result:
    - migration-strategy follow-up now has explicit guardrails and removal
      criteria for retiring `create_tables` compatibility startup path
    - removal rollout order is codified to keep future implementation slices
      reversible and auditable
  - Validation:
    - doc-and-context sync plus targeted migration-strategy review recorded in
      this slice

- [x] PRJ-305 Derive and record the next execution queue after reflection lane closure
  - Status: DONE
  - Group: Post-Reflection Planning Baseline
  - Owner: Planner + Product Docs
  - Depends on: PRJ-304
  - Priority: P1
  - Result:
    - post-reflection hardening queue is now seeded through `PRJ-309` from
      remaining open decisions
    - execution continuity is preserved after `PRJ-304` without ad-hoc queue
      selection
  - Validation:
    - doc-and-context sync plus targeted planning coherence review recorded in
      this slice

- [x] PRJ-304 Sync docs/context/runbook for reflection deployment baseline and readiness contract
  - Status: DONE
  - Group: Reflection Deployment Baseline
  - Owner: Product Docs + Ops/Release
  - Depends on: PRJ-303
  - Priority: P1
  - Result:
    - planning, project state, and runbook truth are now synchronized after the
      post-convergence reflection implementation slices
    - release and rollback guidance now consistently include the reflection
      readiness gate
  - Validation:
    - doc-and-context sync plus targeted ops-runbook review recorded in this
      slice

- [x] PRJ-303 Add reflection deployment-readiness regressions and smoke script alignment
  - Status: DONE
  - Group: Reflection Deployment Baseline
  - Owner: Backend Builder + Ops/Release
  - Depends on: PRJ-302
  - Priority: P1
  - Result:
    - regression coverage now pins reflection deployment-readiness blocker
      signals in shared scheduler contracts and `/health` integration paths
    - release smoke scripts now fail fast on reflection deployment-readiness
      blockers with explicit fallback checks for older runtimes
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_reflection_worker.py tests/test_scheduler_worker.py tests/test_scheduler_contracts.py`

- [x] PRJ-302 Add explicit `/health.reflection` deployment-readiness summary for chosen runtime-mode baseline
  - Status: DONE
  - Group: Reflection Deployment Baseline
  - Owner: Backend Builder + Ops/Release
  - Depends on: PRJ-301
  - Priority: P1
  - Result:
    - `/health.reflection` now exposes deployment-readiness posture
      (`ready`, `blocking_signals`, baseline/selected runtime mode)
    - reflection-mode migration can now be verified through health contract
      signals instead of log-only interpretation
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_scheduler_contracts.py tests/test_scheduler_worker.py tests/test_reflection_worker.py`

- [x] PRJ-301 Define production reflection runtime-mode deployment baseline and external-dispatch readiness criteria
  - Status: DONE
  - Group: Reflection Deployment Baseline
  - Owner: Planner + Ops/Release
  - Depends on: PRJ-300
  - Priority: P1
  - Result:
    - production baseline now keeps `REFLECTION_RUNTIME_MODE=in_process` as
      default posture
    - deferred reflection dispatch now has explicit rollout-readiness criteria
      instead of implicit operator judgment
  - Validation:
    - doc-and-context sync plus targeted reflection-topology contract review
      recorded in this slice

- [x] PRJ-300 Derive and record the first post-convergence execution queue
  - Status: DONE
  - Group: Post-Convergence Planning Baseline
  - Owner: Planner + Product Docs
  - Depends on: PRJ-299
  - Priority: P1
  - Result:
    - first post-convergence execution queue is now seeded through `PRJ-304`
      from remaining open decisions and reflected in planning docs plus task
      board state
    - execution does not stall after `PRJ-299` because the next lane is
      explicitly scoped into small reversible slices
  - Validation:
    - doc-and-context sync plus targeted planning coherence review recorded in
      this slice

- [x] PRJ-299 Add release-readiness regressions and sync docs/context/runbook
  - Status: DONE
  - Group: Operational Hardening And Release Truth
  - Owner: QA/Test + Product Docs + Ops/Release
  - Depends on: PRJ-298
  - Priority: P1
  - Result:
    - `/health` now exposes release-readiness gate posture and smoke scripts
      fail fast on production-policy drift
    - release-readiness regressions and operational docs now match the
      target-state production baseline
    - planning, project state, and runbook truth remain synchronized at the
      end of the convergence queue
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-298 Finalize deployment and release truth for Coolify/manual fallback and smoke ownership
  - Status: DONE
  - Group: Operational Hardening And Release Truth
  - Owner: Ops/Release
  - Depends on: PRJ-297
  - Priority: P1
  - Result:
    - deployment automation, manual fallback, and release smoke ownership are
      documented as one coherent operational path
    - execution work stops assuming deploy behavior that operations cannot yet
      prove
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-297 Enforce migration-first and internal-debug posture through explicit runtime gates
  - Status: DONE
  - Group: Operational Hardening And Release Truth
  - Owner: Backend Builder
  - Depends on: PRJ-296
  - Priority: P1
  - Result:
    - runtime and config boundaries reflect the agreed production target while
      keeping any temporary escape hatches explicit and reviewable
    - startup and API policy posture move closer to the final deployment shape
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_api_routes.py tests/test_main_lifespan_policy.py`

- [x] PRJ-296 Define the target production posture for migration-only startup, strict defaults, and the internal debug boundary
  - Status: DONE
  - Group: Operational Hardening And Release Truth
  - Owner: Planner + Ops/Release
  - Depends on: PRJ-295
  - Priority: P1
  - Result:
    - one target production baseline defines migration-only startup posture,
      strict policy defaults, and the intended internal-versus-public debug
      boundary
    - later hardening slices can remove temporary rollout ambiguity instead of
      creating more diagnostic layers
  - Validation:
    - doc-and-context sync plus targeted production-baseline review recorded in
      this slice

- [x] PRJ-295 Add dual-loop execution-boundary regressions and sync docs/context
  - Status: DONE
  - Group: Attention And Proposal Execution Boundary
  - Owner: QA/Test + Product Docs
  - Depends on: PRJ-294
  - Priority: P1
  - Result:
    - turn assembly, proposal handoff, proactive delivery, and permission-gated
      external intent flows are pinned end to end
    - docs and context now describe one coherent dual-loop execution model
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_reflection_worker.py tests/test_action_executor.py tests/test_planning_agent.py`

- [x] PRJ-294 Route proactive outreach and connector permission gates through the shared attention/proposal boundary
  - Status: DONE
  - Group: Attention And Proposal Execution Boundary
  - Owner: Backend Builder
  - Depends on: PRJ-293
  - Priority: P1
  - Result:
    - proactive delivery and external-connector permission outcomes now share
      one conscious execution boundary
    - connector suggestions and outreach plans stop bypassing the same gating
      model used for batched conversation handling
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_planning_agent.py tests/test_api_routes.py tests/test_runtime_pipeline.py`

- [x] PRJ-293 Implement end-to-end proposal persistence and conscious handoff decisions
  - Status: DONE
  - Group: Attention And Proposal Execution Boundary
  - Owner: Backend Builder
  - Depends on: PRJ-292
  - Priority: P1
  - Result:
    - subconscious proposals can persist durably and re-enter conscious runtime
      through explicit handoff decisions
    - user-visible actions remain blocked until conscious runtime accepts or
      merges a proposal
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_memory_repository.py tests/test_runtime_pipeline.py tests/test_planning_agent.py`

- [x] PRJ-292 Define a durable proposal lifecycle and canonical turn-assembly ownership contract
  - Status: DONE
  - Group: Attention And Proposal Execution Boundary
  - Owner: Planner
  - Depends on: PRJ-291
  - Priority: P1
  - Result:
    - proposal persistence, handoff decisions, and pending-turn ownership have
      one explicit contract owner
    - future dual-loop changes no longer need to infer whether attention or
      planning owns a boundary
  - Validation:
    - doc-and-context sync plus targeted dual-loop contract review recorded in
      this slice

- [x] PRJ-291 Add adaptive-governance regressions and sync docs/context
  - Status: DONE
  - Group: Adaptive Cognition Governance
  - Owner: QA/Test + Product Docs
  - Depends on: PRJ-290
  - Priority: P1
  - Result:
    - anti-feedback-loop, cross-goal-leakage, and adaptive influence scope
      expectations are pinned by regression coverage
    - docs and context describe the same adaptive governance rules
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_role_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`

- [x] PRJ-288 Define evidence thresholds and influence policy for adaptive signals
  - Status: DONE
  - Group: Adaptive Cognition Governance
  - Owner: Planner
  - Depends on: PRJ-287
  - Priority: P1
  - Result:
    - canonical contracts now define one explicit adaptive influence policy for
      affective, relation, preference, and theta signals
    - adaptive influence now has documented evidence gates, precedence, and
      tie-break boundaries instead of undocumented expansion
  - Validation:
    - doc-and-context sync plus targeted adaptive-policy review recorded in
      this slice
    - `.\.venv\Scripts\python -m pytest -q tests/test_role_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`

- [x] PRJ-287 Add production retrieval rollout regressions and sync docs/context
  - Status: DONE
  - Group: Production Memory Retrieval Rollout
  - Owner: QA/Test + Product Docs
  - Depends on: PRJ-286
  - Priority: P1
  - Result:
    - production retrieval diagnostics are now regression-pinned for hybrid
      query defaults in runtime integration tests and rollout posture in health
      contract tests
    - planning, project state, runtime-reality, and open-decisions docs are
      synchronized to the rollout state after semantic+affective+relation
      source-family enablement support
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_context_agent.py tests/test_runtime_pipeline.py`

- [x] PRJ-286 Extend vector rollout to affective and relation families with explicit gating
  - Status: DONE
  - Group: Production Memory Retrieval Rollout
  - Owner: Backend Builder
  - Depends on: PRJ-285
  - Priority: P1
  - Result:
    - affective conclusion embeddings now materialize vectors with explicit
      refresh ownership metadata (`materialized_on_write` vs
      `pending_manual_refresh`) under source-family gates
    - relation embedding writes are now source-gated and materialize vectors
      with the same refresh ownership contract when `relation` rollout is
      enabled
    - hybrid retrieval vector queries now include relation source family so
      rollout can progress from semantic baseline toward full source coverage
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py`
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_memory_repository.py tests/test_context_agent.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- [x] PRJ-285 Implement the provider-owned semantic and episodic vector materialization path
  - Status: DONE
  - Group: Production Memory Retrieval Rollout
  - Owner: Backend Builder
  - Depends on: PRJ-284
  - Priority: P1
  - Result:
    - semantic conclusion embeddings now materialize vectors on write when
      refresh ownership is `on_write`, including deterministic fallback when
      non-implemented providers are requested
    - episodic embedding writes now explicitly honor refresh ownership
      (`materialized_on_write` vs `pending_manual_refresh`) with provider/model
      fallback metadata for retrieval diagnostics
    - retrieval no longer treats semantic embeddings as primarily diagnostic
      shells during the baseline rollout
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_memory_repository.py`
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_memory_repository.py tests/test_context_agent.py tests/test_runtime_pipeline.py`

- [x] PRJ-284 Define the production retrieval baseline for provider, refresh ownership, and family rollout order
  - Status: DONE
  - Group: Production Memory Retrieval Rollout
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-283
  - Priority: P1
  - Result:
    - one target production baseline now defines provider ownership, refresh
      ownership, default vector posture, and family rollout order
      (`episodic+semantic -> affective -> relation`)
    - retrieval implementation slices can now converge on one stable baseline
      instead of reopening rollout strategy each cycle
  - Validation:
    - doc-and-context sync plus targeted retrieval-baseline review recorded
      across `docs/planning/open-decisions.md`,
      `docs/architecture/26_env_and_config.md`,
      `docs/implementation/runtime-reality.md`, and
      `docs/operations/runtime-ops-runbook.md`

- [x] PRJ-283 Add background-topology regressions and sync docs/context
  - Status: DONE
  - Group: Background Reflection Topology
  - Owner: QA/Test + Product Docs
  - Depends on: PRJ-282
  - Priority: P1
  - Result:
    - regression coverage now pins worker-mode handoff behavior in
      `in_process|deferred` operation across reflection retry posture,
      scheduler runtime logs, and `/health.reflection.topology`
    - planning, project state, and runtime-ops docs are synchronized to the
      converged background-topology contract through `PRJ-283`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_scheduler_worker.py tests/test_api_routes.py tests/test_main_lifespan_policy.py`

- [x] PRJ-282 Add worker-mode health, queue-drain, and retry handoff contract
  - Status: DONE
  - Group: Background Reflection Topology
  - Owner: Backend Builder + Ops/Release
  - Depends on: PRJ-281
  - Priority: P1
  - Result:
    - `/health.reflection.topology` now exposes explicit handoff posture for
      in-process and deferred operation (`queue_drain_owner`,
      `external_driver_expected`, enqueue/scheduler dispatch decisions, and
      retry ownership metadata)
    - scheduler reflection tick logs now emit mode-aware handoff fields so
      queue-drain/retry ownership remains observable when external dispatch is
      expected
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_api_routes.py tests/test_scheduler_worker.py tests/test_logging.py`
    - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_contracts.py`

- [x] PRJ-281 Extract the reflection enqueue/dispatch boundary from app-local scheduler ownership
  - Status: DONE
  - Group: Background Reflection Topology
  - Owner: Backend Builder
  - Depends on: PRJ-280
  - Priority: P1
  - Result:
    - runtime and scheduler now consume one shared reflection dispatch-boundary
      contract (`reflection_enqueue_dispatch_decision` and
      `reflection_scheduler_dispatch_decision`) instead of duplicating
      mode/worker ownership rules
    - runtime enqueue behavior now keeps durable enqueue ownership while
      dispatch intent is explicitly mode-aware (`in_process|deferred`) even when
      a reflection worker instance is attached
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_scheduler_worker.py tests/test_runtime_pipeline.py tests/test_main_lifespan_policy.py`
    - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_contracts.py`

- [x] PRJ-280 Define target-state reflection topology and worker-mode contract
  - Status: DONE
  - Group: Background Reflection Topology
  - Owner: Planner + Ops/Release
  - Depends on: PRJ-279
  - Priority: P1
  - Result:
    - canonical contracts now define reflection topology ownership across
      `in_process|deferred` runtime modes, durable queue semantics, and
      mode-independent enqueue ownership
    - runtime-reality and ops docs now describe operator-visible posture and
      topology invariants without redefining architecture
  - Validation:
    - doc-and-context sync completed; targeted topology review recorded across
      `docs/architecture/15_runtime_flow.md`,
      `docs/architecture/16_agent_contracts.md`,
      `docs/implementation/runtime-reality.md`, and
      `docs/operations/runtime-ops-runbook.md`

- [x] PRJ-279 Add foreground architecture-parity regressions and sync docs/context
  - Status: DONE
  - Group: Foreground Runtime Convergence
  - Owner: QA/Test + Product Docs
  - Depends on: PRJ-278
  - Priority: P1
  - Result:
    - architecture-parity regressions now pin foreground boundary ordering in
      runtime, API debug payload, and logging test surfaces
    - docs, planning, and context are synchronized to the converged foreground
      ownership boundary through `PRJ-279`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_logging.py tests/test_graph_state_contract.py`

- [x] PRJ-278 Align graph/runtime orchestration boundaries for baseline load, memory write, and reflection trigger
  - Status: DONE
  - Group: Foreground Runtime Convergence
  - Owner: Backend Builder
  - Depends on: PRJ-277
  - Priority: P1
  - Result:
    - runtime now exposes explicit pre-graph seed ownership, graph-stage
      execution boundary, and post-graph follow-up ownership in
      `RuntimeOrchestrator`
    - foreground flow keeps target-state traceability without breaking the
      action boundary
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_graph_state_contract.py tests/test_graph_stage_adapters.py tests/test_main_lifespan_policy.py`

- [x] PRJ-277 Introduce an explicit response-execution contract for expression-to-action handoff
  - Status: DONE
  - Group: Foreground Runtime Convergence
  - Owner: Backend Builder
  - Depends on: PRJ-276
  - Priority: P1
  - Result:
    - expression now emits explicit response-execution handoff data consumed by
      action as the execution contract boundary
    - action execution no longer depends on implicit expression coupling for
      delivery preparation
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_expression_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_graph_stage_adapters.py tests/test_graph_state_contract.py`

- [x] PRJ-276 Define target-state foreground ownership and graph boundary invariants
  - Status: DONE
  - Group: Foreground Runtime Convergence
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-275
  - Priority: P1
  - Result:
    - target-state ownership is now explicit for graph-owned versus
      runtime-owned foreground segments (`baseline load`, stage graph,
      episodic memory write, reflection trigger)
    - canonical contracts now include migration invariants that keep stage
      output keys, ordering, and side-effect ownership stable during
      orchestration convergence
  - Validation:
    - doc-and-context sync completed; targeted contract diff review recorded
      across `docs/architecture/15_runtime_flow.md`,
      `docs/architecture/16_agent_contracts.md`, and
      `docs/implementation/runtime-reality.md`

- [x] PRJ-275 Sync source-rollout enforcement recommendation/alignment slice across docs, planning, and context
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement Alignment
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-274
  - Priority: P2
  - Result:
    - task board, project state, iteration plan, and open-decisions docs are
      synchronized through `PRJ-275`
    - canonical env/config and runtime ops docs now include source-rollout
      enforcement recommendation/alignment diagnostics
    - runtime reality docs now record startup source-rollout enforcement hint
      posture and shared alignment ownership
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_config.py`
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-274 Add startup regression coverage for source-rollout enforcement recommendation/alignment hints
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement Alignment
  - Owner: QA/Test
  - Depends on: PRJ-273
  - Priority: P2
  - Result:
    - startup log regressions now pin `embedding_source_rollout_enforcement_hint`
      posture for aligned and below-recommendation scenarios
    - warning/block log regressions now pin recommendation and alignment fields
      for warn and strict startup paths
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py`

- [x] PRJ-273 Expand `/health.memory_retrieval` contract regressions for source-rollout enforcement recommendation/alignment fields
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement Alignment
  - Owner: QA/Test
  - Depends on: PRJ-272
  - Priority: P2
  - Result:
    - API health contract tests now pin source-rollout enforcement recommendation
      and alignment fields across vectors-disabled, pending-rollout, strict
      blocked, and rollout-complete states
    - `/health` regression coverage now includes aligned strict posture once
      rollout is complete
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-272 Add shared snapshot regression coverage for source-rollout enforcement recommendation/alignment diagnostics
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement Alignment
  - Owner: QA/Test
  - Depends on: PRJ-271
  - Priority: P2
  - Result:
    - embedding strategy unit regressions now pin recommendation/alignment
      semantics for vectors-disabled, pending-rollout, rollout-complete, strict
      blocked, and strict aligned states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py`

- [x] PRJ-271 Add startup source-rollout enforcement alignment hint logs from shared diagnostics
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement Alignment
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-270
  - Priority: P2
  - Result:
    - startup now emits `embedding_source_rollout_enforcement_hint` with current
      enforcement, recommendation, alignment, and rollout completion context
    - hint log posture is shared across aligned, below-recommendation, and
      above-recommendation scenarios
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_embedding_strategy.py`

- [x] PRJ-270 Enrich startup source-rollout enforcement warning/block logs with recommendation/alignment diagnostics
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement Alignment
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-269
  - Priority: P2
  - Result:
    - `embedding_source_rollout_warning` now includes recommended enforcement and
      alignment diagnostics from shared snapshot ownership
    - `embedding_source_rollout_block` now includes recommendation/alignment
      diagnostics for strict pending-rollout fail-fast posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py`

- [x] PRJ-269 Expose source-rollout enforcement recommendation/alignment diagnostics through `/health.memory_retrieval`
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement Alignment
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-268
  - Priority: P2
  - Result:
    - `/health.memory_retrieval` now surfaces source-rollout enforcement
      recommendation/alignment fields
      (`semantic_embedding_recommended_source_rollout_enforcement`,
      `semantic_embedding_source_rollout_enforcement_alignment`,
      `semantic_embedding_source_rollout_enforcement_alignment_state`,
      `semantic_embedding_source_rollout_enforcement_alignment_hint`)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_embedding_strategy.py`

- [x] PRJ-268 Add source-rollout enforcement alignment state/hint diagnostics in shared embedding strategy snapshot
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement Alignment
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-267
  - Priority: P2
  - Result:
    - shared snapshot now exposes source-rollout enforcement alignment state/hint
      (`semantic_embedding_source_rollout_enforcement_alignment_state`,
      `semantic_embedding_source_rollout_enforcement_alignment_hint`)
    - alignment state semantics now distinguish aligned, below-recommendation,
      above-recommendation, and vectors-disabled posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py`

- [x] PRJ-267 Add source-rollout enforcement alignment primitive diagnostics in shared embedding strategy snapshot
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement Alignment
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-266
  - Priority: P2
  - Result:
    - shared snapshot now exposes source-rollout enforcement alignment primitive
      (`semantic_embedding_source_rollout_enforcement_alignment`) against
      rollout-aware recommendation posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py`

- [x] PRJ-266 Add source-rollout enforcement recommendation diagnostics in shared embedding strategy snapshot
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement Alignment
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-265
  - Priority: P2
  - Result:
    - shared snapshot now exposes rollout-aware source-rollout enforcement
      recommendation (`semantic_embedding_recommended_source_rollout_enforcement`)
      with `warn` while rollout is pending and `strict` when rollout is complete
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py`

- [x] PRJ-265 Sync embedding source-rollout enforcement slice across docs, planning, and context
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-264
  - Priority: P2
  - Result:
    - task board, project state, iteration plan, and open-decisions docs are
      synchronized through `PRJ-265`
    - canonical env/config and runtime ops docs now include source-rollout
      enforcement controls and diagnostics
    - runtime reality docs now record startup source-rollout enforcement
      warning/block posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_config.py`
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-264 Add startup source-rollout enforcement warning/block logs from shared diagnostics
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-263
  - Priority: P2
  - Result:
    - startup now emits `embedding_source_rollout_warning` when rollout is
      pending and enforcement stays in `warn`
    - startup now emits `embedding_source_rollout_block` and fails fast when
      rollout is pending and `EMBEDDING_SOURCE_ROLLOUT_ENFORCEMENT=strict`
    - runtime policy regressions now pin both warn-mode visibility and strict
      startup block behavior for pending rollout posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_embedding_strategy.py`

- [x] PRJ-263 Expose source-rollout enforcement diagnostics through `/health.memory_retrieval`
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-262
  - Priority: P2
  - Result:
    - `/health.memory_retrieval` now surfaces source-rollout enforcement fields
      (`semantic_embedding_source_rollout_enforcement`,
      `semantic_embedding_source_rollout_enforcement_state`,
      `semantic_embedding_source_rollout_enforcement_hint`)
    - health contract regressions now pin vectors-disabled, pending-rollout,
      and fully-enabled rollout enforcement posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_embedding_strategy.py`

- [x] PRJ-262 Add source-rollout enforcement diagnostics in shared embedding strategy snapshot
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-261
  - Priority: P2
  - Result:
    - shared embedding strategy snapshot now exposes source-rollout enforcement
      diagnostics
      (`semantic_embedding_source_rollout_enforcement`,
      `semantic_embedding_source_rollout_enforcement_state`,
      `semantic_embedding_source_rollout_enforcement_hint`)
    - rollout enforcement posture is now machine-readable for vectors-disabled,
      pending-rollout, and fully-enabled rollout states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py`

- [x] PRJ-261 Add source-rollout enforcement runtime setting contract
  - Status: DONE
  - Group: Embedding Source Rollout Enforcement
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-260
  - Priority: P2
  - Result:
    - runtime settings now expose
      `EMBEDDING_SOURCE_ROLLOUT_ENFORCEMENT` (`warn|strict`) with `warn`
      default
    - config regressions now pin defaults, strict mode acceptance, and invalid
      mode rejection
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py`

- [x] PRJ-260 Sync embedding refresh-strategy guidance slice across docs, planning, and context
  - Status: DONE
  - Group: Embedding Refresh Strategy Guidance
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-259
  - Priority: P2
  - Result:
    - task board, project state, iteration plan, and open-decisions docs are
      synchronized through `PRJ-260`
    - canonical env/config and runtime ops docs now include refresh
      cadence/recommendation/alignment diagnostics
    - runtime reality docs now record startup refresh-hint posture and shared
      refresh strategy ownership
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-259 Add startup refresh-strategy hint logs from shared diagnostics
  - Status: DONE
  - Group: Embedding Refresh Strategy Guidance
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-258
  - Priority: P2
  - Result:
    - startup refresh warning logs now include cadence diagnostics for manual
      posture visibility
    - startup now emits `embedding_refresh_hint` when refresh mode is not
      aligned with rollout recommendation posture
    - runtime log regressions now pin manual-override and
      on-write-before-manual-recommendation hint paths
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_embedding_strategy.py`

- [x] PRJ-258 Add refresh recommendation-alignment diagnostics in shared embedding strategy snapshot
  - Status: DONE
  - Group: Embedding Refresh Strategy Guidance
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-257
  - Priority: P2
  - Result:
    - shared embedding strategy snapshot now exposes refresh alignment posture
      (`semantic_embedding_refresh_alignment_state`,
      `semantic_embedding_refresh_alignment_hint`) against rollout-aware
      refresh recommendation
    - `/health.memory_retrieval` now surfaces refresh alignment posture across
      vectors-disabled, active rollout, and fully-enabled rollout states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py`

- [x] PRJ-257 Add refresh strategy recommendation diagnostics in shared embedding strategy snapshot
  - Status: DONE
  - Group: Embedding Refresh Strategy Guidance
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-256
  - Priority: P2
  - Result:
    - shared embedding strategy snapshot now exposes recommended refresh mode
      (`semantic_embedding_recommended_refresh_mode`) using rollout-aware
      semantics (`on_write` during active rollout, `manual` for mature/full
      source rollout)
    - `/health.memory_retrieval` now surfaces recommended refresh posture for
      baseline and full-source rollout states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py`

- [x] PRJ-256 Add refresh cadence diagnostics in shared embedding strategy snapshot
  - Status: DONE
  - Group: Embedding Refresh Strategy Guidance
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-255
  - Priority: P2
  - Result:
    - shared embedding strategy snapshot now exposes refresh cadence diagnostics
      (`semantic_embedding_refresh_cadence_state`,
      `semantic_embedding_refresh_cadence_hint`) for vectors-disabled, on-write,
      and manual high/moderate/low-frequency modes
    - `/health.memory_retrieval` now surfaces refresh cadence posture in all
      tested retrieval configurations
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py`

- [x] PRJ-255 Sync embedding source-rollout sequencing slice across docs, planning, and context
  - Status: DONE
  - Group: Embedding Source Rollout Sequencing
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-254
  - Priority: P2
  - Result:
    - task board, project state, iteration plan, and open-decisions docs are
      synchronized through `PRJ-255`
    - canonical env/config and runtime ops docs now include source-rollout
      sequencing and progress diagnostics
    - runtime reality docs now record startup source-rollout hint behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-254 Add startup source-rollout hint logs from shared sequencing diagnostics
  - Status: DONE
  - Group: Embedding Source Rollout Sequencing
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-253
  - Priority: P2
  - Result:
    - startup source-coverage warnings now include rollout completion and
      progress context from one shared snapshot owner
    - startup now emits `embedding_source_rollout_hint` when vectors are
      enabled and rollout still has a pending next source kind
    - runtime log regressions now pin rollout hint behavior for pending and
      all-sources-enabled states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_api_routes.py`

- [x] PRJ-253 Add source-rollout progress diagnostics in shared embedding strategy snapshot
  - Status: DONE
  - Group: Embedding Source Rollout Sequencing
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-252
  - Priority: P2
  - Result:
    - shared embedding strategy snapshot now exposes source-rollout progress
      fields (`semantic_embedding_source_rollout_phase_index`,
      `semantic_embedding_source_rollout_phase_total`,
      `semantic_embedding_source_rollout_progress_percent`)
    - `/health.memory_retrieval` now surfaces rollout progress posture across
      vectors-disabled, partial, baseline, and full-source states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py`

- [x] PRJ-252 Add source-rollout sequencing diagnostics in shared embedding strategy snapshot
  - Status: DONE
  - Group: Embedding Source Rollout Sequencing
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-251
  - Priority: P2
  - Result:
    - shared embedding strategy snapshot now exposes explicit source sequencing
      diagnostics (`semantic_embedding_source_rollout_order`,
      `semantic_embedding_source_rollout_enabled_sources`,
      `semantic_embedding_source_rollout_missing_sources`,
      `semantic_embedding_source_rollout_next_source_kind`)
    - `/health.memory_retrieval` now exposes machine-readable next-source
      guidance for rollout operations
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py`

- [x] PRJ-251 Add relation-aware source-rollout completion posture in shared embedding strategy snapshot
  - Status: DONE
  - Group: Embedding Source Rollout Sequencing
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-250
  - Priority: P2
  - Result:
    - source-rollout state now distinguishes full vector-source activation
      (`all_vector_sources_enabled`) from semantic+affective baseline
    - shared diagnostics now expose explicit completion posture through
      `semantic_embedding_source_rollout_completion_state`
    - `/health.memory_retrieval` and unit tests now pin relation-inclusive
      full rollout behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py`

- [x] PRJ-250 Sync embedding strict-rollout guidance slice across docs, planning, and context
  - Status: DONE
  - Group: Embedding Strategy Strict Rollout Guidance
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-249
  - Priority: P2
  - Result:
    - task board, project state, iteration plan, and open-decisions docs are
      synchronized through `PRJ-250`
    - canonical env/config and runtime ops docs now include strict-rollout
      preflight/recommendation/alignment fields and startup
      `embedding_strategy_hint` posture
    - implementation reality docs now record shared strict-rollout ownership
      across `/health` and startup diagnostics
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-249 Add startup embedding strategy rollout hints from shared strict-rollout diagnostics
  - Status: DONE
  - Group: Embedding Strategy Strict Rollout Guidance
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-248
  - Priority: P2
  - Result:
    - startup now emits `embedding_strategy_hint` when vectors are enabled and
      enforcement alignment is visible (`below|aligned|mixed|above`)
    - hint logs now include strict-rollout readiness, violation summary,
      recommendation, and recommended enforcement posture from one shared
      snapshot owner
    - runtime policy log regressions now pin hint behavior for
      below-recommendation and aligned strict posture cases
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_embedding_strategy.py`

- [x] PRJ-248 Add embedding enforcement-alignment diagnostics in shared strategy snapshot
  - Status: DONE
  - Group: Embedding Strategy Strict Rollout Guidance
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-247
  - Priority: P2
  - Result:
    - shared embedding strategy snapshot now exposes per-control alignment
      fields (`semantic_embedding_provider_ownership_enforcement_alignment`,
      `semantic_embedding_model_governance_enforcement_alignment`) plus
      combined alignment posture
      (`semantic_embedding_enforcement_alignment_state`,
      `semantic_embedding_enforcement_alignment_hint`)
    - `/health.memory_retrieval` now surfaces alignment posture in baseline,
      vectors-disabled, fallback, and strict scenarios
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py`

- [x] PRJ-247 Add embedding strict-rollout recommendation diagnostics in shared strategy snapshot
  - Status: DONE
  - Group: Embedding Strategy Strict Rollout Guidance
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-246
  - Priority: P2
  - Result:
    - shared embedding strategy snapshot now exposes strict-rollout
      recommendation fields
      (`semantic_embedding_strict_rollout_recommendation`,
      `semantic_embedding_recommended_provider_ownership_enforcement`,
      `semantic_embedding_recommended_model_governance_enforcement`)
    - recommendation posture is now visible in `/health.memory_retrieval` for
      deterministic baseline, provider fallback, deterministic custom-model, and
      vectors-disabled states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py`

- [x] PRJ-246 Add embedding strict-rollout preflight diagnostics in shared strategy snapshot
  - Status: DONE
  - Group: Embedding Strategy Strict Rollout Guidance
  - Owner: Backend Builder + QA/Test
  - Depends on: PRJ-245
  - Priority: P2
  - Result:
    - shared embedding strategy snapshot now exposes strict-rollout preflight
      diagnostics
      (`semantic_embedding_strict_rollout_violations`,
      `semantic_embedding_strict_rollout_violation_count`,
      `semantic_embedding_strict_rollout_ready`,
      `semantic_embedding_strict_rollout_state`,
      `semantic_embedding_strict_rollout_hint`)
    - strict rollout now has one machine-readable readiness owner across
      `/health.memory_retrieval` and startup logging pathways
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py`

- [x] PRJ-245 Add embedding source-rollout recommendation posture in shared diagnostics
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-244
  - Priority: P2
  - Result:
    - shared embedding strategy helper now exposes source-rollout recommendation
      posture through
      `semantic_embedding_source_rollout_state`,
      `semantic_embedding_source_rollout_hint`, and
      `semantic_embedding_source_rollout_recommendation`
    - `/health.memory_retrieval` now surfaces source-rollout posture for
      vectors-disabled, semantic+affective baseline, semantic-only,
      affective-only, and foundational-only source sets
    - startup source-coverage warning now includes shared source-rollout
      diagnostics for operator rollout guidance
    - docs/context/planning are synchronized through `PRJ-245`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`

- [x] PRJ-244 Add embedding owner-strategy recommendation posture in shared diagnostics
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-243
  - Priority: P2
  - Result:
    - shared embedding strategy helper now exposes explicit owner-strategy
      recommendation posture through
      `semantic_embedding_owner_strategy_state`,
      `semantic_embedding_owner_strategy_hint`, and
      `semantic_embedding_owner_strategy_recommendation`
    - `/health.memory_retrieval` now surfaces owner-strategy recommendation
      posture for vectors-disabled, deterministic baseline/manual, and fallback
      provider ownership states
    - startup fallback warning now includes shared owner-strategy diagnostics
      for operator visibility
    - docs/context/planning are synchronized through `PRJ-244`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`

- [x] PRJ-243 Add embedding model-governance enforcement posture and strict startup block option
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-242
  - Priority: P2
  - Result:
    - runtime config now exposes explicit model-governance enforcement posture
      through `EMBEDDING_MODEL_GOVERNANCE_ENFORCEMENT` (`warn|strict`)
    - shared embedding strategy helper now exposes
      `semantic_embedding_model_governance_enforcement`,
      `semantic_embedding_model_governance_enforcement_state`, and
      `semantic_embedding_model_governance_enforcement_hint`
    - startup now supports strict model-governance block mode for
      deterministic custom-model-name posture, while warn mode remains
      warning-only
    - docs/context/planning are synchronized through `PRJ-243`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_config.py tests/test_api_routes.py tests/test_main_runtime_policy.py`

- [x] PRJ-242 Add embedding provider-ownership enforcement posture and strict startup block option
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-241
  - Priority: P2
  - Result:
    - runtime config now exposes explicit provider-ownership enforcement posture
      through `EMBEDDING_PROVIDER_OWNERSHIP_ENFORCEMENT` (`warn|strict`)
    - shared embedding strategy helper now exposes
      `semantic_embedding_provider_ownership_enforcement`,
      `semantic_embedding_provider_ownership_enforcement_state`, and
      `semantic_embedding_provider_ownership_enforcement_hint`
    - startup now supports strict provider-ownership block mode for fallback
      ownership posture, while warn mode remains warning-only
    - docs/context/planning are synchronized through `PRJ-242`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_config.py tests/test_api_routes.py tests/test_main_runtime_policy.py`

- [x] PRJ-241 Add embedding provider-ownership posture diagnostics and startup warning enrichment
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-240
  - Priority: P2
  - Result:
    - shared embedding strategy helper now exposes provider-ownership posture
      diagnostics
      (`semantic_embedding_provider_ownership_state`,
      `semantic_embedding_provider_ownership_hint`) so ownership visibility is
      explicit for deterministic baseline, fallback, and vectors-disabled modes
    - `/health.memory_retrieval` now surfaces provider-ownership diagnostics
      through the same shared embedding strategy helper
    - startup `embedding_strategy_warning` now includes provider-ownership
      diagnostics when fallback posture is active
    - docs/context/planning are synchronized through `PRJ-241`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`

- [x] PRJ-240 Add embedding model-governance posture diagnostics and startup warning alignment
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-239
  - Priority: P2
  - Result:
    - shared embedding strategy helper now exposes model-governance posture
      diagnostics
      (`semantic_embedding_model_governance_state`,
      `semantic_embedding_model_governance_hint`) alongside provider/model and
      refresh/source posture
    - `/health.memory_retrieval` now surfaces model-governance diagnostics from
      the same shared helper semantics
    - startup warning flow now emits
      `embedding_model_governance_warning` for deterministic custom-model-name
      posture so potentially misleading model config is operator-visible
    - docs/context/planning are synchronized through `PRJ-240`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`

- [x] PRJ-239 Unify embedding refresh posture semantics in shared strategy helper
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-238
  - Priority: P2
  - Result:
    - shared embedding strategy helper now owns refresh posture fields
      (`semantic_embedding_refresh_mode`,
      `semantic_embedding_refresh_interval_seconds`) and derived refresh
      diagnostics (`semantic_embedding_refresh_state`,
      `semantic_embedding_refresh_hint`)
    - `/health.memory_retrieval` and startup refresh warning flow now consume
      one shared refresh-posture owner, reducing drift risk
    - docs/context/planning are synchronized through `PRJ-239`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`

- [x] PRJ-238 Add explicit embedding refresh-cadence posture visibility and startup warning coverage
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-237
  - Priority: P2
  - Result:
    - runtime config now exposes explicit embedding refresh-cadence posture
      through `EMBEDDING_REFRESH_MODE` (`on_write|manual`) and
      `EMBEDDING_REFRESH_INTERVAL_SECONDS`
    - `/health.memory_retrieval` now exposes
      `semantic_embedding_refresh_mode` and
      `semantic_embedding_refresh_interval_seconds` for operator visibility
    - startup embedding strategy warnings now include
      `embedding_refresh_warning` when semantic vectors are enabled with manual
      refresh posture
    - docs/context/planning are synchronized through `PRJ-238`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_api_routes.py tests/test_main_runtime_policy.py`

- [x] PRJ-237 Add embedding source-coverage posture diagnostics and startup warning alignment
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-236
  - Priority: P2
  - Result:
    - shared embedding strategy helper now exposes source-coverage posture for
      current vector retrieval path
      (`semantic_embedding_source_coverage_state`,
      `semantic_embedding_source_coverage_hint`)
    - `/health.memory_retrieval` now exposes those source-coverage diagnostics
      alongside provider/model/source configuration posture
    - startup now emits `embedding_source_coverage_warning` when vectors are
      enabled but semantic/affective source coverage is partial or missing,
      using the same shared coverage-state semantics as health
    - docs/context/planning are synchronized through `PRJ-237`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_config.py tests/test_action_executor.py tests/test_memory_repository.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_main_lifespan_policy.py`

- [x] PRJ-236 Add explicit embedding source-family scope configuration and runtime gating
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-235
  - Priority: P2
  - Result:
    - runtime config now exposes `EMBEDDING_SOURCE_KINDS` with validation and
      explicit allowed family set (`episodic|semantic|affective|relation`)
    - action and memory repository embedding writes now respect enabled source
      families, so embedding persistence scope is explicit instead of implicit
    - `/health.memory_retrieval` now exposes effective configured embedding
      source kinds for operator visibility
    - docs/context/planning are synchronized through `PRJ-236`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_config.py tests/test_action_executor.py tests/test_memory_repository.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_main_lifespan_policy.py`

- [x] PRJ-235 Unify embedding warning posture semantics across health and startup logging
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-234
  - Priority: P2
  - Result:
    - one shared helper now owns embedding strategy posture and warning state
      semantics used by both `/health.memory_retrieval` and startup warning
      logging
    - `memory_retrieval` now exposes explicit warning posture fields
      (`semantic_embedding_warning_state`, `semantic_embedding_warning_hint`)
      in addition to provider/model readiness posture
    - startup warning behavior is now tied to the same shared warning state
      (`provider_fallback_active`) used by health diagnostics
    - docs/context/planning are synchronized through `PRJ-235`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_embedding_strategy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`

- [x] PRJ-234 Align conclusion embedding shell metadata with configured embedding strategy posture
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-233
  - Priority: P2
  - Result:
    - `MemoryRepository` now owns embedding strategy posture
      (`provider/model/dimensions`) so conclusion-driven semantic/affective
      embedding shells no longer use hardcoded `pending/0` values
    - conclusion embedding shells now persist effective model/dimensions plus
      requested-vs-effective provider metadata and explicit
      `pending_vector_materialization` status
    - app startup wiring now passes embedding strategy settings into
      `MemoryRepository`
    - docs/context/planning are synchronized through `PRJ-234`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_main_runtime_policy.py tests/test_main_lifespan_policy.py`

- [x] PRJ-233 Add embedding provider readiness posture and startup fallback warning
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-232
  - Priority: P2
  - Result:
    - `/health.memory_retrieval` now exposes provider readiness posture through
      `semantic_embedding_provider_ready` and
      `semantic_embedding_posture` (`ready|fallback_deterministic`)
    - startup now emits `embedding_strategy_warning` whenever semantic vectors
      are enabled but requested embedding provider/model posture falls back to
      deterministic execution
    - planning/docs/context are synchronized through `PRJ-233`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_config.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- [x] PRJ-232 Add embedding strategy config posture and deterministic fallback visibility
  - Status: DONE
  - Group: Embedding Strategy Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-231
  - Priority: P2
  - Result:
    - runtime settings now expose explicit embedding strategy controls
      (`EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS`) with
      bounded validation
    - action/runtime now consume configured embedding dimensions and deterministic
      fallback posture when non-implemented providers are requested
    - `GET /health.memory_retrieval` now exposes requested vs effective
      embedding provider/model posture plus fallback hint and dimensions
    - task board, project state, and planning/docs artifacts are synchronized
      through `PRJ-232`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- [x] PRJ-231 Add semantic vector retrieval feature gate and health posture visibility
  - Status: DONE
  - Group: Semantic Retrieval Activation Posture
  - Owner: Backend Builder + QA/Test + Product Docs
  - Depends on: PRJ-230
  - Priority: P2
  - Result:
    - runtime now supports explicit `SEMANTIC_VECTOR_ENABLED` posture, so
      hybrid retrieval can run in `hybrid_vector_lexical` (default) or
      `lexical_only` mode without hidden behavior
    - action now skips episodic embedding writes when semantic vectors are
      disabled
    - `GET /health` now exposes `memory_retrieval` posture fields
      (`semantic_vector_enabled`, `semantic_retrieval_mode`) for operator
      visibility
    - task board, project state, and planning docs are now synchronized through
      `PRJ-231` with no hidden `READY` work
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- [x] PRJ-230 Sync compat activity posture slice across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Query-Compat Activity Posture
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-229
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record compat
      activity posture as complete through `PRJ-230`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_config.py`

- [x] PRJ-229 Record compat activity posture completion and validation evidence in project state
  - Status: DONE
  - Group: Production Debug Query-Compat Activity Posture
  - Owner: Product Docs
  - Depends on: PRJ-228
  - Priority: P3
  - Result:
    - project state now records activity posture decision and latest validation
      evidence for this slice
  - Validation:
    - context sync review

- [x] PRJ-228 Sync planning docs for compat activity posture slice closure
  - Status: DONE
  - Group: Production Debug Query-Compat Activity Posture
  - Owner: Product Docs
  - Depends on: PRJ-227
  - Priority: P3
  - Result:
    - next-iteration plan now records activity posture slice completion and
      queue advancement through `PRJ-230`
  - Validation:
    - docs sync review

- [x] PRJ-227 Document compat activity posture fields in architecture and operations docs
  - Status: DONE
  - Group: Production Debug Query-Compat Activity Posture
  - Owner: Product Docs
  - Depends on: PRJ-226
  - Priority: P3
  - Result:
    - architecture, operations runbook, runtime-reality, and open-decisions
      docs now include compat activity posture fields and semantics
  - Validation:
    - docs sync review

- [x] PRJ-226 Add API regression for stale historical compat activity posture
  - Status: DONE
  - Group: Production Debug Query-Compat Activity Posture
  - Owner: QA/Test
  - Depends on: PRJ-225
  - Priority: P2
  - Result:
    - API tests now pin `stale_historical_attempts` posture when configured
      stale threshold is crossed after an observed compat attempt
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-225 Extend API regressions for compat activity posture fields
  - Status: DONE
  - Group: Production Debug Query-Compat Activity Posture
  - Owner: QA/Test
  - Depends on: PRJ-224
  - Priority: P2
  - Result:
    - API health contract tests now pin activity posture fields across
      no-attempt, compat-disabled, and recent-attempt scenarios
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-224 Add telemetry unit regressions for compat activity posture helper states
  - Status: DONE
  - Group: Production Debug Query-Compat Activity Posture
  - Owner: QA/Test
  - Depends on: PRJ-223
  - Priority: P2
  - Result:
    - telemetry tests now pin activity posture helper states and hints for
      disabled/no-attempt/stale/recent compat usage
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-223 Expose compat activity posture through `/health.runtime_policy`
  - Status: DONE
  - Group: Production Debug Query-Compat Activity Posture
  - Owner: Backend Builder
  - Depends on: PRJ-222
  - Priority: P2
  - Result:
    - `/health.runtime_policy` now exposes
      `event_debug_query_compat_activity_state` and
      `event_debug_query_compat_activity_hint`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-222 Add shared compat activity posture helper from telemetry/freshness snapshots
  - Status: DONE
  - Group: Production Debug Query-Compat Activity Posture
  - Owner: Backend Builder
  - Depends on: PRJ-221
  - Priority: P2
  - Result:
    - debug compat core now derives migration activity posture that separates
      disabled, no-attempt, stale-historical, and recent-attempt states while
      keeping sunset readiness contract unchanged
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-221 Derive compat activity posture slice from open decisions
  - Status: DONE
  - Group: Production Debug Query-Compat Activity Posture
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-220
  - Priority: P2
  - Result:
    - next architecture-alignment slice now focuses on activity posture
      visibility for compat-route migration windows
  - Validation:
    - planning-to-implementation sync review

- [x] PRJ-220 Sync compat freshness signal slice across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Query-Compat Freshness Signal
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-219
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record compat
      freshness signaling as complete through `PRJ-220`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_config.py`

- [x] PRJ-219 Document compat freshness threshold and fields in architecture/ops/local/runtime docs
  - Status: DONE
  - Group: Production Debug Query-Compat Freshness Signal
  - Owner: Product Docs
  - Depends on: PRJ-218
  - Priority: P3
  - Result:
    - architecture, local-development, ops runbook, runtime-reality, and
      open-decisions docs now include compat freshness fields and
      `EVENT_DEBUG_QUERY_COMPAT_STALE_AFTER_SECONDS`
  - Validation:
    - docs sync review

- [x] PRJ-218 Extend config regressions for compat freshness threshold defaults and bounds
  - Status: DONE
  - Group: Production Debug Query-Compat Freshness Signal
  - Owner: QA/Test
  - Depends on: PRJ-217
  - Priority: P2
  - Result:
    - config tests now pin default freshness threshold, explicit override, and
      too-low validation rejection for
      `EVENT_DEBUG_QUERY_COMPAT_STALE_AFTER_SECONDS`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py`

- [x] PRJ-217 Extend API regressions for compat freshness policy fields
  - Status: DONE
  - Group: Production Debug Query-Compat Freshness Signal
  - Owner: QA/Test
  - Depends on: PRJ-216
  - Priority: P2
  - Result:
    - API health contract tests now pin freshness fields across no-attempt and
      attempted compat-route paths, including configured stale-threshold
      visibility
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-216 Add telemetry unit regressions for compat freshness helper states
  - Status: DONE
  - Group: Production Debug Query-Compat Freshness Signal
  - Owner: QA/Test
  - Depends on: PRJ-215
  - Priority: P2
  - Result:
    - telemetry tests now pin freshness helper states
      (`no_attempts_recorded|fresh|stale`) and threshold validation
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-215 Keep test fixture and request-level health wiring aligned with configurable freshness threshold
  - Status: DONE
  - Group: Production Debug Query-Compat Freshness Signal
  - Owner: Backend Builder
  - Depends on: PRJ-214
  - Priority: P2
  - Result:
    - API test settings fixture now exposes
      `event_debug_query_compat_stale_after_seconds` and health coverage pins
      configured threshold behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-214 Add explicit compat freshness-threshold setting to runtime config
  - Status: DONE
  - Group: Production Debug Query-Compat Freshness Signal
  - Owner: Backend Builder
  - Depends on: PRJ-213
  - Priority: P2
  - Result:
    - runtime settings now expose
      `EVENT_DEBUG_QUERY_COMPAT_STALE_AFTER_SECONDS` with default `86400` and
      bounded validation (`>=1`)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py`

- [x] PRJ-213 Expose compat freshness helper output through `/health.runtime_policy`
  - Status: DONE
  - Group: Production Debug Query-Compat Freshness Signal
  - Owner: Backend Builder
  - Depends on: PRJ-212
  - Priority: P2
  - Result:
    - `/health.runtime_policy` now exposes stale-threshold, last-attempt age,
      and freshness state fields derived from compat telemetry snapshot
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-212 Add shared compat freshness helper from telemetry snapshot
  - Status: DONE
  - Group: Production Debug Query-Compat Freshness Signal
  - Owner: Backend Builder
  - Depends on: PRJ-211
  - Priority: P2
  - Result:
    - debug compat core now derives freshness posture from
      `last_attempt_at` with explicit stale threshold and state mapping
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-211 Derive compat freshness signal slice from open decisions
  - Status: DONE
  - Group: Production Debug Query-Compat Freshness Signal
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-210
  - Priority: P2
  - Result:
    - next architecture-alignment slice now focuses on explicit compat-route
      freshness posture for migration-window interpretation
  - Validation:
    - planning-to-implementation sync review

- [x] PRJ-210 Sync compat recent-window configurability slice across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Window Configurability
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-209
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record compat recent
      window configurability as complete through `PRJ-210`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`

- [x] PRJ-209 Document compat recent-window setting in planning and implementation docs
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Window Configurability
  - Owner: Product Docs
  - Depends on: PRJ-208
  - Priority: P3
  - Result:
    - open-decisions and runtime-reality docs now include
      `EVENT_DEBUG_QUERY_COMPAT_RECENT_WINDOW` semantics
  - Validation:
    - docs sync review

- [x] PRJ-208 Document compat recent-window setting in architecture and ops/local docs
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Window Configurability
  - Owner: Product Docs
  - Depends on: PRJ-207
  - Priority: P3
  - Result:
    - architecture, local-development, and ops docs now include
      `EVENT_DEBUG_QUERY_COMPAT_RECENT_WINDOW` defaults and purpose
  - Validation:
    - docs sync review

- [x] PRJ-207 Extend API regressions for configured compat recent-window behavior
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Window Configurability
  - Owner: QA/Test
  - Depends on: PRJ-206
  - Priority: P2
  - Result:
    - API tests now pin that configured recent window size bounds rolling
      compat counters and trend rates/state outputs
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-206 Extend config regressions for compat recent-window defaults and bounds
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Window Configurability
  - Owner: QA/Test
  - Depends on: PRJ-205
  - Priority: P2
  - Result:
    - config tests now pin default value, explicit override, and too-low
      validation failure for compat recent-window setting
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py`

- [x] PRJ-205 Extend telemetry unit regressions for configurable recent-window size
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Window Configurability
  - Owner: QA/Test
  - Depends on: PRJ-204
  - Priority: P2
  - Result:
    - telemetry unit tests now pin custom recent-window behavior and reject
      non-positive window values
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-204 Add explicit compat recent-window setting to runtime config
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Window Configurability
  - Owner: Backend Builder
  - Depends on: PRJ-203
  - Priority: P2
  - Result:
    - runtime settings now expose `EVENT_DEBUG_QUERY_COMPAT_RECENT_WINDOW`
      with default `20` and bounded validation (`>=1`)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py`

- [x] PRJ-203 Wire compat recent-window setting into lifespan telemetry initialization
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Window Configurability
  - Owner: Backend Builder
  - Depends on: PRJ-202
  - Priority: P2
  - Result:
    - app lifespan now initializes debug compat telemetry with configured
      recent-window size
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-202 Keep request-level telemetry fallback aligned with configured recent-window setting
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Window Configurability
  - Owner: Backend Builder
  - Depends on: PRJ-201
  - Priority: P2
  - Result:
    - request-level telemetry fallback now respects configured recent-window
      size from app settings
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_debug_compat_telemetry.py`

- [x] PRJ-201 Derive compat recent-window configurability slice from open decisions
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Window Configurability
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-200
  - Priority: P2
  - Result:
    - next architecture-alignment slice now focuses on configurable rolling
      window size for compat telemetry trends
  - Validation:
    - planning-to-implementation sync review

- [x] PRJ-200 Sync compat rolling-trend refinement slice across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Query-Compat Rolling Trend Refinement
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-199
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record compat
      rolling-trend refinement as complete through `PRJ-200`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`

- [x] PRJ-199 Document rolling-trend refinement semantics in planning and implementation docs
  - Status: DONE
  - Group: Production Debug Query-Compat Rolling Trend Refinement
  - Owner: Product Docs
  - Depends on: PRJ-198
  - Priority: P3
  - Result:
    - open-decisions and runtime-reality docs now describe rolling trend as
      release-window signal and attempt-based migration posture semantics
  - Validation:
    - docs sync review

- [x] PRJ-198 Document rolling-trend fields and states in architecture and ops docs
  - Status: DONE
  - Group: Production Debug Query-Compat Rolling Trend Refinement
  - Owner: Product Docs
  - Depends on: PRJ-197
  - Priority: P3
  - Result:
    - architecture and ops docs now include recent trend fields/states and
      operator interpretation guidance
  - Validation:
    - docs sync review

- [x] PRJ-197 Extend API regressions for rolling-trend mixed/disabled states
  - Status: DONE
  - Group: Production Debug Query-Compat Rolling Trend Refinement
  - Owner: QA/Test
  - Depends on: PRJ-196
  - Priority: P2
  - Result:
    - API tests now pin rolling trend state outputs across mixed and disabled
      compat-route scenarios
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-196 Extend health contract regressions for rolling-window telemetry fields
  - Status: DONE
  - Group: Production Debug Query-Compat Rolling Trend Refinement
  - Owner: QA/Test
  - Depends on: PRJ-195
  - Priority: P2
  - Result:
    - health endpoint policy tests now pin rolling telemetry counters and
      recent trend outputs
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-195 Add telemetry unit regressions for rolling-trend helper states
  - Status: DONE
  - Group: Production Debug Query-Compat Rolling Trend Refinement
  - Owner: QA/Test
  - Depends on: PRJ-194
  - Priority: P2
  - Result:
    - telemetry unit tests now pin rolling trend helper behavior for
      `no_recent_attempts|mixed|compat_disabled` states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-194 Extend compat telemetry snapshot with rolling-window counters
  - Status: DONE
  - Group: Production Debug Query-Compat Rolling Trend Refinement
  - Owner: Backend Builder
  - Depends on: PRJ-193
  - Priority: P2
  - Result:
    - compat telemetry snapshot now exposes recent window size and
      recent allowed/blocked counters for trend derivation
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py`

- [x] PRJ-193 Expose rolling-trend helper output through `/health.runtime_policy`
  - Status: DONE
  - Group: Production Debug Query-Compat Rolling Trend Refinement
  - Owner: Backend Builder
  - Depends on: PRJ-192
  - Priority: P2
  - Result:
    - `/health.runtime_policy` now exposes recent attempts/rates/state fields
      from one shared helper
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-192 Add shared rolling-trend helper for compat telemetry snapshots
  - Status: DONE
  - Group: Production Debug Query-Compat Rolling Trend Refinement
  - Owner: Backend Builder
  - Depends on: PRJ-191
  - Priority: P2
  - Result:
    - debug compat core now provides a reusable rolling-trend helper that maps
      recent rates into operator states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-191 Derive compat rolling-trend refinement slice from open decisions
  - Status: DONE
  - Group: Production Debug Query-Compat Rolling Trend Refinement
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-190
  - Priority: P2
  - Result:
    - next architecture-alignment slice now focuses on rolling-window compat
      trend visibility for migration monitoring
  - Validation:
    - planning-to-implementation sync review

- [x] PRJ-190 Sync compat recent-trend slice across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Trend Signals
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-189
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record compat
      recent-trend signaling as complete through `PRJ-190`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`

- [x] PRJ-189 Document compat recent-trend fields in planning and implementation docs
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Trend Signals
  - Owner: Product Docs
  - Depends on: PRJ-188
  - Priority: P3
  - Result:
    - open-decisions and runtime-reality docs now describe rolling-window compat
      trend fields exposed by health policy
  - Validation:
    - docs sync review

- [x] PRJ-188 Document compat recent-trend fields in architecture and ops docs
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Trend Signals
  - Owner: Product Docs
  - Depends on: PRJ-187
  - Priority: P3
  - Result:
    - architecture and ops docs now include
      `event_debug_query_compat_recent_attempts_total`,
      `event_debug_query_compat_recent_allow_rate`,
      `event_debug_query_compat_recent_block_rate`, and
      `event_debug_query_compat_recent_state`
  - Validation:
    - docs sync review

- [x] PRJ-187 Extend API regressions for compat recent-trend state outputs
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Trend Signals
  - Owner: QA/Test
  - Depends on: PRJ-186
  - Priority: P2
  - Result:
    - API tests now pin recent-trend state behavior in disabled and mixed
      compat attempt scenarios
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-186 Extend health contract regressions for recent-trend fields
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Trend Signals
  - Owner: QA/Test
  - Depends on: PRJ-185
  - Priority: P2
  - Result:
    - health endpoint policy tests now pin recent attempts/rates/state fields
      in default and production snapshots
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-185 Add telemetry unit regressions for recent-trend helper states
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Trend Signals
  - Owner: QA/Test
  - Depends on: PRJ-184
  - Priority: P2
  - Result:
    - telemetry unit tests now pin `no_recent_attempts`, `mixed`, and
      `compat_disabled` recent-state mapping
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-184 Extend telemetry snapshot with rolling-window counters
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Trend Signals
  - Owner: Backend Builder
  - Depends on: PRJ-183
  - Priority: P2
  - Result:
    - compat telemetry snapshots now include rolling-window counters
      (`recent_window_size`, `recent_attempts_total`, `recent_allowed_total`,
      `recent_blocked_total`) for trend derivation
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py`

- [x] PRJ-183 Expose compat recent-trend helper output through `/health.runtime_policy`
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Trend Signals
  - Owner: Backend Builder
  - Depends on: PRJ-182
  - Priority: P2
  - Result:
    - `/health.runtime_policy` now exposes recent attempts/rates/state via
      one shared recent-trend helper
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-182 Add shared compat recent-trend helper from telemetry snapshot
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Trend Signals
  - Owner: Backend Builder
  - Depends on: PRJ-181
  - Priority: P2
  - Result:
    - debug compat core now derives rolling-window attempts/rates/state from
      telemetry snapshots
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-181 Derive compat recent-trend slice from open decisions
  - Status: DONE
  - Group: Production Debug Query-Compat Recent Trend Signals
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-180
  - Priority: P2
  - Result:
    - next architecture-alignment slice now focuses on rolling-window compat
      trend visibility for release-window migration monitoring
  - Validation:
    - planning-to-implementation sync review

- [x] PRJ-180 Sync compat-sunset readiness-boolean slice across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness Signal
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-179
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record compat sunset
      readiness boolean/reason signaling as complete through `PRJ-180`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`

- [x] PRJ-179 Document compat sunset readiness boolean/reason in planning and implementation docs
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness Signal
  - Owner: Product Docs
  - Depends on: PRJ-178
  - Priority: P3
  - Result:
    - open-decisions and runtime-reality docs now include explicit
      `event_debug_query_compat_sunset_ready` and
      `event_debug_query_compat_sunset_reason` semantics
  - Validation:
    - docs sync review

- [x] PRJ-178 Document compat sunset readiness boolean/reason in architecture and ops docs
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness Signal
  - Owner: Product Docs
  - Depends on: PRJ-177
  - Priority: P3
  - Result:
    - architecture and ops docs now describe machine-readable compat sunset
      readiness fields and reasons
  - Validation:
    - docs sync review

- [x] PRJ-177 Extend mixed allowed/blocked compat-route regressions for sunset readiness fields
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness Signal
  - Owner: QA/Test
  - Depends on: PRJ-176
  - Priority: P2
  - Result:
    - compat-route API regressions now pin readiness=false and migration-needed
      reason when compat attempts are observed
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-176 Extend health contract regressions for sunset readiness boolean/reason
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness Signal
  - Owner: QA/Test
  - Depends on: PRJ-175
  - Priority: P2
  - Result:
    - health endpoint policy regressions now pin
      `event_debug_query_compat_sunset_ready` and
      `event_debug_query_compat_sunset_reason` across default and production
      policy postures
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-175 Add unit regressions for compat attempts with zero allows
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness Signal
  - Owner: QA/Test
  - Depends on: PRJ-174
  - Priority: P2
  - Result:
    - telemetry unit tests now pin that compat attempts (even fully blocked)
      still require migration before disabling compatibility route
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-174 Align compat recommendation logic with observed attempt presence
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness Signal
  - Owner: Backend Builder
  - Depends on: PRJ-173
  - Priority: P2
  - Result:
    - recommendation now treats any observed compat attempts as migration-needed
      instead of relying on allowed-count only
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py`

- [x] PRJ-173 Add shared compat sunset readiness boolean/reason helper outputs
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness Signal
  - Owner: Backend Builder
  - Depends on: PRJ-172
  - Priority: P2
  - Result:
    - debug compat core now emits machine-readable sunset decision fields based
      on recommendation state
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-172 Expose compat sunset readiness boolean/reason through `/health.runtime_policy`
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness Signal
  - Owner: Backend Builder
  - Depends on: PRJ-171
  - Priority: P2
  - Result:
    - `/health.runtime_policy` now includes
      `event_debug_query_compat_sunset_ready` and
      `event_debug_query_compat_sunset_reason`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-171 Derive compat sunset readiness-boolean slice from open decisions
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness Signal
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-170
  - Priority: P2
  - Result:
    - next architecture-alignment slice now adds explicit machine-readable
      go/no-go sunset signal for compatibility debug route
  - Validation:
    - planning-to-implementation sync review

- [x] PRJ-170 Sync compat-sunset recommendation slice across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Recommendation
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-169
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record compat-sunset
      recommendation signals as complete through `PRJ-170`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`

- [x] PRJ-169 Document compat-sunset recommendation signals in planning and implementation docs
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Recommendation
  - Owner: Product Docs
  - Depends on: PRJ-168
  - Priority: P3
  - Result:
    - open-decisions and runtime-reality docs now describe compat allow/block
      rates and recommendation guidance fields exposed via `/health`
  - Validation:
    - docs sync review

- [x] PRJ-168 Document compat-sunset recommendation signals in architecture and ops docs
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Recommendation
  - Owner: Product Docs
  - Depends on: PRJ-167
  - Priority: P3
  - Result:
    - architecture and ops docs now include
      `event_debug_query_compat_allow_rate`,
      `event_debug_query_compat_block_rate`, and
      `event_debug_query_compat_recommendation`
  - Validation:
    - docs sync review

- [x] PRJ-167 Extend compat-route blocked-path regressions for recommendation signals
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Recommendation
  - Owner: QA/Test
  - Depends on: PRJ-166
  - Priority: P2
  - Result:
    - compat-route tests now pin blocked-path telemetry and recommendation
      posture when production keeps compat route disabled
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-166 Extend health contract regressions for compat-sunset recommendation fields
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Recommendation
  - Owner: QA/Test
  - Depends on: PRJ-165
  - Priority: P2
  - Result:
    - health endpoint tests now pin allow/block rates and recommendation output
      in default and production policy snapshots
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-165 Add unit regressions for compat-sunset recommendation helper behavior
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Recommendation
  - Owner: QA/Test
  - Depends on: PRJ-164
  - Priority: P2
  - Result:
    - telemetry unit tests now pin recommendation behavior for disabled,
      no-traffic, and active-migration compat-route states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-164 Keep compat-route telemetry outcome classification aligned with debug access checks
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Recommendation
  - Owner: Backend Builder
  - Depends on: PRJ-163
  - Priority: P2
  - Result:
    - compat-route telemetry continues to classify allowed vs blocked outcomes
      after access checks, so recommendation inputs remain trustworthy
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-163 Expose compat-sunset rates and recommendation through `/health.runtime_policy`
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Recommendation
  - Owner: Backend Builder
  - Depends on: PRJ-162
  - Priority: P2
  - Result:
    - `/health.runtime_policy` now includes
      `event_debug_query_compat_allow_rate`,
      `event_debug_query_compat_block_rate`, and
      `event_debug_query_compat_recommendation`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-162 Add shared compat-sunset recommendation helper from telemetry snapshots
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Recommendation
  - Owner: Backend Builder
  - Depends on: PRJ-161
  - Priority: P2
  - Result:
    - debug compat core now derives allow/block rates and recommendation from
      one shared helper fed by telemetry snapshots
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-161 Derive compat-sunset recommendation slice from open decisions
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Recommendation
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-160
  - Priority: P2
  - Result:
    - next architecture-alignment slice now focuses on decision-ready compat
      sunset guidance based on observable route usage signals
  - Validation:
    - planning-to-implementation sync review

- [x] PRJ-160 Sync query-compat sunset-readiness slice across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-159
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record query-compat
      sunset-readiness as complete through `PRJ-160`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py tests/test_api_routes.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_config.py`

- [x] PRJ-159 Document query-compat deprecation telemetry and headers in canonical docs
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness
  - Owner: Product Docs
  - Depends on: PRJ-158
  - Priority: P3
  - Result:
    - architecture, ops, local-dev, runtime-reality, and planning docs now
      describe compat-route deprecation headers and health telemetry surface
  - Validation:
    - docs sync review

- [x] PRJ-158 Add API regressions for compat-route telemetry tracking
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness
  - Owner: QA/Test
  - Depends on: PRJ-157
  - Priority: P2
  - Result:
    - API tests now pin compat-route health telemetry counters for allowed and
      blocked attempts
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-157 Add API regressions for compat-route deprecation header contract
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness
  - Owner: QA/Test
  - Depends on: PRJ-156
  - Priority: P2
  - Result:
    - API tests now pin `X-AION-Debug-Compat-Deprecated=true` on accepted
      compatibility route responses
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-156 Add unit regressions for debug query-compat telemetry contract
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness
  - Owner: QA/Test
  - Depends on: PRJ-155
  - Priority: P2
  - Result:
    - dedicated telemetry unit tests now pin default and mutation behavior for
      compat-route counters and timestamp fields
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-155 Expose compat-route telemetry through `/health.runtime_policy`
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness
  - Owner: Backend Builder
  - Depends on: PRJ-154
  - Priority: P2
  - Result:
    - `/health.runtime_policy` now includes
      `event_debug_query_compat_telemetry` with attempt/allow/block counters
      plus last-attempt timestamps
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-154 Track blocked compat-route attempts across policy and token rejections
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness
  - Owner: Backend Builder
  - Depends on: PRJ-153
  - Priority: P2
  - Result:
    - compat-route telemetry now records blocked attempts for policy-denied and
      debug-access-denied request outcomes
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-153 Track successful compat-route debug responses
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness
  - Owner: Backend Builder
  - Depends on: PRJ-152
  - Priority: P2
  - Result:
    - compat-route telemetry now records allowed attempts only after successful
      debug response generation
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-152 Add explicit in-process telemetry contract for debug query-compat usage
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness
  - Owner: Backend Builder
  - Depends on: PRJ-151
  - Priority: P2
  - Result:
    - `DebugQueryCompatTelemetry` now owns compat-route usage counters and
      timestamp snapshots for migration sunset observability
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_debug_compat_telemetry.py`

- [x] PRJ-151 Derive query-compat sunset-readiness slice from open decisions
  - Status: DONE
  - Group: Production Debug Query-Compat Sunset Readiness
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-150
  - Priority: P2
  - Result:
    - next architecture-alignment slice now focuses on measurable compat-route
      sunset readiness (deprecation signaling and usage telemetry)
  - Validation:
    - planning-to-implementation sync review

- [x] PRJ-150 Sync query-compat hardening across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Query-Compat Hardening
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-149
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record query-compat
      hardening as complete through `PRJ-150`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_api_routes.py tests/test_config.py`

- [x] PRJ-149 Document query-compat policy posture in architecture, ops, and planning docs
  - Status: DONE
  - Group: Production Debug Query-Compat Hardening
  - Owner: Product Docs
  - Depends on: PRJ-148
  - Priority: P3
  - Result:
    - env/config, local-dev, ops, runtime-reality, and open-decisions docs now
      describe `EVENT_DEBUG_QUERY_COMPAT_ENABLED`, production-default disabled
      compat route posture, and strict mismatch visibility for
      `event_debug_query_compat_enabled=true`
  - Validation:
    - docs sync review

- [x] PRJ-148 Add production API regression for explicit query-compat opt-in behavior
  - Status: DONE
  - Group: Production Debug Query-Compat Hardening
  - Owner: QA/Test
  - Depends on: PRJ-147
  - Priority: P2
  - Result:
    - API tests now pin that production `POST /event?debug=true` works only
      when compat route is explicitly enabled and token policy is satisfied
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-147 Add production API regression for default query-compat route denial
  - Status: DONE
  - Group: Production Debug Query-Compat Hardening
  - Owner: QA/Test
  - Depends on: PRJ-146
  - Priority: P2
  - Result:
    - API tests now pin production default behavior where compatibility
      `POST /event?debug=true` is blocked unless explicitly enabled
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-146 Extend health-policy regressions for query-compat mismatch visibility
  - Status: DONE
  - Group: Production Debug Query-Compat Hardening
  - Owner: QA/Test
  - Depends on: PRJ-145
  - Priority: P2
  - Result:
    - health endpoint tests now pin explicit compat-route mismatch list/count
      behavior in production policy snapshots
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-145 Extend startup strict-block regressions for query-compat mismatch posture
  - Status: DONE
  - Group: Production Debug Query-Compat Hardening
  - Owner: QA/Test
  - Depends on: PRJ-144
  - Priority: P2
  - Result:
    - startup strict-policy tests now pin violation payloads that include
      `event_debug_query_compat_enabled=true` in multi-mismatch production
      scenarios
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py`

- [x] PRJ-144 Extend runtime-policy regressions for query-compat and token-missing combined posture
  - Status: DONE
  - Group: Production Debug Query-Compat Hardening
  - Owner: QA/Test
  - Depends on: PRJ-143
  - Priority: P2
  - Result:
    - runtime-policy tests now pin combined mismatch list/count when production
      debug route keeps query-compat enabled and token policy is unmet
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`

- [x] PRJ-143 Route production query-compat mismatch detection through shared helper
  - Status: DONE
  - Group: Production Debug Query-Compat Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-142
  - Priority: P2
  - Result:
    - production mismatch detection now calls one helper for compat-route
      posture so mismatch semantics remain centralized
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py`

- [x] PRJ-142 Add shared helper for production query-compat mismatch ownership
  - Status: DONE
  - Group: Production Debug Query-Compat Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-141
  - Priority: P2
  - Result:
    - runtime policy now includes explicit helper ownership for production
      query-compat mismatch detection
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`

- [x] PRJ-141 Derive production query-compat hardening slice from open decisions
  - Status: DONE
  - Group: Production Debug Query-Compat Hardening
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-140
  - Priority: P2
  - Result:
    - next architecture-alignment slice now resolves policy-observability and
      test-coverage gaps for production debug query-compat route posture
  - Validation:
    - planning-to-implementation sync review

- [x] PRJ-140 Sync strict-token-mismatch hardening across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Strict-Policy Hardening
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-139
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record strict token
      mismatch hardening as complete through `PRJ-140`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_api_routes.py tests/test_config.py`

- [x] PRJ-139 Update open decisions and runtime reality for strict token-missing mismatch posture
  - Status: DONE
  - Group: Production Debug Strict-Policy Hardening
  - Owner: Product Docs
  - Depends on: PRJ-138
  - Priority: P3
  - Result:
    - planning and runtime-reality docs now explicitly capture
      `event_debug_token_missing=true` strict mismatch behavior and posture
  - Validation:
    - docs sync review

- [x] PRJ-138 Document strict token-missing mismatch semantics in architecture and ops docs
  - Status: DONE
  - Group: Production Debug Strict-Policy Hardening
  - Owner: Product Docs
  - Depends on: PRJ-137
  - Priority: P3
  - Result:
    - architecture and ops docs now include strict mismatch examples that cover
      missing debug-token policy posture in production
  - Validation:
    - docs sync review

- [x] PRJ-137 Extend health mismatch regressions for strict token-missing policy
  - Status: DONE
  - Group: Production Debug Strict-Policy Hardening
  - Owner: QA/Test
  - Depends on: PRJ-136
  - Priority: P2
  - Result:
    - API health tests now pin production mismatch list/count with
      `event_debug_token_missing=true` where applicable
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-136 Extend startup strict-block regressions for token-missing mismatch
  - Status: DONE
  - Group: Production Debug Strict-Policy Hardening
  - Owner: QA/Test
  - Depends on: PRJ-135
  - Priority: P2
  - Result:
    - startup strict-policy tests now pin error/log violation payloads that
      include `event_debug_token_missing=true` in multi-mismatch scenarios
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py`

- [x] PRJ-135 Extend runtime-policy mismatch regressions for token-missing cases
  - Status: DONE
  - Group: Production Debug Strict-Policy Hardening
  - Owner: QA/Test
  - Depends on: PRJ-134
  - Priority: P2
  - Result:
    - runtime-policy tests now pin mismatch list/count behavior when production
      debug token is required but not configured
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`

- [x] PRJ-134 Include production token-missing state in policy mismatch count helpers
  - Status: DONE
  - Group: Production Debug Strict-Policy Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-133
  - Priority: P2
  - Result:
    - mismatch count and strict readiness now include token-missing production
      posture through one shared mismatch owner
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py`

- [x] PRJ-133 Add explicit production token-missing mismatch entry
  - Status: DONE
  - Group: Production Debug Strict-Policy Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-132
  - Priority: P2
  - Result:
    - production policy mismatch output now emits
      `event_debug_token_missing=true` when debug exposure is enabled in
      production and token requirement mode is active without a configured token
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`

- [x] PRJ-132 Add shared helper for production debug token-missing detection
  - Status: DONE
  - Group: Production Debug Strict-Policy Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-131
  - Priority: P2
  - Result:
    - runtime policy now has explicit helper ownership for
      token-missing detection in production debug posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`

- [x] PRJ-131 Derive strict-rollout token-missing hardening slice from open decisions
  - Status: DONE
  - Group: Production Debug Strict-Policy Hardening
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-130
  - Priority: P2
  - Result:
    - next architecture-alignment slice now resolves strict-rollout gap where
      production debug token-missing posture was visible but not part of policy
      mismatch counts
  - Validation:
    - planning-to-implementation sync review

- [x] PRJ-130 Sync production debug posture hardening across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Policy Observability
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-129
  - Priority: P2
  - Result:
    - task board, project state, and iteration plan now record production debug
      posture hardening as complete through `PRJ-130`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_api_routes.py tests/test_config.py`

- [x] PRJ-129 Update open decisions and implementation reality for debug posture signals
  - Status: DONE
  - Group: Production Debug Policy Observability
  - Owner: Product Docs
  - Depends on: PRJ-128
  - Priority: P3
  - Result:
    - planning and implementation docs now reflect `debug_access_posture` and
      `debug_token_policy_hint`, including startup warning behavior for relaxed
      token requirement mode
  - Validation:
    - docs sync review

- [x] PRJ-128 Document debug posture signals in architecture and ops docs
  - Status: DONE
  - Group: Production Debug Policy Observability
  - Owner: Product Docs
  - Depends on: PRJ-127
  - Priority: P3
  - Result:
    - architecture and operations docs now include
      `debug_access_posture|debug_token_policy_hint` as operator-visible
      runtime policy signals
  - Validation:
    - docs sync review

- [x] PRJ-127 Add startup warning regression for relaxed production token requirement
  - Status: DONE
  - Group: Production Debug Policy Observability
  - Owner: QA/Test
  - Depends on: PRJ-126
  - Priority: P2
  - Result:
    - startup policy tests now pin warning behavior when production debug is
      enabled and `PRODUCTION_DEBUG_TOKEN_REQUIRED=false`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py`

- [x] PRJ-126 Add runtime-policy snapshot regressions for debug posture and hints
  - Status: DONE
  - Group: Production Debug Policy Observability
  - Owner: QA/Test
  - Depends on: PRJ-125
  - Priority: P2
  - Result:
    - runtime-policy tests now pin `debug_access_posture` and
      `debug_token_policy_hint` across disabled, token-gated, missing-token,
      and open-no-token states
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`

- [x] PRJ-125 Extend health endpoint regressions for debug posture signals
  - Status: DONE
  - Group: Production Debug Policy Observability
  - Owner: QA/Test
  - Depends on: PRJ-124
  - Priority: P2
  - Result:
    - `/health.runtime_policy` tests now pin
      `debug_access_posture|debug_token_policy_hint` and production token
      requirement modes
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-124 Add relaxed-mode production debug warning in startup policy logs
  - Status: DONE
  - Group: Production Debug Policy Observability
  - Owner: Backend Builder
  - Depends on: PRJ-123
  - Priority: P2
  - Result:
    - startup logging now emits explicit warning when production debug is
      enabled with token requirement mode disabled and no configured token
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py`

- [x] PRJ-123 Expose debug posture and hint fields in runtime policy snapshot
  - Status: DONE
  - Group: Production Debug Policy Observability
  - Owner: Backend Builder
  - Depends on: PRJ-122
  - Priority: P2
  - Result:
    - runtime policy snapshot now emits `debug_access_posture` and
      `debug_token_policy_hint` for operator-visible debug hardening posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py`

- [x] PRJ-122 Add shared debug token policy hint helper
  - Status: DONE
  - Group: Production Debug Policy Observability
  - Owner: Backend Builder
  - Depends on: PRJ-121
  - Priority: P2
  - Result:
    - runtime policy now exposes one shared helper for concise debug token
      hardening guidance (`debug_token_policy_hint`)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`

- [x] PRJ-121 Add shared debug access posture helper
  - Status: DONE
  - Group: Production Debug Policy Observability
  - Owner: Backend Builder
  - Depends on: PRJ-120
  - Priority: P2
  - Result:
    - runtime policy now models explicit debug access posture
      (`disabled|token_gated|production_token_required_missing|open_no_token`)
      for debug route policy diagnostics
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`

- [x] PRJ-120 Sync production-debug-token hardening across source-of-truth docs/context
  - Status: DONE
  - Group: Production Debug Policy Hardening
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-119
  - Priority: P2
  - Result:
    - task board, project state, and iteration planning now record completion
      through `PRJ-120` for production debug-token hardening
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_api_routes.py`

- [x] PRJ-119 Document production debug-token policy in operations and local docs
  - Status: DONE
  - Group: Production Debug Policy Hardening
  - Owner: Product Docs
  - Depends on: PRJ-118
  - Priority: P3
  - Result:
    - runtime ops and local development docs now describe
      `PRODUCTION_DEBUG_TOKEN_REQUIRED` and its production behavior
  - Validation:
    - docs sync review

- [x] PRJ-118 Document production debug-token env contract in architecture docs
  - Status: DONE
  - Group: Production Debug Policy Hardening
  - Owner: Product Docs
  - Depends on: PRJ-117
  - Priority: P3
  - Result:
    - canonical env/config docs now include `PRODUCTION_DEBUG_TOKEN_REQUIRED`
      and related `/health.runtime_policy` visibility
  - Validation:
    - docs sync review

- [x] PRJ-117 Add startup-policy logging regression for disabled token-requirement mode
  - Status: DONE
  - Group: Production Debug Policy Hardening
  - Owner: QA/Test
  - Depends on: PRJ-116
  - Priority: P2
  - Result:
    - runtime-policy startup logging tests now pin behavior when production
      token requirement is explicitly disabled
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py`

- [x] PRJ-116 Extend runtime-policy snapshot regressions for production token policy signal
  - Status: DONE
  - Group: Production Debug Policy Hardening
  - Owner: QA/Test
  - Depends on: PRJ-115
  - Priority: P2
  - Result:
    - runtime-policy tests now pin `production_debug_token_required` snapshot
      behavior across production and non-production cases
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`

- [x] PRJ-115 Add API-route regressions for production debug-token enforcement
  - Status: DONE
  - Group: Production Debug Policy Hardening
  - Owner: QA/Test
  - Depends on: PRJ-114
  - Priority: P2
  - Result:
    - API tests now pin production behavior for debug endpoints when no debug
      token is configured and requirement mode is enabled/disabled
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-114 Enforce production debug-token requirement in debug route access guard
  - Status: DONE
  - Group: Production Debug Policy Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-113
  - Priority: P2
  - Result:
    - debug access guard now rejects production debug payload access when debug
      exposure is enabled and token requirement mode is enabled without a
      configured token
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-113 Expose production debug-token policy signal in runtime policy snapshot
  - Status: DONE
  - Group: Production Debug Policy Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-112
  - Priority: P2
  - Result:
    - runtime policy snapshot now reports
      `production_debug_token_required` for operator-visible policy posture
      through `/health`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py`

- [x] PRJ-112 Add production debug-token requirement helper to runtime policy core
  - Status: DONE
  - Group: Production Debug Policy Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-111
  - Priority: P2
  - Result:
    - runtime policy now has an explicit shared helper for production
      debug-token requirement mode with safe defaults
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`

- [x] PRJ-111 Add explicit production debug-token requirement setting
  - Status: DONE
  - Group: Production Debug Policy Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-110
  - Priority: P2
  - Result:
    - runtime config now exposes `PRODUCTION_DEBUG_TOKEN_REQUIRED` (default
      `true`) as a first-class policy switch
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py`

- [x] PRJ-110 Sync attention-config hardening across source-of-truth docs/context
  - Status: DONE
  - Group: Attention Observability Hardening
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-109
  - Priority: P2
  - Result:
    - task board, project state, and iteration planning now record the
      attention-config hardening slice as completed through `PRJ-110`
    - queue bookkeeping remains explicit with no hidden READY work
  - Validation:
    - docs/context sync review + `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_main_lifespan_policy.py tests/test_api_routes.py`

- [x] PRJ-109 Document attention tuning env vars in runtime ops runbook
  - Status: DONE
  - Group: Attention Observability Hardening
  - Owner: Product Docs
  - Depends on: PRJ-108
  - Priority: P3
  - Result:
    - runbook now documents optional attention tuning env vars for burst window
      and turn lifecycle cleanup thresholds
  - Validation:
    - docs sync review

- [x] PRJ-108 Document attention timing env contract in architecture config docs
  - Status: DONE
  - Group: Attention Observability Hardening
  - Owner: Product Docs
  - Depends on: PRJ-107
  - Priority: P3
  - Result:
    - canonical env/config doc now includes `ATTENTION_BURST_WINDOW_MS`,
      `ATTENTION_ANSWERED_TTL_SECONDS`, and `ATTENTION_STALE_TURN_SECONDS`
      including boundary semantics
  - Validation:
    - docs sync review

- [x] PRJ-107 Keep strict-lifespan regression fixtures compatible with attention settings
  - Status: DONE
  - Group: Attention Observability Hardening
  - Owner: QA/Test
  - Depends on: PRJ-106
  - Priority: P2
  - Result:
    - strict-policy lifespan fixtures include explicit attention setting fields,
      preventing fixture drift after config-surface expansion
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_lifespan_policy.py`

- [x] PRJ-106 Add attention-threshold validation regressions in config tests
  - Status: DONE
  - Group: Attention Observability Hardening
  - Owner: QA/Test
  - Depends on: PRJ-105
  - Priority: P2
  - Result:
    - config tests now pin invalid attention threshold behavior (negative burst
      window, too-low answered TTL, stale threshold below answered TTL)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py`

- [x] PRJ-105 Add default attention-config regression coverage
  - Status: DONE
  - Group: Attention Observability Hardening
  - Owner: QA/Test
  - Depends on: PRJ-104
  - Priority: P2
  - Result:
    - default settings coverage now pins attention defaults:
      `burst_window_ms=120`, `answered_ttl=5.0`, `stale_turn=30.0`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py`

- [x] PRJ-104 Make `/health` attention posture fully config-driven
  - Status: DONE
  - Group: Attention Observability Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-103
  - Priority: P2
  - Result:
    - `/health.attention` now reflects live coordinator thresholds that are
      wired from runtime settings rather than startup defaults only
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-103 Wire attention timing settings into app lifespan coordinator setup
  - Status: DONE
  - Group: Attention Observability Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-102
  - Priority: P2
  - Result:
    - app startup now initializes `AttentionTurnCoordinator` from settings
      values for burst window and TTL/stale thresholds
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_lifespan_policy.py tests/test_api_routes.py`

- [x] PRJ-102 Add bounded validation for attention timing config
  - Status: DONE
  - Group: Attention Observability Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-101
  - Priority: P2
  - Result:
    - settings validation now enforces non-negative burst window, minimum
      answered TTL, and stale threshold ordering vs answered TTL
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py`

- [x] PRJ-101 Add explicit attention timing settings to runtime config
  - Status: DONE
  - Group: Attention Observability Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-100
  - Priority: P2
  - Result:
    - runtime config now exposes first-class attention timing controls for
      burst coalescing and turn lifecycle cleanup
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_api_routes.py`

- [x] PRJ-100 Expose attention turn-assembly posture via `/health`
  - Status: DONE
  - Group: Attention Observability
  - Owner: Backend Builder
  - Depends on: PRJ-099
  - Priority: P2
  - Result:
    - `/health` now exposes an explicit `attention` snapshot with
      `burst_window_ms`, turn TTLs, and pending/claimed/answered counters so
      burst-coalescing posture is operator-visible
    - runtime turn-assembly behavior stays unchanged; this slice adds
      observability-only diagnostics and regression coverage
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-099 Add explicit compatibility hint headers for `POST /event?debug=true`
  - Status: DONE
  - Group: Public API Shape
  - Owner: Backend Builder
  - Depends on: PRJ-098
  - Priority: P2
  - Result:
    - `POST /event?debug=true` now emits explicit compatibility headers
      (`X-AION-Debug-Compat`, `Link`) that point operators to
      `POST /event/debug` as the preferred internal debug route
    - compatibility behavior stays intact while migration intent is now
      machine-visible in API responses and route-level tests
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`

- [x] PRJ-098 Add explicit internal debug endpoint while preserving `/event?debug=true`
  - Status: DONE
  - Group: Public API Shape
  - Owner: Backend Builder
  - Depends on: PRJ-097
  - Priority: P2
  - Result:
    - runtime now exposes explicit `POST /event/debug` for internal full-runtime
      debug payload access, guarded by the same debug policy/token checks as
      `POST /event?debug=true`
    - public `POST /event` contract remains compact by default, while debug
      behavior is now available through a clear internal route
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-097 Add connector expansion and capability-discovery proposals
  - Status: DONE
  - Group: External Productivity Connectors
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-096
  - Priority: P1
  - Result:
    - reflection now derives explicit `suggest_connector_expansion` proposals
      from repeated unmet connector needs, and planning promotes accepted
      proposals into bounded `connector_capability_discovery_intent` outputs
    - connector capability-discovery outputs now remain suggestion-only through
      permission gates (`proposal_only_no_external_access`) and episode payload
      traces (`connector_expansion_update`) without self-authorized side effects
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_reflection_worker.py`
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-096 Add connected-drive access contracts for cloud files and documents
  - Status: DONE
  - Group: External Productivity Connectors
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-095
  - Priority: P1
  - Result:
    - runtime now exposes explicit connected-drive domain intents with guarded
      read/suggest/mutate operation modes
    - planning and action contracts now include cloud-drive permission gates
      and non-side-effect connector payload traces (`drive_connector_update`)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_graph_state_contract.py`

- [x] PRJ-095 Add external task-system adapter contracts for connected task apps
  - Status: DONE
  - Group: External Productivity Connectors
  - Owner: Backend Builder
  - Depends on: PRJ-094
  - Priority: P1
  - Result:
    - planning and action contracts now expose explicit external task-system
      sync intents (`external_task_sync`) without provider-specific coupling
    - runtime now carries connector permission gate outputs so external task
      adapters stay authorization-bound and action-layer controlled
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_api_routes.py tests/test_config.py tests/test_graph_state_contract.py tests/test_schema_baseline.py`

- [x] PRJ-094 Add calendar integration boundary and scheduling-intent contract
  - Status: DONE
  - Group: External Productivity Connectors
  - Owner: Backend Builder
  - Depends on: PRJ-093
  - Priority: P1
  - Result:
    - planning and action contracts now expose explicit calendar scheduling
      intents (`calendar_scheduling`) with mutate/read permission semantics
    - calendar connector suggestions remain proposal/intention outputs until
      action-layer permission gates allow execution
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_api_routes.py tests/test_config.py tests/test_graph_state_contract.py tests/test_schema_baseline.py`

- [x] PRJ-093 Define the external connector contract, capability model, and permission gates
  - Status: DONE
  - Group: External Productivity Connectors
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-092
  - Priority: P1
  - Result:
    - runtime contracts now include connector capability and permission-gate
      outputs with explicit read/suggest/mutate operation modes
    - planning outputs now carry connector permission gates as first-class
      contracts instead of ad hoc integration assumptions
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_api_routes.py tests/test_config.py tests/test_graph_state_contract.py tests/test_schema_baseline.py`

- [x] PRJ-092 Add regression coverage for dual-loop coordination and batched conversation handling
  - Status: DONE
  - Group: Attention Gating And Dual-Loop Coordination
  - Owner: Backend Builder
  - Depends on: PRJ-091
  - Priority: P1
  - Result:
    - regression coverage now pins subconscious proposal persistence/handoff,
      proactive attention gating, and burst-turn runtime behavior
    - contract-level tests now fail fast when conscious/subconscious ownership
      or connector permission boundaries drift
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_api_routes.py tests/test_config.py tests/test_graph_state_contract.py tests/test_schema_baseline.py`

- [x] PRJ-091 Separate conscious wakeups from subconscious cadence
  - Status: DONE
  - Group: Attention Gating And Dual-Loop Coordination
  - Owner: Backend Builder
  - Depends on: PRJ-090
  - Priority: P1
  - Result:
    - subconscious reflection now persists proposal candidates while conscious
      planning/runtime explicitly accepts, defers, or discards them
    - proactive scheduler wakeups now pass through explicit attention-gate
      checks, keeping subconscious cadence non-user-facing
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_api_routes.py tests/test_config.py tests/test_graph_state_contract.py tests/test_schema_baseline.py`

- [x] PRJ-090 Add an attention gate for proactive delivery
  - Status: DONE
  - Group: Attention Gating And Dual-Loop Coordination
  - Owner: Backend Builder
  - Depends on: PRJ-089
  - Priority: P1
  - Result:
    - proactive scheduler events now evaluate an explicit attention gate
      (quiet hours, cooldown, unanswered backlog) before delivery planning
    - planning/runtime now defer proactive delivery through a typed
      `respect_attention_gate` branch when gate constraints block outreach
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_api_routes.py tests/test_config.py tests/test_graph_state_contract.py tests/test_schema_baseline.py`

- [x] PRJ-089 Add read-only tool and research policy for subconscious execution
  - Status: DONE
  - Group: Attention Gating And Dual-Loop Coordination
  - Owner: Backend Builder
  - Depends on: PRJ-088
  - Priority: P1
  - Result:
    - subconscious proposal records now carry explicit `research_policy` and
      `allowed_tools` fields with `read_only` as the normalized default
    - reflection/runtime proposal flow now preserves read-only tool boundaries
      so subconscious research cannot bypass conscious action ownership
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_api_routes.py tests/test_config.py tests/test_graph_state_contract.py tests/test_schema_baseline.py`

- [x] PRJ-088 Add subconscious proposal persistence and conscious promotion rules
  - Status: DONE
  - Group: Attention Gating And Dual-Loop Coordination
  - Owner: Backend Builder
  - Depends on: PRJ-087
  - Priority: P1
  - Result:
    - repository now persists subconscious proposals in a dedicated
      `aion_subconscious_proposal` table with pending/accepted/deferred/discarded
      status tracking
    - planning/runtime now record conscious proposal handoff decisions and
      resolve pending proposals only through conscious stage ownership
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_api_routes.py tests/test_config.py tests/test_graph_state_contract.py tests/test_schema_baseline.py`

- [x] PRJ-087 Define internal planning-state ownership and external productivity boundaries
  - Status: DONE
  - Group: Attention Gating And Dual-Loop Coordination
  - Owner: Product Docs + Backend Builder
  - Depends on: PRJ-086
  - Priority: P1
  - Result:
    - architecture/runtime contracts now keep internal goals/tasks as core
      planning state while external systems are treated as permissioned
      connector projections
    - docs and graph-state contracts now separate internal planning ownership
      from external connector capability and permission boundaries
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_action_executor.py tests/test_api_routes.py tests/test_config.py tests/test_graph_state_contract.py tests/test_schema_baseline.py`

- [x] PRJ-086 Implement message burst coalescing and pending-turn ownership
  - Status: DONE
  - Group: Attention Gating And Dual-Loop Coordination
  - Owner: Backend Builder
  - Depends on: PRJ-085
  - Priority: P1
  - Result:
    - Telegram burst events now pass through an attention-turn coordinator that
      coalesces rapid pending messages into one assembled turn payload before
      foreground runtime execution
    - pending/claimed/answered ownership now gates duplicate webhook events so
      duplicate updates and already-claimed turn events return queued no-op
      responses instead of triggering duplicate runtime replies
    - `/event` now returns explicit queue metadata for non-owner burst events,
      while owner events keep the existing public runtime response contract
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_event_normalization.py tests/test_runtime_pipeline.py tests/test_api_routes.py`

- [x] PRJ-085 Define the attention inbox, turn-assembly contract, and proposal handoff model
  - Status: DONE
  - Group: Attention Gating And Dual-Loop Coordination
  - Owner: Planner + Backend Builder
  - Depends on: PRJ-084
  - Priority: P1
  - Result:
    - runtime graph-state contracts now define explicit attention inbox,
      turn-assembly, subconscious proposal, and proposal-handoff model surfaces
      for conscious/subconscious coordination
    - architecture and implementation docs now align on one contract vocabulary
      for attention items, pending turn ownership, and conscious proposal
      decisions
    - the contract boundary now exists without introducing hidden side effects
      or bypassing conscious action ownership
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_graph_state_contract.py`

- [x] PRJ-084 Add proactive delivery controls, throttling, and regression coverage
  - Status: DONE
  - Group: Scheduled And Proactive Runtime
  - Owner: Backend Builder
  - Depends on: PRJ-083
  - Priority: P1
  - Result:
    - proactive planning now applies explicit delivery guardrails for user opt-in,
      recent outbound limits, unanswered proactive limits, and delivery-target
      presence before any outreach is executed
    - action execution now enforces proactive delivery guard outputs as a
      defensive boundary, preventing proactive delivery when guardrails defer
      outreach
    - proactive scheduler events can now preserve `chat_id` delivery targets,
      and proactive scheduler replies route through Telegram when a delivery
      target is available
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_api_routes.py tests/test_runtime_pipeline.py`

- [x] PRJ-083 Add a proactive decision engine with interruption guardrails
  - Status: DONE
  - Group: Scheduled And Proactive Runtime
  - Owner: Backend Builder
  - Depends on: PRJ-082
  - Priority: P1
  - Result:
    - scheduler proactive payloads now normalize explicit trigger/importance/urgency
      and user-context guardrail fields in one shared contract owner
    - proactive decision scoring now runs through a dedicated engine with bounded
      interruption cost evaluation, returning typed proactive decision output
    - motivation and planning now consume proactive decisions to either defer
      outreach or build typed proactive warning/reminder/insight-style plans
      without bypassing existing action boundaries
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`

- [x] PRJ-082 Add scheduled reflection and maintenance cadence
  - Status: DONE
  - Group: Scheduled And Proactive Runtime
  - Owner: Backend Builder
  - Depends on: PRJ-081
  - Priority: P1
  - Result:
    - scheduler worker now runs reflection and maintenance cadence independently
      from user-event turns, with explicit runtime guardrails for
      `in_process|deferred` reflection modes
    - `/health` now exposes scheduler runtime posture (`enabled`, `running`,
      cadence intervals, and latest tick summaries) so cadence wiring is
      observable during operations
    - cadence intervals are now clamped through scheduler contract rules so
      runtime configuration stays bounded by shared scheduler limits
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_scheduler_worker.py tests/test_scheduler_contracts.py tests/test_api_routes.py tests/test_config.py tests/test_reflection_worker.py tests/test_main_lifespan_policy.py`
    - `.\.venv\Scripts\python -m pytest -q`

- [x] PRJ-081 Make the reflection runtime ready for scheduled and out-of-process execution
  - Status: DONE
  - Group: Scheduled And Proactive Runtime
  - Owner: Backend Builder
  - Depends on: PRJ-080
  - Priority: P1
  - Result:
    - runtime now persists reflection tasks even when no in-process worker is attached,
      so deferred/scheduler/out-of-process reflection execution remains durable
    - reflection runtime mode is now explicit (`in_process|deferred`) and health
      semantics respect mode-aware worker expectations
    - reflection worker now exposes one-shot pending-task drain execution
      (`run_pending_once`) so external schedulers/workers can process queue state
      without long-running in-process loop ownership
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_main_lifespan_policy.py`

- [x] PRJ-080 Define scheduler events, cadence rules, and runtime boundaries
  - Status: DONE
  - Group: Scheduled And Proactive Runtime
  - Owner: Backend Builder
  - Depends on: PRJ-079
  - Priority: P1
  - Result:
    - scheduler-originated events now have explicit runtime normalization contracts
      (`source=scheduler`, scoped subsource rules, payload normalization)
    - runtime configuration now exposes explicit cadence boundaries for scheduler,
      reflection, maintenance, and proactive loops
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_event_normalization.py tests/test_scheduler_contracts.py`

- [x] PRJ-079 Make runtime relation-aware in retrieval, context, role, planning, and expression
  - Status: DONE
  - Group: Relation System
  - Owner: Backend Builder
  - Depends on: PRJ-078
  - Priority: P1
  - Result:
    - runtime now loads high-confidence relation records into graph/runtime state
      and maps relation cues into context, role, planning, and expression behavior
    - relation cues now influence collaboration/support stance in a bounded,
      test-covered way
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_role_agent.py tests/test_planning_agent.py tests/test_expression_agent.py tests/test_runtime_pipeline.py`

- [x] PRJ-078 Extend reflection to derive and maintain relation updates
  - Status: DONE
  - Group: Relation System
  - Owner: Backend Builder
  - Depends on: PRJ-077
  - Priority: P1
  - Result:
    - reflection now derives relation signals from episodic interaction evidence
      and persists scoped relation updates with confidence and provenance metadata
    - relation update events are observable through dedicated reflection log entries
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_runtime_pipeline.py`

- [x] PRJ-077 Define the relation data model, scopes, and repository surface
  - Status: DONE
  - Group: Relation System
  - Owner: Backend Builder
  - Depends on: PRJ-076
  - Priority: P1
  - Result:
    - repository now has a dedicated scoped relation model (`aion_relation`) with
      confidence, evidence count, decay rate, and source metadata
    - repository APIs now support upsert and retrieval of relations independently
      from generic conclusions
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_schema_baseline.py`
    - `.\.venv\Scripts\python -m alembic upgrade head --sql`

- [x] PRJ-076 Add semantic retrieval evaluation and observability
  - Status: DONE
  - Group: Semantic Retrieval Infrastructure
  - Owner: Backend Builder
  - Depends on: PRJ-075
  - Priority: P1
  - Result:
    - hybrid retrieval diagnostics now expose lexical/vector candidate counts
      and similarity/overlap scoring signals for runtime observability
    - runtime memory-load logging now surfaces hybrid retrieval summaries
      (`hybrid_vector_hits`, `hybrid_lexical_hits`)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_logging.py tests/test_runtime_pipeline.py tests/test_memory_repository.py`

- [x] PRJ-075 Implement hybrid retrieval across episodic, semantic, and affective memory
  - Status: DONE
  - Group: Semantic Retrieval Infrastructure
  - Owner: Backend Builder
  - Depends on: PRJ-074
  - Priority: P1
  - Result:
    - repository now exposes hybrid retrieval that blends episodic, semantic,
      and affective memory candidates using lexical overlap and vector similarity
    - runtime memory-load now consumes the hybrid bundle with deterministic
      embedding fallback when provider embeddings are unavailable
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_memory_repository.py tests/test_runtime_pipeline.py`

- [x] PRJ-074 Add pgvector-backed storage and migration scaffolding
  - Status: DONE
  - Group: Semantic Retrieval Infrastructure
  - Owner: DB/Migrations
  - Depends on: PRJ-073
  - Priority: P1
  - Result:
    - schema now includes `aion_semantic_embedding` with PostgreSQL `vector`
      extension scaffolding and non-Postgres JSON fallback compatibility
    - migration path now includes pgvector extension creation and semantic index baseline
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_schema_baseline.py tests/test_memory_repository.py`
    - `.\.venv\Scripts\python -m alembic upgrade head --sql`

- [x] PRJ-073 Define the embedding and semantic retrieval contract
  - Status: DONE
  - Group: Semantic Retrieval Infrastructure
  - Owner: Backend Builder
  - Depends on: PRJ-072
  - Priority: P1
  - Result:
    - shared contracts now define semantic source kinds, embedding records,
      retrieval query shape, and similarity hit/result payloads
    - deterministic embedding and cosine helper modules now provide a stable
      fallback baseline for retrieval tests and offline environments
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_semantic_contracts.py tests/test_memory_repository.py tests/test_schema_baseline.py`

- [x] PRJ-072 Add optional LangChain utility wrappers only where they reduce code
  - Status: DONE
  - Group: Graph Orchestration Adoption
  - Owner: Backend Builder
  - Depends on: PRJ-071
  - Priority: P1
  - Result:
    - OpenAI prompt construction now uses optional LangChain prompt templates
      behind a compatibility wrapper and remains fully functional without LangChain
    - LangChain support is now opt-in utility surface, not orchestration core
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_openai_prompting.py tests/test_expression_agent.py tests/test_runtime_pipeline.py`

- [x] PRJ-071 Migrate the foreground runtime orchestration to LangGraph
  - Status: DONE
  - Group: Graph Orchestration Adoption
  - Owner: Backend Builder
  - Depends on: PRJ-070
  - Priority: P1
  - Result:
    - foreground cognitive stages now run through LangGraph (`StateGraph`)
      while preserving stage boundaries, stage-level logging, and public/runtime
      contracts
    - runtime still loads baseline state and performs memory/reflection follow-up
      outside graph execution, keeping migration incremental and regression-safe
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_logging.py tests/test_graph_state_contract.py tests/test_graph_stage_adapters.py`

- [x] PRJ-069 Define the LangGraph migration boundary and compatibility contract
  - Status: DONE
  - Group: Graph Orchestration Adoption
  - Owner: Planner
  - Depends on: PRJ-068
  - Priority: P1
  - Result:
    - runtime now exposes an explicit graph compatibility state contract
      (`GraphRuntimeState`) plus conversion helpers from/to foreground
      `RuntimeResult`
    - canonical/runtime docs now define a contract-pinned migration boundary
      so LangGraph rollout can proceed incrementally without a big-bang rewrite
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_graph_state_contract.py`
- [x] PRJ-070 Introduce graph-compatible state adapters around current stage modules
  - Status: DONE
  - Group: Graph Orchestration Adoption
  - Owner: Backend Builder
  - Depends on: PRJ-069
  - Priority: P1
  - Result:
    - graph-compatible stage adapters now wrap perception, affective
      assessment, context, motivation, role, planning, expression, and action
      without changing the current orchestrator path
    - action-delivery shaping now uses one shared helper reusable by current
      orchestrator and future graph nodes
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_graph_stage_adapters.py tests/test_runtime_pipeline.py`

- [x] PRJ-065 Split reflection into smaller concern-owned modules
  - Status: DONE
  - Group: Adaptive Signal Governance And Heuristic Reduction
  - Owner: Backend Builder
  - Depends on: PRJ-064
  - Priority: P1
  - Result:
    - reflection logic was split into concern-owned modules:
      `app/reflection/goal_conclusions.py`,
      `app/reflection/adaptive_signals.py`,
      `app/reflection/affective_signals.py`
    - `app/reflection/worker.py` now focuses on orchestration and persistence
      flow instead of owning all inference details
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_runtime_pipeline.py`
- [x] PRJ-066 Add anti-self-reinforcement rules for adaptive signals
  - Status: DONE
  - Group: Adaptive Signal Governance And Heuristic Reduction
  - Owner: Backend Builder
  - Depends on: PRJ-065
  - Priority: P1
  - Result:
    - adaptive inference now requires outcome evidence (domain/preference update
      markers plus successful action), reducing self-reinforcement loops from
      role-only traces
    - collaboration-preference fallback now prefers explicit user-visible cues
      from recent events over plan-step self-feedback
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_role_agent.py tests/test_motivation_engine.py tests/test_expression_agent.py`
- [x] PRJ-067 Audit and prune low-leverage milestone heuristics
  - Status: DONE
  - Group: Adaptive Signal Governance And Heuristic Reduction
  - Owner: Backend Builder
  - Depends on: PRJ-066
  - Priority: P1
  - Result:
    - milestone pressure heuristics were pruned to phase-consistency signals and
      arc/transition evidence, removing low-leverage pure time-window drift
      triggers
    - regression now pins that stale time alone does not create lingering
      completion pressure
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_context_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py`
- [x] PRJ-068 Add multi-goal-aware reflection and planning tests
  - Status: DONE
  - Group: Adaptive Signal Governance And Heuristic Reduction
  - Owner: QA/Test
  - Depends on: PRJ-067
  - Priority: P1
  - Result:
    - reflection tests now pin goal-conclusion scope selection against recent
      turn hints when multiple active goals coexist
    - planning tests now pin event-to-goal matching across multiple active goals
      and task sets
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_reflection_worker.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`

- [x] PRJ-061 Formalize memory-layer contracts in docs and repository APIs
  - Status: DONE
  - Group: Scoped Memory And Retrieval Depth
  - Owner: Product Docs
  - Depends on: PRJ-060
  - Priority: P1
  - Result:
    - docs and repository contracts now share explicit layer vocabulary
      (`episodic`, `semantic`, `affective`, `operational`)
    - repository now exposes layer-aware APIs and classification helpers for
      episodic retrieval, conclusion-layer reads, and operational view reads
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_context_agent.py tests/test_runtime_pipeline.py`
- [x] PRJ-062 Add explicit domain action intents to the planning and action contract
  - Status: DONE
  - Group: Planning And Action Intent Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-061
  - Priority: P1
  - Result:
    - planning output now carries explicit typed `domain_intents` for
      goal/task/task-status and preference updates, plus `noop`
    - contracts/docs/runtime reality now define planning-owned intent and
      action-owned execution boundary explicitly
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`
- [x] PRJ-063 Move durable domain writes from text parsing to explicit intents
  - Status: DONE
  - Group: Planning And Action Intent Hardening
  - Owner: Backend Builder
  - Depends on: PRJ-062
  - Priority: P1
  - Result:
    - action no longer reparses raw event text for goal/task/task-status or
      preference durable updates
    - action executes only explicit `plan.domain_intents` and persists
      resulting intent outcomes in episodic payload metadata
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_runtime_pipeline.py tests/test_memory_repository.py`
- [x] PRJ-064 Add contract tests for planning-owned intent and action-owned execution
  - Status: DONE
  - Group: Planning And Action Intent Hardening
  - Owner: QA/Test
  - Depends on: PRJ-063
  - Priority: P1
  - Result:
    - planning, action, and runtime tests now pin typed intent emission,
      no-intent no-write behavior, and end-to-end plan->action ownership
    - regressions that reintroduce action-side raw-text domain parsing now fail
      through contract-level tests
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_planning_agent.py tests/test_action_executor.py tests/test_runtime_pipeline.py`

- [x] PRJ-029 Split canonical architecture docs from transitional runtime reality
  - Status: DONE
  - Group: Documentation Integrity
  - Owner: Product Docs
  - Depends on: PRJ-028
  - Priority: P2
  - Result:
    - `docs/architecture/` now again describes the canonical AION architecture
      and human-oriented cognitive flow
    - transitional runtime details were moved into
      `docs/implementation/runtime-reality.md`
    - docs index and project context now describe the two-layer documentation
      model explicitly
  - Validation:
    - doc-only change, no automated validation required
- [x] PRJ-000 Establish Personality-specific agent workflow scaffolding
- [x] PRJ-001..PRJ-010 Runtime contract, release-smoke, memory, and motivation alignment slices completed and captured in docs and tests
- [x] PRJ-014 Add a reusable stage-level structured logging scaffold
  - Status: DONE
  - Group: Observability And Runtime Honesty
  - Owner: Backend Builder
  - Depends on: none
  - Priority: P2
  - Files:
    - `app/core/runtime.py`
    - `app/core/logging.py`
  - Done when:
    - each runtime stage logs success or failure with `event_id`, `trace_id`, stage, and duration
    - stage logs include short summaries instead of raw payload dumps
    - related docs or project state mention the new observability surface if it changes repo truth
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py`
- [x] PRJ-015 Tighten the event normalization and public API boundary
  - Status: DONE
  - Group: Observability And Runtime Honesty
  - Owner: Planner
  - Depends on: none
  - Priority: P2
  - Result:
    - API event normalization now enforces explicit source/subsource and a small payload boundary
    - text normalization and meta fallback rules are test-covered, including length caps aligned with persistence limits
    - `EventRuntimeResponse` now uses shared `MotivationMode` contract typing
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_event_normalization.py tests/test_api_routes.py`
- [x] PRJ-016 Move startup toward migration-first schema ownership
  - Status: DONE
  - Group: Observability And Runtime Honesty
  - Owner: DB/Migrations
  - Depends on: none
  - Priority: P2
  - Result:
    - app startup now defaults to migration-first behavior
    - startup `create_tables()` moved behind explicit compatibility mode (`STARTUP_SCHEMA_MODE=create_tables`)
    - migration and deployment expectations were synchronized in docs and context
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_schema_baseline.py tests/test_config.py`
    - `.\.venv\Scripts\python -m alembic upgrade head --sql`
- [x] PRJ-017 Make the expression-to-action handoff explicit and test-covered
  - Status: DONE
  - Group: Stage Boundary Alignment
  - Owner: Backend Builder
  - Depends on: PRJ-016
  - Priority: P2
  - Result:
    - runtime now materializes an explicit `ActionDelivery` handoff between
      expression and action
    - action side effects consume the handoff contract instead of implicit
      expression/event coupling
    - runtime and action tests pin Telegram/API delivery behavior through the
      explicit contract
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_action_executor.py tests/test_expression_agent.py`
- [x] PRJ-019 Add runtime stage ownership and architecture-to-code traceability
  - Status: DONE
  - Group: Architecture Traceability And Contract Tests
  - Owner: Product Docs
  - Depends on: PRJ-016
  - Priority: P3
  - Result:
    - runtime stage ownership and primary validation surfaces are now documented
      in overview and architecture docs
    - runtime-contract docs now explicitly distinguish public `/event` response
      from debug-only internal payload shape
    - current-runtime differences versus intended architecture are explicit and
      searchable in canonical docs
  - Validation:
    - doc-only change, no automated validation required
- [x] PRJ-018 Reduce expression/action integration coupling without changing behavior
  - Status: DONE
  - Group: Stage Boundary Alignment
  - Owner: Backend Builder
  - Depends on: PRJ-017
  - Priority: P2
  - Result:
    - action execution now delegates channel delivery to integration-level
      `DeliveryRouter`
    - integration delivery consumes explicit `ActionDelivery` contract instead
      of runtime-local channel assumptions
    - API and Telegram delivery behavior remains stable under regression tests
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_action_executor.py tests/test_delivery_router.py`
- [x] PRJ-020 Add contract-level runtime flow smoke tests for architecture invariants
  - Status: DONE
  - Group: Architecture Traceability And Contract Tests
  - Owner: QA/Test
  - Depends on: PRJ-017, PRJ-019
  - Priority: P2
  - Result:
    - runtime flow invariants now have dedicated contract smoke tests across
      runtime pipeline, API boundary shape, and stage-logger payload contract
    - architectural drift on stage order, action boundary, or trace/log payload
      keys now causes fast regression failures
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_api_routes.py tests/test_logging.py`
- [x] PRJ-021 Add explicit debug payload exposure gate for `/event`
  - Status: DONE
  - Group: Public API Shape
  - Owner: Backend Builder
  - Depends on: none
  - Priority: P3
  - Result:
    - debug payload exposure for `POST /event?debug=true` is now controlled by
      explicit config (`EVENT_DEBUG_ENABLED`)
    - API behavior is test-covered for both debug-enabled and debug-disabled
      paths
    - environment and operations docs now describe the gate and policy surface
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_config.py`
- [x] PRJ-022 Expose runtime policy flags in `/health` for operator traceability
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Ops/Release
  - Depends on: none
  - Priority: P3
  - Result:
    - `/health` now includes non-secret runtime policy flags (`startup_schema_mode`, `event_debug_enabled`)
    - API tests pin the added health payload contract
    - runtime ops and planning docs now describe the policy visibility surface
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`
- [x] PRJ-023 Add production visibility warning for debug payload policy
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: none
  - Priority: P3
  - Result:
    - startup now emits an explicit warning when `APP_ENV=production` and
      `EVENT_DEBUG_ENABLED=true`
    - warning behavior is pinned with targeted startup policy tests
    - runtime ops and planning docs now explain how operators should interpret
      and clear this warning
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_config.py tests/test_main_runtime_policy.py`
- [x] PRJ-024 Add production visibility warning for schema compatibility mode
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: none
  - Priority: P3
  - Result:
    - startup now emits an explicit warning when `APP_ENV=production` and
      `STARTUP_SCHEMA_MODE=create_tables`
    - warning behavior is pinned with targeted startup policy tests
    - runtime ops and planning docs now explain why schema compatibility mode
      should remain temporary in production
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_config.py`
- [x] PRJ-025 Harden production default for debug payload exposure policy
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-023
  - Priority: P3
  - Result:
    - event debug exposure now uses environment-aware effective policy
      (enabled by default in non-production, disabled by default in production)
    - `/health` now exposes `event_debug_source` so operators can distinguish
      explicit config from environment-derived default behavior
    - startup warnings and docs were aligned with explicit-vs-default policy
      semantics
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_config.py tests/test_main_runtime_policy.py`
- [x] PRJ-026 Add optional strict production policy enforcement for startup
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-024, PRJ-025
  - Priority: P3
  - Result:
    - startup runtime-policy checks now support `PRODUCTION_POLICY_ENFORCEMENT=warn|strict`
    - production mismatch cases (`EVENT_DEBUG_ENABLED=true`, `STARTUP_SCHEMA_MODE=create_tables`) can now fail fast in strict mode
    - `/health` now exposes `production_policy_enforcement` so operators can verify active enforcement posture
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
- [x] PRJ-027 Add lifespan-level fail-fast regression test for strict policy mode
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: QA/Test
  - Depends on: PRJ-026
  - Priority: P3
  - Result:
    - startup strict-policy fail-fast behavior is now pinned at `lifespan` entry, not only in helper-level policy tests
    - regression test confirms mismatch block happens before database initialization side effects
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_lifespan_policy.py tests/test_main_runtime_policy.py tests/test_config.py tests/test_api_routes.py`
- [x] PRJ-028 Add lifespan-level fail-fast regression coverage for strict schema mismatch
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: QA/Test
  - Depends on: PRJ-027
  - Priority: P3
  - Result:
    - startup strict-policy fail-fast behavior is now lifecycle-covered for both mismatch families
      (`EVENT_DEBUG_ENABLED=true` and `STARTUP_SCHEMA_MODE=create_tables`)
    - regression tests confirm strict-mode mismatch blocks runtime before database initialization in both cases
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_lifespan_policy.py tests/test_main_runtime_policy.py tests/test_config.py tests/test_api_routes.py`
- [x] PRJ-029 Unify runtime policy mismatch detection and expose mismatch preview in `/health`
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-028
  - Priority: P3
  - Result:
    - runtime policy resolution now has one shared owner (`app/core/runtime_policy.py`) reused by startup warning/block checks and `/health`
    - `/health.runtime_policy` now includes `production_policy_mismatches` for operator-visible mismatch preview
    - regression coverage now pins shared policy snapshot semantics plus startup and API consumers
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_main_runtime_policy.py tests/test_main_lifespan_policy.py tests/test_api_routes.py`
- [x] PRJ-030 Add shared mismatch-count helper for runtime policy
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-029
  - Priority: P3
  - Result:
    - shared `production_policy_mismatch_count()` helper now exposes mismatch cardinality from one source of truth
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`
- [x] PRJ-031 Add shared strict-startup-block predicate helper
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-030
  - Priority: P3
  - Result:
    - shared `strict_startup_blocked()` helper now encodes strict enforcement block semantics in one place
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_main_runtime_policy.py`
- [x] PRJ-032 Add shared strict-rollout-readiness helper
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-031
  - Priority: P3
  - Result:
    - shared `strict_rollout_ready()` helper now reports whether strict-mode rollout has zero policy mismatches
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`
- [x] PRJ-033 Extend runtime policy snapshot with readiness fields
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-032
  - Priority: P3
  - Result:
    - `runtime_policy_snapshot` now includes `production_policy_mismatch_count`, `strict_startup_blocked`, and `strict_rollout_ready`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py`
- [x] PRJ-034 Keep startup strict-block checks aligned with shared policy helper
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-033
  - Priority: P3
  - Result:
    - startup now consumes shared strict-block predicate so startup and `/health` policy semantics remain aligned
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py tests/test_main_lifespan_policy.py`
- [x] PRJ-035 Expose strict-rollout readiness fields through `/health`
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Ops/Release
  - Depends on: PRJ-033
  - Priority: P3
  - Result:
    - `/health.runtime_policy` now exposes mismatch count and strict readiness/block state for operator triage
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`
- [x] PRJ-036 Add runtime-policy unit regression coverage for readiness helpers
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: QA/Test
  - Depends on: PRJ-032
  - Priority: P3
  - Result:
    - runtime-policy unit tests now pin mismatch count and strict rollout/block helper behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`
- [x] PRJ-037 Expand `/health` API contract tests for strict readiness fields
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: QA/Test
  - Depends on: PRJ-035
  - Priority: P3
  - Result:
    - API tests now pin mismatch count and strict readiness/block outputs for multiple policy combinations
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`
- [x] PRJ-038 Add startup regression for warn-mode multi-mismatch non-block behavior
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: QA/Test
  - Depends on: PRJ-034
  - Priority: P3
  - Result:
    - startup tests now explicitly pin that `warn` mode logs warnings without strict startup block even under multiple mismatches
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py`
- [x] PRJ-039 Sync planning/context/docs for strict rollout readiness contract
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Product Docs
  - Depends on: PRJ-035
  - Priority: P3
  - Result:
    - planning, context, architecture, and ops docs now describe strict rollout readiness fields and current runtime truth
  - Validation:
    - doc-and-context sync plus regression evidence recorded in this slice
- [x] PRJ-040 Add strict-rollout recommendation helper for production policy
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-039
  - Priority: P3
  - Result:
    - shared helper now derives `recommended_production_policy_enforcement` from environment and mismatch readiness
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`
- [x] PRJ-041 Add strict-rollout action hint helper
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-040
  - Priority: P3
  - Result:
    - shared helper now emits concise rollout hints (`not_applicable_non_production`, `resolve_mismatches_before_strict`, `can_enable_strict`)
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py`
- [x] PRJ-042 Expose strict-rollout recommendation fields through runtime policy snapshot and `/health`
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Ops/Release
  - Depends on: PRJ-041
  - Priority: P3
  - Result:
    - `/health.runtime_policy` now includes `recommended_production_policy_enforcement` and `strict_rollout_hint`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py tests/test_runtime_policy.py`
- [x] PRJ-043 Add startup informational hint for strict-rollout readiness in production warn mode
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-042
  - Priority: P3
  - Result:
    - startup now logs `runtime_policy_hint` when production is in `warn` mode and strict rollout is ready
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py`
- [x] PRJ-044 Expand runtime-policy and startup/API regression coverage for recommendation hints
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: QA/Test
  - Depends on: PRJ-043
  - Priority: P3
  - Result:
    - tests now pin recommendation/hint fields in snapshot and `/health`, plus startup info-hint behavior in production warn mode
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_main_runtime_policy.py`
- [x] PRJ-045 Sync docs/context for strict-rollout recommendation contract
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Product Docs
  - Depends on: PRJ-044
  - Priority: P3
  - Result:
    - planning, context, architecture, and ops docs now describe strict-rollout recommendation and hint fields
  - Validation:
    - doc-and-context sync plus regression evidence recorded in this slice
- [x] PRJ-046 Add optional debug-token runtime setting for event debug access
  - Status: DONE
  - Group: Public API Shape
  - Owner: Backend Builder
  - Depends on: PRJ-045
  - Priority: P3
  - Result:
    - settings now support optional `EVENT_DEBUG_TOKEN` for debug payload access control
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_config.py tests/test_runtime_policy.py`
- [x] PRJ-047 Add runtime-policy token-required signal for debug payload access
  - Status: DONE
  - Group: Public API Shape
  - Owner: Backend Builder
  - Depends on: PRJ-046
  - Priority: P3
  - Result:
    - runtime policy snapshot now exposes `event_debug_token_required`
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py`
- [x] PRJ-048 Enforce debug-token header for `POST /event?debug=true` when configured
  - Status: DONE
  - Group: Public API Shape
  - Owner: Backend Builder
  - Depends on: PRJ-047
  - Priority: P3
  - Result:
    - debug runtime payload endpoint now requires `X-AION-Debug-Token` when `EVENT_DEBUG_TOKEN` is configured
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_api_routes.py`
- [x] PRJ-049 Add production warning for debug exposure without debug token
  - Status: DONE
  - Group: Runtime Ops Visibility
  - Owner: Backend Builder
  - Depends on: PRJ-048
  - Priority: P3
  - Result:
    - startup now warns when production debug exposure is enabled and no debug token is configured
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_main_runtime_policy.py`
- [x] PRJ-050 Expand config/runtime/API/startup regression coverage for debug token gate
  - Status: DONE
  - Group: Public API Shape
  - Owner: QA/Test
  - Depends on: PRJ-049
  - Priority: P3
  - Result:
    - tests now pin token-required health policy field, debug endpoint token rejection/acceptance, and startup token-warning behavior
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_policy.py tests/test_api_routes.py tests/test_main_runtime_policy.py tests/test_config.py tests/test_main_lifespan_policy.py`
- [x] PRJ-051 Sync docs/context for debug-token-gated debug payload contract
  - Status: DONE
  - Group: Public API Shape
  - Owner: Product Docs
  - Depends on: PRJ-050
  - Priority: P3
  - Result:
    - architecture, operations, local-dev, planning docs and context now describe optional debug-token-gated debug payload access
  - Validation:
    - doc-and-context sync plus regression evidence recorded in this slice
- [x] PRJ-052 Add API user-id header fallback to reduce shared anonymous language/profile drift
  - Status: DONE
  - Group: Language Handling Strategy
  - Owner: Backend Builder
  - Depends on: PRJ-051
  - Priority: P2
  - Result:
    - API event normalization now accepts a route-provided fallback user id
      and `POST /event` now passes `X-AION-User-Id` as fallback identity input
      when `meta.user_id` is not provided
    - API user identity precedence is now explicit and test-covered
      (`meta.user_id` first, then `X-AION-User-Id`, then `anonymous`)
    - runtime reality, local-dev, ops, planning, and context docs now describe
      the multi-user API identity guardrail
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_event_normalization.py tests/test_api_routes.py`
    - `.\.venv\Scripts\python -m pytest -q`
- [x] PRJ-053 Define the affective assessment contract and runtime placeholders
  - Status: DONE
  - Group: Affective Understanding And Empathy
  - Owner: Planner
  - Depends on: PRJ-052
  - Priority: P1
  - Result:
    - runtime contracts now define a first-class affective slot
      (`affect_label`, `intensity`, `needs_support`, `confidence`, `source`,
      `evidence`)
    - perception now emits deterministic affective placeholder data and runtime
      carries it as top-level `RuntimeResult.affective`
    - architecture/runtime-reality/planning/context docs now align around the
      explicit affective contract before AI-assisted behavior slices
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_affective_contract.py tests/test_language_runtime.py tests/test_runtime_pipeline.py tests/test_api_routes.py`
    - `.\.venv\Scripts\python -m pytest -q`
- [x] PRJ-054 Add an AI-assisted affective assessor with deterministic fallback
  - Status: DONE
  - Group: Affective Understanding And Empathy
  - Owner: Backend Builder
  - Depends on: PRJ-053
  - Priority: P1
  - Result:
    - runtime now runs a dedicated `AffectiveAssessor` stage that can consume
      LLM classification and normalize it to the explicit affective contract
    - deterministic fallback remains active when classifier client is missing,
      unavailable, or returns invalid payload
    - runtime stage logs now expose affective source (`ai_classifier` vs
      `fallback`) for operator traceability
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_affective_assessor.py tests/test_language_runtime.py tests/test_runtime_pipeline.py tests/test_expression_agent.py`
    - `.\.venv\Scripts\python -m pytest -q`
- [x] PRJ-055 Wire affective assessment through motivation, role, and expression
  - Status: DONE
  - Group: Affective Understanding And Empathy
  - Owner: Backend Builder
  - Depends on: PRJ-054
  - Priority: P1
  - Result:
    - motivation, role, and expression now consume `perception.affective` as
      the primary support/emotion signal instead of local emotional keyword
      ladders
    - supportive behavior remains traceable to one affective owner across
      runtime stages (`affective_assessment` -> `motivation`/`role`/`expression`)
    - targeted tests now encode affective-driven behavior in stage-level unit
      paths and runtime pipeline integration
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_role_agent.py tests/test_expression_agent.py tests/test_runtime_pipeline.py`
    - `.\.venv\Scripts\python -m pytest -q`
- [x] PRJ-056 Add empathy-oriented evaluation fixtures and regression tests
  - Status: DONE
  - Group: Affective Understanding And Empathy
  - Owner: QA/Test
  - Depends on: PRJ-055
  - Priority: P1
  - Result:
    - empathy-focused shared fixtures now cover emotionally heavy, ambiguous,
      and mixed-intent turns
    - motivation, expression, and runtime regression tests now parametrize these
      fixtures to pin support quality through the affective contract path
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_runtime_pipeline.py tests/test_expression_agent.py tests/test_motivation_engine.py`
- [x] PRJ-057 Introduce scoped conclusions for global, goal, and task context
  - Status: DONE
  - Group: Scoped Memory And Retrieval Depth
  - Owner: Backend Builder
  - Depends on: PRJ-056
  - Priority: P1
  - Result:
    - `aion_conclusion` now supports scoped records (`scope_type`, `scope_key`)
      for `global|goal|task` context with scoped uniqueness guarantees
    - reflection now persists goal-operational conclusions with goal scope instead
      of forcing all operational state into one user-global slot
    - memory repository APIs now support scoped conclusion and runtime-preference
      queries, including scope-aware filtering with optional global fallback
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py`
    - `.\.venv\Scripts\python -m pytest -q tests/test_schema_baseline.py`
    - `.\.venv\Scripts\python -m alembic upgrade head --sql`
    - `.\.venv\Scripts\python -m pytest -q`
- [x] PRJ-058 Refactor runtime consumers to use scoped reflection state
  - Status: DONE
  - Group: Scoped Memory And Retrieval Depth
  - Owner: Backend Builder
  - Depends on: PRJ-057
  - Priority: P1
  - Result:
    - runtime state load now resolves a primary active goal and reads scoped
      runtime preferences and scoped conclusions with global fallback
    - context, motivation, planning, and milestone enrichment consume the
      scoped state for the active goal path
    - regression coverage now pins that unrelated goal conclusions do not leak
      into the current turn
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`
- [x] PRJ-059 Add an affective memory layer and reflection outputs
  - Status: DONE
  - Group: Scoped Memory And Retrieval Depth
  - Owner: Backend Builder
  - Depends on: PRJ-058
  - Priority: P1
  - Result:
    - episodic payloads now persist lightweight affective tags
      (`affect_label`, `affect_intensity`, `affect_needs_support`,
      `affect_source`, `affect_evidence`)
    - reflection now derives slower-moving affective conclusions
      (`affective_support_pattern`, `affective_support_sensitivity`)
    - runtime preferences, context summaries, and motivation scoring now consume
      those affective reflection signals
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_action_executor.py tests/test_memory_repository.py tests/test_reflection_worker.py tests/test_context_agent.py tests/test_motivation_engine.py tests/test_runtime_pipeline.py`
- [x] PRJ-060 Add retrieval ranking and compression beyond the latest-five load
  - Status: DONE
  - Group: Scoped Memory And Retrieval Depth
  - Owner: Backend Builder
  - Depends on: PRJ-059
  - Priority: P1
  - Result:
    - runtime memory load depth now fetches beyond a fixed latest-five limit
      (`RuntimeOrchestrator.MEMORY_LOAD_LIMIT=12`)
    - context retrieval ranking now includes affective relevance in addition to
      language, layer mode, topical overlap, and importance
    - runtime integration tests pin that deeper history can surface ranked
      relevant memory instead of being cut off by shallow fetch depth
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_runtime_pipeline.py`
- [x] PRJ-011 Extract shared goal/task selection helpers
  - Status: DONE
  - Group: Shared Signal Engine Extraction
  - Owner: Backend Builder
  - Depends on: none
  - Priority: P1
  - Done when:
    - tokenization, priority ranking, task-status ranking, and related-goal selection no longer live in multiple copies
    - behavior stays unchanged
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_context_agent.py tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_runtime_pipeline.py`
- [x] PRJ-012 Extract shared goal-progress and milestone-history signal helpers
  - Status: DONE
  - Group: Shared Signal Engine Extraction
  - Owner: Backend Builder
  - Depends on: PRJ-011
  - Priority: P1
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q tests/test_motivation_engine.py tests/test_planning_agent.py tests/test_reflection_worker.py tests/test_runtime_pipeline.py`
- [x] PRJ-013 Split oversized heuristic modules after helper extraction
  - Status: DONE
  - Group: Shared Signal Engine Extraction
  - Owner: Backend Builder
  - Depends on: PRJ-011, PRJ-012
  - Priority: P2
  - Validation:
    - `.\.venv\Scripts\python -m pytest -q`

Fresh Shell Tiering Pass (2026-04-28)

- `dashboard` guidance now uses explicit lead/support tiers instead of reading
  like a flatter stack of equal cards
- `chat` topbar controls now use a calmer premium density closer to the
  canonical reference rhythm
- `personality` highlight metrics now use one anchored feature tile plus
  supporting cards, reducing the equal-card dashboard feel
- Next smallest useful parity loop after deploy:
  - dashboard recent/intention relationship and lower-column pacing
  - chat support-column spacing against the portrait crop
  - personality mobile crop and side-panel compression

Final Flagship Detail Loop Freeze (2026-04-28)

- a detailed last-mile checklist now lives in:
  - `docs/planning/final-flagship-canonical-detail-checklist.md`
- `PRJ-772` is now DONE:
  - `.codex/tasks/PRJ-772-final-flagship-canonical-detail-loops.md`
- the verified implementation slice covered:
  - dashboard lower-rhythm and sidebar pacing
  - chat support-column hierarchy tightening
  - personality side-stack ordering and quieter recent-activity closure
  - later route proportion/density tuning for:
    - dashboard center-stage authority
    - chat transcript width hierarchy
    - personality embodied-stage balance and mobile callout compression
- validation:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
- next smallest parity loop after deploy:
  - dashboard hero-to-lower transition and scenic closure proportion
  - chat portrait crop versus support-panel spacing
  - personality mobile callout compression and side-panel stacking proof

Fresh Closure And Mobile Compression Pass (2026-04-28)

- `dashboard` now treats the flow band more like a flagship bridge and the
  scenic summary more like the route's final closure
- `chat` portrait crop and planning inset were both rebalanced for a calmer
  relationship on desktop and mobile
- `personality` mobile callouts are now narrower and more inward-facing, so
  the figure stage keeps more ceremonial balance under compression
- next smallest parity loop after deploy:
  - dashboard hero-scene crop and signal-card connector proportion
  - chat support-column proof against real transcript length
  - personality tablet/mobile screenshot proof for callout readability

Fresh Proportion And Density Pass (2026-04-28)

- `dashboard` center-stage authority was increased through a slightly larger
  hero figure area and longer signal connectors
- `chat` now gives more desktop room back to the transcript and uses tighter
  message-width hierarchy for longer reading comfort
- `personality` now uses a slightly taller hero and more inward mobile callout
  compression to preserve the ceremonial read
- validation after this pass:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
- next smallest parity loop after deploy:
  - dashboard screenshot proof for hero crop and scenic closure authority
  - chat screenshot proof with a longer real conversation
  - personality tablet/mobile proof for callout readability and overlap safety

Fresh Shell Spine And Route Calm Pass (2026-04-28)

- shared authenticated chrome is now calmer and more premium:
  - the desktop rail was narrowed slightly
  - utility bar controls were compacted
  - flagship routes now sit under lighter inset chrome
- `dashboard` now uses denser stage/sidebar spacing so the route reads more
  like one composed flagship scene
- `chat` now uses tighter transcript rhythm and quieter support-column spacing
  so context behaves more like supporting atmosphere than a second dashboard
- `personality` now keeps the side stack tighter so the embodied stage remains
  the ceremonial center
- validation after this pass:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
- next smallest parity loop after deploy:
  - dashboard screenshot proof for hero dominance versus sidebar pacing
  - chat proof with a longer real transcript against the support column
  - personality proof for tablet/mobile side-stack calmness

Fresh Closure Ceremony And Composer Unification Pass (2026-04-28)

- `dashboard` scenic closure is now taller, tighter, and more intentionally
  cropped so the route ends more like one flagship scene
- `chat` composer, action tray, and feature strip are now denser and more
  visually unified, reducing the feel of separate stacked widgets
- `personality` callouts now use slightly lighter cards and longer connector
  lines, so the embodied explanation reads more explicitly at a glance
- validation after this pass:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
- next smallest parity loop after deploy:
  - dashboard proof for one-screen read versus lower-grid drag
  - chat proof for empty-state and long-transcript elegance
  - personality proof for connector visibility and mobile ceremonial balance

Fresh One-Screen Read And Embodied Continuity Pass (2026-04-28)

- `dashboard` lower-grid and summary closure are now tighter so the route is
  closer to a one-screen flagship read
- `chat` preview transcript now feels more intentionally designed and less like
  a plain fallback state
- `personality` now links hero and timeline more explicitly through tighter
  shell rhythm and a more integrated timeline panel
- validation after this pass:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
- next smallest parity loop after deploy:
  - dashboard proof for lower-half drag versus canonical one-screen pacing
  - chat proof for preview state and long transcript density
  - personality proof for hero-to-timeline continuity and mobile balance

Fresh Dashboard Compaction Pass (2026-04-28)

- `dashboard` conversation-channel state now lives inside the guidance column
  as a compact support surface instead of a full-width second band
- `dashboard` flow notes were reduced to a tighter two-card finish so the
  route holds a more canonical one-screen feel
- validation after this pass:
  - `Push-Location .\web; npm run build; Pop-Location`
  - result: passed
- next smallest parity loop after deploy:
  - dashboard screenshot proof for total route height and flagship hierarchy
  - chat screenshot proof for transcript-first balance
  - personality screenshot proof for embodied-map calmness
