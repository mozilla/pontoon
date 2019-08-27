/* @flow */

import { TextElement, serializeExpression } from 'fluent-syntax';

import type { FluentElement } from './types';


/**
 * Return a flattened list of Fluent elements.
 *
 * Takes a list of Fluent SyntaxNode elements, extracts a serialized value for
 * each and returns an array with a single TextElement containing those values.
 *
 * @param {Array<SyntaxNode>} elements A list of Fluent SyntaxNode lements to flatten.
 *
 * @returns {Array<TextElement>} An array containing a single TextElement which
 * contains all elements' values serialized.
 */
export default function flattenElements(elements: Array<FluentElement>): Array<FluentElement> {
    const values = elements.map(element => {
        switch (element.type) {
            case 'TextElement':
                return element.value;
            default:
                return serializeExpression(element);
        }
    });

    return [
        new TextElement(values.join('')),
    ];
}
