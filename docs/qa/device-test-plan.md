# Android intake acceptance plan ? unverified

Record phone/emulator model, Android and TalkBack versions, build/commit, font_scale and display
settings, test timestamp, expected/observed behavior and screenshot/video filenames. Use synthetic
photos and numbers only. Mark Pass only after execution. All rows below are currently Not run.

## Normal entry and camera

Start with a clean development build. Confirm Start is disabled with separate Maker/session reasons.
Select Maker, confirm only the session reason remains, choose demo mode and verify the current
wording says no sign-in/upload and local storage. Start becomes enabled. Tailor remains unavailable.
Deny camera permission; confirm the message, Settings link and Front/Back library controls work.
Run future/photo-picker.md for native picker selection, cancellation, replacement and removal.

## QA seeds and deterministic scenarios

Use npm run qa:start and the custom-scheme development build, not Expo Go as a substitute.
Run each intake YAML individually before the whole directory. Require Seeded: <name> after hydration.
The photo-check scenario must demonstrate each side remains independent and Continue cannot be
used with either side unchecked. Confirm draft-survives-restart never reapplies a seed after restart.

For measurement checks, use the synthetic 52/70/45/60 cm shirt values. Show the 6-to-60 correction;
replace confirmed 52 with valid 53 and verify confirmation clears until a different field is focused.
Check missing values and retained draft state. Demo mode must never offer Upload.

For mock failure, enable the QA failure control, Upload, verify failure and retained confirmations,
disable the control and retry. Require Test upload only. Nothing left this device. and the Mock badge.
This uses no network. Actual weak-network behavior remains blocked by future/live-network-failure.md.

## Accessibility and release checks

Repeat intake at normal font scale and a measured 2.0 scale when the device supports it; also record
maximum available font/display settings separately. Inspect wrapping, clipping, scrolling and controls.
With TalkBack, verify distinct Front/Back controls, checked state, focus order, visible hints, symbol-free
confirmation/status speech and announcement of new warnings. Capture an observation; props alone
cannot prove speech. Check whether visible hints and accessibilityHint cause unwanted repetition.

Stop QA Metro, run npm run qa:remove, and verify app/dev is absent. JS export gate evidence is
separate from release APK inspection and attempts to open all four seed links in the actual release.
No seeded state or success marker should appear in release. Record the APK hash and build settings.

| Area | Status | Observation/artifact |
| --- | --- | --- |
| Entry guidance, demo and Tailor | Not run | |
| Denied camera and native picker | Not run | |
| Front/Back independent checks and gating | Not run | |
| Blank inspiration and mock provenance | Not run | |
| Missing, implausible and edited measurements | Not run | |
| Restart persistence and demo upload absence | Not run | |
| Mock rejection and retry | Not run | |
| TalkBack labels, focus and announcements | Not run | |
| Measured large-text layout and touch targets | Not run | |
| Real-network failure | Blocked; live client required | |
| Release APK seed exclusion | Not run | |

D6 reviews actual Android results; D1/D2 review accessibility findings; release owner verifies the
artifact. X2 reviews claims used outside the team. Record failures and limitations alongside passes.
