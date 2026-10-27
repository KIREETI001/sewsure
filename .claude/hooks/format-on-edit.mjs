// PostToolUse (Edit|Write|MultiEdit): format the edited file when the formatter is installed.
// Never blocks; missing tools are skipped so the hook works before the toolchain exists.
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import { readInput, repoRelative } from "./lib.mjs";

const input = await readInput();
const filePath = input.tool_input?.file_path;
const rel = repoRelative(filePath);
if (!rel) process.exit(0);

const root = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const ext = path.extname(rel).toLowerCase();
const run = (cmd, args, cwd = root) => spawnSync(cmd, args, { cwd, stdio: "ignore", shell: process.platform === "win32" });

if (ext === ".py") {
  // Prefer the project's ruff through uv, fall back to a global ruff.
  const r = run("uv", ["run", "--quiet", "ruff", "format", filePath]);
  if (r.status !== 0) run("ruff", ["format", filePath]);
} else if ([".ts", ".tsx", ".js", ".jsx", ".mjs", ".json"].includes(ext)) {
  // Use the prettier installed in the nearest app; never download one.
  const app = rel.startsWith("apps/") ? path.join(root, rel.split("/").slice(0, 2).join("/")) : root;
  if (existsSync(path.join(app, "node_modules", ".bin"))) {
    run("npx", ["--no-install", "prettier", "--write", filePath], app);
  }
}
process.exit(0);
