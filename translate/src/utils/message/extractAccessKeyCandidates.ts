import type { Message, Pattern } from 'messageformat';
import type { MessageEntry } from '.';

function getPatternText({ body }: Pattern): string {
  let res = '';
  for (const el of body) {
    if (el.type === 'text') {
      res += el.value;
    }
  }
  return res;
}

function getMessageText(message: Message): string {
  switch (message.type) {
    case 'message':
      return getPatternText(message.pattern);
    case 'select': {
      let res = '';
      for (const { value } of message.variants) {
        res += getPatternText(value);
      }
      return res;
    }
  }
  return '';
}

/**
 * Return a set of potential access key candidates from either the attribute
 * with an ID `label` or the message value.
 *
 * @param message A (flat) Fluent message to extract access key candidates from.
 * @param label The label of the current key; expected to end with `accesskey`
 * @returns A set of access key candidates.
 */
export function extractAccessKeyCandidates(
  message: MessageEntry,
  label: string,
): string[] {
  let source: Message | undefined;

  const prefixEnd = label.indexOf('accesskey');
  const prefix = label.substring(0, prefixEnd);

  if (!prefix) {
    // Generate access key candidates from the 'label' attribute or the message value
    source =
      message.attributes?.get('label') ??
      message.value ??
      message.attributes?.get('value') ??
      message.attributes?.get('aria-label');
  } else {
    source = message.attributes?.get(`${prefix}label`);
  }
  if (source) {
    const keys = getMessageText(source)
      // Exclude placeables (message is flat). See bug 1447103 for details.
      .replace(/{[^}]*}/g, '')
      .replace(/[^\p{Letter}\p{Number}]/gu, '')
      .split('');

    // Extract unique candidates
    return Array.from(new Set(keys));
  } else {
    return [];
  }
}
