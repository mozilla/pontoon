import type { EditorMessage } from '~/context/Editor';

/**
 * Return a set of potential access key candidates from either the attribute
 * with an ID `label` or the message value.
 *
 * @param label The label of the current key; expected to end with `accesskey`
 * @returns A set of access key candidates.
 */
export function extractAccessKeyCandidates(
  message: EditorMessage,
  label: string,
): string[] {
  let source: string | undefined;

  const prefixEnd = label.indexOf('accesskey');
  const prefix = label.substring(0, prefixEnd);

  if (prefix) {
    const name = `${prefix}label`;
    source = message
      .filter((field) => field.name === name)
      .map((field) => field.value)
      .join('');
  } else {
    // Generate access key candidates from the 'label' attribute or the message value
    for (const name of ['label', '', 'value', 'aria-label']) {
      const field = message.filter((field) => field.name === name);
      if (field.length) {
        source = field.map((field) => field.value).join('');
        break;
      }
    }
  }
  if (!source) {
    return [];
  }

  const keys = source
    // Exclude placeables (message is flat). See bug 1447103 for details.
    .replace(/{[^}]*}/g, '')
    .replace(/[^\p{Letter}\p{Number}]/gu, '');

  // Extract unique candidates
  return Array.from(new Set(keys.split('')));
}
