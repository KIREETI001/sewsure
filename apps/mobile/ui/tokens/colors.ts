/**
 * Colour tokens. Palette: undyed linen and calico surfaces, indigo "thread"
 * as the primary, madder-red accent. Every text/background pair listed in
 * `contrastPairs` is checked by `ui/scripts/check-contrast.mjs` (WCAG 2.2 AA).
 */
export type StateColors = { bg: string; fg: string; border: string };

export type ColorTokens = {
  background: string;
  surface: string;
  surfaceAlt: string;
  text: string;
  textSecondary: string;
  /** Borders of interactive controls: at least 3:1 against surface. */
  border: string;
  /** Decorative dividers only; never the sole boundary of a control. */
  divider: string;
  primary: string;
  onPrimary: string;
  accent: string;
  onAccent: string;
  danger: string;
  focusRing: string;
  stateVerified: StateColors;
  stateNeedsInfo: StateColors;
  stateInspiration: StateColors;
  stateFailed: StateColors;
  stateSuperseded: StateColors;
  mock: StateColors;
};

export const lightColors: ColorTokens = {
  background: "#FAF7F2",
  surface: "#FFFFFF",
  surfaceAlt: "#F1EBE1",
  text: "#1F1B16",
  textSecondary: "#554C42",
  border: "#7A6F63",
  divider: "#DDD4C7",
  primary: "#2B4A7A",
  onPrimary: "#FFFFFF",
  accent: "#9C3A22",
  onAccent: "#FFFFFF",
  danger: "#A31F1F",
  focusRing: "#1B4FD8",
  stateVerified: { bg: "#E2F1E6", fg: "#14502A", border: "#14502A" },
  stateNeedsInfo: { bg: "#FFF0C7", fg: "#5F4200", border: "#5F4200" },
  stateInspiration: { bg: "#E9E6F6", fg: "#3A3170", border: "#3A3170" },
  stateFailed: { bg: "#FBE4E1", fg: "#7A1616", border: "#7A1616" },
  stateSuperseded: { bg: "#E8E8E8", fg: "#3D3D3D", border: "#3D3D3D" },
  mock: { bg: "#1F1B16", fg: "#FFE27A", border: "#FFE27A" },
};

export const darkColors: ColorTokens = {
  background: "#15120E",
  surface: "#201C17",
  surfaceAlt: "#2A251F",
  text: "#F4EEE5",
  textSecondary: "#C2B8AB",
  border: "#9A8F82",
  divider: "#3D372F",
  primary: "#9DB9EA",
  onPrimary: "#0E1B33",
  accent: "#F0A28A",
  onAccent: "#3A1206",
  danger: "#FF9C9C",
  focusRing: "#8FB0FF",
  stateVerified: { bg: "#173824", fg: "#B6E8C4", border: "#B6E8C4" },
  stateNeedsInfo: { bg: "#40300A", fg: "#FFDD8A", border: "#FFDD8A" },
  stateInspiration: { bg: "#2A2554", fg: "#D2CCFF", border: "#D2CCFF" },
  stateFailed: { bg: "#4A1A1A", fg: "#FFC4C4", border: "#FFC4C4" },
  stateSuperseded: { bg: "#333333", fg: "#D9D9D9", border: "#D9D9D9" },
  mock: { bg: "#FFE27A", fg: "#1F1B16", border: "#1F1B16" },
};

export type ColorScheme = "light" | "dark";
export const colorSchemes: Record<ColorScheme, ColorTokens> = {
  light: lightColors,
  dark: darkColors,
};

/** [foreground path, background path, minimum ratio, description] */
export const contrastPairs: (readonly [string, string, number, string])[] = [
  ["text", "background", 4.5, "body text on page"],
  ["text", "surface", 4.5, "body text on card"],
  ["text", "surfaceAlt", 4.5, "body text on alt surface"],
  ["textSecondary", "background", 4.5, "secondary text on page"],
  ["textSecondary", "surface", 4.5, "secondary text on card"],
  ["textSecondary", "surfaceAlt", 4.5, "secondary text on alt surface"],
  ["onPrimary", "primary", 4.5, "primary button label"],
  ["onAccent", "accent", 4.5, "accent button label"],
  ["primary", "background", 4.5, "primary as text/link on page"],
  ["primary", "surface", 4.5, "primary as text/link on card"],
  ["danger", "surface", 4.5, "error text on card"],
  ["danger", "background", 4.5, "error text on page"],
  ["stateVerified.fg", "stateVerified.bg", 4.5, "verified badge text"],
  ["stateNeedsInfo.fg", "stateNeedsInfo.bg", 4.5, "needs-info badge text"],
  ["stateInspiration.fg", "stateInspiration.bg", 4.5, "inspiration badge text"],
  ["stateFailed.fg", "stateFailed.bg", 4.5, "failed-checks badge text"],
  ["stateSuperseded.fg", "stateSuperseded.bg", 4.5, "superseded badge text"],
  ["mock.fg", "mock.bg", 4.5, "mock badge text"],
  ["border", "surface", 3, "control border on card"],
  ["border", "background", 3, "control border on page"],
  ["focusRing", "background", 3, "focus ring on page"],
  ["focusRing", "surface", 3, "focus ring on card"],
  ["stateVerified.border", "surface", 3, "verified badge border"],
  ["stateNeedsInfo.border", "surface", 3, "needs-info badge border"],
  ["stateInspiration.border", "surface", 3, "inspiration badge border"],
  ["stateFailed.border", "surface", 3, "failed-checks badge border"],
  ["stateSuperseded.border", "surface", 3, "superseded badge border"],
];
