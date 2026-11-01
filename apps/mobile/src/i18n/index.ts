import { en, type MessageKey } from "./en";

export type { MessageKey };

const catalogue: Record<string, string> = en;

/** Looks up a string and fills `{name}` placeholders. Only English exists for now. */
export const t = (key: MessageKey, vars?: Record<string, string | number>): string => {
  const template = catalogue[key] ?? key;
  if (!vars) return template;
  return template.replace(/\{(\w+)\}/g, (_, name: string) => String(vars[name] ?? `{${name}}`));
};
