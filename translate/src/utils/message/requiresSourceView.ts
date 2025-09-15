import { isSelectMessage } from '@mozilla/l10n';
import type { MessageEntry } from '.';

const MAX_RICH_VARIANTS = 15;

/** If `true`, the message can only be shown in an FTL source editor.  */
export function requiresSourceView(entry: MessageEntry): boolean {
  if (entry.format !== 'fluent') {
    return false;
  }
  if (!entry.id) {
    return true;
  }

  let fieldCount = !entry.value
    ? 0
    : isSelectMessage(entry.value)
      ? entry.value.alt.length
      : 1;

  if (entry.attributes) {
    for (const attr of entry.attributes.values()) {
      fieldCount += isSelectMessage(attr) ? attr.alt.length : 1;
    }
  }

  return fieldCount === 0 || fieldCount > MAX_RICH_VARIANTS;
}
