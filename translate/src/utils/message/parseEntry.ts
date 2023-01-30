import { Resource } from '@fluent/syntax';
import { fluentToResourceData } from '@messageformat/fluent';
import type { MessageEntry } from '.';
import { parseFlatFluent } from './parseFlatFluent';

/**
 * Parse Fluent source
 *
 * @returns `null` on parse error
 */
export function parseEntry(source: string): MessageEntry | null {
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
  return null;
}
