import type { MessageEntry } from '.';
import { entryPatterns } from './entryPatterns';

export function hasOuterWhitespace(entry: MessageEntry): boolean {
  for (const pattern of entryPatterns(entry)) {
    const el0 = pattern[0];
    if (typeof el0 === 'string' && /^\s/.test(el0)) {
      return true;
    }
    const el1 = pattern.at(-1)!;
    if (typeof el1 === 'string' && /\s$/.test(el1)) {
      return true;
    }
  }
  return false;
}
