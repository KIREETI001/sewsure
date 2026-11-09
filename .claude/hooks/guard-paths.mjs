// PreToolUse (Edit|Write|MultiEdit|NotebookEdit): keep agents away from secrets,
// signing keys and production infrastructure.
import path from "node:path";
import { readInput, block, repoRelative } from "./lib.mjs";

const input = await readInput();
const filePath = input.tool_input?.file_path ?? input.tool_input?.notebook_path;
if (!filePath) process.exit(0);

const rel = repoRelative(filePath);
const base = path.basename(filePath).toLowerCase();

const SECRET_NAMES = [/^\.env(\..*)?$/, /\.(keystore|jks|p12|pfx|pem|key|mobileprovision)$/, /^google-services\.json$/, /^credentials(\..*)?$/, /^secrets?\.(json|ya?ml|env|txt|toml)$/];
const ALLOWED_TEMPLATES = [/^\.env\.example$/, /^\.env\.sample$/];

if (SECRET_NAMES.some((re) => re.test(base)) && !ALLOWED_TEMPLATES.some((re) => re.test(base))) {
  block(`"${base}" looks like a secret or signing file. Secrets live in Key Vault or EAS credentials, never in files agents edit. Edit .env.example instead.`);
}

if (rel && rel.startsWith("infrastructure/prod/")) {
  block("infrastructure/prod/ is changed by founders only (A3). Change staging or a shared module and propose the prod change in the PR description.");
}

process.exit(0);
