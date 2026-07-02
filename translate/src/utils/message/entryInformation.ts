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

const xmlFormats = new Set<MessageEntry['format']>([
  'android',
  'xcode',
  'xliff',
]);

export function htmlElementEscapes(entry: MessageEntry): RegExp | null {
  const set = new Set<string>();
  if (xmlFormats.has(entry.format)) {
    for (const pattern of entryPatterns(entry)) {
      for (const el of pattern) {
        let src;
        if (typeof el === 'string') {
          src = el;
        } else if (el.fn === 'html' && el._) {
          src = el._;
        } else {
          continue;
        }
        const match = src.match(/<\/?[\w-]+/g);
        if (match) {
          for (const m of match) {
            set.add(m.substring(1));
          }
        }
      }
    }
  }
  return set.size
    ? new RegExp(`<(${Array.from(set).join('|')})\\b`, 'g')
    : null;
}
