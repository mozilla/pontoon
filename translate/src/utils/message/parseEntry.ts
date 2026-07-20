import {
  fluentParseEntry,
  mf2ParseMessage,
  normalizeMessage,
  propertiesParsePattern,
  type Message,
} from '@mozilla/l10n';
import type { MessageEntry } from '.';
import { specialFormats } from './specialFormats';

/**
 * Parse a message source as a {@link MessageEntry}.
 *
 * @returns `null` on parse error
 */
export function parseEntry(
  format: string,
  source: string,
): MessageEntry | null {
  try {
    if (format === 'fluent') {
      const [id, entry] = fluentParseEntry(source);
      const value = entry['='] ? normalizeMessage(entry['=']) : null;
      if (entry['+']) {
        const attributes = new Map<string, Message>();
        for (const [name, value] of Object.entries(entry['+'])) {
          attributes.set(name, normalizeMessage(value));
        }
        return { format, id, value, attributes };
      }
      return value ? { format, id, value } : null;
    } else if (format === 'properties') {
      return {
        format: 'properties',
        id: '',
        value: propertiesParsePattern(source)
          // FIXME: https://bugzilla.mozilla.org/show_bug.cgi?id=2055465
          .map((el) =>
            typeof el === 'string' ? el.replaceAll('\\r', '\r') : el,
          ),
      };
    } else if (specialFormats.has(format)) {
      return {
        format: format as MessageEntry['format'],
        id: '',
        value: mf2ParseMessage(source),
      };
    } else {
      return { format: 'plain', id: '', value: source ? [source] : [] };
    }
  } catch (error) {
    const msg = error instanceof Error ? error.message : String(error);
    console.warn(`Parse error: ${msg}, with entry source:\n${source}`);
  }
  return null;
}
