# Synthetic intake seeds (issue #31, Part A)

`createIntakeSeed(name)` returns a fresh, complete `IntakeDraft` for each of the four
names in `INTAKE_SEED_NAMES`. `applyIntakeSeed(name, target)` applies it in one patch
to an explicitly supplied store action. Reapplying any seed resets every draft field;
the normal store `reset()` returns to empty intake. No API or authentication is called.

Use these helpers in tests or the explicitly generated QA route. A persisted store must finish hydration and
have no pending upload or other writers before applying a seed. The helper does not
cancel in-flight application work. The factory itself has no store side effects.

- `capture-ready`: shirt, checked Front/Back images, guest mode.
- `inspiration-ready`: adds synthetic text, relaxed fit and beginner skill.
- `measurements-signed-in`: adds an explicitly synthetic mock identity, not guest;
  measurements remain empty, matching PR #32's E2E README.
- `measurements-confirmed`: adds all required shirt values: 52, 70, 45 and 60 cm
  (chest flat width, shoulder to hem, shoulder width and sleeve length). Existing
  validation must accept them without warnings before the fixed test confirmation
  timestamp is applied. Export uses the existing centimetre-to-millimetre conversion.

Images are embedded, offline 800x800 PNG shirt diagrams made from coloured rectangles,
not photographs. Front has a centre seam; Back does not. There are no participant
records or body measurements. Checked photos simulate the user checklist only;
neither image quality AI nor feasibility checks have run. Confirmation timestamps
and the `user_entered` origin simulate UI entries, not real measurement evidence.
Every seed clears upload state, receipt provenance, body consent and inactive inspiration.

Normal production entry points do not import these modules. The QA-only route workflow
below is the only navigation entry point. A runtime `__DEV__` check is not used as
proof of exclusion.

## Mock upload failure simulation (Part B1)

`installMockUploadFailure()` installs a test-only wrapper using `getApi` / `setApi`.
It starts with predictable upload rejection (`MOCK_UPLOAD_FAILURE_MESSAGE`). Call
`controller.setFailure(false)` to recover using the existing mock upload response
and provenance, or `setFailure(true)` to fail again. Other mock methods are unchanged.
No network is used. Installation refuses any client other than the default `mockApi`,
including nested installations, so it cannot wrap a live backend.

Always call `controller.dispose()` in `finally` or test teardown after pending
mutations settle. Disposal clears failure and restores the original client if the
wrapper still owns the API slot; it never overwrites a subsequently installed client.
Disposal is idempotent, and a disposed controller cannot be enabled again. Each new
installation starts fresh. Importing the module alone does not install anything.

The controller does not edit intake state, authentication, consent or validation.
Tests exercise the existing measurements screen to verify persisted draft retention
and retry with identical input, including measurement confirmations. No production
entry point imports the controller. The generated QA screen alone exposes test controls.

## QA seed deep links (Part B2)

From `apps/mobile`, run `npm run qa:start` (Windows PowerShell: `npm.cmd run qa:start`).
This generates exactly `app/dev/seed/[name].tsx`, a re-export of `src/dev/SeedRoute.tsx`,
then starts Expo with `SEWSURE_QA_ROUTES=1` and a cleared Metro cache. The file is ignored
by Git. No normal app screen or navigation file is changed. Use a development Android
app that registers the existing `sewsure` scheme, connected to this Metro server.
Expo Go alone is not proof of the custom-scheme device flow.

Open any of these links:

```text
sewsure://dev/seed/capture-ready
sewsure://dev/seed/inspiration-ready
sewsure://dev/seed/measurements-signed-in
sewsure://dev/seed/measurements-confirmed
```

The route waits for Zustand's `onFinishHydration` (or proceeds if already hydrated),
applies a complete seed once per mounted seed session, and displays exactly
`Seeded: <name>`. Re-renders preserve later user edits; changing the name starts a new
session. Invalid/array-valued names show `Invalid seed name` without editing the store.
Failed hydration never produces a success confirmation. Use D6's `launchApp: clearState: true`
before each flow; do not seed over an in-flight upload. Reopening the same still-mounted
route is not a reset command: leave it or relaunch before applying the same name again.

The QA screen renders Capture for `capture-ready`, Inspiration for `inspiration-ready`,
and Measurements for both measurement seeds, beneath the persistent confirmation.
This lets D6 assert the confirmation and then interact with existing screen controls.

For mock failure testing, tap `Enable mock upload failure`, then `Upload`; after failure,
tap `Disable mock upload failure`, then `Try upload again`. Controls do not reapply the
seed. Leaving/changing the seed session disposes the controller. The mock-only guard
refuses any other API client. Airplane mode does not affect the offline mock client:
D6's PR #32 offline-draft flow must use these controls instead for mock testing.
No claim is made that the existing Maestro flows have run.

Stop the QA server, run `npm run qa:remove`, then start normal development with
`npm start -- --clear`. Removal is idempotent and only deletes the exact generated
file and empty parent directories. It refuses an edited route and preserves unrelated
files. Do not manually add files under `app/dev`: the entire directory is reserved
and any leftover contents will keep the build gate closed.

### Build-time release gate and verification

`app.config.js` rejects **any** `app/dev` directory unless both the explicit QA flag
and `NODE_ENV=development` are present. There is no runtime-only security guard.
Normal production builds must first remove the generated route. A stale route causes
a build failure, even with the QA flag set. With the directory absent, Router's normal
`app` context cannot discover it, and no production module imports `src/dev`.

Research checked installed Expo Router **58.0.27** and Expo CLI **58.1.16**:

- [Expo environment variables](https://docs.expo.dev/guides/environment-variables/): SDK 58
  commands select their mode; `expo export` forces production unless `--dev` is supplied.
  Installed `@expo/cli/build/src/export/index.js` calls `loadEnvFiles` with that mode
  before config evaluation; no internal API is imported by our implementation.
- [Router custom roots](https://docs.expo.dev/router/reference/src-directory/) are documented
  but discouraged. This workflow keeps the default root, with no Metro overrides.

Reproduce Android JS evidence (PowerShell; run from `apps/mobile`):

```powershell
$env:EXPO_NO_TELEMETRY = '1'
$env:SEWSURE_QA_ROUTES = '1'
npm.cmd run qa:prepare
npx.cmd expo export --platform android --dev --no-bytecode --source-maps --max-workers 1 --output-dir dist/qa-proof
node scripts/verify-release-export.cjs dist/qa-proof --qa
# Expected failure, even though SEWSURE_QA_ROUTES is still 1:
npx.cmd expo export --platform android --no-bytecode --source-maps --output-dir dist/blocked-proof
npm.cmd run qa:remove
npx.cmd expo export --platform android --no-bytecode --source-maps --max-workers 1 --output-dir dist/release-proof
node scripts/verify-release-export.cjs dist/release-proof
Remove-Item Env:SEWSURE_QA_ROUTES
```

Use fresh output directories for each verification. The inspector requires normal
intake sources to be present and checks every emitted JS bundle and source map,
including indexed map sections. It rejects `app/dev` and `src/dev` sources, seed/failure
strings, synthetic PNG data and the route context path in release. Its QA mode requires
the generated route and all four dev modules as a positive control. It prints bundle
SHA256 hashes for evidence. `--no-bytecode` intentionally emits inspectable JS and
produces Expo's performance warning; it is not a release APK build configuration.

An Android JS export proves this bundle's exclusion only. It does not prove a signed
APK, Android intent handling, Maestro visibility/layout or device performance. Rerun
exclusion verification when changing routing, Expo versions or release build tooling.

Local evidence, 2026-11-06: the QA Android export contained 1,363 mapped sources,
including the generated route and four `src/dev` modules. Production export with
that route present was rejected by app config even with `SEWSURE_QA_ROUTES=1`.
After `qa:remove`, production Android JS export succeeded with the same QA flag still
set: 1,223 mapped sources, zero test-only sources, and no seed markers or route path.
The generated route was left removed after verification.

```text
QA JS SHA256: afdb28f423954beefca4ee238ac6fe20f19049da9572b7a8c55806705e3d1807
Production JS SHA256: 4f201c57057c49e53da0a1bbdd71ea9929b161408f408c19dedd0f665c01bfdb
```
