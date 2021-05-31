import isSimpleElement from './isSimpleElement';
import type { Entry } from '@fluent/syntax';

/**
 * Return true when message represents a simple message.
 *
 * A simple message has no attributes and all value
 * elements are simple.
 */
export default function isSimpleMessage(message: Entry): boolean {
    if (
        message &&
        (message.type === 'Message' || message.type === 'Term') &&
        message.attributes &&
        !message.attributes.length &&
        message.value &&
        message.value.elements.every(isSimpleElement)
    ) {
        return true;
    }

    return false;
}
