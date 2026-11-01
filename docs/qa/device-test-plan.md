# 15-minute real-device check (Android)

For a founder with one Android phone. First real-device check of the intake flow. Nothing here has been done yet.

**Before you start (`needs-human`):** install a build of the app (`com.sewsure.mobile`, a dev build or APK). Use test photos of a garment you own, not of a person. Do not type real body measurements: use made-up numbers. Do not photograph anyone's face.

Mark "Pass" in the table only for what you actually saw.

## 0. Setup (2 min)
1. Note phone model, Android version, app build or commit.
2. In Settings, set Font size and Display size to the **largest**. This is the 200% check. Leave TalkBack off for now.
3. Uninstall and reinstall the app, or clear its storage, so you start clean.

## 1. Entry (2 min)
1. Open the app. Is the title readable with no text cut off?
2. Is **Start** greyed out? Can you tell what you must do to enable it without guessing? (known issue)
3. Tap **Tailor**: a note says tailor tools come later. Tap **Maker or owner**.
4. Tap **Try demo mode**, then **Start**.

## 2. Camera permission denied (2 min)
1. On Capture, tap **Take photo: Front**. Choose the deny option on the system prompt.
2. Expect "Camera access is off..." and **Choose from library** still works. Tap **Open settings**: it should open the app's settings. Come back.

## 3. Photos and category (2 min)
1. Tap **Choose from library** for Front and Back and pick a garment photo (a tiny one shows the "photo is small" notice).
2. **Continue** must stay off until both photos are ticked "Sharp, evenly lit..." and a garment type is chosen.
3. Tick both, choose the type, tap **Continue**.

## 4. Inspiration (1 min)
1. Leave it blank: expect "Nothing entered yet" and **Surprise Me**. Tap it: an idea appears with a **Mock** marker.
2. Pick a fit and a skill, then **Continue**.

## 5. Measurements (3 min)
1. Type **6** in Chest. Expect "looks small. Did you mean 60 cm?". Tap **Use 60 cm**: "✓ Confirmed: 60 cm".
2. Type **52** in the other fields; tap the next field after each. Each should show ✓ Confirmed.
3. Type **500** in a field: only a suggestion, no "Keep" button.
4. Close the app (swipe it away), reopen, tap **Start** and **Continue** twice. Are your values still there? Does the status say "Not uploaded"?
5. In demo mode there must be no **Upload** button.

## 6. Screen reader (3 min)
1. Turn on TalkBack. Swipe through Capture with both photos: can you tell the Front and Back **Retake** buttons apart? (known issue)
2. On Measurements trigger the warning again. Is it read out when it appears? Is a symbol read before it?
3. Can every control be reached and activated with swipe and double-tap?

## Results

| Step | Pass / Fail / Not tried | What you saw (screenshot name) |
|---|---|---|
| 1.1 title readable at largest font | | |
| 1.2 Start disabled, reason clear | | |
| 2.2 denied-camera message, library still works | | |
| 3.2 Continue gated | | |
| 4.1 Surprise Me with Mock marker | | |
| 5.1 6 cm to 60 cm fix | | |
| 5.3 500 cm has no Keep | | |
| 5.4 draft survives restart | | |
| 5.5 no Upload in demo | | |
| 6.1 Front/Back distinguishable | | |
| 6.2 warning announced, no stray symbol | | |
| Anything cut off, overlapping or hard to tap | | |

Send results and screenshots to D6 / L0. Screenshots must not show a real person or personal data.
