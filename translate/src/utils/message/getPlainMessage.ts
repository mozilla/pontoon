import { fluentSerializePattern, Pattern, type Message } from '@mozilla/l10n';
import type { MessageEntry } from '.';
import { parseEntry } from './parseEntry';

/**
 * Return a plain string representation of a given message.
 *
 * @param format The format of the file of the concerned entity.
 * @returns If the format is `'fluent'` or `'gettext'`, return a simplified
 *   version of the translation. Otherwise, return the original translation.
 */
export function getPlainMessage(
  message: string | MessageEntry,
  format: string,
): string {
  if (!message) {
    return '';
  }

  let entry: MessageEntry | null;
  if (typeof message === 'string') {
    entry = parseEntry(format, message);
    if (!entry) {
      return message;
    }
  } else {
    entry = message;
  }

  if (entry.value) {
    return previewMessage(entry.value);
  }

  if (entry.attributes) {
    for (const attr of entry.attributes.values()) {
      const preview = previewMessage(attr);
      if (preview) {
        return preview;
      }
    }
  }

  return '';
}

function previewMessage(message: Message): string {
  // Presumes that the last variant is the most appropriate
  // to use as a generic representation of the message.

  let pattern: Pattern;
  if (Array.isArray(message)) pattern = message;
  else if (message.msg) pattern = message.msg;
  else {
    pattern = message.alt.find((v) =>
      v.keys.every((key) => typeof key !== 'string'),
    )!.pat;
  }

  return fluentSerializePattern(pattern, {
    escapeSyntax: false,
    onError: () => {},
  });
}
