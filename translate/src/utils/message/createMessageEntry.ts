import type { Message } from '@mozilla/l10n';
import type { MessageEntry } from '.';

export function createMessageEntry(
  format: MessageEntry['format'],
  id: string,
  value: Message,
  properties?: Record<string, Message>,
): MessageEntry {
  if (format === 'fluent' && properties) {
    const attributes = new Map(Object.entries(properties));
    const value_ = Array.isArray(value) && value.length === 0 ? null : value;
    return { format, id, value: value_, attributes };
  } else {
    return { format, id, value };
  }
}
