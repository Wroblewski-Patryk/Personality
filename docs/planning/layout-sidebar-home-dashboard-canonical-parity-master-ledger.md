# Layout, Sidebar, Home, Dashboard Canonical Parity Master Ledger

## Purpose

This document is the current master audit for the highest-value visual
convergence lane in the web app:

- authenticated parent layout
- authenticated sidebar
- public layout
- public home / landing
- authenticated dashboard

The target is not general aesthetic similarity.
The target is execution-ready, screenshot-driven convergence toward the
canonical references already frozen in `docs/ux/`.

## Canonical Sources

- `docs/ux/canonical-web-screen-reference-set.md`
- `docs/ux/assets/aviary-sidebar-layout-canonical-reference-v1.png`
- `docs/ux/assets/aion-landing-canonical-reference-v1.png`
- `docs/ux/assets/aion-dashboard-canonical-reference-v2.png`
- `docs/ux/assets/aviary-persona-figure-canonical-reference-v1.png`
- `docs/ux/visual-direction-brief.md`
- `docs/ux/experience-quality-bar.md`
- `docs/ux/screen-quality-checklist.md`
- `docs/ux/background-and-decorative-asset-strategy.md`

## Current Implementation Surfaces

- `web/src/App.tsx`
- `web/src/index.css`

## Audit Basis

This ledger compares:

1. the frozen canonical references
2. the current route and shell structure in `web/src/App.tsx`
3. the current visual system and responsive rules in `web/src/index.css`
4. the latest approved shell decisions already recorded in:
   - `docs/planning/layout-dashboard-public-home-canonical-master-audit.md`
   - `docs/planning/sidebar-layout-canonical-convergence-plan.md`
   - `docs/ux/design-memory.md`

## Executive Summary

The product is no longer far from the canonical mood, but it is still far from
canonical composition.

The most important finding is that the remaining drift is now mostly structural
and hierarchical:

- the parent layout still behaves like a polished app shell, not a flagship
  frame hosting ceremonial module screens
- the sidebar is much closer, but still not pixel-close in lockup alignment,
  rhythm, inventory posture, and support-card finish
- the public home is improved in the first viewport, but the full-page story
  still reads like a converted auth page rather than a purpose-built editorial
  landing
- the dashboard is visually rich, but still too modular and too long in
  reading rhythm compared with the canonical one-screen flagship tableau

## Primary Conclusion

Further random polishing will now produce diminishing returns.

The next effective implementation sequence must be:

1. shell and layout frame exactness
2. sidebar exactness
3. public home exactness
4. dashboard exactness
5. only then additional route polish

## Detailed Gap Ledger

### 1. Authenticated Parent Layout

#### 1.1 Shell framing

Canonical target:

- one premium inset canvas
- left rail as structural spine
- route surface as dominant object
- almost no visible "app chrome"

Current drift:

- the shell still reads as `sidebar + utility bar + page cards`
- the top utility bar is useful but still too obviously a reusable app-control
  strip rather than part of one flagship composition
- content starts too abruptly under the utility bar
- the shell stage background is still a diffuse atmospheric layer rather than
  a deliberate frame that increases the authority of the active screen

Required change:

- reduce visible shell chrome hierarchy above route content
- increase the sense that the route surface itself is the hero object
- tighten the gap logic between rail, utility bar, and active canvas

Files likely touched:

- `web/src/App.tsx`
- `web/src/index.css`

#### 1.2 Desktop account surface

Canonical target:

- sidebar contains only compact identity posture
- account management should not interrupt the flagship frame

Current drift:

- desktop account panel still appears as a separate wide admin surface
- when open, it weakens route composition and competes with dashboard or other
  screens

Required change:

- move account management into a lighter drawer/dropover or quieter auxiliary
  posture
- avoid introducing a second large panel above flagship content

#### 1.3 Mobile/tablet shell

Canonical target:

- intentional sibling composition to desktop
- not just desktop shell collapsing into utility rows and pills

Current drift:

- mobile header still reads like a practical fallback
- route switching and account controls are serviceable, but not yet canonical

Required change:

- redesign mobile shell framing as a deliberate composition after desktop shell
  is locked

### 2. Authenticated Sidebar

#### 2.1 Lockup alignment

Canonical target:

- brand mark and wordmark read as one delicate top-left lockup
- subtitle sits as a quieter continuation of the same block

Current drift:

- current sidebar lockup still feels too centered and too componentized
- current scale and spacing are close, but not yet as delicate as the canonical
  screenshot

Required change:

- shift toward a more left-anchored editorial lockup
- reduce visible "widget" feeling in the header of the rail

#### 2.2 Nav inventory contract

Canonical target:

- Dashboard
- Chat
- Personality
- Memory
- Reflections
- Plans
- Goals
- Insights
- Tools
- Automations
- Integrations
- Settings

Current drift:

- current contract exposes only:
  - dashboard
  - chat
  - personality
  - tools
  - settings

Decision still required for final 1:1:

1. layout-only parity on current routes
2. route-shell expansion to support full canonical inventory

Recommended execution:

- do not invent fake routes
- finish visual parity on current implemented inventory first
- then explicitly expand route shells if the product scope confirms it

#### 2.3 Nav button anatomy

Canonical target:

- thin line icons
- softer long active pill
- one-line labels
- perfectly consistent button rhythm

Current drift:

- current button treatment is good, but still slightly heavier and more
  component-like
- active pill is still too obviously a UI state component rather than a soft
  selection glow

Required change:

- further soften border contrast
- slightly lengthen and simplify active-state geometry
- tune icon/label spacing to match the canonical rail more exactly

#### 2.4 Support stack

Canonical target:

- health card
- compact identity card
- quiet closure card

Current drift:

- health card is close but still too orb-forward
- identity card is close but still slightly too operational
- quote card still relies on CSS content to correct encoded text instead of
  clean source copy

Required change:

- clean quote copy in source, not only through pseudo-elements
- reduce health emblem visual weight
- further tighten support-card heights and spacing

### 3. Public Layout And Public Home

#### 3.1 Narrative hierarchy

Canonical target:

- landing-first story
- auth as one module
- trust and value proposition before mechanics

Current drift:

- first viewport is materially improved, but downstream composition still
  reveals its auth-first origin
- the auth block remains one of the strongest objects too early in the page
- proof column still reads like stacked support cards rather than premium
  editorial continuation

Required change:

- demote auth module below the product story
- increase editorial flow in the proof and continuation sections
- make the page read as one landing, not hero plus auth grid

#### 3.2 First viewport

Canonical target:

- immediate promise
- stronger emotional trust anchor
- more sculpted right-side figure balance

Current drift:

- the hero is directionally right, but still too balanced between left copy and
  right stage
- the canonical landing gives slightly more authority to the embodied right
  scene and slightly calmer control density on the left

Required change:

- rebalance hero columns again toward stronger right-side authority
- reduce pill noise under the CTA cluster
- make the hero read more like one scene and less like copy plus supporting
  module

#### 3.3 Mid-page bridge and story grid

Canonical target:

- elegant feature bridge
- proof/testimonial rhythm
- quieter trust continuation

Current drift:

- current feature bridge still contains too many repeated "cards"
- current auth/proof lower grid is practical but not editorial
- current trust band is useful but not yet a memorable closure gesture

Required change:

- reduce repeated boxed-card rhythm
- convert part of the lower public grid into more open band/list composition
- strengthen one calm testimonial or trust-led centerpiece

### 4. Dashboard

#### 4.1 Hero authority

Canonical target:

- center figure dominates
- side cards feel connected to the same cognition field
- hero reads as one tableau

Current drift:

- current dashboard hero is rich, but still slightly too "figure plus panels"
- left and right signal columns still feel like adjacent card stacks
- greeting/copy zone above the hero still behaves like page intro copy more
  than integrated hero framing

Required change:

- compress intro copy
- increase central-stage authority relative to sidecards
- reduce independent panel feeling in side columns

#### 4.2 Right editorial column

Canonical target:

- one elegant column with clear lead/support hierarchy

Current drift:

- current guidance/intention/channel/recent stack is improved, but still reads
  like multiple well-designed cards rather than one editorial support rail

Required change:

- give one clear lead card
- flatten the visual priority of secondary cards
- reduce card-family variety

#### 4.3 Lower route rhythm

Canonical target:

- one-screen flagship read
- lower region supports the hero, not competes with it

Current drift:

- lower dashboard still contains too many equally important blocks
- route can still feel like "hero plus another dashboard beneath"
- scenic closure exists, but does not yet fully own the ending

Required change:

- reduce lower-grid density
- merge or quiet secondary metrics
- let one closure composition carry the route ending

#### 4.4 Dashboard-specific persona adaptation

Canonical target:

- same persona as shared canonical figure
- dashboard-specific callouts
- orchestration-oriented posture

Current drift:

- `PRJ-795` improved this a lot, but callout placement and crop still need live
  screenshot tuning
- current dashboard note cards are structurally right, but not yet obviously
  canonical in spacing or authority

Required change:

- do a deploy screenshot loop for:
  - note placement
  - crop
  - central-stage dominance
  - relation between caption, badge, and side cards

## Canonical 1:1 Blocking Issues

These are the issues most likely to prevent final screenshot parity even after
smaller polish:

1. sidebar inventory mismatch versus current route contract
2. shell/account-panel behavior not yet aligned with canonical compositional
   restraint
3. public home lower-half story still structurally auth-derived
4. dashboard still too long in reading hierarchy below the hero

## Recommended Execution Queue

### PRJ-800A Parent Layout Frame Exactness

Goal:

- finish the authenticated shell frame so route canvases dominate and shell
  chrome recedes

Scope:

- `web/src/App.tsx`
- `web/src/index.css`

Definition of done:

- utility bar hierarchy reduced
- account surface no longer interrupts flagship reading
- shell gap/padding rhythm supports route hero authority

### PRJ-800B Sidebar Pixel-Close Pass

Goal:

- achieve near-1:1 rail proportion, lockup, active pill, and support-stack
  finish on current implemented routes

Scope:

- `web/src/App.tsx`
- `web/src/index.css`

Definition of done:

- rail matches canonical proportions and rhythm closely
- support stack no longer needs CSS-content correction tricks
- route inventory policy for missing items is explicitly documented

### PRJ-800C Public Home Structural Convergence

Goal:

- move the full landing from "hero + auth page" to canonical editorial landing

Scope:

- `web/src/App.tsx`
- `web/src/index.css`

Definition of done:

- auth module becomes secondary to landing story
- lower public grid becomes more editorial and less card-driven
- first viewport and continuation feel like one composed public surface

### PRJ-800D Dashboard Canonical Composition Pass

Goal:

- compress dashboard into a more canonical one-screen flagship read

Scope:

- `web/src/App.tsx`
- `web/src/index.css`

Definition of done:

- hero clearly dominates
- right column is more editorial than modular
- lower region supports the hero instead of competing with it

### PRJ-800E Screenshot-Parity Closure

Goal:

- compare deployed `layout + sidebar + home + dashboard` directly to the
  canonical references and tune the remaining visible mismatches

Evidence required:

- desktop
- tablet
- mobile where relevant
- parity notes for loading, empty, error, and success if touched in scope

## Validation Expectations For The Next Execution Lane

Before calling any of these surfaces close to final:

- run `Push-Location .\web; npm run build; Pop-Location`
- capture fresh screenshots after the route is running
- compare screenshots directly against:
  - `aviary-sidebar-layout-canonical-reference-v1.png`
  - `aion-landing-canonical-reference-v1.png`
  - `aion-dashboard-canonical-reference-v2.png`
- record exact remaining mismatches in task notes

## Final Planning Note

The repo is no longer at the "invent the direction" stage for these surfaces.

It is now at the "close exact visible differences with discipline" stage.

That means future changes for this lane should prefer:

- fewer but larger structural passes
- screenshot-driven parity proof
- less card invention
- less shell chrome
- more authority for the canonical compositions

