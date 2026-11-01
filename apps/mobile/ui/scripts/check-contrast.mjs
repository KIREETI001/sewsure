// Usage: node apps/mobile/ui/scripts/check-contrast.mjs
// Needs Node >= 22.18 (strips TypeScript types natively when importing tokens).
import { colorSchemes, contrastPairs } from "../tokens/colors.ts";

const channel = (v) => {
  const c = v / 255;
  return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
};
const luminance = (hex) => {
  const n = parseInt(hex.slice(1), 16);
  return (
    0.2126 * channel((n >> 16) & 255) + 0.7152 * channel((n >> 8) & 255) + 0.0722 * channel(n & 255)
  );
};
const ratio = (a, b) => {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
};
const get = (obj, path) => path.split(".").reduce((o, k) => o[k], obj);

let failures = 0;
for (const [scheme, tokens] of Object.entries(colorSchemes)) {
  for (const [fg, bg, min, what] of contrastPairs) {
    const r = ratio(get(tokens, fg), get(tokens, bg));
    const ok = r >= min;
    if (!ok) failures += 1;
    console.log(
      `${ok ? "PASS" : "FAIL"} [${scheme}] ${what}: ${fg} on ${bg} = ${r.toFixed(2)} (min ${min})`,
    );
  }
}
if (failures > 0) {
  console.error(`\n${failures} contrast pair(s) below WCAG AA.`);
  process.exit(1);
}
console.log("\nAll contrast pairs meet WCAG AA.");
