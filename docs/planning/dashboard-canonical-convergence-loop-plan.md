# Dashboard Canonical Convergence Loop Plan

## Purpose

This document freezes one explicit compare-plan-build loop for the authenticated
`dashboard` route.

The route now exists and is directionally aligned with the approved dashboard
reference, but it still does not fully reproduce the canonical flagship
composition in the browser.

This plan records the current drift in implementation terms so future loops can
close the gap deliberately instead of relying on general polish language.

## Canonical Target

- `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`

## Evidence Baseline

- public production deploy now serves runtime build revision:
  - `ffd9401766e5219366feeed65804ce8585ed0aed`
- public root HTML also exposes:
  - `meta[name="aion-web-build-revision"]`
  - `content="ffd9401766e5219366feeed65804ce8585ed0aed"`
- authenticated screenshot parity still needs a browser-capable logged-in pass
  against the deployed shell

## Current Implementation Baseline

- `/dashboard` now exists as the first authenticated route
- default post-login navigation now lands on `/dashboard`
- the route already includes:
  - shared premium shell
  - central embodied figure stage
  - signal cards
  - guidance column
  - cognitive-flow band
  - lower overview cards

## Gap Matrix

### 1. Shell Depth Gap

What currently drifts:

- the left rail is calmer and stronger than before, but still lacks the exact
  compositional confidence of the canonical dashboard shell
- the shell does not yet create the same "app inside a ceremonial surface"
  feeling as the reference

What the canonical target shows:

- navigation feels deeply integrated into one editorial frame
- rail support cards are not just utility blocks; they feel like part of the
  flagship narrative
- utility chrome and the main canvas feel equally premium

Implementation direction:

- continue strengthening shared shell materials
- keep rail support cards as narrative surfaces, not generic status modules
- verify desktop proportions after deploy, not just in local code

### 2. Hero Stage Composition Gap

What currently drifts:

- the figure stage is directionally correct but still simpler than the
  canonical centerpiece
- the current stage lacks enough environmental detail, connective structure,
  and fine-grain ceremonial framing around the figure
- side cards feel adjacent to the figure rather than visibly connected to it

What the canonical target shows:

- the figure feels embedded in one luminous cognition field
- side metric cards and the figure are connected by intentional visual lines
- the background atmosphere contributes meaningful depth rather than acting as
  a neutral container

Implementation direction:

- add more intentional connective ornament or dedicated art layers around the
  figure stage
- prefer route-specific background artwork over CSS-only atmosphere when the
  current gradients stop being sufficient
- tighten figure crop and vertical balance so the stage feels anchored rather
  than simply centered

### 3. Guidance Column Gap

What currently drifts:

- the guidance column is structurally present, but still not as refined or as
  vertically tiered as the canonical reference
- the lower intention story still reads more like a pleasant panel than a
  flagship concluding note

What the canonical target shows:

- a top block for curated guidance
- a separate recent-activity cluster
- a bottom story/intention card with stronger visual gravity

Implementation direction:

- preserve the three-tier hierarchy explicitly
- increase contrast between guidance cards, recent activity, and the closing
  intention story
- consider a dedicated background artwork for the closing intention surface

### 4. Cognitive Flow Band Gap

What currently drifts:

- the band now has the right parts, but it still reads more like a composed
  component group than the elegant central rail shown in the reference
- the current implementation still carries too much card logic and not enough
  "single continuous instrument" feeling

What the canonical target shows:

- one dominant horizontal cognition rail
- current phase visible as part of the same orchestration object
- lower visual noise despite many semantic stages

Implementation direction:

- reduce perceived fragmentation inside the flow band
- refine spacing, connector logic, and active-stage emphasis
- make the side summary feel integrated into the band rather than attached

### 5. Lower Card Family Gap

What currently drifts:

- the bottom cards are useful and premium, but still not as visually distinct
  and art-directed as the canonical dashboard
- several cards remain too "component-like" rather than feeling like bespoke
  flagship modules

What the canonical target shows:

- active goals with strong but quiet progress rhythm
- current focus with a more atmospheric visual core
- memory growth with cleaner visual storytelling
- reflection highlights with lighter density and stronger editorial spacing
- bottom summary band with scenic closure

Implementation direction:

- continue route-specific treatment of the lower cards
- introduce dedicated background art when CSS-only treatment starts flattening
  the route
- prefer fewer stronger visual signatures over more box styling

### 6. Canonical Asset Dependency Gap

What currently drifts:

- some surfaces are already art-backed, but several dashboard details still
  depend on gradients and decorative CSS where the canonical view clearly
  relies on bespoke imagery

What the canonical target implies:

- at least some of the dashboard premium effect comes from dedicated visual
  assets, not just layout polish

Implementation direction:

- generate route-specific dashboard support artwork when:
  - the hero background needs more depth
  - the intention card needs richer closure
  - the bottom summary band needs scenic atmosphere
- store any approved generated assets in both:
  - `docs/ux/assets/`
  - `web/public/`

## Required Loop For Each Next Pass

1. compare the current browser result to the canonical dashboard asset
2. write down the next smallest visible gap
3. implement only that bounded gap
4. run:
   - `Push-Location .\web; npm run build; Pop-Location`
5. capture fresh proof
6. update:
   - `.codex/context/PROJECT_STATE.md`
   - `.codex/context/TASK_BOARD.md`
   - relevant task file
7. repeat until the route feels materially indistinguishable in structure,
   hierarchy, and atmosphere

## Immediate Next Slice Recommendation

The next best dashboard-only slice should focus on:

- hero-stage connective detail and atmosphere
- intention-card art direction
- bottom summary-band atmosphere
- deploy-backed screenshot parity for authenticated desktop first

## Related Sources

- `docs/ux/canonical-web-screen-reference-set.md`
- `docs/ux/design-memory.md`
- `docs/ux/screen-quality-checklist.md`
- `docs/ux/experience-quality-bar.md`
