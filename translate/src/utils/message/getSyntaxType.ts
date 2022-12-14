import type { Entry, PatternElement } from '@fluent/syntax';

import { isSimpleElement } from './isSimpleElement';
import { isSimpleSingleAttributeMessage } from './isSimpleSingleAttributeMessage';

/**
 * Return the syntax type of a given Fluent message.
 *
 * @returns One of:
 *   - `'simple'`: can be shown as a simple string using the generic editor
 *   - `'rich'`: can be shown in a rich editor
 *   - `'complex'`: can only be shown in a source editor
 */
export function getSyntaxType(message: Entry): 'simple' | 'rich' | 'complex' {
  if (!message || !isSupportedMessage(message)) {
    return 'complex';
  }

  if (isSimpleMessage(message) || isSimpleSingleAttributeMessage(message)) {
    return 'simple';
  }

  return 'rich';
}

/**
 * Return true when message represents a message, supported in rich FTL editor.
 *
 * Message is supported if it's valid and all value elements
 * and all attribute elements are supported.
 */
function isSupportedMessage({ attributes, type, value }: Entry): boolean {
  if (
    // Parse error
    type === 'Junk' ||
    // Comments
    type === 'Comment' ||
    type === 'GroupComment' ||
    type === 'ResourceComment'
  ) {
    return false;
  }

  if (value && !areSupportedElements(value.elements)) {
    return false;
  }

  return attributes.every(
    ({ value }) => value && areSupportedElements(value.elements),
  );
}

/**
 * Return true when all elements are supported in rich FTL editor.
 *
 * Elements are supported if they are:
 * - simple elements or
 * - select expressions, whose variants are simple elements
 */
const areSupportedElements = (elements: PatternElement[]) =>
  elements.every(
    (element) =>
      isSimpleElement(element) ||
      (element.type === 'Placeable' &&
        element.expression.type === 'SelectExpression' &&
        element.expression.variants.every((variant) =>
          variant.value.elements.every((element) => isSimpleElement(element)),
        )),
  );

/**
 * Return true when message represents a simple message.
 *
 * A simple message has no attributes and all value
 * elements are simple.
 */
const isSimpleMessage = ({ attributes, type, value }: Entry) =>
  (type === 'Message' || type === 'Term') &&
  !attributes?.length &&
  !!value?.elements.every(isSimpleElement);
