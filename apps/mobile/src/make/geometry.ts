/** Display helpers: millimetres in, plain-language cm and inch equivalents out. */
import type { CutLine, CutPlan } from "./types";

/** mm to cm for display only, one decimal, no trailing ".0". */
export const mmToCmText = (mm: number): string => {
  const cm = Math.round(mm) / 10;
  return Number.isInteger(cm) ? String(cm) : cm.toFixed(1);
};

/** Nearest eighth of an inch, e.g. 525 mm -> "20 5/8". */
export const mmToInchText = (mm: number): string => {
  const eighths = Math.round((mm / 25.4) * 8);
  const whole = Math.floor(eighths / 8);
  const rem = eighths % 8;
  if (rem === 0) return String(whole);
  const g = rem % 4 === 0 ? 4 : rem % 2 === 0 ? 2 : 1;
  const frac = `${rem / g}/${8 / g}`;
  return whole === 0 ? frac : `${whole} ${frac}`;
};

/** Mean y of a line in mm, which for horizontal cut/fold lines is the distance from the origin. */
export const lineDepthMm = (line: CutLine): number => {
  const ys = line.points_mm.map((p) => p[1]);
  return ys.reduce((a, b) => a + b, 0) / ys.length;
};

export interface Bounds {
  minX: number;
  minY: number;
  maxX: number;
  maxY: number;
}

export function planBounds(pieceLines: CutLine[]): Bounds {
  const pts = pieceLines.flatMap((l) => l.points_mm);
  const xs = pts.map((p) => p[0]);
  const ys = pts.map((p) => p[1]);
  return {
    minX: Math.min(...xs),
    minY: Math.min(...ys),
    maxX: Math.max(...xs),
    maxY: Math.max(...ys),
  };
}

export const originLandmarkText = (plan: CutPlan): string => plan.coordinate_frame.origin_landmark.replace(/_/g, " ");
