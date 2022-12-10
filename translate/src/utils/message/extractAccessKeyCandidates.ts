import type { Message, Pattern, Term } from '@fluent/syntax';

function getTextRecursively({ elements }: Pattern): string {
  let result = '';
  for (const element of elements) {
    switch (element.type) {
      case 'TextElement':
        result += element.value;
        break;
      case 'Placeable':
        if (element.expression.type === 'SelectExpression') {
          for (const variant of element.expression.variants) {
            result += getTextRecursively(variant.value);
          }
        }
        break;
    }
  }
  return result;
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
  message: Message | Term,
  label: string,
): string[] {
  const getAttr = (name: string) =>
    message.attributes.find((attr) => attr.id.name === name)?.value;

  let source: Pattern | undefined;

  const prefixEnd = label.indexOf('accesskey');
  const prefix = label.substring(0, prefixEnd);

  if (!prefix) {
    // Generate access key candidates from the 'label' attribute or the message value
    source =
      getAttr('label') ??
      message.value ??
      getAttr('value') ??
      getAttr('aria-label');
  } else {
    source = getAttr(`${prefix}label`);
  }
  if (source) {
    const text = getTextRecursively(source);

    const keys = text
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
