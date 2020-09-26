/* @flow */

import flattenDeep from 'lodash.flattendeep';

import parser from './parser';
import serialize from './serialize';

/**
 * Turn a Fluent message into a simple string, without any syntax sigils.
 *
 * This function returns the most pertinent content that can be found in the
 * message, without the ID, attributes or selectors.
 *
 * For example:
 *   > my-message = Hello, World!
 *   "Hello, World!"
 *
 *   > my-selector =
 *   >     I like { $gender ->
 *   >        [male] him
 *   >        [female] her
 *   >       *[other] them
 *   >     }
 *   "I like them"
 *
 * @param {string} content A Fluent string to parse and simplify.
 *
 * @returns {string} A simplified version of the Fluent message, or the original
 * content if it isn't a valid Fluent message.
 */
export default function getSimplePreview(content: ?string) {
    if (!content) {
        return '';
    }

    const message = parser.parseEntry(content);

    if (message.type === 'Junk') {
        return content;
    }

    let tree;
    if (message.value) {
        tree = message;
    } else {
        tree = message.attributes[0];
    }

    let elements = serialize(tree.value.elements);

    return flattenDeep(elements).join('');
}
