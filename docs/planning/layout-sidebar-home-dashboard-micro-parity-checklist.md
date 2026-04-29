# Layout, Sidebar, Home, Dashboard Micro Parity Checklist

## Purpose

This checklist supplements:

- `docs/planning/layout-sidebar-home-dashboard-canonical-parity-master-ledger.md`

The master ledger captures structural drift and execution order.
This checklist goes one level deeper and enumerates the visible sub-elements
that must be checked before the corresponding surface can be called
canonically close.

It exists to answer one question honestly:

`Did we review every major visible element?`

For this lane, the answer should only become `yes` when each item below is
either:

- matched
- intentionally deferred with reason
- or explicitly blocked by route-contract scope

## Audit Status Legend

- `MATCHED`: already close enough for this lane
- `DRIFT`: visible difference still requires implementation
- `BLOCKED`: cannot be closed without explicit scope decision

## 1. Authenticated Parent Layout

### 1.1 Outer shell frame

- Shell max width and inset margin: `DRIFT`
- Shell corner radius versus canonical softness: `DRIFT`
- Shell border visibility versus canonical subtlety: `DRIFT`
- Shell inner padding top/bottom/side balance: `DRIFT`
- Shell atmospheric background staying supportive, not dominant: `MATCHED`

### 1.2 Rail-to-canvas relationship

- Desktop rail width versus canonical proportion: `DRIFT`
- Gap between rail and route canvas: `DRIFT`
- First content edge alignment after the rail: `DRIFT`
- The route canvas visually dominating the shell: `DRIFT`

### 1.3 Utility bar

- Utility bar height and vertical density: `DRIFT`
- Utility bar corner radius and surface weight: `DRIFT`
- Utility bar reading as premium framing, not generic chrome: `DRIFT`
- Search/control cluster pacing: `DRIFT`
- Account posture inside utility bar: `DRIFT`

### 1.4 Account management behavior

- Compact identity in sidebar only: `MATCHED`
- Expanded desktop account surface staying quiet: `DRIFT`
- Expanded account surface not interrupting route composition: `DRIFT`

### 1.5 Mobile/tablet parent shell

- Mobile header hierarchy: `DRIFT`
- Mobile route switcher reading as deliberate flagship shell: `DRIFT`
- Tablet shell composition distinct from simple desktop collapse: `DRIFT`

## 2. Authenticated Sidebar

### 2.1 Brand block

- Mark-to-word spacing: `DRIFT`
- Wordmark scale: `DRIFT`
- Subtitle spacing and alignment: `DRIFT`
- Entire lockup feeling left-anchored instead of centered component: `DRIFT`

### 2.2 Navigation stack

- Exact row height: `DRIFT`
- Exact vertical gap between rows: `DRIFT`
- Icon stroke/lightness: `DRIFT`
- Label x-position relative to icon: `DRIFT`
- Hover state subtlety: `DRIFT`
- Active pill length and softness: `DRIFT`
- Active text/icon contrast versus canonical screenshot: `DRIFT`

### 2.3 Inventory contract

- Canonical missing items represented: `BLOCKED`
- Current-route-only inventory documented: `MATCHED`

### 2.4 Health card

- Card height: `DRIFT`
- Internal top/bottom padding: `DRIFT`
- Emblem size relative to card: `DRIFT`
- Emblem complexity relative to canonical diagnostic star: `DRIFT`
- Status line hierarchy: `MATCHED`
- Quiet button proportion: `DRIFT`

### 2.5 Identity card

- Card height and breathing room: `DRIFT`
- Persona crop inside avatar: `DRIFT`
- Name/role text hierarchy: `DRIFT`
- Chevron subtlety: `DRIFT`

### 2.6 Closure quote card

- Quote mark source text cleanliness: `DRIFT`
- Quote line-break and width: `DRIFT`
- Signature treatment: `DRIFT`
- Decorative wash at the bottom: `MATCHED`
- Card acting as quiet closure rather than another widget: `DRIFT`

## 3. Public Layout And Home

### 3.1 Public nav

- Nav height and spacing: `DRIFT`
- Nav links density: `DRIFT`
- CTA pair proportion and hierarchy: `DRIFT`
- Nav integrating into landing rather than floating above it: `DRIFT`

### 3.2 Hero left column

- Headline line breaks relative to canonical screenshot: `DRIFT`
- Headline scale relative to the figure stage: `DRIFT`
- Body copy width and vertical rhythm: `DRIFT`
- CTA row priority and spacing: `DRIFT`
- Pill cluster under CTAs being too noisy: `DRIFT`

### 3.3 Hero right stage

- Persona crop scale relative to full hero: `DRIFT`
- Negative space around figure: `DRIFT`
- Anchored cognition-card positions: `DRIFT`
- Stage reading as one composed scene: `DRIFT`
- Painterly atmosphere retained via real asset strategy: `MATCHED`

### 3.4 Bridge band

- Feature strip reading as elegant bridge rather than row of cards: `DRIFT`
- Proof bridge copy and pill balance: `DRIFT`
- The whole band acting as a continuation of the hero: `DRIFT`

### 3.5 Lower public story

- Auth panel visual priority versus public story: `DRIFT`
- Proof column reading editorially instead of stacked support cards: `DRIFT`
- Quote card prominence and placement: `DRIFT`
- Trust band closure gesture: `DRIFT`

### 3.6 Public responsive behavior

- Hero collapse on tablet: `DRIFT`
- Mobile CTA rhythm: `DRIFT`
- Mobile proof and auth ordering: `DRIFT`
- Trust band compression on mobile: `DRIFT`

## 4. Dashboard

### 4.1 Intro zone

- Greeting emblem quality and source text cleanliness: `DRIFT`
- Greeting copy compactness: `DRIFT`
- Chips under intro copy being supportive rather than attention-taking: `DRIFT`
- Intro zone visually merging into the hero instead of reading as a page header: `DRIFT`

### 4.2 Central hero stage

- Central figure crop authority: `DRIFT`
- Persona note placement: `DRIFT`
- Persona note scale and translucency: `DRIFT`
- Halo/atmosphere strength: `DRIFT`
- Caption card size and placement: `DRIFT`
- Badge relation to caption and hero edge: `DRIFT`

### 4.3 Side signal columns

- Card widths relative to center stage: `DRIFT`
- Connector-line feeling: `DRIFT`
- Internal text density: `DRIFT`
- Collective reading as one cognition scene rather than two small stacks: `DRIFT`

### 4.4 Hero note bridge

- Note width: `DRIFT`
- Note copy length: `DRIFT`
- Border softness and separation from the hero: `DRIFT`

### 4.5 Right editorial rail

- Lead-card dominance: `DRIFT`
- Secondary-card flattening: `DRIFT`
- Intention card authority: `DRIFT`
- Conversation channel card compactness: `DRIFT`
- Recent activity card quietness: `DRIFT`
- Whole column reading as one support rail: `DRIFT`

### 4.6 Flow band

- Whether it still feels like a module instead of an instrument: `DRIFT`
- Density of tokens and copy: `DRIFT`
- Relation to the hero and lower blocks: `DRIFT`

### 4.7 Lower region

- Number of equally important cards: `DRIFT`
- Goals/focus/memory/reflection balance: `DRIFT`
- Scenic closure authority: `DRIFT`
- Whether the route still feels like two screens stacked: `DRIFT`

### 4.8 Dashboard responsive behavior

- Tablet hero dominance: `DRIFT`
- Support column behavior on narrower widths: `DRIFT`
- Lower region collapse preserving flagship reading: `DRIFT`

## 5. Route-Level 1:1 Risks

- Missing canonical sidebar routes will continue to create a visible inventory
  delta until route expansion is approved.
- The shell will keep feeling product-like until the account surface and
  utility bar are demoted.
- The landing will keep feeling auth-derived until the lower public grid is
  redesigned structurally.
- The dashboard will keep feeling sectioned until the lower half is simplified
  and the hero gains more dominance.

## 6. Execution Use

Each implementation pass for this lane should now:

1. pick one section from the master ledger
2. use the matching sub-elements from this checklist as acceptance gates
3. record which items moved from `DRIFT` to `MATCHED`
4. leave the rest visible for the next pass

