/* @flow */

import flattenPatternElements from './flattenPatternElements';

import type { FluentMessage } from './types';

/**
 * Return a flattened Fluent message.
 *
 * Takes a Fluent message and returns a copy with flattened value and
 * attributes elements.
 *
 * @param {FluentMessage} message A Fluent message to flatten.
 *
 * @returns {FluentMessage} A copy of the given Fluent message with flattened
 * value and attributes elements.
 */
export default function flattenMessage(message: FluentMessage): FluentMessage {
    const flatMessage = message.clone();

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
