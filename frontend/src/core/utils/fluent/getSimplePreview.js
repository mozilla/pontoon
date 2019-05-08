/* @flow */

import { FluentParser, serializeExpression } from 'fluent-syntax';
import flattenDeep from 'lodash.flattendeep';


const parser = new FluentParser({ withSpans: false });


/**
 * Returns a list of values from a Fluent AST.
 *
 * Walks the given elements' AST and return the most pertinent value for each.
 */
function serialize(elements) {
    return elements.map(elt => {
        if (elt.type === 'TextElement') {
            return elt.value;
        }

        if (elt.type === 'Placeable') {
            if (elt.expression.type === 'SelectExpression') {
                const defaultVariants = elt.expression.variants.filter(v => v.default);
                return serialize(defaultVariants[0].value.elements);
            }
            else {
                const expression = serializeExpression(elt.expression);
                return `{ ${expression} }`;
            }
        }

        return null;
    });
}


/**
 * Turn a Fluent message into a simple version of that message.
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
    }
    else {
        tree = message.attributes[0];
    }

    let elements = serialize(tree.value.elements);

    return flattenDeep(elements).join('');
}
