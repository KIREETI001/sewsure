/**
 * Default English strings for the shared components. App screens should
 * override via the i18n catalogue (pass `label`/props); these are fallbacks
 * so the components render standalone. No guarantee wording here.
 */
export const uiStrings = {
  stateVerified: 'Verified within supported checks',
  stateNeedsInfo: 'Needs more information',
  stateInspiration: 'Inspiration only',
  stateAccessibilityPrefix: 'Design status',
  mock: 'MOCK DATA',
  mockAccessibility: 'Mock data from a fixture, not a real result',
  unitCm: 'cm',
  stepDone: 'Done',
  stepNotDone: 'Not done',
  checked: 'Checked',
  unchecked: 'Not checked',
  stepOf: (n: number, total: number) => `Step ${n} of ${total}`,
  mmStored: (mm: number) => `${mm} mm stored`,
} as const;
