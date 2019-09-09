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
    let simpleElements = [];

    elements.forEach((element, index) => {
        if (element.type === 'Placeable' && element.expression.type === 'SelectExpression') {
            // Before adding SelectExpression merge collected simple elements into a TextElement
            if (simpleElements.length) {
                flatElements.push(new TextElement(simpleElements.join('')));
                simpleElements = [];
            }

            // Flatten SelectExpression variant elements
            element.expression.variants.forEach(variant => {
                variant.value.elements = flattenElements(variant.value.elements);
            });

            flatElements.push(element);
        }
        else {
            if (element.type === 'TextElement') {
                simpleElements.push(element.value);
            }
            else {
                simpleElements.push(serializeExpression(element));
            }

            // Before the end of loop merge collected simple elements into a TextElement
            if (index === elements.length - 1) {
                flatElements.push(new TextElement(simpleElements.join('')));
            }
        }
    });

    return flatElements;
}
