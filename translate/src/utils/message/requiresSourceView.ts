import type { MessageEntry } from '.';

const MAX_RICH_VARIANTS = 15;

/** If `true`, the message can only be shown in an FTL source editor.  */
export function requiresSourceView(
  format: string,
  entry: MessageEntry | null,
): boolean {
  if (format !== 'fluent') {
    return false;
  }
  if (!entry || !entry.id) {
    return true;
  }

  let fieldCount = !entry.value
    ? 0
    : entry.value.type === 'select'
      ? entry.value.variants.length
      : 1;

  if (entry.attributes) {
    for (const attr of entry.attributes.values()) {
      fieldCount += attr.type === 'select' ? attr.variants.length : 1;
    }
  }

  return fieldCount === 0 || fieldCount > MAX_RICH_VARIANTS;
}
