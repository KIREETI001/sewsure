# Accessibility checklist: intake screens (release 0.1.0, `main` at c46c5d8)

Auditor: D6. Date: 2026-11-01. Blueprint §9.2 and `apps/mobile/CLAUDE.md`.

**Nothing in this document was verified on a device or with TalkBack.** No Android tooling was available (see `test-run-log.md`).

How each result was reached:
- **Run (Jest)**: ran in `apps/mobile/e2e/audit/a11y.audit.test.tsx` or the existing suites. Checks props and rendered text, not real layout or speech.
- **Read**: verified by reading the code only.
- **Not verified**: needs a device. The 15-minute test in `device-test-plan.md` covers it.

## Summary

| Screen | Screen-reader labels | Text 200% | Touch targets 44 pt | Not colour alone |
|---|---|---|---|---|
| Entry (`index`) | Pass (Run) | Not verified (Read: no blockers) | Pass on declared sizes (Run); on device not verified | Fail: disabled Start (Run) |
| Capture | Fail: duplicate names (Run) | Not verified (Read: no blockers) | Pass on declared sizes (Run) | Pass (Run, Read) |
| Inspiration | Pass (Run) | Not verified (Read: no blockers) | Pass on declared sizes (Run) | Fail: disabled Continue (Run) |
| Measurements | Pass, but symbols are spoken (Run) | Not verified (Read: no blockers) | Pass on declared sizes (Run) | Pass (Run); format hint not visible (Run) |

## Detail

### 1. Screen-reader labels

| Item | Result | Evidence |
|---|---|---|
| Every button, radio and checkbox on all four screens has a role and a non-empty name | Pass, **Run** | audit, 5 screen states |
| Headings use `accessibilityRole="header"` | Pass, **Read** | `plain/index.tsx` `Heading` |
| Photos have a label | Pass, **Read** | `capture.photoAlt`, `inspiration.imageAlt`. The inspiration label does not describe the content |
| Chips announce selected state | Pass, **Run** | `accessibilityState.checked` plus a tick in the text |
| Front and Back photo controls are distinguishable | **Fail**, Run | `Retake` and the photo-check checkbox have identical names for Front and Back. `Take photo`, `Choose from library` and `Remove photo` do include the side |
| Decorative symbols (`!`, `✗`, `i`, `✓`, `○`) hidden from screen readers | **Fail**, Run | Notice symbol Text has no `importantForAccessibility="no"`, so TalkBack would read it before each message |
| Warnings announced when they appear | Not verified | `Notice` sets `accessibilityRole="alert"` on a non-accessible View; whether TalkBack announces is unknown |
| Text field label and hint | Partial, **Read** | label is spoken twice (visible Text plus `accessibilityLabel`); the format hint is only spoken, never shown |
| Focus order | Not verified | single ScrollView in reading order (Read) |

### 2. Text scaling to 200%

| Item | Result | Evidence |
|---|---|---|
| Scaling not disabled, no cap under 2.0 | Pass, **Run** | audit, 5 states |
| No fixed heights on Text or TextInput | Pass, **Run** | audit, 5 states |
| Row layouts wrap | Pass, **Read** | `Row` uses `flexWrap: "wrap"` |
| Layout at 200% on a real screen (long chip labels, two-line buttons, Notice with buttons) | **Not verified** | needs a phone at maximum font and display size |
| Chip with `borderRadius: 22` and a long wrapped label | Not verified | may look clipped at 200%; no functional blocker found |

### 3. Touch targets of at least 44 pt

| Item | Result | Evidence |
|---|---|---|
| Declared `minHeight`/`minWidth` of every interactive element is 44 or more | Pass, **Run** | Button 48, Chip 44; audit, 5 states |
| `TextInput` height | Pass, **Read** | `minHeight: 48` |
| Actual rendered size and spacing between adjacent chips | **Not verified** | needs a device; chips sit in a wrapping Row with gap 8 |
| Header back button | Not verified | native, not app code |

### 4. States do not rely on colour alone

| Item | Result | Evidence |
|---|---|---|
| Selected chip: tick plus checked state | Pass, **Run** | audit |
| Implausible measurement: text message plus symbol | Pass, **Run** | audit |
| Confirmed measurement: `✓ Confirmed: N cm` | Pass, **Run** | existing screen tests |
| Upload status: symbol plus words (`○ Not uploaded`, `✓ Uploaded`) | Pass, **Run** | existing screen tests |
| Mock marker: text `Mock`, dashed border | Pass, **Read** | `MockBadge` |
| Disabled Start (Entry) | **Fail**, Run | dims to 45% opacity only; no text says what is needed |
| Disabled Continue (Inspiration) when only fit or skill is missing | **Fail**, Run | no text says why |
| Disabled Continue (Capture) | Pass, **Read** | explained by `capture.checkNeeded` / `category.needed` |
| Upload / Continue (Measurements) | Pass, **Read** | `Still needed: ...` appears after a tap |
| Contrast of the intake palette (`plain/index.tsx`) | Not verified | these colours are not in D1's checked token set, and no checker was run on them |
| Dark mode | Not verified | screens use fixed light colours; `StatusBar style="auto"` may give light icons on the white header |

## Not covered

Screens 5-10 (`(studio)`, `(make)`, tailor, settings) are not merged. Re-run this checklist when they land. Switch Access, keyboard navigation and reduced motion were not assessed.
