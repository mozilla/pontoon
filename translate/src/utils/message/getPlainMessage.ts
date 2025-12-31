import {
  fluentSerializePattern,
  Pattern,
  serializePattern,
  type Message,
} from '@mozilla/l10n';
import type { MessageEntry } from '.';
import { parseEntry } from './parseEntry';
import { editablePattern } from './placeholders';

/**
 * Return a plain string representation of a given message.
 *
 * @param format The format of the file of the concerned entity.
 * @returns If the format is `'fluent'`, `'android'`, or `'gettext'`, return a simplified
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
    return previewMessage(format, entry.value);
  }

  if (entry.attributes) {
    for (const attr of entry.attributes.values()) {
      const preview = previewMessage(format, attr);
      if (preview) {
        return preview;
      }
    }
  }

  return '';
}

function previewMessage(format: string, message: Message): string {
  let pattern: Pattern;
  if (Array.isArray(message)) pattern = message;
  else if (message.msg) pattern = message.msg;
  else {
    const catchall =
      message.alt.find((v) => v.keys.every((key) => typeof key !== 'string')) ??
      message.alt.at(-1)!;
    pattern = catchall.pat;
  }

  return format === 'fluent'
    ? fluentSerializePattern(pattern, {
        escapeSyntax: false,
        onError: () => {},
      })
    : editablePattern(pattern);
}
