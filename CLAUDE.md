Run `npm run tokens` to regenerate `tokens.json` and `src/styles/tokens.css` (Light/Dark themes) from `design/figma-variables.json` — the Figma variables export, which includes the `VooDoo · Typography` collection (Inter, weights 400–700, sizes 10–48, line heights 14–56; the VooDoo text styles are bound to these variables). To check that a fresh Figma export still matches the repo, run `npm run typography:check -- <export.json>`.

Product spec for "Нагадайка" (the app this design system/course case is being built for): see [docs/product-spec.md](docs/product-spec.md) — read it before product, UX, or AI-logic work.

Typography is part of the design system: pages use the `--font-family-*`, `--font-weight-*` and `--font-size-*` tokens (Inter is loaded by `tokens.css`) and never hard-code fonts.

Design values (sizes, stroke widths, spacing, coordinates, radii) are whole numbers only — no decimals or fractions. Round, don't use `0.5`-style values or em fractions.
