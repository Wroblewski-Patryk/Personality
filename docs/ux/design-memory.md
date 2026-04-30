# Design Memory

## Approved Reuse Patterns

- Conversation shell:
  Keep message reading effortless and input affordances stable across states.
- Safe Markdown chat messages:
  Render transcript Markdown as semantic message content inside the existing
  chat bubble pattern, using escaped React-rendered elements for emphasis,
  lists, and code. Do not use raw HTML injection for user-authored content, and
  let long message bodies expand naturally inside the transcript scroll surface
  instead of clamping the bubble.
- Settings groups:
  Prefer clear sectioning, short helper copy, and visible save or success
  feedback.
- Capability cards:
  Show current state, user control, and trust implications in one compact
  surface.
- Embodied cognition motif:
  Use one humane synthetic figure, anchored pins, and timeline rails to map
  internal cognition concepts into memorable product visuals without turning the shell into a
  sci-fi console.
- Timeline-backed metadata:
  Attach labels, chips, and mini-stats to explicit rails or sections instead of
  leaving metadata as floating decorative fragments.
- Chat background artwork:
  Use one route-specific right-weighted illustration with strong negative space
  on the left for transcript readability, instead of trying to fake the full
  premium effect from gradients alone.
- Personality figure artwork:
  Use one route-specific embodied figure asset with enough negative space for
  anchored callouts and side panels, instead of relying on generic CSS-only
  humanoid placeholders.
- Shared canonical persona figure:
  Reuse one approved Aviary persona figure across `landing`, `dashboard`,
  `chat`, `personality`, and other flagship modules. Adapt the crop, callout
  map, and supporting objects to the route context instead of inventing a
  different being per screen.
- Route-specific persona adaptation:
  Keep one continuous Aviary identity across flagship routes, but do not reuse
  the exact same pose-and-props composition everywhere. The route decides the
  supporting objects:
  - `personality`: knowledge-and-identity props such as book, writing tool,
    page, symbolic mapping anchors
  - `dashboard`: orchestration, guidance, cognition-field, and overview props
    rather than personality-specific study props
  - `chat`: conversation, continuity, listening, and response-shaping props
  - `landing`: welcoming, trust, and orientation props with the calmest
    composition
  Route-specific adaptation is required unless the user explicitly approves a
  repeated composition.
- Flagship utility bar:
  Use one calm top utility band with search, compact actions, and account
  posture to give authenticated routes dashboard-grade framing without
  inventing route-local chrome.
- Flagship overview stage:
  Use one central embodied stage with flanking signal cards, a guidance column,
  and a cognitive-flow band so `dashboard` feels like the conductor of the
  shell instead of a generic analytics grid.
- Dashboard scenic closure:
  When the flagship dashboard starts feeling flat, add bespoke raster artwork
  to the intention card and the lower summary band before piling on more CSS
  decoration.
- Dashboard cognition field:
  When the central dashboard hero still feels too generic, add one dedicated
  scenic atmosphere asset behind the figure and use light connective ornament
  before adding more standalone cards.
- Unified dashboard hero artwork:
  When the canonical dashboard depends on one continuous scenic composition,
  prefer one wide raster hero artwork that already integrates the shared
  persona, aura, and right-side cognition detail instead of layering a separate
  figure asset over a second atmosphere image.
  For `dashboard`, do not reuse the `personality` prop family such as the book,
  page, or writing tool. The dashboard hero should instead use guidance,
  orchestration, overview, and cognition-field symbols.
- Frame-first flagship shell:
  Keep the public and authenticated shells premium, inset, and composed, but
  do not simulate browser controls, title bars, or fake window chrome as part
  of the canonical layout.
- Canonical authenticated sidebar spine:
  Use one narrow premium rail with brand block, icon-led module stack, system
  health card, signed-in identity card, and quiet aphorism closure as the
  reusable left spine for authenticated routes instead of route-local or
  analytics-style sidebars.
- Landing-first public entry:
  Keep authentication as one conversion module inside a broader trust-led
  landing story with hero, embodied motif, feature strip, and trust closure
  instead of making sign-in the whole page.
- Public auth as modal continuation:
  On the public landing, session entry should open as a modal layer over the
  flagship scene instead of appearing as a co-equal inline section beneath the
  trust closure.
- Scenic background treatment:
  When a route-specific hero illustration is meant to behave like atmosphere or
  stage art, render it as the scenic background layer of the section instead of
  as an obvious nested image card inside another card.
- Landing hero stage composition:
  Keep the public landing copy and scenic figure inside one shared hero stage,
  with roughly a `40/60` split between copy and scene on desktop. Avoid
  redundant nested scenic wrappers when the artwork is already acting as the
  route background. The landing copy should sit on top of that same scenic
  stage, not beside it in a separate sibling column.
- Integrated composer tray:
  Keep the main chat input, send control, and low-priority support actions
  inside one shared tray so the conversation footer reads like one premium
  surface instead of stacked unrelated controls.
- Brand logotype and font pairing:
  Use the canonical Aviary bird logomark with the `AVIARY` wordmark in
  `Cormorant Garamond` for major headers and `Inter` for operational UI,
  instead of mixing unrelated display and body families across routes.
- Product naming boundary:
  keep `Aviary` for app-brand surfaces, while the embodied personality remains
  unnamed until a later identity-forming product decision.
- Surface-first flagship closure:
  Close one flagship surface at a time and do not open the next dependent
  route until the current one is visually at least `95%` aligned with the
  active spec.
- Canonical spec with user interpretation:
  When a canonical screenshot exists, treat it as the base spec, but merge in
  explicit user-requested deviations as approved interpretation notes instead
  of ignoring them or silently reverting to the image.
- Canonical conflict escalation:
  If two user-requested visual notes conflict, or if a new note conflicts with
  a previously accepted interpretation, stop and ask the user which direction
  should win before implementing.

## Reuse Notes

- New UX patterns should improve calmness and trust, not add novelty.
- Record proven patterns here when they should guide future shell work.
- The approved reference for the embodied cognition motif now lives in
  `docs/ux/aion-visual-motif-system.md`.
- The current approved chat art direction reference now also includes
  `docs/ux/assets/aion-chat-background-reference-v1.png`.
- The current approved personality route preview now also includes
  `docs/ux/assets/aviary-persona-figure-canonical-reference-v1.png`.
- The current approved flagship-shell pattern now includes a shared utility
  top bar reused across premium authenticated routes.
- The current approved canonical web screen-set now lives in
  `docs/ux/canonical-web-screen-reference-set.md`.
- The current approved dashboard hero implementation asset now includes
  `docs/ux/assets/aviary-dashboard-hero-canonical-reference-v4.png`.
- The current approved landing hero implementation asset now includes
  `docs/ux/assets/aviary-landing-hero-canonical-reference-v1.png`.
- Future web UX tasks should capture post-deploy screenshots and compare them
  directly against the canonical screen-set instead of relying only on memory
  or prompt descriptions.
- Future flagship UX tasks should use a `95%` parity gate per surface instead
  of polishing multiple screens in parallel.
- When a canonical screenshot drives implementation, record background and
  decorative fidelity rules here so future parity passes reuse them instead of
  flattening them into generic gradients.
## 2026-04-30 - Public home full-bleed shell framing

- The public `home` surface should not read as a nested panel or browser-like
  window.
- Use full-width `header`, `hero`, and `footer` sections, each with its own
  full-width shell/background treatment.
- Keep inner navigation, hero copy, bridge content, and trust-band content
  visually aligned through a consistent max-width rhythm, even if the DOM does
  not use a separate wrapper for every section.
- On wide screens, let the public navigation float above the scenic hero
  background rather than sitting inside a separate framed card.
- Treat the landing artwork as the hero-stage background, not as an image
  nested inside another visible container.
