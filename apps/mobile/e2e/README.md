# D6 mobile QA: integration workflow

All Maestro flows are **unverified on Android**. YAML parsing and Jest are not device execution.
See docs/qa/test-run-log.md for dated results and limitations. PR #32's history is preserved;
Milestone 2 reconciles its expectations with PRs #33, #37, #38, #39, #42 and #43.

## Automated JavaScript tests

From apps/mobile (PowerShell uses npm.cmd):

```powershell
npm.cmd test -- --ci --runInBand
npm.cmd run test:a11y
npm.cmd run typecheck
npm.cmd run lint
```

The normal Jest configuration excludes /e2e/. test:a11y explicitly overrides that exclusion:

```powershell
node node_modules/jest/bin/jest.js --ci --runInBand --testPathIgnorePatterns /node_modules/ --testMatch "**/e2e/audit/*.test.tsx"
```

All five former expected failures are normal regression tests: unique photo-control names,
Entry guidance, Inspiration guidance, visible measurement hints, and decorative-symbol hiding.
Precise queries avoid matching multiple messages/hints. The original ../../app imports are correct
from e2e/audit; the earlier integration audit's claim that they needed another parent was mistaken.
These tests check rendered text, accessibility props and declared styles, not actual speech or layout.

## Android execution (planned, not run)

Use an installed Android development build of com.sewsure.mobile that registers the sewsure scheme,
an available emulator/device, platform tools and Maestro. Expo Go alone does not prove custom links.
From apps/mobile, run npm.cmd run qa:start in one terminal and leave Metro running. In another:

```powershell
adb devices
maestro test e2e/intake/permission-denied.yaml
maestro test e2e/intake/
```

Stop QA Metro afterward, run npm.cmd run qa:remove, and confirm app/dev is absent before any
normal or production build. Use fresh output directories for the export gate workflow documented
in src/dev/README.md. JavaScript export exclusion is narrower than actual APK exclusion.

## Seeds and isolation

seed/apply.yaml clears app storage, opens sewsure://dev/seed/${SEED}, and waits for the exact
Seeded: <name> confirmation after hydration. It must run against the QA development workflow.
Never seed over an in-flight upload. Reopening a still-mounted seed route is not a reset command.

- capture-ready: shirt with checked synthetic Front and Back, demo mode.
- inspiration-ready: synthetic text, fit and skill added.
- measurements-signed-in: synthetic mock identity, no real authentication, no measurements.
- measurements-confirmed: 52, 70, 45 and 60 cm confirmed with synthetic timestamps.

No participant photos or body measurements are used. Checkmarks do not prove real image quality.

## Scenario changes and device checkpoints

| Flow | Intended evidence; Android execution still pending |
| --- | --- |
| entry-guest-demo | Current #33 wording and normal demo navigation |
| permission-denied | Denied camera, Settings and accessible Front library action |
| photo-checks-gate | Seeded Front/Back checks toggle independently; Continue disabled until both checked |
| blank-inspiration-surprise | Blank prompt produces a mock-marked idea; verify index 1 selects the action, not the radio |
| missing-values | Upload lists missing fields and keeps Not uploaded status |
| implausible-units | Explicit correction from 6 to 60 cm |
| edit-reconfirm | Replace 52 with valid 53; old confirmation disappears and exact new confirmation follows blur |
| draft-survives-restart | Restart without reseeding; navigate to persisted values |
| offline-draft | Local mock rejection/retry using Enable/Disable mock upload failure; NOT a network test |

Selectors use intended symbol-free accessible status labels, escaped literal punctuation/parentheses,
checked/enabled state selectors and scrolling. Actual Android hierarchy, keyboard blur, scroll reachability,
custom-scheme routing and native button casing must be verified on a device. Do not broaden selectors
merely to hide failures. MockBadge is selected through Sample data, not a real result.

future/live-network-failure.md preserves the blocked live-network case separately from mock testing.
future/photo-picker.md preserves manual image-picker/replace/cancel coverage; its native hierarchy varies
by Android version. The synthetic PNG fixture remains available. The deterministic checkbox flow does
not claim to test the picker, real photo quality, server persistence or real authentication.

Syntax references used during reconciliation: [state selectors](https://docs.maestro.dev/reference/selectors/state-selectors),
[scrollUntilVisible](https://docs.maestro.dev/reference/commands-available/scrolluntilvisible),
[eraseText](https://docs.maestro.dev/reference/commands-available/erasetext).
