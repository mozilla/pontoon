/* @flow */

import areSupportedElements from './areSupportedElements';

/**
 * Return true when message represents a message, supported in rich FTL editor.
 *
 * Message is supported if it's valid and all value elements
 * and all attribute elements are supported.
 */
export default function isSupportedMessage(message: Object) {
    // Parse error
    if (message.type === 'Junk') {
        return false;
    }

    if (message.value && !areSupportedElements(message.value.elements)) {
        return false;
    }

    return message.attributes.every((attribute) => {
        return (
            attribute.value && areSupportedElements(attribute.value.elements)
        );
    });
}
