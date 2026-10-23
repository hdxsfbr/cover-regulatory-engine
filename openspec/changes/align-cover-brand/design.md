# Design

## Context
The current UI has a green palette, Google-hosted fonts, text-only logo and native disclosure triangles. The supplied Cover homepage uses an actual symbol/wordmark, charcoal (#202020), white, warm gray (#808076), mixed Roman-serif/sans headings and plus controls.

## Goals / Non-Goals
Goals: recognizable brand alignment, calmer information hierarchy, locally available identity assets, readable assessment density.
Non-goals: copying marketing photography, adding a marketing funnel, changing source acquisition or regulatory calculations, redistributing commercial/trial font files.

## Decisions
- Extract public SVG wordmark/plus/close artwork from the supplied site's DOM and download its published favicon. Strip site-specific attributes; use a dark wordmark on the app's light header. Record source and date.
- Replace green decorative colors with shared neutral CSS tokens in the existing stylesheet rather than layering another theme framework. Keep distinct, contrast-safe success/warning/error treatments.
- Use Georgia for editorial headings and Helvetica/Arial for controls and data, reflecting the site's pairing without a font network dependency. Use mixed serif/sans for the landing headline; dense results remain sans-serif.
- Keep native details/summary semantics and use local artwork for their visual indicators. Refine spacing, borders, hover/focus states and responsive header sizing without changing DOM reading order.

## Risks / Trade-offs
- Brand colors are not all suitable for small text → use darker neutral text and preserve readable semantic colors.
- Larger headings can wrap badly on mobile → verify 390px and 760px widths and keyboard disclosures.
- Marketing fonts are not redistributed → system equivalents vary slightly by platform.
