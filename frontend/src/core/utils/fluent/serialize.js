/* @flow */

import { serializeExpression } from '@fluent/syntax';

/**
 * Returns a list of values from a Fluent AST.
 *
 * Walks the given elements' AST and return the most pertinent value for each.
 */
export default function serialize(elements: Array<Object>): Array<any> {
    return elements.map((elt) => {
        if (elt.type === 'TextElement') {
            return elt.value;
        }

        if (elt.type === 'Placeable') {
            if (elt.expression.type === 'SelectExpression') {
                const defaultVariants = elt.expression.variants.filter(
                    (v) => v.default,
                );
                return serialize(defaultVariants[0].value.elements);
            } else {
                const expression = serializeExpression(elt.expression);
                return `{ ${expression} }`;
            }
        }

        return null;
    });
}
