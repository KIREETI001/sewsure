# Synthetic intake seeds (issue #31, Part A)

`createIntakeSeed(name)` returns a fresh, complete `IntakeDraft` for each of the four
names in `INTAKE_SEED_NAMES`. `applyIntakeSeed(name, target)` applies it in one patch
to an explicitly supplied store action. Reapplying any seed resets every draft field;
the normal store `reset()` returns to empty intake. No API or authentication is called.

Use these helpers in tests only for now. A persisted store must finish hydration and
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

There is no seed route, UI, deep-link handler or production import. Part B must establish
and verify build-time release exclusion before exposing `sewsure://dev/seed/<name>`.
A runtime `__DEV__` check alone is not proof of exclusion. These helpers do not unblock
Maestro deep-link flows yet.
