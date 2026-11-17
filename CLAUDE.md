Run `npm run tokens` to regenerate `tokens.json` and `src/styles/tokens.css` (Light/Dark themes) from `design/figma-variables.json` — the Figma variables export, which includes the `VooDoo · Typography` collection (Inter, weights 400–700, sizes 10–48, line heights 14–56; the VooDoo text styles are bound to these variables). To check that a fresh Figma export still matches the repo, run `npm run typography:check -- <export.json>`.

Product spec for "Нагадайка" (the app this design system/course case is being built for): see [docs/product-spec.md](docs/product-spec.md) — read it before product, UX, or AI-logic work.

Typography is part of the design system: pages use the `--font-family-*`, `--font-weight-*` and `--font-size-*` tokens (Inter is loaded by `tokens.css`) and never hard-code fonts.

Design values (sizes, stroke widths, spacing, coordinates, radii) are whole numbers only — no decimals or fractions. Round, don't use `0.5`-style values or em fractions.

Tone of voice in the app (all UI copy, push notifications, errors): friendly and always informal — address the user as «ти» (never «Ви»), short and warm, first person for Нагадайка. Friendly, not familiar: no slang, and button labels stay neutral and clear («Почати», not «Погнали»). Don't overload copy with extra meanings or jokes — if a phrase can be cut without losing meaning, cut it. No jokes about health or in errors/critical messages. When asked to "slightly rewrite" a text, keep its message exact. Approved phrases are not changed without a request. The mascot is called Квітуня; the product is Нагадайка. Details: docs/product-spec.md, section 3.1.

Mascot imagery: no outline/stroke around the 3D flower — it is separated from the background only by a soft shadow (large blur, semi-transparent). Use `assets/mascot/nagadayka-3d-cutout.png` (transparent) on coloured backgrounds, not the white-background original.

Screens are built for mobile only; no desktop layouts. The Figma frames are 440 × 956 (file "DE", page "Нагадайка концепт"): HTML screens use those design pixels and scale to the phone width, and Figma is the source of truth for layout and copy.
