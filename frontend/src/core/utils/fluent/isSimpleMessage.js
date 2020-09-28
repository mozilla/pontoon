/* @flow */

import isSimpleElement from './isSimpleElement';

/**
 * Return true when message represents a simple message.
 *
 * A simple message has no attributes and all value
 * elements are simple.
 */
export default function isSimpleMessage(message: Object) {
    if (
        message &&
        message.attributes &&
        !message.attributes.length &&
        message.value &&
        message.value.elements.every(isSimpleElement)
    ) {
        return true;
    }

    return false;
}
