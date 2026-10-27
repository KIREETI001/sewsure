// Shared helpers for SewSure Claude Code hooks.
// Hooks receive the tool call as JSON on stdin. Exiting with code 2 blocks the
// call and shows stderr to the agent; exit 0 lets it through.
import path from "node:path";

export async function readInput() {
  let raw = "";
  for await (const chunk of process.stdin) raw += chunk;
  try {
    return JSON.parse(raw || "{}");
  } catch {
    return {};
  }
}

export function block(reason) {
  process.stderr.write(`Blocked by SewSure project hook: ${reason}\n`);
  process.exit(2);
}

// Repo-relative path with forward slashes, or null when outside the repo.
export function repoRelative(filePath) {
  if (!filePath) return null;
  const root = process.env.CLAUDE_PROJECT_DIR || process.cwd();
  const rel = path.relative(path.resolve(root), path.resolve(root, filePath));
  if (rel.startsWith("..") || path.isAbsolute(rel)) return null;
  return rel.split(path.sep).join("/");
}
