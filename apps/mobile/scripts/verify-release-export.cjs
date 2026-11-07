/* global __dirname */
const fs = require("node:fs");
const path = require("node:path");
const { createHash } = require("node:crypto");

const directory = path.resolve(process.argv[2] || path.join(__dirname, "../dist/release-proof"));
const qa = process.argv.includes("--qa");
function files(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const file = path.join(dir, entry.name);
    return entry.isDirectory() ? files(file) : [file];
  });
}
const all = files(directory);
const bundles = all.filter((file) => file.endsWith(".js"));
const maps = all.filter((file) => file.endsWith(".js.map"));
if (!bundles.length || !maps.length)
  throw new Error("Require JS bundles and external source maps.");
function mapSources(map) {
  if (Array.isArray(map.sections))
    return map.sections.flatMap((section) => mapSources(section.map));
  if (!Array.isArray(map.sources)) throw new Error("Unrecognized source map format.");
  return map.sources;
}
const sources = maps
  .flatMap((file) => mapSources(JSON.parse(fs.readFileSync(file, "utf8"))))
  .map((source) => source.replaceAll("\\", "/"));
if (!sources.some((source) => source.endsWith("app/(intake)/measurements.tsx"))) {
  throw new Error("Missing normal intake screen: wrong or incomplete export.");
}
const testSources = sources.filter((source) => /(?:^|\/)(src\/dev|app\/dev)\//.test(source));
const markers = [
  "Seeded: ",
  "Synthetic test idea:",
  "Synthetic test: mock intake upload failed.",
  "data:image/png;base64,iVBOR",
];
if (qa) {
  for (const suffix of [
    "app/dev/seed/[name].tsx",
    "src/dev/SeedRoute.tsx",
    "src/dev/intakeSeeds.ts",
    "src/dev/syntheticPhotos.ts",
    "src/dev/mockUploadFailure.ts",
  ]) {
    if (!testSources.some((source) => source.endsWith(suffix)))
      throw new Error(`QA control missing ${suffix}`);
  }
} else {
  if (testSources.length)
    throw new Error(`Test-only sources in release: ${testSources.join(", ")}`);
  for (const bundle of bundles) {
    const code = fs.readFileSync(bundle, "utf8");
    for (const marker of markers) {
      if (code.includes(marker)) throw new Error(`Test marker in release: ${marker}`);
    }
    if (code.includes("dev/seed")) throw new Error("QA route in release route context.");
  }
}
console.log(
  `${qa ? "QA positive control" : "Release exclusion"} passed: ${sources.length} mapped sources; ${testSources.length} test-only sources.`,
);
for (const bundle of bundles) {
  console.log(
    `${path.relative(directory, bundle)} SHA256 ${createHash("sha256").update(fs.readFileSync(bundle)).digest("hex")}`,
  );
}
