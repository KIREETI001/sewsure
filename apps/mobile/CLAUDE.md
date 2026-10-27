# apps/mobile

Owner: Delfine. Agents: D1 Design System, D2 Intake Flow, D3 Design Studio, D4 Cut & DIY, D5 Tailor & Settings, D6 Mobile QA & Accessibility.

Expo (current SDK) + React Native + TypeScript, Expo Router, TanStack Query, Zustand, React Native Skia, Expo Camera / Image Picker. Android APK first. Tests: Jest + React Native Testing Library, Maestro flows in `e2e/`.

## Rules

- The app is an interface layer. It never computes feasibility, never sets a design state and never holds model keys.
- The API client is generated from `packages/contracts`. Fixtures come from `packages/contracts/fixtures`. Anything rendered from a fixture shows a visible "mock" marker.
- Handle 0, 1, 2 or 3 candidates. Never pad to three.
- Design states always use text plus a symbol. Colour alone never signals verified or infeasible.
- Show lengths in cm with the unit label. Keep the mm value from the API as the source.
- Keep a local draft of measurements until the authenticated upload succeeds, and show whether it has uploaded.
- Every async screen has loading, failure and retry states. No silent loss of user input.
- Accessibility: screen-reader labels on every control and image, text scaling to 200%, touch targets of at least 44 pt.
- No guarantee wording in strings. Strings live in the i18n catalogue, not inline.
- Edge states to cover are listed in blueprint §9.1 and §18.2. Each needs a Maestro flow.
