# Mobile end-to-end flows (Maestro) and audits

Owner: D6 Mobile QA. Nothing here has been run on a device yet. See `docs/qa/test-run-log.md` for what actually ran.

## Layout

| Path | What |
|---|---|
| `intake/*.yaml` | One flow per edge state in blueprint §9.1 rows 1-4 and §18.2 #1-#3 |
| `seed/` | Starting states. `entry-guest.yaml` is UI-driven. `apply.yaml` uses a dev deep link that does not exist yet |
| `fixtures/synthetic-garment.png` | Synthetic 800x800 image (no real person or garment) for `addMedia` |
| `audit/a11y.audit.test.tsx` | Jest accessibility audit of the four intake screens. Runs today, no device needed |

## Run the flows (needs a device or emulator)

```bash
# one-off: Java 17+, Android SDK platform-tools, Maestro CLI, an APK or dev build of com.sewsure.mobile
maestro test apps/mobile/e2e/intake/permission-denied.yaml
maestro test apps/mobile/e2e/intake/
```

## Seeding approach

Flows must start from a known state, and the app persists its draft in AsyncStorage (`sewsure.intake.draft.v1`), so there are two ways in:

1. **UI-driven** (works with no app change): `launchApp: clearState: true`, then tap through. Fine for entry and permission flows. Too slow and too picker-dependent for measurement flows, because the Android photo picker UI differs per device.
2. **Dev seed link** (needs a change in `apps/mobile/app`, owned by D2): a development-build-only route `sewsure://dev/seed/<name>` that patches `useIntakeStore` with synthetic data, then shows the text `Seeded: <name>`. Names: `capture-ready` (both photos ticked, shirt), `inspiration-ready` (+ text, fit, skill), `measurements-signed-in` (ready, signed in not guest, no measurements), `measurements-confirmed` (all four shirt values confirmed, chest 52 cm). It must be compiled out of release builds. Flows call it through `seed/apply.yaml`. Until it exists, every flow that uses `apply.yaml` is blocked.

Never seed real photos or body measurements. Fixtures are synthetic.

## Audit test

```bash
cd apps/mobile
npx jest --testPathIgnorePatterns /node_modules/ --testMatch "**/e2e/audit/*.test.tsx" --silent
```

`it.failing` cases are confirmed bugs with an issue. When the owner fixes one the test goes red, so change it to `it`.
