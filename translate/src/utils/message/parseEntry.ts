import {
  fluentParseEntry,
  mf2ParseMessage,
  serializePattern,
  type FormatKey,
  type Message,
  type Pattern,
} from '@mozilla/l10n';
import type { MessageEntry } from '.';

/**
 * Parse a `'fluent'`, `'android'`, or `'gettext'` message source as a {@link MessageEntry}.
 *
 * @returns `null` on parse error or unsupported format
 */
export function parseEntry(
  format: string,
  source: string,
): MessageEntry | null {
  try {
    switch (format) {
      case 'fluent': {
        const [id, entry] = fluentParseEntry(source);
        const value = entry['='] ? flatMessage('fluent', entry['=']) : null;
        if (entry['+']) {
          const attributes = new Map<string, Message>();
          for (const [name, value] of Object.entries(entry['+'])) {
            attributes.set(name, flatMessage('fluent', value));
          }
          return { format, id, value, attributes };
        }
        return value ? { format, id, value } : null;
      }

      case 'android':
      case 'gettext':
        return { format, id: '', value: mf2ParseMessage(source) };
    }
  } catch {}
  return null;
}

/**
 * Empty Fluent string literals `{ "" }` are dropped.
 */
function flatMessage(format: FormatKey, msg: Message): Message {
  const flatPattern = (pat: Pattern) => [
    serializePattern(format, pat).replace(/{ "" }/g, ''),
  ];
  if (Array.isArray(msg)) return flatPattern(msg);
  if (msg.msg) return { decl: msg.decl, msg: flatPattern(msg.msg) };
  const flatAlt = msg.alt.map((v) => ({
    keys: v.keys,
    pat: flatPattern(v.pat),
  }));
  return { decl: msg.decl, sel: msg.sel, alt: flatAlt };
}
