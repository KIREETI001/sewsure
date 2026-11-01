/**
 * English strings for screens 7-8 (cut guide, DIY steps). Kept in its own catalogue file so it
 * does not collide with other agents editing src/i18n/en.ts; merge into en.ts when convenient.
 * No guarantee wording: see tests/make/strings.test.ts.
 */
export const makeEn = {
  "make.mockNote": "Sample data from a fixture. Not a real result.",
  "make.loading": "Loading your cut guide…",
  "make.loadFailed": "The cut guide did not load. Nothing was changed. Try again.",
  "make.retry": "Try again",
  "make.back": "Back",

  // Gate
  "make.gate.title": "Cut guide not available",
  "make.gate.reason.idea_only":
    "This is an idea only. It is outside the recipes we can check, so there is no cut guide.",
  "make.gate.reason.needs_input":
    "We need more measurements or a correction before we can check this design.",
  "make.gate.reason.failed_checks": "This design did not pass the checks, so there is no cut guide.",
  "make.gate.reason.superseded":
    "You changed this design after it was checked. This older version is read-only.",
  "make.gate.reason.plan_mismatch":
    "The cut plan does not belong to this version of the design, so it is not shown.",
  "make.gate.reason.no_plan": "There is no cut plan for this design yet.",
  "make.gate.next.ask_tailor": "Next step: ask a tailor, or explore the idea without cutting.",
  "make.gate.next.add_measurements": "Next step: add or correct your measurements.",
  "make.gate.next.choose_supported_change": "Next step: pick a change that the checks support.",
  "make.gate.next.open_newer_revision": "Next step: open the newer version. It must pass its own checks.",
  "make.gate.next.go_back": "Next step: go back to your designs.",
  "make.gate.openNewer": "Open newer version",
  "make.gate.addMeasurements": "Add measurements",

  // Cut guide
  "make.cut.title": "Cut guide",
  "make.cut.approx":
    "Lines are approximate. Always measure on the real garment with a ruler before you cut.",
  "make.cut.fromLandmark": "{cm} cm ({inches} in) below the {landmark}",
  "make.cut.hemAllowance": "Hem allowance: {cm} cm",
  "make.cut.seamAllowance": "Seam allowance: {cm} cm",
  "make.cut.pieceHeading": "{piece}",
  "make.cut.prohibited": "Do not cut across: {regions}",
  "make.cut.diagramHeading": "Dimensioned diagram",
  "make.cut.diagramAlt":
    "Diagram of {piece} with its cut, fold and stitch lines. Distances are listed below the diagram.",
  "make.cut.overlayHeading": "Photo overlay",
  "make.cut.overlayAlt": "Your garment photo with cut, fold and stitch lines drawn on it.",
  "make.cut.overlayApprox": "Overlay is approximate, within {tol} cm on your photo. Check with a ruler.",
  "make.cut.kind.cut": "Cut (solid line)",
  "make.cut.kind.fold": "Fold (dashed line)",
  "make.cut.kind.stitch": "Stitch (dotted line)",
  "make.cut.kind.reference": "Reference (thin line)",
  "make.cut.fallbackHeading": "Showing the diagram instead of a photo overlay",
  "make.cut.fallback.mode_diagram": "The photo overlay is not offered for this plan.",
  "make.cut.fallback.not_calibrated": "Your photo has not been calibrated against a ruler yet.",
  "make.cut.fallback.rejected": "The photo calibration was rejected.",
  "make.cut.fallback.out_of_tolerance": "The photo calibration was not close enough to draw lines.",
  "make.cut.fallback.missing_calibration_data": "The calibration data is incomplete.",
  "make.cut.fallback.missing_projection": "We cannot place the lines on your photo yet.",
  "make.cut.fallback.photo_not_verified": "The photo has not been verified.",
  "make.cut.fallbackApiReason": "Reason from the server: {reason}",
  "make.cut.continue": "Continue to DIY steps",

  // Checkpoints
  "make.cp.heading": "Ruler checkpoints",
  "make.cp.intro":
    "Cutting cannot be undone. Tick each checkpoint only after you measured with a ruler. You cannot skip this.",
  "make.cp.detail": "{cm} cm from the {landmark}, give or take {tol} cm",
  "make.cp.remaining": "{n} checkpoint(s) left before any cut step",
  "make.cp.done": "All checkpoints ticked. Cut steps are now unlocked.",
  "make.cp.reset": "Checkpoints reset because this design changed. Measure again.",

  // Demo / review
  "make.draft.banner":
    "Not yet reviewed. This recipe is a draft that no sewist has reviewed. Demo only: do not use it on a real garment.",
  "make.draft.blocked":
    "This recipe has not been reviewed by a sewist, so it cannot be shown as a guide. Use the tailor route instead.",
  "make.draft.badge": "Not yet reviewed",

  // DIY
  "make.diy.title": "DIY steps",
  "make.diy.tools": "Tools",
  "make.diy.materials": "Materials",
  "make.diy.skills": "Skills used",
  "make.diy.practice": "Practice first",
  "make.diy.practiceNote": "Try these on spare fabric before you work on your garment.",
  "make.diy.progress": "{done} of {total} steps ticked",
  "make.diy.resume": "Resume at step {n}: {title}",
  "make.diy.resumeButton": "Go to step {n}",
  "make.diy.tick": "I did this step",
  "make.diy.untick": "Undo tick",
  "make.diy.irreversible": "This step cannot be undone.",
  "make.diy.lockedCheckpoint": "Locked. Tick every ruler checkpoint first.",
  "make.diy.selfReported": "Ticks are your own record. They are not checked by anyone.",
  "make.diy.extraRequired":
    "This recipe needs a tool or skill you did not list. A tailor may be a better fit.",
  "make.diy.openCheckpoints": "Go to ruler checkpoints",
  "make.diy.empty": "No steps came back for this design.",
} as const;

export type MakeKey = keyof typeof makeEn;

export const tm = (key: MakeKey, vars?: Record<string, string | number>): string => {
  const template: string = makeEn[key];
  if (!vars) return template;
  return template.replace(/\{(\w+)\}/g, (_, n: string) => String(vars[n] ?? `{${n}}`));
};
