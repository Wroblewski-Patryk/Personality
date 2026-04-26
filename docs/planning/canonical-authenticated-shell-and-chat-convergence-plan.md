# Canonical Authenticated Shell And Chat Convergence Plan

## Purpose

This plan defines the next convergence lane needed to bring the authenticated
web shell and the `chat` route materially closer to the approved canonical
references.

The current implementation already captures much of the approved warmth,
material softness, and motif intent. The remaining gap is no longer basic
visual direction. The remaining gap is compositional fidelity:

- the parent authenticated shell still feels heavier and more dashboard-like
  than the canonical chat target
- the `chat` route still exposes too much process structure in the foreground
- the right side of the route is still too much of a module instead of a calm,
  ambient, useful support context
- future routes still need one stricter parent-shell grammar so `chat`,
  `personality`, `tools`, and `settings` feel like one product family

## Canonical Inputs

- `docs/ux/assets/aion-chat-canonical-reference-v2.png`
- `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`
- `docs/ux/assets/aion-personality-canonical-reference-v1.png`
- `docs/ux/aion-visual-motif-system.md`
- `docs/ux/canonical-web-screen-reference-set.md`
- `docs/ux/design-memory.md`
- `docs/ux/visual-direction-brief.md`
- `docs/ux/screen-quality-checklist.md`

## Current State Summary

The current shell is no longer a generic application frame. It already has:

- warm editorial materials
- reusable motif-aware surfaces
- a dedicated `chat` workspace
- a route-specific premium background artwork
- a stronger `personality` route than the earlier utility shell

That progress should be preserved.

The next work should not restart the system from zero.
It should reduce divergence from the canonical route targets while preserving
existing shared primitives where they still fit.

## Gap Analysis

### 1. Parent Shell Is Too Heavy For Canonical Chat

Current drift:

- the left rail is still broad, card-like, and visually dominant
- account and status blocks feel more like dashboard furniture than calm shell
  framing
- the route sits inside a strong boxed workspace, while the canonical target
  feels lighter and more continuous

Target posture:

- the authenticated shell should feel like elegant framing around the route,
  not like a second product inside the route
- navigation must become quieter and more architectural
- the route canvas should carry more of the emotional weight than the shell

### 2. Chat Still Carries Too Much Dashboard DNA

Current drift:

- `cognitive flow` is still a large, explicit process rail
- the bottom feature strip still reads like a distinct dashboard section
- several chat panels still compete with the transcript instead of supporting it

Target posture:

- `chat` must stay calmer than `dashboard`
- conversation must dominate the experience
- supporting context should be minimal, useful, and emotionally quiet

### 3. Transcript Components Are Still Too Inspector-Like

Current drift:

- assistant cards still read partly like structured data cards
- metadata and detail affordances are more explicit than in the canonical target
- transcript rhythm is more rectangular and modular than conversational

Target posture:

- message cards should feel lighter, softer, and more narrative
- timestamps and metadata should recede
- action affordances should feel editorial and companion-like rather than tool-like

### 4. Right-Side Support Column Needs A Different Hierarchy

Current drift:

- the portrait area still behaves like a hero card
- support content is split across a process rail and a separate lower card
- the current composition is denser than the canonical chat target

Target posture:

- the right side should become one restrained support column
- the embodied AION presence should feel ambient and emotionally resonant
- context cards should be smaller in number, clearer in purpose, and closer to:
  - intent
  - memory highlights
  - notes
  - suggested next step

### 5. Composer Is Closer, But Not Yet Canonical

Current drift:

- the composer is still visually separated from the surrounding quick actions
- action chips and composer controls do not yet read as one premium tray
- the send cluster still feels functional before it feels signature

Target posture:

- bottom chips and composer should feel like one beautifully integrated action zone
- controls should stay obvious but visually lighter
- the tray should look excellent on repeated daily use, not just in a single mockup

### 6. Cross-Route Shell Grammar Is Not Yet Strict Enough

Current drift:

- `personality`, `tools`, and `settings` reuse the current materials, but not
  yet the same top-level shell logic that the canonical set implies
- route chrome, side framing, and supporting panels still vary more than the
  canonical family suggests

Target posture:

- one parent authenticated shell should hold:
  - left navigation posture
  - top utility bar posture
  - route canvas proportions
  - secondary context behavior
  - bottom action or footer behavior rules
- each route should then specialize inside that shared frame

### 7. Responsive Translation Still Needs A Canonical Pass

Current drift:

- desktop is ahead of tablet and mobile in motif fidelity
- mobile still risks becoming a reduced copy of desktop instead of a
  purpose-built canonical interpretation

Target posture:

- tablet should become a deliberate middle composition
- mobile should preserve the same luxury and emotional clarity through crop,
  spacing, and control grouping

## Convergence Principles

### Preserve What Already Works

- keep the warm palette direction
- keep the editorial softness
- keep the approved route-specific art direction
- keep shared reusable primitives when they still fit the canonical route set

### Reduce Structural Noise Before Adding More Illustration

If a screen feels less premium than the canonical reference, first remove:

- excess panel boundaries
- repeated metadata
- duplicated support surfaces
- over-explicit process scaffolding

before adding:

- more glow
- more chips
- more cards
- more decorative layers

### Make Chat Calmer Than Dashboard

The canonical screen-set explicitly distinguishes the two.

- `dashboard` may stay more ceremonial and more informationally rich
- `chat` must remain softer, quieter, and more intimate

### Let Personality Carry The Richest Embodiment

The shell should support all routes, but `personality` should remain the
richest embodied-cognition explanation surface.

That means:

- `chat` should use the figure as support
- `personality` should use the figure as explanation

## Planned Execution Queue

### PRJ-734 Freeze Canonical Shell And Chat Convergence Contract

Purpose:
- record the current gap matrix and the approved target posture

Output:
- one execution-ready plan
- source-of-truth sync so the next implementation slices aim at the same
  convergence target

### PRJ-735 Shared Authenticated Shell Spine And Chrome Reduction

Purpose:
- refit the parent authenticated shell so it reads as one elegant frame across
  `chat`, `personality`, `tools`, and `settings`

Scope:
- left rail proportions
- top utility bar posture
- quieter account and status framing
- route canvas proportions
- shared spacing and framing rules

Acceptance focus:
- shell becomes less boxy, less dashboard-heavy, and more canonical

### PRJ-736 Chat Transcript, Quick Actions, And Composer Convergence

Purpose:
- move the conversation core toward the canonical premium-chat reading rhythm

Scope:
- transcript card softness
- message hierarchy
- inline action treatment
- quick-action chip row
- integrated composer tray

Acceptance focus:
- conversation-first hierarchy
- lighter metadata
- more graceful bottom action zone

### PRJ-737 Chat Support Column And Ambient Embodiment Convergence

Purpose:
- transform the right side of `chat` from a composed module stack into a calm,
  useful support column

Scope:
- reduce or restyle explicit process rail density
- rebalance portrait scale and crop
- introduce smaller, purpose-specific context cards
- align the right column more closely with canonical intent/memory/note/next-step posture

Acceptance focus:
- right side becomes supportive, not competitive
- AION presence feels ambient, not panelized

### PRJ-738 Personality Convergence On The Shared Canonical Shell

Purpose:
- ensure `personality` inherits the improved parent shell while keeping its
  richer embodied map role

Scope:
- migrate `personality` framing onto the updated shell
- preserve the route as the richest motif explanation surface
- align supporting side panels with the calmer canonical family

Acceptance focus:
- `personality` feels like the same product as `chat`, but with deeper
  embodied cognition density

### PRJ-739 Shared Route Art, Material, And Typography Polish

Purpose:
- close the remaining premium-gap across motif-led routes through shared
  visual refinements instead of route-local hacks

Scope:
- typography hierarchy
- panel edge treatment
- icon and chip weight
- supporting illustration crops or route-specific artwork where approved

Acceptance focus:
- the product reads as one luxury-calibrated system, not several adjacent route skins

### PRJ-740 Responsive, State, And Accessibility Proof

Purpose:
- verify that the convergence work survives real product use

Scope:
- desktop
- tablet
- mobile
- loading
- empty
- error
- success
- touch
- pointer
- keyboard
- contrast
- reduced motion

Acceptance focus:
- no breakpoint loses the canonical product character

### PRJ-741 Production Screenshot Parity And Baseline Freeze

Purpose:
- compare live or deploy-equivalent captures against the canonical route assets
  and freeze the accepted baseline

Scope:
- post-deploy screenshot capture
- gap notes
- final design-memory and context sync

Acceptance focus:
- accepted parity is evidenced, not assumed

## Acceptance Criteria For The Lane

This convergence lane is complete when:

- the authenticated shell clearly behaves as one parent frame across motif-led routes
- `chat` is visibly calmer than `dashboard`
- `chat` keeps conversation as the primary experience
- the right support area becomes minimal, useful, and emotionally resonant
- `personality` inherits the same shell while remaining the richest embodied route
- desktop, tablet, and mobile all preserve the canonical family feeling
- accepted post-deploy screenshots are compared against the canonical references

## Risks To Watch

- overfitting the current implementation to one static desktop image and
  hurting repeated-use ergonomics
- adding more decorative layers instead of reducing compositional noise
- letting `chat` inherit too much `dashboard` structure
- polishing route-local details before the parent shell is corrected
- converging desktop while leaving mobile and tablet behind

## Recommended Working Order

1. refit the parent shell
2. simplify the `chat` core
3. rebalance the `chat` support column
4. port the improved shell to `personality`
5. do one shared premium polish pass
6. prove responsive, state, accessibility, and production parity
