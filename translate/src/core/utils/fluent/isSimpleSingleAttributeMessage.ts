import type { Entry } from '@fluent/syntax';

import { isSimpleElement } from './isSimpleElement';

/**
 * Return true when message has no value and a single attribute with only simple
 * elements.
 */
export function isSimpleSingleAttributeMessage(message: Entry): boolean {
  if (
    message.type === 'Message' &&
    !message.value &&
    message.attributes &&
    message.attributes.length === 1 &&
    message.attributes[0].value.elements.every(isSimpleElement)
  ) {
    return true;
  }

  return false;
}
