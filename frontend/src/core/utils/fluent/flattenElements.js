/* @flow */

import { TextElement, serializeExpression } from 'fluent-syntax';

import type { FluentElement } from './types';


/**
 * Return a flattened list of Fluent elements.
 *
 * @param {Array<SyntaxNode>} elements A list of Fluent SyntaxNode elements to flatten.
 *
 * @returns {Array<TextElement|Placeable>} An array containing elements of type
 * TextElement (merging serialized values of neighbour simple elements) and
 * Placeable (representing select expressions).
 */
export default function flattenElements(elements: Array<FluentElement>): Array<FluentElement> {
    const flatElements = [];
    let textFragments = [];

    elements.forEach(element => {
        if (
            element.type === 'Placeable' &&
            element.expression && element.expression.type === 'SelectExpression'
        ) {
            // Before adding SelectExpression merge any collected text fragments into a TextElement
            if (textFragments.length) {
                flatElements.push(new TextElement(textFragments.join('')));
                textFragments = [];
            }

            // Flatten SelectExpression variant elements
            element.expression.variants.forEach(variant => {
                variant.value.elements = flattenElements(variant.value.elements);
            });

            flatElements.push(element);
        }
        else {
            if (element.type === 'TextElement' && typeof(element.value) === 'string') {
                textFragments.push(element.value);
            }
            else {
                textFragments.push(serializeExpression(element));
            }
        }
    });

    // Merge any remaining collected text fragments into a TextElement
    if (textFragments.length) {
        flatElements.push(new TextElement(textFragments.join('')));
    }

    return flatElements;
}
