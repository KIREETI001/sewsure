const { defineConfig, globalIgnores } = require("eslint/config");
const expo = require("eslint-config-expo/flat");

module.exports = defineConfig([
  expo,
  globalIgnores(["node_modules/", ".expo/", "dist/"]),
  {
    // "@/" aliases are verified by tsc; the import plugin does not read tsconfig paths.
    rules: { "import/no-unresolved": ["error", { ignore: ["^@/"] }] },
  },
  { files: ["jest.setup.ts"], rules: { "@typescript-eslint/no-require-imports": "off" } },
]);
