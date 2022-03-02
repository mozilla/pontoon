import flattenPatternElements from './flattenPatternElements';

import type { Entry } from '@fluent/syntax';

/**
 * Return a flattened Fluent message.
 *
 * Takes a Fluent message and returns a copy with flattened value and
 * attributes elements.
 *
 * @param {Entry} message A Fluent message to flatten.
 *
 * @returns {Entry} A copy of the given Fluent message with flattened
 * value and attributes elements.
 */
export default function flattenMessage(message: Entry): Entry {
    const flatMessage = message.clone();
    if (flatMessage.type !== 'Message' && flatMessage.type !== 'Term') {
        return flatMessage;
    }

    if (flatMessage.value && flatMessage.value.elements.length > 0) {
        flatMessage.value.elements = flattenPatternElements(
            flatMessage.value.elements,
        );
    }

    if (flatMessage.attributes) {
        flatMessage.attributes.forEach((attribute) => {
            if (attribute.value && attribute.value.elements.length > 0) {
                attribute.value.elements = flattenPatternElements(
                    attribute.value.elements,
                );
            }
        });
    }

    return flatMessage;
}
