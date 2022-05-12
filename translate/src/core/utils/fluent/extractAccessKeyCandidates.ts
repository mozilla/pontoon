import type { Entry, Pattern, TextElement } from '@fluent/syntax';

/**
 * Returns a flat list of Text Elements, either standalone or from SelectExpression variants
 */
function getTextElementsRecursively(
  { elements }: Pattern,
  result: TextElement[] = [],
): TextElement[] {
  for (const element of elements) {
    switch (element.type) {
      case 'TextElement':
        result.push(element);
        break;
      case 'Placeable':
        if (element.expression.type === 'SelectExpression') {
          for (const variant of element.expression.variants) {
            getTextElementsRecursively(variant.value, result);
          }
        }
        break;
    }
  }

  return result;
}

/**
 * Return a list of potential access key candidates.
 *
 * The method first checks if the message contains an attribute with an ID 'accesskey',
 * and then generates a list of unique characters from either the attribute with an ID
 * 'label' or the message value.
 *
 * @param {Entry} message A (flat) Fluent message to extract access key candidates from.
 * @returns {?Array<string>} A list of access key candidates.
 */
export function extractAccessKeyCandidates(
  message: Entry,
): Array<string> | null {
  // Safeguard against non-message Fluent entries
  if (message.type !== 'Message') {
    return null;
  }
  // If message has no attributes, return null
  if (!message.attributes) {
    return null;
  }

  const attributeIDs = message.attributes.map((attribute) => attribute.id.name);

  // If message has no accesskey attribute, return null
  if (attributeIDs.indexOf('accesskey') === -1) {
    return null;
  }

  // Generate access key candidates from the 'label' attribute or the message value
  let source = null;
  if (message.attributes && attributeIDs.indexOf('label') !== -1) {
    source = message.attributes.find(
      (attribute) => attribute.id.name === 'label',
    );
  } else if (message.value) {
    source = message;
  }

  if (!source || !source.value) {
    return null;
  }

  const textElements = getTextElementsRecursively(source.value);

  // Collect values of TextElements
  const values = textElements.map((element) => {
    let value = '';
    if (element && typeof element.value === 'string') {
      value = element.value
        // Exclude placeables (message is flat). See bug 1447103 for details.
        .replace(/{[^}]*}/g, '')
        // Exclude whitespace
        .replace(/\s/g, '');
    }
    return value;
  });

  // Create a list of single-character keys
  const keys = values.join('').split('');

  // Extract unique candidates
  return keys.filter((key, i, array) => array.indexOf(key) === i);
}
