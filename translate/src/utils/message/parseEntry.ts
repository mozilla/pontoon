import { Resource } from '@fluent/syntax';
import { fluentToResourceData } from '@messageformat/fluent';
import { parseMessage } from 'messageformat';
import type { MessageEntry } from '.';
import { parseFlatFluent } from './parseFlatFluent';

/**
 * Parse `'fluent'` or `'gettext'` message source as a {@link MessageEntry}.
 *
 * @returns `null` on parse error or unsupported format
 */
export function parseEntry(
  format: string,
  source: string,
): MessageEntry | null {
  switch (format) {
    case 'fluent': {
      const fluentEntry = parseFlatFluent(source);
      const { data } = fluentToResourceData(new Resource([fluentEntry]));
      for (const [id, attributes] of data) {
        const value = attributes.get('') ?? null;
        if (value && attributes.size === 1) {
          return { id, value };
        }
        attributes.delete('');
        return { id, value, attributes };
      }
      break;
    }
    case 'gettext':
      return { id: '', value: parseMessage(source) };
  }
  return null;
}
