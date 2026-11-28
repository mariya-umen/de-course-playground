Run `npm run tokens` to regenerate `tokens.json` and `src/styles/tokens.css` (Light/Dark themes) from `design/figma-variables.json` — the Figma variables export, which includes the `VooDoo · Typography` collection (Inter for text, Unbounded for display, weights 400–900, sizes 10–48, line heights 14–56; the VooDoo text styles are bound to these variables). To check that a fresh Figma export still matches the repo, run `npm run typography:check -- <export.json>`.

Design system pages shown on GitHub (`docs/design-system.md`, `docs/design-system/`, `docs/screens/`) are generated: after changing tokens or screens run `npm run tokens`, then `python3 scripts/build-design-docs.py` (and `python3 scripts/functional-map/build_map.py` for the map). The prototype takes colours and component sizes from component tokens, not hand-written values. Figma variables and `design/figma-variables.json` are kept identical.

Product spec for "Нагадайка" (the app this design system/course case is being built for): see [docs/product-spec.md](docs/product-spec.md) — read it before product, UX, or AI-logic work.

Typography is part of the design system: pages use the `--font-family-*`, `--font-weight-*` and `--font-size-*` tokens (Inter and Unbounded are loaded by `tokens.css`) and never hard-code fonts. Headings are Unbounded Regular (the welcome headline Medium, card titles ExtraBold), the wordmark is Unbounded Bold uppercase, everything else is Inter.

Visual concept (Figma page «Нагадайка концепт», 15 frames): solid blue background `--status-info-bg-strong`; the flower photo only on the first screen; header = wordmark + «Mom’s AI assistant for everyday routines» (12px, 60% opacity); the 3D flower (`assets/mascot/nagadayka-flower.png`) is cropped by the screen edges; dark glass surfaces (`--surface-shade`, black 15%) and orange primary buttons.

Design values (sizes, stroke widths, spacing, coordinates, radii) are whole numbers only — no decimals or fractions. Round, don't use `0.5`-style values or em fractions.

Tone of voice in the app (all UI copy, push notifications, errors): friendly and always informal — address the user as «ти» (never «Ви»), short and warm, first person for Нагадайка. Friendly, not familiar: no slang, and button labels stay neutral and clear («Почати», not «Погнали»). Don't overload copy with extra meanings or jokes — if a phrase can be cut without losing meaning, cut it. No jokes about health or in errors/critical messages. When asked to "slightly rewrite" a text, keep its message exact. Approved phrases are not changed without a request. The mascot is called Квітуня; the product is Нагадайка. Details: docs/product-spec.md, section 3.1.

Mascot imagery: no outline/stroke around the 3D flower — it is separated from the background only by a soft shadow (large blur, semi-transparent). Use `assets/mascot/nagadayka-3d-cutout.png` (transparent) on coloured backgrounds, not the white-background original.

Screens are built for mobile only; no desktop layouts. The Figma frames are 440 × 956 (file "DE", page "Нагадайка концепт"): HTML screens use those design pixels and scale to the phone width, and Figma is the source of truth for layout and copy.

Workflow for screens: build one screen at a time; a screen is done only when Maria writes that it is ок. Use the style of the Figma concept ("Нагадайка концепт"), propose improvements separately instead of silently changing the concept.

Orange elements (primary buttons, the mic button, selected chips and options) always use the light `--text-inverse` label, never the dark one: the dark label looks heavy.

Git workflow: all changes go through pull requests (a feature branch per change set, never commits straight to main). After Maria approves the work, open the PR and merge it automatically (merge commit, delete the branch), then update local main.
