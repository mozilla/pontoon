/* @flow */

import isSimpleElement from './isSimpleElement';
import type { FluentMessage } from './types';

/**
 * Return true when message has no value and a single attribute with only simple
 * elements.
 */
export default function isSimpleSingleAttributeMessage(
    message: FluentMessage,
): boolean {
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
