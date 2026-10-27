# SewSure UI kit (`apps/mobile/ui`)

Owner: D1 Design System (approver: Delfine). Tokens and shared components. Screens (D2–D5) import from `ui` and do not restyle them.

```tsx
import { ThemeProvider, Button, StateBadge, MeasurementInput, MockBadge } from '../ui';

<ThemeProvider>            {/* follows OS light/dark; pass scheme="dark" to force */}
  <StateBadge state="needs_info" />
  <MeasurementInput label="Waist" valueMm={waistMm} onChangeMm={setWaistMm} />
  <Button label="Continue" onPress={next} />
</ThemeProvider>
```

## Tokens

- `tokens/colors.ts`: light and dark palettes (linen surfaces, indigo primary, madder accent). Every pair in `contrastPairs` is checked for WCAG AA (4.5:1 text, 3:1 borders, focus ring and badge borders).
- `tokens/typography.ts`: type scale in points. Components keep `allowFontScaling` on and cap at `maxFontScale` (2 = 200%). Do not set fixed heights on text containers.
- `tokens/spacing.ts`: spacing, radius, border widths and `minTouchTarget` (44).

Check contrast after any colour change (Node 22.18+):

```bash
node apps/mobile/ui/scripts/check-contrast.mjs
```

It exits non-zero if any pair fails.

## Components

| Component | Notes |
|---|---|
| `Button` | `primary`/`secondary`/`danger`; role `button`; `loading` sets busy+disabled; min 44 pt. |
| `Card` | Plain container. Set `accessible` + `accessibilityLabel` only when the whole card is one unit. |
| `StateBadge` | Three states only: `verified`, `needs_info`, `inspiration`. Text plus symbol (✓ ? ✦) plus border. It displays a state decided elsewhere (feasibility engine); never compute one here. |
| `MeasurementInput` | Edits **cm**, emits **mm** (`onChangeMm`, rounded to 0.1 mm). `null` means empty or invalid. Origin and `confirmed_at` are the caller's job. |
| `StepCard` | One DIY step; "Done"/"Not done" as text with ✓/○. |
| `ChecklistItem` | Role `checkbox`, `checked` state, ✓ drawn in the box. |
| `MockBadge` | Put on anything rendered from a fixture. |

## Accessibility rules

1. Never signal state by colour alone: always text plus a symbol (see `StateBadge`, `StepCard`, error text prefix `!`).
2. Every interactive element has a role, a label and `accessibilityState`.
3. Touch targets are at least 44 x 44 pt.
4. Support text scaling to 200%; let text wrap.
5. Decorative symbols are hidden from screen readers; the text carries the meaning.
6. No guarantee wording ("guaranteed", "perfect fit", "100% accurate") in any string.

## Strings

`strings.ts` holds English fallbacks so components render standalone. Screens should pass labels from the i18n catalogue; once D2 sets up i18n, these defaults should move into it.

## Not done yet

- Tests in `__tests__/` need D2's scaffold (jest-expo, RNTL) and have not been run.
- Figma mirror and Code Connect: not done (see the PR).
