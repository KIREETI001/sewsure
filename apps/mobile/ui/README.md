# SewSure UI kit (`apps/mobile/ui`)

Owner: D1 Design System (approver: Delfine). Tokens and shared components. Screens (D2–D5) import from `ui` and do not restyle them.

```tsx
import { ThemeProvider, Button, StateBadge, MeasurementInput } from "../ui";

// ThemeProvider follows OS light/dark; pass scheme="dark" to force.
<ThemeProvider>
  <StateBadge state={design.state} /> {/* the API value, passed straight through */}
  <MeasurementInput
    label="Waist"
    text={draft.inputCm}
    onChange={({ text, mm, status }) => save(text, mm, status)}
    onBlur={confirmIfClean}
  />
  <Button label="Continue" onPress={next} />
</ThemeProvider>;
```

## Tokens

- `tokens/colors.ts`: light and dark palettes (linen surfaces, indigo primary, madder accent). Every pair in `contrastPairs` is checked for WCAG AA (4.5:1 text, 3:1 borders, focus ring and badge borders).
- `tokens/typography.ts`: type scale in points. Components keep `allowFontScaling` on and cap at `maxFontScale` (2 = 200%). Do not set fixed heights on text containers.
- `tokens/spacing.ts`: spacing, radius, border widths and `minTouchTarget` (44).

Check contrast after any colour change (Node 22.18+). It exits non-zero if any pair fails.

```bash
node ui/scripts/check-contrast.mjs
```

## Components

| Component          | Notes                                                                                                                                                                                                                                                                                                                                                                                            |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Button`           | `primary`/`secondary`/`danger`; role `button`; `loading` sets busy+disabled; min 44 pt.                                                                                                                                                                                                                                                                                                          |
| `Card`             | Plain container. Set `accessible` + `accessibilityLabel` only when the whole card is one unit.                                                                                                                                                                                                                                                                                                   |
| `StateBadge`       | Takes the contract `DesignState` directly: `PASS_SUPPORTED_CHECKS` (✓ Verified within supported checks), `NEEDS_INPUT` (? Needs more information), `IDEA_ONLY` (✦ Inspiration only), `FAILED_CHECKS` (✗ Did not pass checks), `SUPERSEDED` (↺ Replaced by a newer version). Text plus symbol plus border. It displays a state set by the feasibility engine; screens must not map or derive one. |
| `MeasurementInput` | Controlled: `text` (cm as typed) and `onChange({ text, mm, status })` with `status` `empty`/`invalid`/`ok`. Other `TextInput` props (`onBlur`, `onFocus`, ...) pass through. The caller owns the draft, origin and `confirmed_at`. `parseCmToMm` rejects zero, negatives and `.5`, same grammar as D2's `parseCm`.                                                                               |
| `StepCard`         | One DIY step; "Done"/"Not done" as text with ✓/○.                                                                                                                                                                                                                                                                                                                                                |
| `ChecklistItem`    | Role `checkbox`, `checked` state, ✓ drawn in the box.                                                                                                                                                                                                                                                                                                                                            |
| `MockBadge`        | Put on anything rendered from a fixture.                                                                                                                                                                                                                                                                                                                                                         |

## Accessibility rules

1. Never signal state by colour alone: always text plus a symbol (see `StateBadge`, `StepCard`, error text prefix `!`).
2. Every interactive element has a role, a label and `accessibilityState`.
3. Touch targets are at least 44 x 44 pt.
4. Support text scaling to 200%; let text wrap.
5. Decorative symbols are hidden from screen readers; the text carries the meaning.
6. No guarantee wording ("guaranteed", "perfect fit", "100% accurate") in any string.

## Strings

`strings.ts` holds English fallbacks so components render standalone. Moving them into `src/i18n` needs a change outside `ui/` (see the PR).

## Testing

Tests in `__tests__/` run in the app scaffold (jest-expo, `@testing-library/react-native` v14, where `render` and `fireEvent` are async). Decorative symbols are hidden from screen readers, so query them with `{ includeHiddenElements: true }`.

## Not done yet

- Figma mirror and Code Connect.
