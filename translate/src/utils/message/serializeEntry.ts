import type { MessageEntry } from '.';
import {
  fluentSerializeEntry,
  mf2SerializeMessage,
  serializePattern,
  type Pattern,
} from '@mozilla/l10n';
import { entryPatterns } from './entryPatterns';

export function serializeEntry(entry: MessageEntry | null): string {
  if (!entry) {
    return '';
  }

  switch (entry.format) {
    case 'fluent': {
      const { id, value, attributes } = escapeLineStarts(entry);
      const attr = attributes ? Object.fromEntries(attributes) : undefined;
      let msg = value;
      // Ensure that an entry with a non-null value serializes with a non-empty pattern,
      // even if the entry has attributes and would be valid with an empty value.
      if (Array.isArray(msg) && msg.every((p) => p === '')) {
        msg = [{ _: '' }];
      }
      return fluentSerializeEntry(
        id,
        { '=': msg!, '+': attr },
        { escapeSyntax: false },
      );
    }

    case 'android':
    case 'gettext':
    case 'webext':
    case 'xcode':
    case 'xliff':
      return entry.value ? mf2SerializeMessage(entry.value) : '';

    default:
      if (Array.isArray(entry.value)) {
        return serializePattern('plain', entry.value);
      }
  }

  throw new Error(`Unsupported ${entry.format} message [${entry.id}]`);
}

function escapeLineStarts(entry: MessageEntry): MessageEntry {
  const res = structuredClone(entry);
  for (const pattern of entryPatterns(res)) {
    let lineStart = pattern.some(
      (el) => typeof el === 'string' && el.includes('\n'),
    );
    const escaped: Pattern = [];
    for (const el of pattern) {
      if (typeof el !== 'string') {
        escaped.push(el);
        lineStart = false;
        continue;
      }
      let text = '';
      for (const ch of el) {
        if (lineStart && (ch === '[' || ch === '*' || ch === '.')) {
          if (text) {
            escaped.push(text);
          }
          escaped.push({ _: ch });
          text = '';
          lineStart = false;
        } else {
          text += ch;
          if (ch === '\n') {
            lineStart = true;
          } else if (ch !== ' ') {
            lineStart = false;
          }
        }
      }
      if (text) {
        escaped.push(text);
      }
    }
    pattern.splice(0, pattern.length, ...escaped);
  }
  return res;
}
