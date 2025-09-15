import type { MessageEntry } from '.';
import {
  fluentSerializeEntry,
  mf2SerializeMessage,
  serializePattern,
} from '@mozilla/l10n';

export function serializeEntry(
  format: string,
  entry: MessageEntry | null,
): string {
  if (!entry) {
    return '';
  }

  switch (format) {
    case 'fluent': {
      const attr = entry.attributes
        ? Object.fromEntries(entry.attributes)
        : undefined;
      let msg = entry.value;
      // Ensure that an entry with a non-null value serializes with a non-empty pattern,
      // even if the entry has attributes and would be valid with an empty value.
      if (Array.isArray(msg) && msg.every((p) => p === '')) msg = [{ _: '' }];
      return fluentSerializeEntry(
        entry.id,
        { '=': msg!, '+': attr },
        { escapeSyntax: false },
      );
    }

    case 'gettext':
      return entry.value ? mf2SerializeMessage(entry.value) : '';

    default:
      if (Array.isArray(entry.value)) {
        return serializePattern('plain', entry.value);
      }
  }

  throw new Error(`Unsupported ${format} message [${entry.id}]`);
}
