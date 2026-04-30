# Design Memory

## Approved Reuse Patterns

- Conversation shell:
  Keep message reading effortless and input affordances stable across states.
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
  `docs/ux/assets/aviary-dashboard-hero-canonical-reference-v3.png`.
- Future web UX tasks should capture post-deploy screenshots and compare them
  directly against the canonical screen-set instead of relying only on memory
  or prompt descriptions.
- Future flagship UX tasks should use a `95%` parity gate per surface instead
  of polishing multiple screens in parallel.
- When a canonical screenshot drives implementation, record background and
  decorative fidelity rules here so future parity passes reuse them instead of
  flattening them into generic gradients.
