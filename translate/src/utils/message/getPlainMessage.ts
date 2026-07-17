import type { Message, Pattern } from '@mozilla/l10n';
import type { MessageEntry } from '.';
import { editablePattern } from './editablePattern';

/** A plain string representation of a message entry.  */
export function getPlainMessage(entry: MessageEntry): string {
  if (entry.value) {
    const preview = previewMessage(entry.format, entry.value);
    if (preview) {
      return preview;
    }
  }

  if (entry.attributes) {
    for (const attr of entry.attributes.values()) {
      const preview = previewMessage(entry.format, attr);
      if (preview) {
        return preview;
      }
    }
  }

  return '';
}

function previewMessage(
  format: MessageEntry['format'],
  message: Message,
): string {
  let pattern: Pattern;
  if (Array.isArray(message)) {
    pattern = message;
  } else if (message.msg) {
    pattern = message.msg;
  } else {
    const catchall =
      message.alt.find((v) => v.keys.every((key) => typeof key !== 'string')) ??
      message.alt.at(-1)!;
    pattern = catchall.pat;
  }

  return editablePattern(format, pattern);
}
