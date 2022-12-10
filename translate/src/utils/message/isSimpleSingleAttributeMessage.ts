import type { Attribute, Entry, Message } from '@fluent/syntax';

import { isSimpleElement } from './isSimpleElement';

/**
 * Return true when message has no value and a single attribute with only simple
 * elements.
 */
export function isSimpleSingleAttributeMessage(
  message: Entry,
): message is Message & { value: never; attributes: [Attribute] } {
  const { attributes, type, value } = message;
  return (
    type === 'Message' &&
    !value &&
    attributes?.length === 1 &&
    attributes[0].value.elements.every(isSimpleElement)
  );
}
