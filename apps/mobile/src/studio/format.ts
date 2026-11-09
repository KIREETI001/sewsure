import { t, type MessageKey } from "@/i18n";

/** Millimetres to a centimetre string for display ("52.5"). The mm value stays the source. */
export const mmToCmText = (mm: number): string => {
  const cm = Math.round(mm) / 10;
  return Number.isInteger(cm) ? String(cm) : cm.toFixed(1);
};

/** "52.5 cm". Signed values keep their sign so a shortfall reads as a shortfall. */
export const formatCm = (mm: number): string => `${mmToCmText(mm)} ${t("common.cm")}`;

/** Catalogue lookup with a plain-language fallback for codes the app does not know yet. */
export const tOr = (key: string, fallback: string, vars?: Record<string, string | number>) => {
  const text = t(key as MessageKey, vars);
  return text === key ? fallback : text;
};

/** SIDE_SEAMS_NOT_VERIFIED -> "side seams not verified". */
export const humanise = (code: string): string => code.toLowerCase().replace(/_/g, " ");

export const failureText = (code: string): string =>
  tOr(`studio.failure.${code}`, t("studio.failure.unknown", { code: humanise(code) }));

export const flagText = (code: string): string =>
  tOr(`studio.flag.${code}`, t("studio.flag.unknown", { code: humanise(code) }));

export const dimensionText = (key: string): string => tOr(`studio.dimension.${key}`, humanise(key));

export const geometryLabel = (key: string): string => {
  const base = key.replace(/_mm$/, "");
  return tOr(`studio.geo.${base}`, humanise(base));
};
