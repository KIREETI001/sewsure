# QA run log

Newest first. A flow is only "passed" if it ran. Every flow so far has **not run**.

## 2026-11-01: baseline audit of `main` at c46c5d8 (D6)

**Machine:** Windows 11, Node 24, npm 11. **Not installed:** `adb`, Android SDK (`%LOCALAPPDATA%\Android` absent), Java, `maestro`. No emulator or phone attached. So no Maestro flow was run and nothing was tried on a device.

| Check | Result | How |
|---|---|---|
| `npm ci` | ok | ran |
| `npx jest` (existing suites) | 69 passed, 3 suites | ran |
| `npx tsc --noEmit` | clean | ran |
| `npx eslint .` | clean | ran |
| `node ui/scripts/check-contrast.mjs` | all pairs meet WCAG AA (D1 tokens only; the intake screens do not use these tokens) | ran |
| `npx expo export --platform android` | Hermes bundle built, 1216 modules | ran. Shows it bundles, not that it launches |
| `e2e/audit/a11y.audit.test.tsx` | 27 passed, of which 5 are `it.failing` (confirmed bugs, below) | ran |
| Maestro flows (11 files) | **not run**. YAML parses (checked with a YAML parser). Selectors checked by reading `en.ts` and the screens | static only |

### Defects found in D2's original flows (fixed here, still unrun)

- `implausible-units.yaml` asserted `Confirmed: 60 cm`, but the text is `✓ Confirmed: 60 cm` and Maestro matches the whole string. It would have failed.
- `permission-denied.yaml` tapped a system button named `Deny`; Android 11+ dialogs say `Don't allow`. Replaced by launching with the camera permission denied. Also tapped `Take photo`, but the accessible name is `Take photo: Front`.
- `offline-draft.yaml` expected the Measurements screen straight after relaunch, but the app reopens on the entry screen, and the fixture client never fails, so airplane mode proves nothing. Marked blocked.
- Several flows assumed a "demo seed build" that does not exist.

### Bugs filed

See the PR description for issue links. Summary: Start/Continue disabled with no stated reason; cm format hint not visible; duplicate Retake and photo-check names; decorative symbols spoken; no seed route and a client that cannot fail.

### Observations, not filed

- The four screens use `src/components/plain`, not D1's `ui/` kit, so D1's contrast checks and 200% font cap do not cover them yet.
- After closing the app the user lands on the entry screen with no "resume draft" cue. The draft is kept (store is persisted) but nothing says so until they reach Measurements.
- `Notice` has `accessibilityRole="alert"` on a non-accessible View. In Jest, `getByRole("alert")` does not find it. Whether TalkBack announces it is unverified.
- Dark mode and status bar contrast (`StatusBar style="auto"` over a white header) unverified.
