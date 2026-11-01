/**
 * Type scale. Sizes are base sizes in points; React Native scales them with
 * the OS font size setting. Components must leave `allowFontScaling` on and
 * cap growth with `maxFontSizeMultiplier` (see `maxFontScale`), never disable it.
 */
export type TextVariant =
  "display" | "title" | "heading" | "body" | "bodyStrong" | "label" | "caption";

export type TextStyleToken = {
  fontSize: number;
  lineHeight: number;
  fontWeight: "400" | "500" | "600" | "700";
};

export const typeScale: Record<TextVariant, TextStyleToken> = {
  display: { fontSize: 32, lineHeight: 40, fontWeight: "700" },
  title: { fontSize: 24, lineHeight: 32, fontWeight: "700" },
  heading: { fontSize: 20, lineHeight: 28, fontWeight: "600" },
  body: { fontSize: 16, lineHeight: 24, fontWeight: "400" },
  bodyStrong: { fontSize: 16, lineHeight: 24, fontWeight: "600" },
  label: { fontSize: 14, lineHeight: 20, fontWeight: "600" },
  caption: { fontSize: 13, lineHeight: 18, fontWeight: "400" },
};

/** Supports OS text scaling up to 200% (project requirement). */
export const maxFontScale = 2;
