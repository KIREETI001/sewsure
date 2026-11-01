// PreToolUse (Bash|PowerShell): stop commands that only founders may run.
import { readInput, block } from "./lib.mjs";

const input = await readInput();
const cmd = String(input.tool_input?.command ?? "");
if (!cmd) process.exit(0);

const RULES = [
  [/\bgit\s+push\b[^\n;|&]*\b(main|master)\b/, "pushing to main. Push your own branch and open a PR."],
  [/\bgit\s+push\b[^\n;|&]*(\s--force\b|\s-f\b|--force-with-lease)/, "force push. Ask a founder."],
  [/\bgh\s+pr\s+merge\b/, "merging a PR. Founders merge."],
  [/\bgh\s+pr\s+review\b[^\n;|&]*--approve/, "approving a PR. Agents cannot approve."],
  [/\bazd\s+(up|down|provision|deploy)\b/, "changing real Azure resources. Write Bicep and a runbook; a founder runs azd."],
  [/\baz\s+[\w-]+(\s+[\w-]+)*\s+(create|delete|purge)\b/, "creating or deleting Azure resources. A founder runs this."],
  [/\beas\s+(submit|credentials)\b/, "store submission or signing credentials. A founder handles these."],
  [/\b(cat|type|Get-Content)\b[^\n;|&]*\.env(\s|$)/, "reading a .env file. Use .env.example."],
];

for (const [re, why] of RULES) {
  if (re.test(cmd)) block(why);
}
process.exit(0);
