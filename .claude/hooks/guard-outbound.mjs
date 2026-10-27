// PreToolUse (outbound MCP tools): agents draft messages and posts, founders send them.
// The matcher in settings.json decides which tools reach this hook, so any call here is blocked.
import { readInput, block } from "./lib.mjs";

const input = await readInput();
block(`${input.tool_name ?? "this tool"} sends or publishes outside the team. Save a draft and list it under needs-human for a founder to send.`);
